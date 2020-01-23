/*
 * A virtio device implementing a hardware random number generator.
 *
 * Copyright 2012 Red Hat, Inc.
 * Copyright 2012 Amit Shah <amit.shah@redhat.com>
 *
 * This work is licensed under the terms of the GNU GPL, version 2 or
 * (at your option) any later version.  See the COPYING file in the
 * top-level directory.
 */

#include "qemu/osdep.h"
#include "qapi/error.h"
#include "qemu/iov.h"
#include "qemu/module.h"
#include "qemu/timer.h"
#include "hw/virtio/virtio.h"
#include "hw/qdev-properties.h"
#include "hw/virtio/virtio-rng.h"
#include "sysemu/rng.h"
#include "sysemu/runstate.h"
#include "qom/object_interfaces.h"
#include "trace.h"

static bool is_guest_ready(VirtIORNG *vrng)
{
    VirtIODevice *vdev = VIRTIO_DEVICE(vrng);
    if (virtio_queue_ready(vrng->input_vq)
        && (vdev->status & VIRTIO_CONFIG_S_DRIVER_OK)) {
        return true;
    }
    trace_virtio_rng_guest_not_ready(vrng);
    return false;
}

static size_t get_request_size(VirtQueue *vq, unsigned quota)
{
    unsigned int in, out;

    virtqueue_get_avail_bytes(vq, &in, &out, quota, 0);
    return in;
}

static void virtio_rng_process(VirtIORNG *vrng);

/* Send data from a char device over to the guest */
static void chr_read(void *opaque, const void *buf, size_t size)
{
    VirtIORNG *vrng = opaque;
    VirtIODevice *vdev = VIRTIO_DEVICE(vrng);
    VirtQueueElement *elem;
    size_t len;
    int offset;

    if (!is_guest_ready(vrng)) {
        return;
    }

    /* we can't modify the virtqueue until
     * our state is fully synced
     */

    if (!runstate_check(RUN_STATE_RUNNING)) {
        trace_virtio_rng_cpu_is_stopped(vrng, size);
        return;
    }

    vrng->quota_remaining -= size;

    offset = 0;
    while (offset < size) {
        elem = virtqueue_pop(vrng->input_vq, sizeof(VirtQueueElement));
        if (!elem) {
            break;
        }
        trace_virtio_rng_popped(vrng);
        len = iov_from_buf(elem->in_sg, elem->in_num,
                           0, buf + offset, size - offset);
        offset += len;

        virtqueue_push(vrng->input_vq, elem, len);
        trace_virtio_rng_pushed(vrng, len);
        g_free(elem);
    }
    virtio_notify(vdev, vrng->input_vq);

    if (!virtio_queue_empty(vrng->input_vq)) {
        /* If we didn't drain the queue, call virtio_rng_process
         * to take care of asking for more data as appropriate.
         */
        virtio_rng_process(vrng);
    }
}

static void virtio_rng_process(VirtIORNG *vrng)
{
    size_t size;
    unsigned quota;

    if (!is_guest_ready(vrng)) {
        return;
    }

    if (vrng->activate_timer) {
        timer_mod(vrng->rate_limit_timer,
                  qemu_clock_get_ms(QEMU_CLOCK_VIRTUAL) + vrng->conf.period_ms);
        vrng->activate_timer = false;
    }

    if (vrng->quota_remaining < 0) {
        quota = 0;
    } else {
        quota = MIN((uint64_t)vrng->quota_remaining, (uint64_t)UINT32_MAX);
    }
    size = get_request_size(vrng->input_vq, quota);

    trace_virtio_rng_request(vrng, size, quota);

    size = MIN(vrng->quota_remaining, size);
    if (size) {
        rng_backend_request_entropy(vrng->rng, size, chr_read, vrng);
    }
}

static void virtio_rng_handle_input(VirtIODevice *vdev, VirtQueue *vq)
{
    VirtIORNG *vrng = VIRTIO_RNG(vdev);
    virtio_rng_process(vrng);
}

static virtio_rng_ctrl_ack virtio_rng_flush(VirtIORNG *vrng)
{
    VirtQueueElement *elem;
    VirtIODevice *vdev = VIRTIO_DEVICE(vrng);

    trace_virtio_rng_flush(vrng);
    while (!virtio_queue_empty(vrng->input_vq)) {
        elem = virtqueue_pop(vrng->input_vq, sizeof(VirtQueueElement));
        if (!elem) {
            break;
        }
        trace_virtio_rng_flush_popped(vrng);
        virtqueue_push(vrng->input_vq, elem, 0);
        trace_virtio_rng_flush_pushed(vrng);
        g_free(elem);
    }
    virtio_notify(vdev, vrng->input_vq);

    return VIRTIO_RNG_OK;
}

static void virtio_rng_handle_ctrl(VirtIODevice *vdev, VirtQueue *vq)
{
    VirtIORNG *vrng = VIRTIO_RNG(vdev);
    VirtQueueElement *elem;
    virtio_rng_ctrl_ack status = VIRTIO_RNG_ERR;
    struct virtio_rng_ctrl_hdr ctrl;
    size_t s;

    trace_virtio_rng_ctrl(vrng);
    for (;;) {
        elem = virtqueue_pop(vq, sizeof(VirtQueueElement));
        if (!elem) {
            break;
        }
        trace_virtio_rng_ctrl_popped(vrng);

        if (iov_size(elem->in_sg, elem->in_num) < sizeof(status) ||
            iov_size(elem->out_sg, elem->out_num) < sizeof(ctrl)) {
            virtio_error(vdev, "virtio-rng ctrl missing headers");
            virtqueue_detach_element(vq, elem, 0);
            g_free(elem);
            break;
        }

        s = iov_to_buf(elem->out_sg, elem->out_num, 0, &ctrl, sizeof(ctrl));
        if (s != sizeof(ctrl)) {
            status = VIRTIO_RNG_ERR;
        } else if (ctrl.cmd == VIRTIO_RNG_CMD_FLUSH) {
            status = virtio_rng_flush(vrng);
        }

        s = iov_from_buf(elem->in_sg, elem->in_num, 0, &status, sizeof(status));
        assert(s == sizeof(status));

        virtqueue_push(vq, elem, sizeof(status));
        trace_virtio_rng_ctrl_pushed(vrng);
        virtio_notify(vdev, vq);
        g_free(elem);
    }
}

static uint64_t virtio_rng_get_features(VirtIODevice *vdev, uint64_t features,
                                        Error **errp)
{
    VirtIORNG *vrng = VIRTIO_RNG(vdev);

    features |= vrng->conf.host_features;

    return features;
}

static void virtio_rng_vm_state_change(void *opaque, int running,
                                       RunState state)
{
    VirtIORNG *vrng = opaque;

    trace_virtio_rng_vm_state_change(vrng, running, state);

    /* We may have an element ready but couldn't process it due to a quota
     * limit or because CPU was stopped.  Make sure to try again when the
     * CPU restart.
     */

    if (running && is_guest_ready(vrng)) {
        virtio_rng_process(vrng);
    }
}

static void check_rate_limit(void *opaque)
{
    VirtIORNG *vrng = opaque;

    vrng->quota_remaining = vrng->conf.max_bytes;
    virtio_rng_process(vrng);
    vrng->activate_timer = true;
}

static void virtio_rng_set_status(VirtIODevice *vdev, uint8_t status)
{
    VirtIORNG *vrng = VIRTIO_RNG(vdev);

    if (!vdev->vm_running) {
        return;
    }
    vdev->status = status;

    /* Something changed, try to process buffers */
    virtio_rng_process(vrng);
}

static void virtio_rng_device_realize(DeviceState *dev, Error **errp)
{
    VirtIODevice *vdev = VIRTIO_DEVICE(dev);
    VirtIORNG *vrng = VIRTIO_RNG(dev);
    Error *local_err = NULL;

    if (vrng->conf.period_ms <= 0) {
        error_setg(errp, "'period' parameter expects a positive integer");
        return;
    }

    /* Workaround: Property parsing does not enforce unsigned integers,
     * So this is a hack to reject such numbers. */
    if (vrng->conf.max_bytes > INT64_MAX) {
        error_setg(errp, "'max-bytes' parameter must be non-negative, "
                   "and less than 2^63");
        return;
    }

    if (vrng->conf.rng == NULL) {
        Object *default_backend = object_new(TYPE_RNG_BUILTIN);

        user_creatable_complete(USER_CREATABLE(default_backend),
                                &local_err);
        if (local_err) {
            error_propagate(errp, local_err);
            object_unref(default_backend);
            return;
        }

        object_property_add_child(OBJECT(dev), "default-backend",
                                  default_backend, &error_abort);

        /* The child property took a reference, we can safely drop ours now */
        object_unref(default_backend);

        object_property_set_link(OBJECT(dev), default_backend,
                                 "rng", &error_abort);
    }

    vrng->rng = vrng->conf.rng;
    if (vrng->rng == NULL) {
        error_setg(errp, "'rng' parameter expects a valid object");
        return;
    }

    virtio_init(vdev, "virtio-rng", VIRTIO_ID_RNG, 0);

    vrng->input_vq = virtio_add_queue(vdev, 8, virtio_rng_handle_input);
    if (virtio_has_feature(vrng->conf.host_features, VIRTIO_RNG_F_CTRL_VQ)) {
        vrng->ctrl_vq = virtio_add_queue(vdev, 8, virtio_rng_handle_ctrl);
    }
    vrng->quota_remaining = vrng->conf.max_bytes;
    vrng->rate_limit_timer = timer_new_ms(QEMU_CLOCK_VIRTUAL,
                                               check_rate_limit, vrng);
    vrng->activate_timer = true;

    vrng->vmstate = qemu_add_vm_change_state_handler(virtio_rng_vm_state_change,
                                                     vrng);
}

static void virtio_rng_device_unrealize(DeviceState *dev, Error **errp)
{
    VirtIODevice *vdev = VIRTIO_DEVICE(dev);
    VirtIORNG *vrng = VIRTIO_RNG(dev);

    qemu_del_vm_change_state_handler(vrng->vmstate);
    timer_del(vrng->rate_limit_timer);
    timer_free(vrng->rate_limit_timer);
    if (virtio_has_feature(vrng->conf.host_features, VIRTIO_RNG_F_CTRL_VQ)) {
        virtio_delete_queue(vrng->ctrl_vq);
    }
    virtio_delete_queue(vrng->input_vq);
    virtio_cleanup(vdev);
}

static const VMStateDescription vmstate_virtio_rng = {
    .name = "virtio-rng",
    .minimum_version_id = 1,
    .version_id = 1,
    .fields = (VMStateField[]) {
        VMSTATE_VIRTIO_DEVICE,
        VMSTATE_END_OF_LIST()
    },
};

static Property virtio_rng_properties[] = {
    /* Set a default rate limit of 2^47 bytes per minute or roughly 2TB/s.  If
     * you have an entropy source capable of generating more entropy than this
     * and you can pass it through via virtio-rng, then hats off to you.  Until
     * then, this is unlimited for all practical purposes.
     */
    DEFINE_PROP_UINT64("max-bytes", VirtIORNG, conf.max_bytes, INT64_MAX),
    DEFINE_PROP_UINT32("period", VirtIORNG, conf.period_ms, 1 << 16),
    DEFINE_PROP_LINK("rng", VirtIORNG, conf.rng, TYPE_RNG_BACKEND, RngBackend *),
    DEFINE_PROP_BIT64("ctrl-queue", VirtIORNG, conf.host_features,
                      VIRTIO_RNG_F_CTRL_VQ, true),
    DEFINE_PROP_END_OF_LIST(),
};

static void virtio_rng_class_init(ObjectClass *klass, void *data)
{
    DeviceClass *dc = DEVICE_CLASS(klass);
    VirtioDeviceClass *vdc = VIRTIO_DEVICE_CLASS(klass);

    dc->props = virtio_rng_properties;
    dc->vmsd = &vmstate_virtio_rng;
    set_bit(DEVICE_CATEGORY_MISC, dc->categories);
    vdc->realize = virtio_rng_device_realize;
    vdc->unrealize = virtio_rng_device_unrealize;
    vdc->get_features = virtio_rng_get_features;
    vdc->set_status = virtio_rng_set_status;
}

static const TypeInfo virtio_rng_info = {
    .name = TYPE_VIRTIO_RNG,
    .parent = TYPE_VIRTIO_DEVICE,
    .instance_size = sizeof(VirtIORNG),
    .class_init = virtio_rng_class_init,
};

static void virtio_register_types(void)
{
    type_register_static(&virtio_rng_info);
}

type_init(virtio_register_types)
