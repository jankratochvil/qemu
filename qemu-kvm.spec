# Build time setting
%define rhev 1

%if %{rhev}
    %bcond_with     guest_agent     # disabled
%else
    %bcond_without  guest_agent     # enabled
%endif

%global SLOF_gittagdate 20120731

%global have_usbredir 1

%ifarch %{ix86} x86_64
    %global have_seccomp 1
    %global have_spice   1
%else
    %global have_usbredir 0
%endif

%ifnarch x86_64
    %global build_only_sub 1
    %global debug_package %{nil}
%endif

%ifarch %{ix86}
    %global kvm_target    i386
%endif
%ifarch x86_64
    %global kvm_target    x86_64
%endif
%ifarch ppc64
    %global kvm_target    ppc64
%endif
%ifarch s390x
    %global kvm_target    s390x
%endif

#Versions of various parts:

%define pkgname qemu-kvm
%define rhel_suffix -rhel
%define rhev_suffix -rhev

# Setup for RHEL/RHEV package handling
# We need to define tree suffixes:
# - pkgsuffix:             used for package name
# - extra_provides_suffix: used for dependency checking of other packages
# - conflicts_suffix:      used to prevent installation of both RHEL and RHEV

%if %{rhev}
    %global pkgsuffix %{rhev_suffix}
    %global extra_provides_suffix %{nil}
    %global conflicts_suffix %{rhel_suffix}
    %global obsoletes_version 15:0-0
%else
    %global pkgsuffix %{nil}
    %global extra_provides_suffix %{rhel_suffix}
    %global conflicts_suffix %{rhev_suffix}
%endif

# Macro to properly setup RHEL/RHEV conflict handling
%define rhel_rhev_conflicts()                                         \
Conflicts: %1%{conflicts_suffix}                                      \
Provides: %1%{extra_provides_suffix} = %{epoch}:%{version}-%{release} \
    %if 0%{?obsoletes_version:1}                                          \
Obsoletes: %1 < %{obsoletes_version}                                      \
    %endif

Summary: QEMU is a FAST! processor emulator
Name: %{pkgname}%{?pkgsuffix}
Version: 1.5.3
Release: 18%{?dist}
# Epoch because we pushed a qemu-1.0 package. AIUI this can't ever be dropped
Epoch: 10
License: GPLv2+ and LGPLv2+ and BSD
Group: Development/Tools
URL: http://www.qemu.org/
# RHEV will build Qemu only on x86_64:
%if %{rhev}
ExclusiveArch: x86_64
%endif
Requires: seabios-bin
Requires: sgabios-bin
Requires: seavgabios-bin
Requires: ipxe-roms-qemu
Requires: %{pkgname}-common%{?pkgsuffix} = %{epoch}:%{version}-%{release}
        %if 0%{?have_seccomp:1}
Requires: libseccomp >= 1.0.0
        %endif

# OOM killer breaks builds with parallel make on s390(x)
%ifarch s390 s390x
    %define _smp_mflags %{nil}
%endif

Source0: http://wiki.qemu-project.org/download/qemu-%{version}.tar.bz2

Source1: qemu.binfmt
# Loads kvm kernel modules at boot
# Not needed anymore - required only for kvm on non i86 archs 
# where we do not ubuild kvm
# Source2: kvm.modules
# Creates /dev/kvm
Source3: 80-kvm.rules
# KSM control scripts
Source4: ksm.service
Source5: ksm.sysconfig
Source6: ksmctl.c
Source7: ksmtuned.service
Source8: ksmtuned
Source9: ksmtuned.conf
Source10: qemu-guest-agent.service
Source11: 99-qemu-guest-agent.rules
Source12: bridge.conf
Source13: qemu-ga.sysconfig
Source14: rhel6-virtio.rom
Source15: rhel6-pcnet.rom
Source16: rhel6-rtl8139.rom
Source17: rhel6-ne2k_pci.rom

# libcacard build fixes (heading upstream)
Patch1: 0000-libcacard-fix-missing-symbols-in-libcacard.so.patch

# Fix migration from qemu-kvm 1.2 to qemu 1.3
#Patch3: 0002-Fix-migration-from-qemu-kvm-1.2.patch

# Flow control series
#Patch4: 0100-char-Split-out-tcp-socket-close-code-in-a-separate-f.patch
#Patch5: 0101-char-Add-a-QemuChrHandlers-struct-to-initialise-char.patch
#Patch6: 0102-iohandlers-Add-enable-disable_write_fd_handler-funct.patch
#Patch7: 0103-char-Add-framework-for-a-write-unblocked-callback.patch
#Patch8: 0104-char-Update-send_all-to-handle-nonblocking-chardev-w.patch
#Patch9: 0105-char-Equip-the-unix-tcp-backend-to-handle-nonblockin.patch
#Patch10: 0106-char-Throttle-when-host-connection-is-down.patch
#Patch11: 0107-virtio-console-Enable-port-throttling-when-chardev-i.patch
#Patch12: 0108-spice-qemu-char.c-add-throttling.patch
#Patch13: 0109-spice-qemu-char.c-remove-intermediate-buffer.patch
#Patch14: 0110-usb-redir-Add-flow-control-support.patch
#Patch15: 0111-char-Disable-write-callback-if-throttled-chardev-is-.patch
#Patch16: 0112-hw-virtio-serial-bus-replay-guest-open-on-destinatio.patch

# Migration compatibility
#Patch17: configure-add-enable-migration-from-qemu-kvm.patch
#Patch18: acpi_piix4-condition-on-minimum_version_id.patch
#Patch19: i8254-fix-migration-from-qemu-kvm-1.1.patch
#Patch20: pc_piix-add-compat-handling-for-qemu-kvm-vga-mem-size.patch
#Patch21: qxl-add-rom_size-compat-property.patch
#Patch22: docs-fix-generating-qemu-doc.html-with-texinfo5.patch
#Patch23: rtc-test-Fix-test-failures-with-recent-glib.patch
#Patch24: iscsi-look-for-pkg-config-file-too.patch
#Patch25: tcg-fix-occcasional-tcg-broken-problem.patch
#Patch26: qxl-better-vga-init-in-enter_vga_mode.patch

# Enable/disable supported features
#Patch27: make-usb-devices-configurable.patch
#Patch28: fix-scripts-make_device_config-sh.patch
Patch29: disable-unsupported-usb-devices.patch
Patch30: disable-unsupported-emulated-scsi-devices.patch
Patch31: disable-various-unsupported-devices.patch
Patch32: disable-unsupported-audio-devices.patch
Patch33: disable-unsupported-emulated-network-devices.patch
Patch34: use-kvm-by-default.patch
Patch35: disable-hpet-device.patch
Patch36: rename-man-page-to-qemu-kvm.patch
Patch37: change-path-from-qemu-to-qemu-kvm.patch

# Fix CPUID model/level values on Conroe/Penryn/Nehalem CPU models 
Patch38: pc-replace-upstream-machine-types-by-rhel7-types.patch
Patch39: target-i386-update-model-values-on-conroe-penryn-nehalem-cpu-models.patch
Patch40: target-i386-set-level-4-on-conroe-penryn-nehalem.patch

# RHEL guest( sata disk ) can not boot up (rhbz #981723)
#Patch41: ahci-Fix-FLUSH-command.patch
# Kill the "use flash device for BIOS unless KVM" misfeature (rhbz #963280)
Patch42: pc-Disable-the-use-flash-device-for-BIOS-unless-KVM-misfeature.patch
# Provide RHEL-6 machine types (rhbz #983991)
Patch43: qemu-kvm-Fix-migration-from-older-version-due-to-i8254-changes.patch
Patch44: pc-Add-machine-type-rhel6-0-0.patch
Patch45: pc-Drop-superfluous-RHEL-6-compat_props.patch
Patch46: vga-Default-vram_size_mb-to-16-like-prior-versions-of-RHEL.patch
Patch47: pc-Drop-RHEL-6-USB-device-compat_prop-full-path.patch
Patch48: pc-Drop-RHEL-6-compat_props-virtio-serial-pci-max_ports-vectors.patch
Patch49: pc-Drop-RHEL-6-compat_props-apic-kvm-apic-vapic.patch
Patch50: qxl-set-revision-to-1-for-rhel6-0-0.patch
Patch51: pc-Give-rhel6-0-0-a-kvmclock.patch
Patch52: pc-Add-machine-type-rhel6-1-0.patch
Patch53: pc-Add-machine-type-rhel6-2-0.patch
Patch54: pc-Add-machine-type-rhel6-3-0.patch
Patch55: pc-Add-machine-type-rhel6-4-0.patch
Patch56: pc-Add-machine-type-rhel6-5-0.patch
Patch57: e1000-Keep-capabilities-list-bit-on-for-older-RHEL-machine-types.patch
# Change s3/s4 default to "disable". (rhbz #980840)  
Patch58: misc-disable-s3-s4-by-default.patch
Patch59: pc-rhel6-compat-enable-S3-S4-for-6-1-and-lower-machine-types.patch
# Support Virtual Memory Disk Format in qemu (rhbz #836675)
Patch60: vmdk-Allow-reading-variable-size-descriptor-files.patch
Patch61: vmdk-refuse-to-open-higher-version-than-supported.patch
#Patch62: vmdk-remove-wrong-calculation-of-relative-path.patch
Patch63: block-add-block-driver-read-only-whitelist.patch

# query mem info from monitor would cause qemu-kvm hang [RHEL-7] (rhbz #970047)
Patch64: kvm-char-io_channel_send-don-t-lose-written-bytes.patch
Patch65: kvm-monitor-maintain-at-most-one-G_IO_OUT-watch.patch
# Throttle-down guest to help with live migration convergence (backport to RHEL7.0) (rhbz #985958)
Patch66: kvm-misc-Introduce-async_run_on_cpu.patch
Patch67: kvm-misc-Add-auto-converge-migration-capability.patch
Patch68: kvm-misc-Force-auto-convegence-of-live-migration.patch
# disable (for now) EFI-enabled roms (rhbz #962563)
Patch69: kvm-misc-Disable-EFI-enabled-roms.patch
# qemu-kvm "vPMU passthrough" mode breaks migration, shouldn't be enabled by default (rhbz #853101)
Patch70: kvm-target-i386-Pass-X86CPU-object-to-cpu_x86_find_by_name.patch
Patch71: kvm-target-i386-Disable-PMU-CPUID-leaf-by-default.patch
Patch72: kvm-pc-set-compat-pmu-property-for-rhel6-x-machine-types.patch
# Remove pending watches after virtserialport unplug (rhbz #992900)
# Patch73: kvm-virtio-console-Use-exitfn-for-virtserialport-too.patch
# Containment of error when an SR-IOV device encounters an error... (rhbz #984604)
Patch74: kvm-linux-headers-Update-to-v3-10-rc5.patch
Patch75: kvm-vfio-QEMU-AER-Qemu-changes-to-support-AER-for-VFIO-PCI-devices.patch

# update qemu-ga config & init script in RHEL7 wrt. fsfreeze hook (rhbz 969942)
Patch76: kvm-misc-qga-fsfreeze-main-hook-adapt-to-RHEL-7-RH-only.patch
# RHEL7 does not have equivalent functionality for __com.redhat_qxl_screendump (rhbz 903910)
Patch77: kvm-misc-add-qxl_screendump-monitor-command.patch
# SEP flag behavior for CPU models of RHEL6 machine types should be compatible (rhbz 960216)
Patch78: kvm-pc_piix-disable-CPUID_SEP-for-6-4-0-machine-types-and-below.patch
# crash command can not read the dump-guest-memory file when paging=false [RHEL-7] (rhbz 981582)
Patch79: kvm-dump-Move-stubs-into-libqemustub-a.patch
Patch80: kvm-cpu-Turn-cpu_paging_enabled-into-a-CPUState-hook.patch
Patch81: kvm-memory_mapping-Move-MemoryMappingList-typedef-to-qemu-typedefs-h.patch
Patch82: kvm-cpu-Turn-cpu_get_memory_mapping-into-a-CPUState-hook.patch
Patch83: kvm-dump-Abstract-dump_init-with-cpu_synchronize_all_states.patch
Patch84: kvm-memory_mapping-Improve-qemu_get_guest_memory_mapping-error-reporting.patch
Patch85: kvm-dump-clamp-guest-provided-mapping-lengths-to-ramblock-sizes.patch
Patch86: kvm-dump-introduce-GuestPhysBlockList.patch
Patch87: kvm-dump-populate-guest_phys_blocks.patch
Patch88: kvm-dump-rebase-from-host-private-RAMBlock-offsets-to-guest-physical-addresses.patch
# RHEL 7 qemu-kvm fails to build on F19 host due to libusb deprecated API (rhbz 996469)
Patch89: kvm-usb-host-libusb-Fix-building-with-libusb-git-master-code.patch
# Live migration support in virtio-blk-data-plane (rhbz 995030)
#Patch90: kvm-dataplane-sync-virtio-c-and-vring-c-virtqueue-state.patch
#Patch91: kvm-virtio-clear-signalled_used_valid-when-switching-from-dataplane.patch
#Patch92: kvm-vhost-clear-signalled_used_valid-on-vhost-stop.patch
Patch93: kvm-migration-notify-migration-state-before-starting-thread.patch
Patch94: kvm-dataplane-enable-virtio-blk-x-data-plane-on-live-migration.patch
#Patch95: kvm-dataplane-refuse-to-start-if-device-is-already-in-use.patch
# qemu-img resize can execute successfully even input invalid syntax (rhbz 992935)
Patch96: kvm-qemu-img-Error-out-for-excess-arguments.patch
# For bz#964304 - Windows guest agent service failed to be started
Patch97: kvm-osdep-add-qemu_get_local_state_pathname.patch
# For bz#964304 - Windows guest agent service failed to be started
Patch98: kvm-qga-determine-default-state-dir-and-pidfile-dynamica.patch
# For bz#964304 - Windows guest agent service failed to be started
Patch99: kvm-configure-don-t-save-any-fixed-local_statedir-for-wi.patch
# For bz#964304 - Windows guest agent service failed to be started
Patch100: kvm-qga-create-state-directory-on-win32.patch
# For bz#964304 - Windows guest agent service failed to be started
Patch101: kvm-qga-save-state-directory-in-ga_install_service-RHEL-.patch
# For bz#964304 - Windows guest agent service failed to be started
Patch102: kvm-Makefile-create-.-var-run-when-installing-the-POSIX-.patch
# For bz#980782 - kernel_irqchip defaults to off instead of on without -machine
Patch103: kvm-qemu-option-Fix-qemu_opts_find-for-null-id-arguments.patch
# For bz#980782 - kernel_irqchip defaults to off instead of on without -machine
Patch104: kvm-qemu-option-Fix-qemu_opts_set_defaults-for-corner-ca.patch
# For bz#980782 - kernel_irqchip defaults to off instead of on without -machine
Patch105: kvm-vl-New-qemu_get_machine_opts.patch
# For bz#980782 - kernel_irqchip defaults to off instead of on without -machine
Patch106: kvm-Fix-machine-options-accel-kernel_irqchip-kvm_shadow_.patch
# For bz#980782 - kernel_irqchip defaults to off instead of on without -machine
Patch107: kvm-microblaze-Fix-latent-bug-with-default-DTB-lookup.patch
# For bz#980782 - kernel_irqchip defaults to off instead of on without -machine
Patch108: kvm-Simplify-machine-option-queries-with-qemu_get_machin.patch
# For bz#838170 - Add live migration support for USB [xhci, usb-uas]
Patch109: kvm-pci-add-VMSTATE_MSIX.patch
# For bz#838170 - Add live migration support for USB [xhci, usb-uas]
Patch110: kvm-xhci-add-XHCISlot-addressed.patch
# For bz#838170 - Add live migration support for USB [xhci, usb-uas]
Patch111: kvm-xhci-add-xhci_alloc_epctx.patch
# For bz#838170 - Add live migration support for USB [xhci, usb-uas]
Patch112: kvm-xhci-add-xhci_init_epctx.patch
# For bz#838170 - Add live migration support for USB [xhci, usb-uas]
Patch113: kvm-xhci-add-live-migration-support.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch114: kvm-pc-set-level-xlevel-correctly-on-486-qemu32-CPU-mode.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch115: kvm-pc-Remove-incorrect-rhel6.x-compat-model-value-for-C.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch116: kvm-pc-rhel6.x-has-x2apic-present-on-Conroe-Penryn-Nehal.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch117: kvm-pc-set-compat-CPUID-0x80000001-.EDX-bits-on-Westmere.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch118: kvm-pc-Remove-PCLMULQDQ-from-Westmere-on-rhel6.x-machine.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch119: kvm-pc-SandyBridge-rhel6.x-compat-fixes.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch120: kvm-pc-Haswell-doesn-t-have-rdtscp-on-rhel6.x.patch
# For bz#972433 - "INFO: rcu_sched detected stalls" after RHEL7 kvm vm migrated
Patch121: kvm-i386-fix-LAPIC-TSC-deadline-timer-save-restore.patch
# For bz#996258 - boot guest with maxcpu=255 successfully but actually max number of vcpu is 160
Patch122: kvm-all.c-max_cpus-should-not-exceed-KVM-vcpu-limit.patch
# For bz#906937 - [Hitachi 7.0 FEAT][QEMU]Add a time stamp to error message (*)
Patch123: kvm-add-timestamp-to-error_report.patch
# For bz#906937 - [Hitachi 7.0 FEAT][QEMU]Add a time stamp to error message (*)
Patch124: kvm-Convert-stderr-message-calling-error_get_pretty-to-e.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch125: kvm-block-package-preparation-code-in-qmp_transaction.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch126: kvm-block-move-input-parsing-code-in-qmp_transaction.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch127: kvm-block-package-committing-code-in-qmp_transaction.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch128: kvm-block-package-rollback-code-in-qmp_transaction.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch129: kvm-block-make-all-steps-in-qmp_transaction-as-callback.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch130: kvm-blockdev-drop-redundant-proto_drv-check.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch131: kvm-block-Don-t-parse-protocol-from-file.filename.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch132: kvm-Revert-block-Disable-driver-specific-options-for-1.5.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch133: kvm-qcow2-Add-refcount-update-reason-to-all-callers.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch134: kvm-qcow2-Options-to-enable-discard-for-freed-clusters.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch135: kvm-qcow2-Batch-discards.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch136: kvm-block-Always-enable-discard-on-the-protocol-level.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch137: kvm-qapi.py-Avoid-code-duplication.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch138: kvm-qapi.py-Allow-top-level-type-reference-for-command-d.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch139: kvm-qapi-schema-Use-BlockdevSnapshot-type-for-blockdev-s.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch140: kvm-qapi-types.py-Implement-base-for-unions.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch141: kvm-qapi-visit.py-Split-off-generate_visit_struct_fields.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch142: kvm-qapi-visit.py-Implement-base-for-unions.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch143: kvm-docs-Document-QAPI-union-types.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch144: kvm-qapi-Add-visitor-for-implicit-structs.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch145: kvm-qapi-Flat-unions-with-arbitrary-discriminator.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch146: kvm-qapi-Add-consume-argument-to-qmp_input_get_object.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch147: kvm-qapi.py-Maintain-a-list-of-union-types.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch148: kvm-qapi-qapi-types.py-native-list-support.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch149: kvm-qapi-Anonymous-unions.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch150: kvm-block-Allow-driver-option-on-the-top-level.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch151: kvm-QemuOpts-Add-qemu_opt_unset.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch152: kvm-blockdev-Rename-I-O-throttling-options-for-QMP.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch153: kvm-qemu-iotests-Update-051-reference-output.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch154: kvm-blockdev-Rename-readonly-option-to-read-only.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch155: kvm-blockdev-Split-up-cache-option.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch156: kvm-qcow2-Use-dashes-instead-of-underscores-in-options.patch
# For bz#1006959 - qemu-iotests false positives
Patch157: kvm-qemu-iotests-filter-QEMU-version-in-monitor-banner.patch
# For bz#1006959 - qemu-iotests false positives
Patch158: kvm-tests-set-MALLOC_PERTURB_-to-expose-memory-bugs.patch
# For bz#1006959 - qemu-iotests false positives
Patch159: kvm-qemu-iotests-Whitespace-cleanup.patch
# For bz#1006959 - qemu-iotests false positives
Patch160: kvm-qemu-iotests-Fixed-test-case-026.patch
# For bz#1006959 - qemu-iotests false positives
Patch161: kvm-qemu-iotests-Fix-test-038.patch
# For bz#1006959 - qemu-iotests false positives
Patch162: kvm-qemu-iotests-Remove-lsi53c895a-tests-from-051.patch
# For bz#974887 - the screen of guest fail to display correctly when use spice + qxl driver
Patch163: kvm-spice-fix-display-initialization.patch
# For bz#921983 - Disable or remove emulated network devices that we will not support
Patch164: kvm-Remove-i82550-network-card-emulation.patch
# For bz#903914 - Disable or remove usb related devices that we will not support
Patch165: kvm-Remove-usb-wacom-tablet.patch
# For bz#903914 - Disable or remove usb related devices that we will not support
Patch166: kvm-Disable-usb-uas.patch
# For bz#947441 - HPET device must be disabled
Patch168: kvm-Remove-no-hpet-option.patch
# For bz#1002286 - Disable or remove device isa-parallel
Patch169: kvm-Disable-isa-parallel.patch
# For bz#949514 - fail to passthrough the USB3.0 stick to windows guest with xHCI controller under pc-i440fx-1.4
Patch170: kvm-xhci-implement-warm-port-reset.patch
# For bz#953304 - Serial number of some USB devices must be fixed for older RHEL machine types
Patch171: kvm-usb-add-serial-bus-property.patch
# For bz#953304 - Serial number of some USB devices must be fixed for older RHEL machine types
Patch172: kvm-rhel6-compat-usb-serial-numbers.patch
# For bz#995866 - fix vmdk support to ESX images
Patch173: kvm-vmdk-fix-comment-for-vmdk_co_write_zeroes.patch
# For bz#1007226 - Introduce bs->zero_beyond_eof
Patch174: kvm-gluster-Add-image-resize-support.patch
# For bz#1007226 - Introduce bs->zero_beyond_eof
Patch175: kvm-block-Introduce-bs-zero_beyond_eof.patch
# For bz#1007226 - Introduce bs->zero_beyond_eof
Patch176: kvm-block-Produce-zeros-when-protocols-reading-beyond-en.patch
# For bz#1007226 - Introduce bs->zero_beyond_eof
Patch177: kvm-gluster-Abort-on-AIO-completion-failure.patch
# For bz#1001131 - Disable or remove device usb-bt-dongle
Patch178: kvm-Preparation-for-usb-bt-dongle-conditional-build.patch
# For bz#1001131 - Disable or remove device usb-bt-dongle
Patch179: kvm-Remove-dev-bluetooth.c-dependency-from-vl.c.patch
# For bz#1009328 - [RFE] Nicer error report when qemu-kvm can't allocate guest RAM
Patch180: kvm-exec-Fix-Xen-RAM-allocation-with-unusual-options.patch
# For bz#1009328 - [RFE] Nicer error report when qemu-kvm can't allocate guest RAM
Patch181: kvm-exec-Clean-up-fall-back-when-mem-path-allocation-fai.patch
# For bz#1009328 - [RFE] Nicer error report when qemu-kvm can't allocate guest RAM
Patch182: kvm-exec-Reduce-ifdeffery-around-mem-path.patch
# For bz#1009328 - [RFE] Nicer error report when qemu-kvm can't allocate guest RAM
Patch183: kvm-exec-Simplify-the-guest-physical-memory-allocation-h.patch
# For bz#1009328 - [RFE] Nicer error report when qemu-kvm can't allocate guest RAM
Patch184: kvm-exec-Drop-incorrect-dead-S390-code-in-qemu_ram_remap.patch
# For bz#1009328 - [RFE] Nicer error report when qemu-kvm can't allocate guest RAM
Patch185: kvm-exec-Clean-up-unnecessary-S390-ifdeffery.patch
# For bz#1009328 - [RFE] Nicer error report when qemu-kvm can't allocate guest RAM
Patch186: kvm-exec-Don-t-abort-when-we-can-t-allocate-guest-memory.patch
# For bz#1009328 - [RFE] Nicer error report when qemu-kvm can't allocate guest RAM
Patch187: kvm-pc_sysfw-Fix-ISA-BIOS-init-for-ridiculously-big-flas.patch
# For bz#903918 - Disable or remove emulated SCSI devices we will not support
Patch188: kvm-virtio-scsi-Make-type-virtio-scsi-common-abstract.patch
# For bz#1009491 - move qga logfiles to new /var/log/qemu-ga/ directory [RHEL-7]
Patch189: kvm-qga-move-logfiles-to-new-directory-for-easier-SELinu.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch190: kvm-target-i386-add-cpu64-rhel6-CPU-model.patch
# For bz#903889 - The value of steal time in "top" command always is "0.0% st" after guest migration
Patch191: kvm-fix-steal-time-MSR-vmsd-callback-to-proper-opaque-ty.patch
# For bz#995866 - fix vmdk support to ESX images
Patch192: kvm-vmdk-Make-VMDK3Header-and-VmdkGrainMarker-QEMU_PACKE.patch
# For bz#995866 - fix vmdk support to ESX images
Patch193: kvm-vmdk-use-unsigned-values-for-on-disk-header-fields.patch
# For bz#995866 - fix vmdk support to ESX images
Patch194: kvm-qemu-iotests-add-poke_file-utility-function.patch
# For bz#995866 - fix vmdk support to ESX images
Patch195: kvm-qemu-iotests-add-empty-test-case-for-vmdk.patch
# For bz#995866 - fix vmdk support to ESX images
Patch196: kvm-vmdk-check-granularity-field-in-opening.patch
# For bz#995866 - fix vmdk support to ESX images
Patch197: kvm-vmdk-check-l2-table-size-when-opening.patch
# For bz#995866 - fix vmdk support to ESX images
Patch198: kvm-vmdk-check-l1-size-before-opening-image.patch
# For bz#995866 - fix vmdk support to ESX images
Patch199: kvm-vmdk-use-heap-allocation-for-whole_grain.patch
# For bz#995866 - fix vmdk support to ESX images
Patch200: kvm-vmdk-rename-num_gtes_per_gte-to-num_gtes_per_gt.patch
# For bz#995866 - fix vmdk support to ESX images
Patch201: kvm-vmdk-Move-l1_size-check-into-vmdk_add_extent.patch
# For bz#995866 - fix vmdk support to ESX images
Patch202: kvm-vmdk-fix-L1-and-L2-table-size-in-vmdk3-open.patch
# For bz#995866 - fix vmdk support to ESX images
Patch203: kvm-vmdk-support-vmfsSparse-files.patch
# For bz#995866 - fix vmdk support to ESX images
Patch204: kvm-vmdk-support-vmfs-files.patch
# For bz#1005036 - When using “-vga qxl” together with “-display vnc=:5” or “-display  sdl” qemu displays  pixel garbage
Patch205: kvm-qxl-fix-local-renderer.patch
# For bz#1008987 - pvticketlocks: add kvm feature kvm_pv_unhalt
Patch206: kvm-linux-headers-update-to-kernel-3.10.0-26.el7.patch
# For bz#1008987 - pvticketlocks: add kvm feature kvm_pv_unhalt
Patch207: kvm-target-i386-add-feature-kvm_pv_unhalt.patch
# For bz#1010881 - backport vcpu soft limit warning
Patch208: kvm-warn-if-num-cpus-is-greater-than-num-recommended.patch
# For bz#1007222 - QEMU core dumped when do hot-unplug virtio serial port during transfer file between host to guest with virtio serial through TCP socket
Patch209: kvm-char-move-backends-io-watch-tag-to-CharDriverState.patch
# For bz#1007222 - QEMU core dumped when do hot-unplug virtio serial port during transfer file between host to guest with virtio serial through TCP socket
Patch210: kvm-char-use-common-function-to-disable-callbacks-on-cha.patch
# For bz#1007222 - QEMU core dumped when do hot-unplug virtio serial port during transfer file between host to guest with virtio serial through TCP socket
Patch211: kvm-char-remove-watch-callback-on-chardev-detach-from-fr.patch
# For bz#1017049 - qemu-img refuses to open the vmdk format image its created
Patch212: kvm-block-don-t-lose-data-from-last-incomplete-sector.patch
# For bz#1017049 - qemu-img refuses to open the vmdk format image its created
Patch213: kvm-vmdk-fix-cluster-size-check-for-flat-extents.patch
# For bz#1017049 - qemu-img refuses to open the vmdk format image its created
Patch214: kvm-qemu-iotests-add-monolithicFlat-creation-test-to-059.patch
# For bz#1001604 - usb hub doesn't work properly (win7 sees downstream port #1 only).
Patch215: kvm-xhci-fix-endpoint-interval-calculation.patch
# For bz#1001604 - usb hub doesn't work properly (win7 sees downstream port #1 only).
Patch216: kvm-xhci-emulate-intr-endpoint-intervals-correctly.patch
# For bz#1001604 - usb hub doesn't work properly (win7 sees downstream port #1 only).
Patch217: kvm-xhci-reset-port-when-disabling-slot.patch
# For bz#1001604 - usb hub doesn't work properly (win7 sees downstream port #1 only).
Patch218: kvm-Revert-usb-hub-report-status-changes-only-once.patch
# For bz#1004290 - Use model 6 for qemu64 and intel cpus
Patch219: kvm-target-i386-Set-model-6-on-qemu64-qemu32-CPU-models.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch220: kvm-pc-rhel6-doesn-t-have-APIC-on-pentium-CPU-models.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch221: kvm-pc-RHEL-6-had-x2apic-set-on-Opteron_G-123.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch222: kvm-pc-RHEL-6-don-t-have-RDTSCP.patch
# For bz#1009285 - -device usb-storage,serial=... crashes with SCSI generic drive
Patch223: kvm-scsi-Fix-scsi_bus_legacy_add_drive-scsi-generic-with.patch
# For bz#1004175 - '-sandbox on'  option  cause  qemu-kvm process hang
Patch224: kvm-seccomp-fine-tuning-whitelist-by-adding-times.patch
# For bz#921465 - Migration can not finished even the "remaining ram" is already 0 kb
Patch225: kvm-block-add-bdrv_write_zeroes.patch
# For bz#921465 - Migration can not finished even the "remaining ram" is already 0 kb
Patch226: kvm-block-raw-add-bdrv_co_write_zeroes.patch
# For bz#921465 - Migration can not finished even the "remaining ram" is already 0 kb
Patch227: kvm-rdma-export-qemu_fflush.patch
# For bz#921465 - Migration can not finished even the "remaining ram" is already 0 kb
Patch228: kvm-block-migration-efficiently-encode-zero-blocks.patch
# For bz#921465 - Migration can not finished even the "remaining ram" is already 0 kb
Patch229: kvm-Fix-real-mode-guest-migration.patch
# For bz#921465 - Migration can not finished even the "remaining ram" is already 0 kb
Patch230: kvm-Fix-real-mode-guest-segments-dpl-value-in-savevm.patch
# For bz#921465 - Migration can not finished even the "remaining ram" is already 0 kb
Patch231: kvm-migration-add-autoconvergence-documentation.patch
# For bz#921465 - Migration can not finished even the "remaining ram" is already 0 kb
Patch232: kvm-migration-send-total-time-in-QMP-at-completed-stage.patch
# For bz#921465 - Migration can not finished even the "remaining ram" is already 0 kb
Patch233: kvm-migration-don-t-use-uninitialized-variables.patch
# For bz#921465 - Migration can not finished even the "remaining ram" is already 0 kb
Patch234: kvm-pc-drop-external-DSDT-loading.patch
# For bz#954195 - RHEL machines <=6.4 should not use mixemu
Patch235: kvm-hda-codec-refactor-common-definitions-into-a-header-.patch
# For bz#954195 - RHEL machines <=6.4 should not use mixemu
Patch236: kvm-hda-codec-make-mixemu-selectable-at-runtime.patch
# For bz#954195 - RHEL machines <=6.4 should not use mixemu
Patch237: kvm-audio-remove-CONFIG_MIXEMU-configure-option.patch
# For bz#954195 - RHEL machines <=6.4 should not use mixemu
Patch238: kvm-pc_piix-disable-mixer-for-6.4.0-machine-types-and-be.patch
# For bz#994414 - hot-unplug chardev with pty backend caused qemu Segmentation fault
Patch239: kvm-chardev-fix-pty_chr_timer.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch240: kvm-qemu-socket-zero-initialize-SocketAddress.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch241: kvm-qemu-socket-drop-pointless-allocation.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch242: kvm-qemu-socket-catch-monitor_get_fd-failures.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch243: kvm-qemu-char-check-optional-fields-using-has_.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch244: kvm-error-add-error_setg_file_open-helper.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch245: kvm-qemu-char-use-more-specific-error_setg_-variants.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch246: kvm-qemu-char-print-notification-to-stderr.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch247: kvm-qemu-char-fix-documentation-for-telnet-wait-socket-f.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch248: kvm-qemu-char-don-t-leak-opts-on-error.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch249: kvm-qemu-char-use-ChardevBackendKind-in-CharDriver.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch250: kvm-qemu-char-minor-mux-chardev-fixes.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch251: kvm-qemu-char-add-chardev-mux-support.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch252: kvm-qemu-char-report-udp-backend-errors.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch253: kvm-qemu-socket-don-t-leak-opts-on-error.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch254: kvm-chardev-handle-qmp_chardev_add-KIND_MUX-failure.patch
# For bz#1019474 - RHEL-7 can't load piix4_pm migration section from RHEL-6.5
Patch255: kvm-acpi-piix4-Enable-qemu-kvm-compatibility-mode.patch
# For bz#1004743 - XSAVE migration format not compatible between RHEL6 and RHEL7
Patch256: kvm-target-i386-support-loading-of-cpu-xsave-subsection.patch
# For bz#997817 - -boot order and -boot once regressed since RHEL-6
Patch257: kvm-vl-Clean-up-parsing-of-boot-option-argument.patch
# For bz#997817 - -boot order and -boot once regressed since RHEL-6
Patch258: kvm-qemu-option-check_params-is-now-unused-drop-it.patch
# For bz#997817 - -boot order and -boot once regressed since RHEL-6
Patch259: kvm-vl-Fix-boot-order-and-once-regressions-and-related-b.patch
# For bz#997817 - -boot order and -boot once regressed since RHEL-6
Patch260: kvm-vl-Rename-boot_devices-to-boot_order-for-consistency.patch
# For bz#997817 - -boot order and -boot once regressed since RHEL-6
Patch261: kvm-pc-Make-no-fd-bootchk-stick-across-boot-order-change.patch
# For bz#997817 - -boot order and -boot once regressed since RHEL-6
Patch262: kvm-doc-Drop-ref-to-Bochs-from-no-fd-bootchk-documentati.patch
# For bz#997817 - -boot order and -boot once regressed since RHEL-6
Patch263: kvm-libqtest-Plug-fd-and-memory-leaks-in-qtest_quit.patch
# For bz#997817 - -boot order and -boot once regressed since RHEL-6
Patch264: kvm-libqtest-New-qtest_end-to-go-with-qtest_start.patch
# For bz#997817 - -boot order and -boot once regressed since RHEL-6
Patch265: kvm-qtest-Don-t-reset-on-qtest-chardev-connect.patch
# For bz#997817 - -boot order and -boot once regressed since RHEL-6
Patch266: kvm-boot-order-test-New-covering-just-PC-for-now.patch
# For bz#1019352 - qemu-guest-agent: "guest-fsfreeze-freeze" deadlocks if the guest have mounted disk images
Patch267: kvm-qemu-ga-execute-fsfreeze-freeze-in-reverse-order-of-.patch
# For bz#989608 - [7.0 FEAT] qemu runtime support for librbd backend (ceph)
Patch268: kvm-rbd-link-and-load-librbd-dynamically.patch
# For bz#989608 - [7.0 FEAT] qemu runtime support for librbd backend (ceph)
Patch269: kvm-rbd-Only-look-for-qemu-specific-copy-of-librbd.so.1.patch
# For bz#989677 - [HP 7.0 FEAT]: Increase KVM guest supported memory to 4TiB
Patch270: kvm-seabios-paravirt-allow-more-than-1TB-in-x86-guest.patch
# For bz#1006468 - libiscsi initiator name should use vm UUID
Patch271: kvm-scsi-prefer-UUID-to-VM-name-for-the-initiator-name.patch
# For bz#928867 - Virtual PMU support during live migration - qemu-kvm
Patch272: kvm-target-i386-remove-tabs-from-target-i386-cpu.h.patch
# For bz#928867 - Virtual PMU support during live migration - qemu-kvm
Patch273: kvm-migrate-vPMU-state.patch
# For bz#1009993 - RHEL7 guests do not issue fdatasyncs on virtio-blk
Patch274: kvm-blockdev-do-not-default-cache.no-flush-to-true.patch
# For bz#1009993 - RHEL7 guests do not issue fdatasyncs on virtio-blk
Patch275: kvm-virtio-blk-do-not-relay-a-previous-driver-s-WCE-conf.patch
# For bz#907743 - qemu-ga: empty reason string for OpenFileFailed error
Patch276: kvm-rng-random-use-error_setg_file_open.patch
# For bz#907743 - qemu-ga: empty reason string for OpenFileFailed error
Patch277: kvm-block-mirror_complete-use-error_setg_file_open.patch
# For bz#907743 - qemu-ga: empty reason string for OpenFileFailed error
Patch278: kvm-blockdev-use-error_setg_file_open.patch
# For bz#907743 - qemu-ga: empty reason string for OpenFileFailed error
Patch279: kvm-cpus-use-error_setg_file_open.patch
# For bz#907743 - qemu-ga: empty reason string for OpenFileFailed error
Patch280: kvm-dump-qmp_dump_guest_memory-use-error_setg_file_open.patch
# For bz#907743 - qemu-ga: empty reason string for OpenFileFailed error
Patch281: kvm-savevm-qmp_xen_save_devices_state-use-error_setg_fil.patch
# For bz#907743 - qemu-ga: empty reason string for OpenFileFailed error
Patch282: kvm-block-bdrv_reopen_prepare-don-t-use-QERR_OPEN_FILE_F.patch
# For bz#907743 - qemu-ga: empty reason string for OpenFileFailed error
Patch283: kvm-qerror-drop-QERR_OPEN_FILE_FAILED-macro.patch
# For bz#787463 - disable ivshmem (was: [Hitachi 7.0 FEAT] Support ivshmem (Inter-VM Shared Memory))
Patch284: kvm-rhel-Drop-ivshmem-device.patch
# For bz#1001144 - Disable or remove device usb-host-linux
Patch285: kvm-usb-remove-old-usb-host-code.patch
# For bz#997702 - Migration from RHEL6.5 host to RHEL7.0 host is failed with virtio-net device
Patch286: kvm-Fix-migration-from-rhel6.5-to-rhel7-with-ipxe.patch
# For bz#994490 - Set per-machine-type SMBIOS strings
Patch287: kvm-pc-Don-t-prematurely-explode-QEMUMachineInitArgs.patch
# For bz#994490 - Set per-machine-type SMBIOS strings
Patch288: kvm-pc-Don-t-explode-QEMUMachineInitArgs-into-local-vari.patch
# For bz#994490 - Set per-machine-type SMBIOS strings
Patch289: kvm-smbios-Normalize-smbios_entry_add-s-error-handling-t.patch
# For bz#994490 - Set per-machine-type SMBIOS strings
Patch290: kvm-smbios-Convert-to-QemuOpts.patch
# For bz#994490 - Set per-machine-type SMBIOS strings
Patch291: kvm-smbios-Improve-diagnostics-for-conflicting-entries.patch
# For bz#994490 - Set per-machine-type SMBIOS strings
Patch292: kvm-smbios-Make-multiple-smbios-type-accumulate-sanely.patch
# For bz#994490 - Set per-machine-type SMBIOS strings
Patch293: kvm-smbios-Factor-out-smbios_maybe_add_str.patch
# For bz#994490 - Set per-machine-type SMBIOS strings
Patch294: kvm-hw-Pass-QEMUMachine-to-its-init-method.patch
# For bz#994490 - Set per-machine-type SMBIOS strings
Patch295: kvm-smbios-Set-system-manufacturer-product-version-by-de.patch
# For bz#994490 - Set per-machine-type SMBIOS strings
Patch296: kvm-smbios-Decouple-system-product-from-QEMUMachine.patch
# For bz#994490 - Set per-machine-type SMBIOS strings
Patch297: kvm-rhel-SMBIOS-type-1-branding.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch298: kvm-cow-make-reads-go-at-a-decent-speed.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch299: kvm-cow-make-writes-go-at-a-less-indecent-speed.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch300: kvm-cow-do-not-call-bdrv_co_is_allocated.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch301: kvm-block-keep-bs-total_sectors-up-to-date-even-for-grow.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch302: kvm-block-make-bdrv_co_is_allocated-static.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch303: kvm-block-do-not-use-total_sectors-in-bdrv_co_is_allocat.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch304: kvm-block-remove-bdrv_is_allocated_above-bdrv_co_is_allo.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch305: kvm-block-expect-errors-from-bdrv_co_is_allocated.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch306: kvm-block-Fix-compiler-warning-Werror-uninitialized.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch307: kvm-qemu-img-always-probe-the-input-image-for-allocated-.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch308: kvm-block-make-bdrv_has_zero_init-return-false-for-copy-.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch309: kvm-block-introduce-bdrv_get_block_status-API.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch310: kvm-block-define-get_block_status-return-value.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch311: kvm-block-return-get_block_status-data-and-flags-for-for.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch312: kvm-block-use-bdrv_has_zero_init-to-return-BDRV_BLOCK_ZE.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch313: kvm-block-return-BDRV_BLOCK_ZERO-past-end-of-backing-fil.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch314: kvm-qemu-img-add-a-map-subcommand.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch315: kvm-docs-qapi-document-qemu-img-map.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch316: kvm-raw-posix-return-get_block_status-data-and-flags.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch317: kvm-raw-posix-report-unwritten-extents-as-zero.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch318: kvm-block-add-default-get_block_status-implementation-fo.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch319: kvm-block-look-for-zero-blocks-in-bs-file.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch320: kvm-qemu-img-fix-invalid-JSON.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch321: kvm-block-get_block_status-set-pnum-0-on-error.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch322: kvm-block-get_block_status-avoid-segfault-if-there-is-no.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch323: kvm-block-get_block_status-avoid-redundant-callouts-on-r.patch
# For bz#1025740 - Saving VM state on qcow2 images results in VM state corruption
Patch324: kvm-qcow2-Restore-total_sectors-value-in-save_vmstate.patch
# For bz#1025740 - Saving VM state on qcow2 images results in VM state corruption
Patch325: kvm-qcow2-Unset-zero_beyond_eof-in-save_vmstate.patch
# For bz#1025740 - Saving VM state on qcow2 images results in VM state corruption
Patch326: kvm-qemu-iotests-Test-for-loading-VM-state-from-qcow2.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch327: kvm-apic-rename-apic-specific-bitopts.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch328: kvm-hw-import-bitmap-operations-in-qdev-core-header.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch329: kvm-qemu-help-Sort-devices-by-logical-functionality.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch330: kvm-devices-Associate-devices-to-their-logical-category.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch331: kvm-Mostly-revert-qemu-help-Sort-devices-by-logical-func.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch332: kvm-qdev-monitor-Group-device_add-help-and-info-qdm-by-c.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch333: kvm-qdev-Replace-no_user-by-cannot_instantiate_with_devi.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch334: kvm-sysbus-Set-cannot_instantiate_with_device_add_yet.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch335: kvm-cpu-Document-why-cannot_instantiate_with_device_add_.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch336: kvm-apic-Document-why-cannot_instantiate_with_device_add.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch337: kvm-pci-host-Consistently-set-cannot_instantiate_with_de.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch338: kvm-ich9-Document-why-cannot_instantiate_with_device_add.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch339: kvm-piix3-piix4-Clean-up-use-of-cannot_instantiate_with_.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch340: kvm-vt82c686-Clean-up-use-of-cannot_instantiate_with_dev.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch341: kvm-isa-Clean-up-use-of-cannot_instantiate_with_device_a.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch342: kvm-qdev-Do-not-let-the-user-try-to-device_add-when-it-c.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch343: kvm-rhel-Revert-unwanted-cannot_instantiate_with_device_.patch
# For bz#1001076 - Disable or remove other block devices we won't support
Patch344: kvm-rhel-Revert-downstream-changes-to-unused-default-con.patch
# For bz#1001076 - Disable or remove other block devices we won't support
Patch345: kvm-rhel-Drop-cfi.pflash01-and-isa-ide-device.patch
# For bz#1001088 - Disable or remove display devices we won't support
Patch346: kvm-rhel-Drop-isa-vga-device.patch
# For bz#1001088 - Disable or remove display devices we won't support
Patch347: kvm-rhel-Make-isa-cirrus-vga-device-unavailable.patch
# For bz#1001123 - Disable or remove device ccid-card-emulated
Patch348: kvm-rhel-Make-ccid-card-emulated-device-unavailable.patch
# For bz#1005695 - QEMU should hide CPUID.0Dh values that it does not support
Patch349: kvm-x86-fix-migration-from-pre-version-12.patch
# For bz#1005695 - QEMU should hide CPUID.0Dh values that it does not support
Patch350: kvm-x86-cpuid-reconstruct-leaf-0Dh-data.patch
# For bz#920021 - qemu-kvm segment fault when reboot guest after hot unplug device with option ROM
Patch351: kvm-kvmvapic-Catch-invalid-ROM-size.patch
# For bz#920021 - qemu-kvm segment fault when reboot guest after hot unplug device with option ROM
Patch352: kvm-kvmvapic-Enter-inactive-state-on-hardware-reset.patch
# For bz#920021 - qemu-kvm segment fault when reboot guest after hot unplug device with option ROM
Patch353: kvm-kvmvapic-Clear-also-physical-ROM-address-when-enteri.patch
# For bz#987582 - Initial Virtualization Differentiation for RHEL7 (Live snapshots)
Patch354: kvm-block-optionally-disable-live-block-jobs.patch
# For bz#1022392 - Disable live-storage-migration in qemu-kvm (migrate -b/-i)
Patch355: kvm-migration-disable-live-block-migration-b-i-for-rhel-.patch
# For bz#987583 - Initial Virtualization Differentiation for RHEL7 (Ceph enablement)
Patch356: kvm-Build-ceph-rbd-only-for-rhev.patch
# For bz#1001180 - Disable or remove devices pci-serial-2x, pci-serial-4x
Patch357: kvm-rhel-Make-pci-serial-2x-and-pci-serial-4x-device-una.patch
# For bz#980415 - libusbx: error [_open_sysfs_attr] open /sys/bus/usb/devices/4-1/bConfigurationValue failed ret=-1 errno=2
Patch358: kvm-usb-host-libusb-Fix-reset-handling.patch
# For bz#980383 - The usb3.0 stick can't be returned back to host after shutdown guest with usb3.0 pass-through
Patch359: kvm-usb-host-libusb-Configuration-0-may-be-a-valid-confi.patch
# For bz#980383 - The usb3.0 stick can't be returned back to host after shutdown guest with usb3.0 pass-through
Patch360: kvm-usb-host-libusb-Detach-kernel-drivers-earlier.patch
# For bz#1010858 - Disable unused human monitor commands
Patch361: kvm-monitor-Remove-pci_add-command-for-Red-Hat-Enterpris.patch
# For bz#1010858 - Disable unused human monitor commands
Patch362: kvm-monitor-Remove-pci_del-command-for-Red-Hat-Enterpris.patch
# For bz#1010858 - Disable unused human monitor commands
Patch363: kvm-monitor-Remove-usb_add-del-commands-for-Red-Hat-Ente.patch
# For bz#1010858 - Disable unused human monitor commands
Patch364: kvm-monitor-Remove-host_net_add-remove-for-Red-Hat-Enter.patch
# For bz#990601 - pvpanic device triggers guest bugs when present by default
Patch365: kvm-fw_cfg-add-API-to-find-FW-cfg-object.patch
# For bz#990601 - pvpanic device triggers guest bugs when present by default
Patch366: kvm-pvpanic-use-FWCfgState-explicitly.patch
# For bz#990601 - pvpanic device triggers guest bugs when present by default
Patch367: kvm-pvpanic-initialization-cleanup.patch
# For bz#990601 - pvpanic device triggers guest bugs when present by default
Patch368: kvm-pvpanic-fix-fwcfg-for-big-endian-hosts.patch
# For bz#990601 - pvpanic device triggers guest bugs when present by default
Patch369: kvm-hw-misc-make-pvpanic-known-to-user.patch
# For bz#990601 - pvpanic device triggers guest bugs when present by default
Patch370: kvm-gdbstub-do-not-restart-crashed-guest.patch
# For bz#990601 - pvpanic device triggers guest bugs when present by default
Patch371: kvm-gdbstub-fix-for-commit-87f25c12bfeaaa0c41fb857713bbc.patch
# For bz#990601 - pvpanic device triggers guest bugs when present by default
Patch372: kvm-vl-allow-cont-from-panicked-state.patch
# For bz#990601 - pvpanic device triggers guest bugs when present by default
Patch373: kvm-hw-misc-don-t-create-pvpanic-device-by-default.patch
# For bz#1007176 - Add VPC and VHDX file formats as supported in qemu-kvm (read-only)
Patch374: kvm-block-vhdx-add-migration-blocker.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch375: kvm-block-drop-bs_snapshots-global-variable.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch376: kvm-block-move-snapshot-code-in-block.c-to-block-snapsho.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch377: kvm-block-fix-vvfat-error-path-for-enable_write_target.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch378: kvm-block-Bugfix-format-and-snapshot-used-in-drive-optio.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch379: kvm-iscsi-use-bdrv_new-instead-of-stack-structure.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch380: kvm-qcow2-Add-corrupt-bit.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch381: kvm-qcow2-Metadata-overlap-checks.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch382: kvm-qcow2-Employ-metadata-overlap-checks.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch383: kvm-qcow2-refcount-Move-OFLAG_COPIED-checks.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch384: kvm-qcow2-refcount-Repair-OFLAG_COPIED-errors.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch385: kvm-qcow2-refcount-Repair-shared-refcount-blocks.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch386: kvm-qcow2_check-Mark-image-consistent.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch387: kvm-qemu-iotests-Overlapping-cluster-allocations.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch388: kvm-w32-Fix-access-to-host-devices-regression.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch389: kvm-add-qemu-img-convert-n-option-skip-target-volume-cre.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch390: kvm-bdrv-Use-Error-for-opening-images.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch391: kvm-bdrv-Use-Error-for-creating-images.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch392: kvm-block-Error-parameter-for-open-functions.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch393: kvm-block-Error-parameter-for-create-functions.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch394: kvm-qemu-img-create-Emit-filename-on-error.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch395: kvm-qcow2-Use-Error-parameter.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch396: kvm-qemu-iotests-Adjustments-due-to-error-propagation.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch397: kvm-block-raw-Employ-error-parameter.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch398: kvm-block-raw-win32-Employ-error-parameter.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch399: kvm-blkdebug-Employ-error-parameter.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch400: kvm-blkverify-Employ-error-parameter.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch401: kvm-block-raw-posix-Employ-error-parameter.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch402: kvm-block-raw-win32-Always-use-errno-in-hdev_open.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch403: kvm-qmp-Documentation-for-BLOCK_IMAGE_CORRUPTED.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch404: kvm-qcow2-Correct-snapshots-size-for-overlap-check.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch405: kvm-qcow2-CHECK_OFLAG_COPIED-is-obsolete.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch406: kvm-qcow2-Correct-endianness-in-overlap-check.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch407: kvm-qcow2-Switch-L1-table-in-a-single-sequence.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch408: kvm-qcow2-Use-pread-for-inactive-L1-in-overlap-check.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch409: kvm-qcow2-Remove-wrong-metadata-overlap-check.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch410: kvm-qcow2-Use-negated-overflow-check-mask.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch411: kvm-qcow2-Make-overlap-check-mask-variable.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch412: kvm-qcow2-Add-overlap-check-options.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch413: kvm-qcow2-Array-assigning-options-to-OL-check-bits.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch414: kvm-qcow2-Add-more-overlap-check-bitmask-macros.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch415: kvm-qcow2-Evaluate-overlap-check-options.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch416: kvm-qapi-types.py-Split-off-generate_struct_fields.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch417: kvm-qapi-types.py-Fix-enum-struct-sizes-on-i686.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch418: kvm-qapi-types-visit.py-Pass-whole-expr-dict-for-structs.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch419: kvm-qapi-types-visit.py-Inheritance-for-structs.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch420: kvm-blockdev-Introduce-DriveInfo.enable_auto_del.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch421: kvm-Implement-qdict_flatten.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch422: kvm-blockdev-blockdev-add-QMP-command.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch423: kvm-blockdev-Separate-ID-generation-from-DriveInfo-creat.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch424: kvm-blockdev-Pass-QDict-to-blockdev_init.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch425: kvm-blockdev-Move-parsing-of-media-option-to-drive_init.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch426: kvm-blockdev-Move-parsing-of-if-option-to-drive_init.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch427: kvm-blockdev-Moving-parsing-of-geometry-options-to-drive.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch428: kvm-blockdev-Move-parsing-of-boot-option-to-drive_init.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch429: kvm-blockdev-Move-bus-unit-index-processing-to-drive_ini.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch430: kvm-blockdev-Move-virtio-blk-device-creation-to-drive_in.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch431: kvm-blockdev-Remove-IF_-check-for-read-only-blockdev_ini.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch432: kvm-qemu-iotests-Check-autodel-behaviour-for-device_del.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch433: kvm-blockdev-Remove-media-parameter-from-blockdev_init.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch434: kvm-blockdev-Don-t-disable-COR-automatically-with-blockd.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch435: kvm-blockdev-blockdev_init-error-conversion.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch436: kvm-sd-Avoid-access-to-NULL-BlockDriverState.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch437: kvm-blockdev-fix-cdrom-read_only-flag.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch438: kvm-block-fix-backing-file-overriding.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch439: kvm-block-Disable-BDRV_O_COPY_ON_READ-for-the-backing-fi.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch440: kvm-block-Don-t-copy-backing-file-name-on-error.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch441: kvm-qemu-iotests-Try-creating-huge-qcow2-image.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch442: kvm-block-move-qmp-and-info-dump-related-code-to-block-q.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch443: kvm-block-dump-snapshot-and-image-info-to-specified-outp.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch444: kvm-block-add-snapshot-info-query-function-bdrv_query_sn.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch445: kvm-block-add-image-info-query-function-bdrv_query_image.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch446: kvm-qmp-add-ImageInfo-in-BlockDeviceInfo-used-by-query-b.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch447: kvm-vmdk-Implement-.bdrv_has_zero_init.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch448: kvm-qemu-iotests-Add-basic-ability-to-use-binary-sample-.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch449: kvm-qemu-iotests-Quote-TEST_IMG-and-TEST_DIR-usage.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch450: kvm-qemu-iotests-fix-test-case-059.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch451: kvm-qapi-Add-ImageInfoSpecific-type.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch452: kvm-block-Add-bdrv_get_specific_info.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch453: kvm-block-qapi-Human-readable-ImageInfoSpecific-dump.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch454: kvm-qcow2-Add-support-for-ImageInfoSpecific.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch455: kvm-qemu-iotests-Discard-specific-info-in-_img_info.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch456: kvm-qemu-iotests-Additional-info-from-qemu-img-info.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch457: kvm-vmdk-convert-error-code-to-use-errp.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch458: kvm-vmdk-refuse-enabling-zeroed-grain-with-flat-images.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch459: kvm-qapi-Add-optional-field-compressed-to-ImageInfo.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch460: kvm-vmdk-Only-read-cid-from-image-file-when-opening.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch461: kvm-vmdk-Implment-bdrv_get_specific_info.patch
# For bz#1025877 - pci-assign lacks MSI affinity support
Patch462: kvm-pci-assign-Add-MSI-affinity-support.patch
# For bz#1025877 - pci-assign lacks MSI affinity support
Patch463: kvm-Fix-potential-resource-leak-missing-fclose.patch
# For bz#1025877 - pci-assign lacks MSI affinity support
Patch464: kvm-pci-assign-remove-the-duplicate-function-name-in-deb.patch
# For bz#922589 - e1000/rtl8139: qemu mac address can not be changed via set the hardware address in guest
Patch465: kvm-net-update-nic-info-during-device-reset.patch
# For bz#922589 - e1000/rtl8139: qemu mac address can not be changed via set the hardware address in guest
Patch466: kvm-net-e1000-update-network-information-when-macaddr-is.patch
# For bz#922589 - e1000/rtl8139: qemu mac address can not be changed via set the hardware address in guest
Patch467: kvm-net-rtl8139-update-network-information-when-macaddr-.patch
# For bz#1026689 - virtio-net: macaddr is reset but network info of monitor isn't updated
Patch468: kvm-virtio-net-fix-up-HMP-NIC-info-string-on-reset.patch
# For bz#1025477 - VFIO MSI affinity
Patch469: kvm-vfio-pci-VGA-quirk-update.patch
# For bz#1025477 - VFIO MSI affinity
Patch470: kvm-vfio-pci-Add-support-for-MSI-affinity.patch
# For bz#1026550 - QEMU VFIO update ROM loading code
Patch471: kvm-vfio-pci-Test-device-reset-capabilities.patch
# For bz#1026550 - QEMU VFIO update ROM loading code
Patch472: kvm-vfio-pci-Lazy-PCI-option-ROM-loading.patch
# For bz#1026550 - QEMU VFIO update ROM loading code
Patch473: kvm-vfio-pci-Cleanup-error_reports.patch
# For bz#1026550 - QEMU VFIO update ROM loading code
Patch474: kvm-vfio-pci-Add-dummy-PCI-ROM-write-accessor.patch
# For bz#1026550 - QEMU VFIO update ROM loading code
Patch475: kvm-vfio-pci-Fix-endian-issues-in-vfio_pci_size_rom.patch
# For bz#1025472 - Nvidia GPU device assignment - qemu-kvm - bus reset support
Patch476: kvm-linux-headers-Update-to-include-vfio-pci-hot-reset-s.patch
# For bz#1025472 - Nvidia GPU device assignment - qemu-kvm - bus reset support
Patch477: kvm-vfio-pci-Implement-PCI-hot-reset.patch
# For bz#1025474 - Nvidia GPU device assignment - qemu-kvm - NoSnoop support
Patch478: kvm-linux-headers-Update-for-KVM-VFIO-device.patch
# For bz#1025474 - Nvidia GPU device assignment - qemu-kvm - NoSnoop support
Patch479: kvm-vfio-pci-Make-use-of-new-KVM-VFIO-device.patch
# For bz#995866 - fix vmdk support to ESX images
Patch480: kvm-vmdk-Fix-vmdk_parse_extents.patch
# For bz#995866 - fix vmdk support to ESX images
Patch481: kvm-vmdk-fix-VMFS-extent-parsing.patch
# For bz#922589 - e1000/rtl8139: qemu mac address can not be changed via set the hardware address in guest
#Patch482: kvm-e1000-rtl8139-update-HMP-NIC-when-every-bit-is-writt.patch
# Patch 482 removed as it has to be discussed and should not be applied yet
# For bz#1005039 - add compat property to disable ctrl_mac_addr feature
Patch483: kvm-don-t-disable-ctrl_mac_addr-feature-for-6.5-machine-.patch

BuildRequires: zlib-devel
BuildRequires: SDL-devel
BuildRequires: which
BuildRequires: texi2html
BuildRequires: gnutls-devel
BuildRequires: cyrus-sasl-devel
BuildRequires: libtool
BuildRequires: libaio-devel
BuildRequires: rsync
BuildRequires: pciutils-devel
BuildRequires: pulseaudio-libs-devel
BuildRequires: libiscsi-devel
BuildRequires: ncurses-devel
BuildRequires: libattr-devel
BuildRequires: libusbx-devel
%if 0%{?have_usbredir:1}
BuildRequires: usbredir-devel >= 0.6
%endif
BuildRequires: texinfo
%if 0%{!?build_only_sub:1}
    %if 0%{?have_spice:1}
BuildRequires: spice-protocol >= 0.12.2
BuildRequires: spice-server-devel >= 0.12.0
    %endif
%endif
%if 0%{?have_seccomp:1}
BuildRequires: libseccomp-devel >= 1.0.0
%endif
# For network block driver
BuildRequires: libcurl-devel
%if 0%{!?build_only_sub:1}
# For gluster block driver
BuildRequires: glusterfs-api-devel
BuildRequires: glusterfs-devel
%endif
# We need both because the 'stap' binary is probed for by configure
BuildRequires: systemtap
BuildRequires: systemtap-sdt-devel
# For smartcard NSS support
BuildRequires: nss-devel
# For XFS discard support in raw-posix.c
# For VNC JPEG support
BuildRequires: libjpeg-devel
# For VNC PNG support
BuildRequires: libpng-devel
# For uuid generation
BuildRequires: libuuid-devel
# For BlueZ device support
BuildRequires: bluez-libs-devel
# For Braille device support
BuildRequires: brlapi-devel
# For test suite
BuildRequires: check-devel
# For virtfs
BuildRequires: libcap-devel
# Hard requirement for version >= 1.3
BuildRequires: pixman-devel
# Documentation requirement
BuildRequires: perl-podlators
BuildRequires: texinfo

%if 0%{!?build_only_sub:1}
Requires: qemu-img = %{epoch}:%{version}-%{release}
%endif

# RHEV-specific changes:
# We provide special suffix for qemu-kvm so the conflit is easy
# In addition, RHEV version should obsolete all RHEL version in case both
# RHEL and RHEV channels are used
%rhel_rhev_conflicts qemu-kvm


%define qemudocdir %{_docdir}/%{pkgname}

%description
QEMU is a generic and open source processor emulator which achieves a good
emulation speed by using dynamic translation. QEMU has two operating modes:

 * Full system emulation. In this mode, QEMU emulates a full system (for
   example a PC), including a processor and various peripherials. It can be
   used to launch different Operating Systems without rebooting the PC or
   to debug system code.
 * User mode emulation. In this mode, QEMU can launch Linux processes compiled
   for one CPU on another CPU.

As QEMU requires no host kernel patches to run, it is safe and easy to use.
%if !%{rhev}
%package -n qemu-img
Summary: QEMU command line tool for manipulating disk images
Group: Development/Tools

%description -n qemu-img
This package provides a command line tool for manipulating disk images
%endif

%if 0%{!?build_only_sub:1}
%package -n qemu-kvm-common%{?pkgsuffix}
Summary: QEMU common files needed by all QEMU targets
Group: Development/Tools
Requires(post): /usr/bin/getent
Requires(post): /usr/sbin/groupadd
Requires(post): /usr/sbin/useradd
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

%description -n qemu-kvm-common%{?pkgsuffix}
QEMU is a generic and open source processor emulator which achieves a good
emulation speed by using dynamic translation.

This package provides the common files needed by all QEMU targets

%rhel_rhev_conflicts qemu-kvm-common
%endif

%if %{with guest_agent}
%package -n qemu-guest-agent
Summary: QEMU guest agent
Group: System Environment/Daemons
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

%description -n qemu-guest-agent
QEMU is a generic and open source processor emulator which achieves a good
emulation speed by using dynamic translation.

This package provides an agent to run inside guests, which communicates
with the host over a virtio-serial channel named "org.qemu.guest_agent.0"

This package does not need to be installed on the host OS.

%post -n qemu-guest-agent
%systemd_post qemu-guest-agent.service

%preun -n qemu-guest-agent
%systemd_preun qemu-guest-agent.service

%postun -n qemu-guest-agent
%systemd_postun_with_restart qemu-guest-agent.service

%endif

%if !%{rhev}
    %if 0%{!?build_only_sub:1}
%package tools
Summary: KVM debugging and diagnostics tools
Group: Development/Tools

%description tools
This package contains some diagnostics and debugging tools for KVM,
such as kvm_stat.
    %endif

%package -n libcacard
Summary:        Common Access Card (CAC) Emulation
Group:          Development/Libraries

%description -n libcacard
Common Access Card (CAC) emulation library.

%package -n libcacard-tools
Summary:        CAC Emulation tools
Group:          Development/Libraries
Requires:       libcacard = %{epoch}:%{version}-%{release}
# older qemu-img has vscclient which is now in libcacard-tools
Requires:       qemu-img >= 3:1.3.0-5

%description -n libcacard-tools
CAC emulation tools.

%package -n libcacard-devel
Summary:        CAC Emulation devel
Group:          Development/Libraries
Requires:       libcacard = %{epoch}:%{version}-%{release}

%description -n libcacard-devel
CAC emulation development files.
%endif

%prep
%setup -q -n qemu-%{version}
%patch1 -p1
#%%patch2 -p1
#%%patch3 -p1
#%%patch4 -p1
#%%patch5 -p1
#%%patch6 -p1
#%%patch7 -p1
#%%patch8 -p1
#%%patch9 -p1
#%%patch10 -p1
#%%patch11 -p1
#%%patch12 -p1
#%%patch13 -p1
#%%patch14 -p1
#%%patch15 -p1
#%%patch16 -p1
#%%patch17 -p1
#%%patch18 -p1
#%%patch19 -p1
#%%patch20 -p1
#%%patch21 -p1
#%%patch22 -p1
#%%patch23 -p1
#%%patch24 -p1
#%%patch25 -p1
#%%patch26 -p1
#%%patch27 -p1
#%%patch28 -p1
%patch29 -p1
%patch30 -p1
%patch31 -p1
%patch32 -p1
%patch33 -p1
%patch34 -p1
%patch35 -p1
%patch36 -p1
%patch37 -p1

# Fix CPUID model/level values on Conroe/Penryn/Nehalem CPU models
%patch38 -p1
%patch39 -p1
%patch40 -p1

#%patch41 -p1
%patch42 -p1
%patch43 -p1
%patch44 -p1
%patch45 -p1
%patch46 -p1
%patch47 -p1
%patch48 -p1
%patch49 -p1
%patch50 -p1
%patch51 -p1
%patch52 -p1
%patch53 -p1
%patch54 -p1
%patch55 -p1
%patch56 -p1
%patch57 -p1
%patch58 -p1
%patch59 -p1
%patch60 -p1
%patch61 -p1
#%%patch62 -p1
%patch63 -p1
%patch64 -p1
%patch65 -p1
%patch66 -p1
%patch67 -p1
%patch68 -p1
%patch69 -p1
%patch70 -p1
%patch71 -p1
%patch72 -p1
#%%patch73 -p1
%patch74 -p1
%patch75 -p1

%patch76 -p1
%patch77 -p1
%patch78 -p1
%patch79 -p1
%patch80 -p1
%patch81 -p1
%patch82 -p1
%patch83 -p1
%patch84 -p1
%patch85 -p1
%patch86 -p1
%patch87 -p1
%patch88 -p1
%patch89 -p1
#%%patch90 -p1
#%%patch91 -p1
#%%patch92 -p1
%patch93 -p1
%patch94 -p1
#%%patch95 -p1
%patch96 -p1
%patch97 -p1
%patch98 -p1
%patch99 -p1
%patch100 -p1
%patch101 -p1
%patch102 -p1
%patch103 -p1
%patch104 -p1
%patch105 -p1
%patch106 -p1
%patch107 -p1
%patch108 -p1
%patch109 -p1
%patch110 -p1
%patch111 -p1
%patch112 -p1
%patch113 -p1
%patch114 -p1
%patch115 -p1
%patch116 -p1
%patch117 -p1
%patch118 -p1
%patch119 -p1
%patch120 -p1
%patch121 -p1
%patch122 -p1
%patch123 -p1
%patch124 -p1
%patch125 -p1
%patch126 -p1
%patch127 -p1
%patch128 -p1
%patch129 -p1
%patch130 -p1
%patch131 -p1
%patch132 -p1
%patch133 -p1
%patch134 -p1
%patch135 -p1
%patch136 -p1
%patch137 -p1
%patch138 -p1
%patch139 -p1
%patch140 -p1
%patch141 -p1
%patch142 -p1
%patch143 -p1
%patch144 -p1
%patch145 -p1
%patch146 -p1
%patch147 -p1
%patch148 -p1
%patch149 -p1
%patch150 -p1
%patch151 -p1
%patch152 -p1
%patch153 -p1
%patch154 -p1
%patch155 -p1
%patch156 -p1
%patch157 -p1
%patch158 -p1
%patch159 -p1
%patch160 -p1
%patch161 -p1
%patch162 -p1
%patch163 -p1
%patch164 -p1
%patch165 -p1
%patch166 -p1
%patch168 -p1
%patch169 -p1
%patch170 -p1
%patch171 -p1
%patch172 -p1
%patch173 -p1
%patch174 -p1
%patch175 -p1
%patch176 -p1
%patch177 -p1
%patch178 -p1
%patch179 -p1
%patch180 -p1
%patch181 -p1
%patch182 -p1
%patch183 -p1
%patch184 -p1
%patch185 -p1
%patch186 -p1
%patch187 -p1
%patch188 -p1
%patch189 -p1
%patch190 -p1
%patch191 -p1
%patch192 -p1
%patch193 -p1
%patch194 -p1
%patch195 -p1
%patch196 -p1
%patch197 -p1
%patch198 -p1
%patch199 -p1
%patch200 -p1
%patch201 -p1
%patch202 -p1
%patch203 -p1
%patch204 -p1
%patch205 -p1
%patch206 -p1
%patch207 -p1
%patch208 -p1
%patch209 -p1
%patch210 -p1
%patch211 -p1
%patch212 -p1
%patch213 -p1
%patch214 -p1
%patch215 -p1
%patch216 -p1
%patch217 -p1
%patch218 -p1
%patch219 -p1
%patch220 -p1
%patch221 -p1
%patch222 -p1
%patch223 -p1
%patch224 -p1
%patch225 -p1
%patch226 -p1
%patch227 -p1
%patch228 -p1
%patch229 -p1
%patch230 -p1
%patch231 -p1
%patch232 -p1
%patch233 -p1
%patch234 -p1
%patch235 -p1
%patch236 -p1
%patch237 -p1
%patch238 -p1
%patch239 -p1
%patch240 -p1
%patch241 -p1
%patch242 -p1
%patch243 -p1
%patch244 -p1
%patch245 -p1
%patch246 -p1
%patch247 -p1
%patch248 -p1
%patch249 -p1
%patch250 -p1
%patch251 -p1
%patch252 -p1
%patch253 -p1
%patch254 -p1
%patch255 -p1
%patch256 -p1
%patch257 -p1
%patch258 -p1
%patch259 -p1
%patch260 -p1
%patch261 -p1
%patch262 -p1
%patch263 -p1
%patch264 -p1
%patch265 -p1
%patch266 -p1
%patch267 -p1
%patch268 -p1
%patch269 -p1
%patch270 -p1
%patch271 -p1
%patch272 -p1
%patch273 -p1
%patch274 -p1
%patch275 -p1
%patch276 -p1
%patch277 -p1
%patch278 -p1
%patch279 -p1
%patch280 -p1
%patch281 -p1
%patch282 -p1
%patch283 -p1
%patch284 -p1
%patch285 -p1
%patch286 -p1
%patch287 -p1
%patch288 -p1
%patch289 -p1
%patch290 -p1
%patch291 -p1
%patch292 -p1
%patch293 -p1
%patch294 -p1
%patch295 -p1
%patch296 -p1
%patch297 -p1
%patch298 -p1
%patch299 -p1
%patch300 -p1
%patch301 -p1
%patch302 -p1
%patch303 -p1
%patch304 -p1
%patch305 -p1
%patch306 -p1
%patch307 -p1
%patch308 -p1
%patch309 -p1
%patch310 -p1
%patch311 -p1
%patch312 -p1
%patch313 -p1
%patch314 -p1
%patch315 -p1
%patch316 -p1
%patch317 -p1
%patch318 -p1
%patch319 -p1
%patch320 -p1
%patch321 -p1
%patch322 -p1
%patch323 -p1
%patch324 -p1
%patch325 -p1
%patch326 -p1
%patch327 -p1
%patch328 -p1
%patch329 -p1
%patch330 -p1
%patch331 -p1
%patch332 -p1
%patch333 -p1
%patch334 -p1
%patch335 -p1
%patch336 -p1
%patch337 -p1
%patch338 -p1
%patch339 -p1
%patch340 -p1
%patch341 -p1
%patch342 -p1
%patch343 -p1
%patch344 -p1
%patch345 -p1
%patch346 -p1
%patch347 -p1
%patch348 -p1
%patch349 -p1
%patch350 -p1
%patch351 -p1
%patch352 -p1
%patch353 -p1
%patch354 -p1
%patch355 -p1
%patch356 -p1
%patch357 -p1
%patch358 -p1
%patch359 -p1
%patch360 -p1
%patch361 -p1
%patch362 -p1
%patch363 -p1
%patch364 -p1
%patch365 -p1
%patch366 -p1
%patch367 -p1
%patch368 -p1
%patch369 -p1
%patch370 -p1
%patch371 -p1
%patch372 -p1
%patch373 -p1
%patch374 -p1
%patch375 -p1
%patch376 -p1
%patch377 -p1
%patch378 -p1
%patch379 -p1
%patch380 -p1
%patch381 -p1
%patch382 -p1
%patch383 -p1
%patch384 -p1
%patch385 -p1
%patch386 -p1
%patch387 -p1
%patch388 -p1
%patch389 -p1
%patch390 -p1
%patch391 -p1
%patch392 -p1
%patch393 -p1
%patch394 -p1
%patch395 -p1
%patch396 -p1
%patch397 -p1
%patch398 -p1
%patch399 -p1
%patch400 -p1
%patch401 -p1
%patch402 -p1
%patch403 -p1
%patch404 -p1
%patch405 -p1
%patch406 -p1
%patch407 -p1
%patch408 -p1
%patch409 -p1
%patch410 -p1
%patch411 -p1
%patch412 -p1
%patch413 -p1
%patch414 -p1
%patch415 -p1
%patch416 -p1
%patch417 -p1
%patch418 -p1
%patch419 -p1
%patch420 -p1
%patch421 -p1
%patch422 -p1
%patch423 -p1
%patch424 -p1
%patch425 -p1
%patch426 -p1
%patch427 -p1
%patch428 -p1
%patch429 -p1
%patch430 -p1
%patch431 -p1
%patch432 -p1
%patch433 -p1
%patch434 -p1
%patch435 -p1
%patch436 -p1
%patch437 -p1
%patch438 -p1
%patch439 -p1
%patch440 -p1
%patch441 -p1
%patch442 -p1
%patch443 -p1
%patch444 -p1
%patch445 -p1
%patch446 -p1
%patch447 -p1
%patch448 -p1
%patch449 -p1
%patch450 -p1
%patch451 -p1
%patch452 -p1
%patch453 -p1
%patch454 -p1
%patch455 -p1
%patch456 -p1
%patch457 -p1
%patch458 -p1
%patch459 -p1
%patch460 -p1
%patch461 -p1
%patch462 -p1
%patch463 -p1
%patch464 -p1
%patch465 -p1
%patch466 -p1
%patch467 -p1
%patch468 -p1
%patch469 -p1
%patch470 -p1
%patch471 -p1
%patch472 -p1
%patch473 -p1
%patch474 -p1
%patch475 -p1
%patch476 -p1
%patch477 -p1
%patch478 -p1
%patch479 -p1
%patch480 -p1
%patch481 -p1
#%patch482 -p1
%patch483 -p1

%build
buildarch="%{kvm_target}-softmmu"

# --build-id option is used for giving info to the debug packages.
extraldflags="-Wl,--build-id";
buildldflags="VL_LDFLAGS=-Wl,--build-id"

%ifarch s390
    # drop -g flag to prevent memory exhaustion by linker
    %global optflags %(echo %{optflags} | sed 's/-g//')
    sed -i.debug 's/"-g $CFLAGS"/"$CFLAGS"/g' configure
%endif

dobuild() {
%if 0%{!?build_only_sub:1}
    ./configure \
        --prefix=%{_prefix} \
        --libdir=%{_libdir} \
        --sysconfdir=%{_sysconfdir} \
        --interp-prefix=%{_prefix}/qemu-%%M \
        --audio-drv-list=pa,alsa \
        --with-confsuffix=/%{pkgname} \
        --localstatedir=%{_localstatedir} \
        --libexecdir=%{_libexecdir} \
        --with-pkgversion=%{pkgname}-%{version}-%{release} \
        --disable-strip \
        --extra-ldflags="$extraldflags -pie -Wl,-z,relro -Wl,-z,now" \
        --extra-cflags="%{optflags} -fPIE -DPIE" \
        --enable-trace-backend=dtrace \
        --enable-werror \
        --disable-xen \
        --disable-virtfs \
        --enable-kvm \
        --enable-libusb \
        --enable-spice \
        --enable-seccomp \
        --disable-fdt \
        --enable-docs \
        --disable-sdl \
        --disable-debug-tcg \
        --disable-sparse \
        --disable-brlapi \
        --disable-bluez \
        --disable-vde \
        --disable-curses \
        --disable-curl \
        --enable-vnc-tls \
        --enable-vnc-sasl \
        --enable-linux-aio \
        --enable-smartcard-nss \
        --enable-usb-redir \
        --enable-vnc-png \
        --disable-vnc-jpeg \
        --enable-vnc-ws \
        --enable-uuid \
        --disable-vhost-scsi \
%if %{with guest_agent}
        --enable-guest-agent \
%else
        --disable-guest-agent \
%endif
%if %{rhev}
        --enable-live-block-ops \
        --enable-ceph-support \
%else
        --disable-live-block-ops \
        --disable-ceph-support \
%endif
        --disable-live-block-migration \
        --enable-glusterfs \
%if %{rhev}
        --block-drv-rw-whitelist=qcow2,raw,file,host_device,nbd,iscsi,gluster,rbd \
%else
        --block-drv-rw-whitelist=qcow2,raw,file,host_device,nbd,iscsi,gluster \
%endif
        --block-drv-ro-whitelist=vmdk,vhdx,vpc \
        "$@"

    echo "config-host.mak contents:"
    echo "==="
    cat config-host.mak
    echo "==="

    make V=1 %{?_smp_mflags} $buildldflags
%else
   ./configure --prefix=%{_prefix} \
               --libdir=%{_libdir} \
               --with-pkgversion=%{pkgname}-%{version}-%{release} \
               --disable-guest-agent \
               --target-list= --cpu=%{_arch}

   make libcacard.la %{?_smp_mflags} $buildldflags
   make vscclient %{?_smp_mflags} $buildldflags
   make qemu-img %{?_smp_mflags} $buildldflags
   make qemu-io %{?_smp_mflags} $buildldflags
   make qemu-nbd %{?_smp_mflags} $buildldflags
   make qemu-img.1 %{?_smp_mflags} $buildldflags
   make qemu-nbd.8 %{?_smp_mflags} $buildldflags
   make qemu-ga %{?_smp_mflags} $buildldflags
%endif
}

dobuild --target-list="$buildarch"

%if 0%{!?build_only_sub:1}
        # Setup back compat qemu-kvm binary
        ./scripts/tracetool.py --backend dtrace --format stap \
          --binary %{_libexecdir}/qemu-kvm --target-arch %{kvm_target} \
          --target-type system --probe-prefix \
          qemu.kvm < ./trace-events > qemu-kvm.stp

        cp -a %{kvm_target}-softmmu/qemu-system-%{kvm_target} qemu-kvm


    gcc %{SOURCE6} -O2 -g -o ksmctl
%endif

%install
%define _udevdir %(pkg-config --variable=udevdir udev)/rules.d

%if 0%{!?build_only_sub:1}
    install -D -p -m 0644 %{SOURCE4} $RPM_BUILD_ROOT%{_libdir}/systemd/system/ksm.service
    install -D -p -m 0644 %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/ksm
    install -D -p -m 0755 ksmctl $RPM_BUILD_ROOT%{_libdir}/systemd/ksmctl

    install -D -p -m 0644 %{SOURCE7} $RPM_BUILD_ROOT%{_libdir}/systemd/system/ksmtuned.service
    install -D -p -m 0755 %{SOURCE8} $RPM_BUILD_ROOT%{_sbindir}/ksmtuned
    install -D -p -m 0644 %{SOURCE9} $RPM_BUILD_ROOT%{_sysconfdir}/ksmtuned.conf

    mkdir -p $RPM_BUILD_ROOT%{_bindir}/
    mkdir -p $RPM_BUILD_ROOT%{_udevdir}

    install -m 0755 scripts/kvm/kvm_stat $RPM_BUILD_ROOT%{_bindir}/
    install -m 0644 %{SOURCE3} $RPM_BUILD_ROOT%{_udevdir}

    make DESTDIR=$RPM_BUILD_ROOT \
        sharedir="%{_datadir}/%{pkgname}" \
        datadir="%{_datadir}/%{pkgname}" \
        install

    mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{pkgname}
    mkdir -p $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset

    # Install compatibility roms
    install %{SOURCE14} $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/
    install %{SOURCE15} $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/
    install %{SOURCE16} $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/
    install %{SOURCE17} $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/

    install -m 0755 qemu-kvm $RPM_BUILD_ROOT%{_libexecdir}/
    install -m 0644 qemu-kvm.stp $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/

    rm $RPM_BUILD_ROOT%{_bindir}/qemu-system-%{kvm_target}
    rm $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/qemu-system-%{kvm_target}.stp

    mkdir -p $RPM_BUILD_ROOT%{qemudocdir}
    install -p -m 0644 -t ${RPM_BUILD_ROOT}%{qemudocdir} Changelog README COPYING COPYING.LIB LICENSE
    mv ${RPM_BUILD_ROOT}%{_docdir}/qemu/qemu-doc.html $RPM_BUILD_ROOT%{qemudocdir}
    mv ${RPM_BUILD_ROOT}%{_docdir}/qemu/qemu-tech.html $RPM_BUILD_ROOT%{qemudocdir}
    mv ${RPM_BUILD_ROOT}%{_docdir}/qemu/qmp-commands.txt $RPM_BUILD_ROOT%{qemudocdir}
    chmod -x ${RPM_BUILD_ROOT}%{_mandir}/man1/*
    chmod -x ${RPM_BUILD_ROOT}%{_mandir}/man8/*

    install -D -p -m 0644 qemu.sasl $RPM_BUILD_ROOT%{_sysconfdir}/sasl2/qemu-kvm.conf

    # Provided by package openbios
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/openbios-ppc
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/openbios-sparc32
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/openbios-sparc64
    # Provided by package SLOF
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/slof.bin

    # Remove unpackaged files.
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/palcode-clipper
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/petalogix*.dtb
    rm -f ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/bamboo.dtb
    rm -f ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/ppc_rom.bin
    rm -f ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/spapr-rtas.bin
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/s390-zipl.rom
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/s390-ccw.img

    # Remove efi roms
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/efi*.rom

    # Provided by package ipxe
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/pxe*rom
    # Provided by package vgabios
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/vgabios*bin
    # Provided by package seabios
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/bios.bin
    # Provided by package sgabios
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/sgabios.bin

    # the pxe gpxe images will be symlinks to the images on
    # /usr/share/ipxe, as QEMU doesn't know how to look
    # for other paths, yet.
    pxe_link() {
        ln -s ../ipxe/$2.rom %{buildroot}%{_datadir}/%{pkgname}/pxe-$1.rom
    }

    pxe_link e1000 8086100e
    pxe_link ne2k_pci 10ec8029
    pxe_link pcnet 10222000
    pxe_link rtl8139 10ec8139
    pxe_link virtio 1af41000

    rom_link() {
        ln -s $1 %{buildroot}%{_datadir}/%{pkgname}/$2
    }

    rom_link ../seavgabios/vgabios-isavga.bin vgabios.bin
    rom_link ../seavgabios/vgabios-cirrus.bin vgabios-cirrus.bin
    rom_link ../seavgabios/vgabios-qxl.bin vgabios-qxl.bin
    rom_link ../seavgabios/vgabios-stdvga.bin vgabios-stdvga.bin
    rom_link ../seavgabios/vgabios-vmware.bin vgabios-vmware.bin
    rom_link ../seabios/bios.bin bios.bin
    rom_link ../sgabios/sgabios.bin sgabios.bin
%endif

%if %{with guest_agent}
    # For the qemu-guest-agent subpackage, install:
    # - the systemd service file and the udev rules:
    mkdir -p $RPM_BUILD_ROOT%{_unitdir}
    mkdir -p $RPM_BUILD_ROOT%{_udevdir}
    install -m 0644 %{SOURCE10} $RPM_BUILD_ROOT%{_unitdir}
    install -m 0644 %{SOURCE11} $RPM_BUILD_ROOT%{_udevdir}

    # - the environment file for the systemd service:
    install -D -p -m 0644 %{SOURCE13} \
      $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/qemu-ga

    # - the fsfreeze hook script:
    install -D --preserve-timestamps \
      scripts/qemu-guest-agent/fsfreeze-hook \
      $RPM_BUILD_ROOT%{_sysconfdir}/qemu-ga/fsfreeze-hook

    # - the directory for user scripts:
    mkdir $RPM_BUILD_ROOT%{_sysconfdir}/qemu-ga/fsfreeze-hook.d

    # - and the fsfreeze script samples:
    mkdir --parents $RPM_BUILD_ROOT%{_datadir}/%{name}/qemu-ga/fsfreeze-hook.d/
    install --preserve-timestamps --mode=0644 \
      scripts/qemu-guest-agent/fsfreeze-hook.d/*.sample \
      $RPM_BUILD_ROOT%{_datadir}/%{name}/qemu-ga/fsfreeze-hook.d/

    # - Install dedicated log directory:
    mkdir -p -v $RPM_BUILD_ROOT%{_localstatedir}/log/qemu-ga/
%endif

%if 0%{!?build_only_sub:1}
    # Install rules to use the bridge helper with libvirt's virbr0
    install -m 0644 %{SOURCE12} $RPM_BUILD_ROOT%{_sysconfdir}/%{pkgname}
    chmod u+s $RPM_BUILD_ROOT%{_libexecdir}/qemu-bridge-helper
%endif

%if !%{rhev}
    make %{?_smp_mflags} $buildldflags DESTDIR=$RPM_BUILD_ROOT install-libcacard
    find $RPM_BUILD_ROOT -name "libcacard.so*" -exec chmod +x \{\} \;
%endif
find $RPM_BUILD_ROOT -name '*.la' -or -name '*.a' | xargs rm -f

%if 0%{?build_only_sub}
    mkdir -p $RPM_BUILD_ROOT%{_bindir}
    mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1/*
    mkdir -p $RPM_BUILD_ROOT%{_mandir}/man8/*
    libtool --mode=install install -m 0755 vscclient $RPM_BUILD_ROOT%{_bindir}/vscclient
    install -m 0755 qemu-img $RPM_BUILD_ROOT%{_bindir}/qemu-img
    install -m 0755 qemu-io $RPM_BUILD_ROOT%{_bindir}/qemu-io
    install -m 0755 qemu-nbd $RPM_BUILD_ROOT%{_bindir}/qemu-nbd
    install -c -m 0644 qemu-img.1 ${RPM_BUILD_ROOT}%{_mandir}/man1/qemu-img.1
    install -c -m 0644 qemu-nbd.8 ${RPM_BUILD_ROOT}%{_mandir}/man8/qemu-nbd.8
    install -c -m 0755  qemu-ga ${RPM_BUILD_ROOT}%{_bindir}/qemu-ga
    chmod -x ${RPM_BUILD_ROOT}%{_mandir}/man1/*
    chmod -x ${RPM_BUILD_ROOT}%{_mandir}/man8/*
%endif

%if %{rhev}
    # Remove files unpackacked for rhev build
    rm -rf ${RPM_BUILD_ROOT}%{_includedir}/cacard
    rm -rf ${RPM_BUILD_ROOT}%{_bindir}/qemu-img
    rm -rf ${RPM_BUILD_ROOT}%{_bindir}/qemu-io
    rm -rf ${RPM_BUILD_ROOT}%{_bindir}/qemu-nbd
    rm -rf ${RPM_BUILD_ROOT}%{_mandir}/man1/qemu-img.1*
    rm -rf ${RPM_BUILD_ROOT}%{_mandir}/man8/qemu-nbd.8*
    rm -rf ${RPM_BUILD_ROOT}%{_bindir}/vscclient
    rm -rf ${RPM_BUILD_ROOT}%{_libdir}/libcacard.so*
    rm -rf ${RPM_BUILD_ROOT}%{_libdir}/pkgconfig/libcacard.pc
    rm -rf ${RPM_BUILD_ROOT}%{_bindir}/kvm_stat
%endif

%if 0%{!?build_only_sub:1}
%check
    make check
%endif
%post
# load kvm modules now, so we can make sure no reboot is needed.
# If there's already a kvm module installed, we don't mess with it
sh %{_sysconfdir}/sysconfig/modules/kvm.modules &> /dev/null || :
    udevadm trigger --subsystem-match=misc --sysname-match=kvm --action=add || :

%if 0%{!?build_only_sub:1}
%post -n qemu-kvm-common%{?pkgsuffix}
    %systemd_post ksm.service
    %systemd_post ksmtuned.service

    getent group kvm >/dev/null || groupadd -g 36 -r kvm
    getent group qemu >/dev/null || groupadd -g 107 -r qemu
    getent passwd qemu >/dev/null || \
       useradd -r -u 107 -g qemu -G kvm -d / -s /sbin/nologin \
       -c "qemu user" qemu

%preun -n qemu-kvm-common%{?pkgsuffix}
    %systemd_preun ksm.service
    %systemd_preun ksmtuned.service

%postun -n qemu-kvm-common%{?pkgsuffix}
    %systemd_postun_with_restart ksm.service
    %systemd_postun_with_restart ksmtuned.service
%endif

%global kvm_files \
%{_udevdir}/80-kvm.rules

%global qemu_kvm_files \
%{_libexecdir}/qemu-kvm \
%{_datadir}/systemtap/tapset/qemu-kvm.stp

%if 0%{!?build_only_sub:1}
%files -n qemu-kvm-common%{?pkgsuffix}
    %defattr(-,root,root)
    %dir %{qemudocdir}
    %doc %{qemudocdir}/Changelog
    %doc %{qemudocdir}/README
    %doc %{qemudocdir}/qemu-doc.html
    %doc %{qemudocdir}/qemu-tech.html
    %doc %{qemudocdir}/qmp-commands.txt
    %doc %{qemudocdir}/COPYING
    %doc %{qemudocdir}/COPYING.LIB
    %doc %{qemudocdir}/LICENSE
    %dir %{_datadir}/%{pkgname}/
    %{_datadir}/%{pkgname}/keymaps/
    %{_mandir}/man1/%{pkgname}.1*
    %attr(4755, -, -) %{_libexecdir}/qemu-bridge-helper
    %config(noreplace) %{_sysconfdir}/sasl2/%{pkgname}.conf
    %{_libdir}/systemd/system/ksm.service
    %{_libdir}/systemd/ksmctl
    %config(noreplace) %{_sysconfdir}/sysconfig/ksm
    %{_libdir}/systemd/system/ksmtuned.service
    %{_sbindir}/ksmtuned
    %config(noreplace) %{_sysconfdir}/ksmtuned.conf
    %dir %{_sysconfdir}/%{pkgname}
    %config(noreplace) %{_sysconfdir}/%{pkgname}/bridge.conf
%endif

%if %{with guest_agent}
%files -n qemu-guest-agent
    %defattr(-,root,root,-)
    %doc COPYING README
    %{_bindir}/qemu-ga
    %{_unitdir}/qemu-guest-agent.service
    %{_udevdir}/99-qemu-guest-agent.rules
    %{_sysconfdir}/sysconfig/qemu-ga
    %{_sysconfdir}/qemu-ga
    %{_datadir}/%{name}/qemu-ga
    %dir %{_localstatedir}/log/qemu-ga
%endif

%if 0%{!?build_only_sub:1}
%files
    %defattr(-,root,root)
    %{_datadir}/%{pkgname}/acpi-dsdt.aml
    %{_datadir}/%{pkgname}/q35-acpi-dsdt.aml
    %{_datadir}/%{pkgname}/bios.bin
    %{_datadir}/%{pkgname}/sgabios.bin
    %{_datadir}/%{pkgname}/linuxboot.bin
    %{_datadir}/%{pkgname}/multiboot.bin
    %{_datadir}/%{pkgname}/kvmvapic.bin
    %{_datadir}/%{pkgname}/vgabios.bin
    %{_datadir}/%{pkgname}/vgabios-cirrus.bin
    %{_datadir}/%{pkgname}/vgabios-qxl.bin
    %{_datadir}/%{pkgname}/vgabios-stdvga.bin
    %{_datadir}/%{pkgname}/vgabios-vmware.bin
    %{_datadir}/%{pkgname}/pxe-e1000.rom
    %{_datadir}/%{pkgname}/pxe-virtio.rom
    %{_datadir}/%{pkgname}/pxe-pcnet.rom
    %{_datadir}/%{pkgname}/pxe-rtl8139.rom
    %{_datadir}/%{pkgname}/pxe-ne2k_pci.rom
    %{_datadir}/%{pkgname}/qemu-icon.bmp
    %{_datadir}/%{pkgname}/rhel6-virtio.rom
    %{_datadir}/%{pkgname}/rhel6-pcnet.rom
    %{_datadir}/%{pkgname}/rhel6-rtl8139.rom
    %{_datadir}/%{pkgname}/rhel6-ne2k_pci.rom
    %config(noreplace) %{_sysconfdir}/%{pkgname}/target-x86_64.conf
    %{?kvm_files:}
    %{?qemu_kvm_files:}

    %if !%{rhev}
%files tools
        %defattr(-,root,root,-)
        %{_bindir}/kvm_stat
    %endif
%endif

%if !%{rhev}
%files -n qemu-img
    %defattr(-,root,root)
    %{_bindir}/qemu-img
    %{_bindir}/qemu-io
    %{_bindir}/qemu-nbd
    %{_mandir}/man1/qemu-img.1*
    %{_mandir}/man8/qemu-nbd.8*

%files -n libcacard
    %defattr(-,root,root,-)
    %{_libdir}/libcacard.so.*

%files -n libcacard-tools
    %defattr(-,root,root,-)
    %{_bindir}/vscclient

%files -n libcacard-devel
    %defattr(-,root,root,-)
    %{_includedir}/cacard
    %{_libdir}/libcacard.so
    %{_libdir}/pkgconfig/libcacard.pc
%endif

%changelog
* Fri Nov 08 2013 Michal Novotny <minovotn@redhat.com> - 1.5.3-18.el7
- Removing leaked patch kvm-e1000-rtl8139-update-HMP-NIC-when-every-bit-is-writt.patch

* Thu Nov 07 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-17.el7
- kvm-pci-assign-Add-MSI-affinity-support.patch [bz#1025877]
- kvm-Fix-potential-resource-leak-missing-fclose.patch [bz#1025877]
- kvm-pci-assign-remove-the-duplicate-function-name-in-deb.patch [bz#1025877]
- kvm-Remove-s390-ccw-img-loader.patch [bz#1017682]
- kvm-Fix-vscclient-installation.patch [bz#1017681]
- kvm-Change-qemu-bridge-helper-permissions-to-4755.patch [bz#1017689]
- kvm-net-update-nic-info-during-device-reset.patch [bz#922589]
- kvm-net-e1000-update-network-information-when-macaddr-is.patch [bz#922589]
- kvm-net-rtl8139-update-network-information-when-macaddr-.patch [bz#922589]
- kvm-virtio-net-fix-up-HMP-NIC-info-string-on-reset.patch [bz#1026689]
- kvm-vfio-pci-VGA-quirk-update.patch [bz#1025477]
- kvm-vfio-pci-Add-support-for-MSI-affinity.patch [bz#1025477]
- kvm-vfio-pci-Test-device-reset-capabilities.patch [bz#1026550]
- kvm-vfio-pci-Lazy-PCI-option-ROM-loading.patch [bz#1026550]
- kvm-vfio-pci-Cleanup-error_reports.patch [bz#1026550]
- kvm-vfio-pci-Add-dummy-PCI-ROM-write-accessor.patch [bz#1026550]
- kvm-vfio-pci-Fix-endian-issues-in-vfio_pci_size_rom.patch [bz#1026550]
- kvm-linux-headers-Update-to-include-vfio-pci-hot-reset-s.patch [bz#1025472]
- kvm-vfio-pci-Implement-PCI-hot-reset.patch [bz#1025472]
- kvm-linux-headers-Update-for-KVM-VFIO-device.patch [bz#1025474]
- kvm-vfio-pci-Make-use-of-new-KVM-VFIO-device.patch [bz#1025474]
- kvm-vmdk-Fix-vmdk_parse_extents.patch [bz#995866]
- kvm-vmdk-fix-VMFS-extent-parsing.patch [bz#995866]
- kvm-e1000-rtl8139-update-HMP-NIC-when-every-bit-is-writt.patch [bz#922589]
- kvm-don-t-disable-ctrl_mac_addr-feature-for-6.5-machine-.patch [bz#1005039]
- Resolves: bz#1005039
  (add compat property to disable ctrl_mac_addr feature)
- Resolves: bz#1017681
  (rpmdiff test "Multilib regressions": vscclient is a libtool script on s390/s390x/ppc/ppc64)
- Resolves: bz#1017682
  (/usr/share/qemu-kvm/s390-ccw.img need not be distributed)
- Resolves: bz#1017689
  (/usr/libexec/qemu-bridge-helper permissions should be 4755)
- Resolves: bz#1025472
  (Nvidia GPU device assignment - qemu-kvm - bus reset support)
- Resolves: bz#1025474
  (Nvidia GPU device assignment - qemu-kvm - NoSnoop support)
- Resolves: bz#1025477
  (VFIO MSI affinity)
- Resolves: bz#1025877
  (pci-assign lacks MSI affinity support)
- Resolves: bz#1026550
  (QEMU VFIO update ROM loading code)
- Resolves: bz#1026689
  (virtio-net: macaddr is reset but network info of monitor isn't updated)
- Resolves: bz#922589
  (e1000/rtl8139: qemu mac address can not be changed via set the hardware address in guest)
- Resolves: bz#995866
  (fix vmdk support to ESX images)

* Thu Nov 07 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-16.el7
- kvm-block-drop-bs_snapshots-global-variable.patch [bz#1026524]
- kvm-block-move-snapshot-code-in-block.c-to-block-snapsho.patch [bz#1026524]
- kvm-block-fix-vvfat-error-path-for-enable_write_target.patch [bz#1026524]
- kvm-block-Bugfix-format-and-snapshot-used-in-drive-optio.patch [bz#1026524]
- kvm-iscsi-use-bdrv_new-instead-of-stack-structure.patch [bz#1026524]
- kvm-qcow2-Add-corrupt-bit.patch [bz#1004347]
- kvm-qcow2-Metadata-overlap-checks.patch [bz#1004347]
- kvm-qcow2-Employ-metadata-overlap-checks.patch [bz#1004347]
- kvm-qcow2-refcount-Move-OFLAG_COPIED-checks.patch [bz#1004347]
- kvm-qcow2-refcount-Repair-OFLAG_COPIED-errors.patch [bz#1004347]
- kvm-qcow2-refcount-Repair-shared-refcount-blocks.patch [bz#1004347]
- kvm-qcow2_check-Mark-image-consistent.patch [bz#1004347]
- kvm-qemu-iotests-Overlapping-cluster-allocations.patch [bz#1004347]
- kvm-w32-Fix-access-to-host-devices-regression.patch [bz#1026524]
- kvm-add-qemu-img-convert-n-option-skip-target-volume-cre.patch [bz#1026524]
- kvm-bdrv-Use-Error-for-opening-images.patch [bz#1026524]
- kvm-bdrv-Use-Error-for-creating-images.patch [bz#1026524]
- kvm-block-Error-parameter-for-open-functions.patch [bz#1026524]
- kvm-block-Error-parameter-for-create-functions.patch [bz#1026524]
- kvm-qemu-img-create-Emit-filename-on-error.patch [bz#1026524]
- kvm-qcow2-Use-Error-parameter.patch [bz#1026524]
- kvm-qemu-iotests-Adjustments-due-to-error-propagation.patch [bz#1026524]
- kvm-block-raw-Employ-error-parameter.patch [bz#1026524]
- kvm-block-raw-win32-Employ-error-parameter.patch [bz#1026524]
- kvm-blkdebug-Employ-error-parameter.patch [bz#1026524]
- kvm-blkverify-Employ-error-parameter.patch [bz#1026524]
- kvm-block-raw-posix-Employ-error-parameter.patch [bz#1026524]
- kvm-block-raw-win32-Always-use-errno-in-hdev_open.patch [bz#1026524]
- kvm-qmp-Documentation-for-BLOCK_IMAGE_CORRUPTED.patch [bz#1004347]
- kvm-qcow2-Correct-snapshots-size-for-overlap-check.patch [bz#1004347]
- kvm-qcow2-CHECK_OFLAG_COPIED-is-obsolete.patch [bz#1004347]
- kvm-qcow2-Correct-endianness-in-overlap-check.patch [bz#1004347]
- kvm-qcow2-Switch-L1-table-in-a-single-sequence.patch [bz#1004347]
- kvm-qcow2-Use-pread-for-inactive-L1-in-overlap-check.patch [bz#1004347]
- kvm-qcow2-Remove-wrong-metadata-overlap-check.patch [bz#1004347]
- kvm-qcow2-Use-negated-overflow-check-mask.patch [bz#1004347]
- kvm-qcow2-Make-overlap-check-mask-variable.patch [bz#1004347]
- kvm-qcow2-Add-overlap-check-options.patch [bz#1004347]
- kvm-qcow2-Array-assigning-options-to-OL-check-bits.patch [bz#1004347]
- kvm-qcow2-Add-more-overlap-check-bitmask-macros.patch [bz#1004347]
- kvm-qcow2-Evaluate-overlap-check-options.patch [bz#1004347]
- kvm-qapi-types.py-Split-off-generate_struct_fields.patch [bz#978402]
- kvm-qapi-types.py-Fix-enum-struct-sizes-on-i686.patch [bz#978402]
- kvm-qapi-types-visit.py-Pass-whole-expr-dict-for-structs.patch [bz#978402]
- kvm-qapi-types-visit.py-Inheritance-for-structs.patch [bz#978402]
- kvm-blockdev-Introduce-DriveInfo.enable_auto_del.patch [bz#978402]
- kvm-Implement-qdict_flatten.patch [bz#978402]
- kvm-blockdev-blockdev-add-QMP-command.patch [bz#978402]
- kvm-blockdev-Separate-ID-generation-from-DriveInfo-creat.patch [bz#978402]
- kvm-blockdev-Pass-QDict-to-blockdev_init.patch [bz#978402]
- kvm-blockdev-Move-parsing-of-media-option-to-drive_init.patch [bz#978402]
- kvm-blockdev-Move-parsing-of-if-option-to-drive_init.patch [bz#978402]
- kvm-blockdev-Moving-parsing-of-geometry-options-to-drive.patch [bz#978402]
- kvm-blockdev-Move-parsing-of-boot-option-to-drive_init.patch [bz#978402]
- kvm-blockdev-Move-bus-unit-index-processing-to-drive_ini.patch [bz#978402]
- kvm-blockdev-Move-virtio-blk-device-creation-to-drive_in.patch [bz#978402]
- kvm-blockdev-Remove-IF_-check-for-read-only-blockdev_ini.patch [bz#978402]
- kvm-qemu-iotests-Check-autodel-behaviour-for-device_del.patch [bz#978402]
- kvm-blockdev-Remove-media-parameter-from-blockdev_init.patch [bz#978402]
- kvm-blockdev-Don-t-disable-COR-automatically-with-blockd.patch [bz#978402]
- kvm-blockdev-blockdev_init-error-conversion.patch [bz#978402]
- kvm-sd-Avoid-access-to-NULL-BlockDriverState.patch [bz#978402]
- kvm-blockdev-fix-cdrom-read_only-flag.patch [bz#978402]
- kvm-block-fix-backing-file-overriding.patch [bz#978402]
- kvm-block-Disable-BDRV_O_COPY_ON_READ-for-the-backing-fi.patch [bz#978402]
- kvm-block-Don-t-copy-backing-file-name-on-error.patch [bz#978402]
- kvm-qemu-iotests-Try-creating-huge-qcow2-image.patch [bz#980771]
- kvm-block-move-qmp-and-info-dump-related-code-to-block-q.patch [bz#980771]
- kvm-block-dump-snapshot-and-image-info-to-specified-outp.patch [bz#980771]
- kvm-block-add-snapshot-info-query-function-bdrv_query_sn.patch [bz#980771]
- kvm-block-add-image-info-query-function-bdrv_query_image.patch [bz#980771]
- kvm-qmp-add-ImageInfo-in-BlockDeviceInfo-used-by-query-b.patch [bz#980771]
- kvm-vmdk-Implement-.bdrv_has_zero_init.patch [bz#980771]
- kvm-qemu-iotests-Add-basic-ability-to-use-binary-sample-.patch [bz#980771]
- kvm-qemu-iotests-Quote-TEST_IMG-and-TEST_DIR-usage.patch [bz#980771]
- kvm-qemu-iotests-fix-test-case-059.patch [bz#980771]
- kvm-qapi-Add-ImageInfoSpecific-type.patch [bz#980771]
- kvm-block-Add-bdrv_get_specific_info.patch [bz#980771]
- kvm-block-qapi-Human-readable-ImageInfoSpecific-dump.patch [bz#980771]
- kvm-qcow2-Add-support-for-ImageInfoSpecific.patch [bz#980771]
- kvm-qemu-iotests-Discard-specific-info-in-_img_info.patch [bz#980771]
- kvm-qemu-iotests-Additional-info-from-qemu-img-info.patch [bz#980771]
- kvm-vmdk-convert-error-code-to-use-errp.patch [bz#980771]
- kvm-vmdk-refuse-enabling-zeroed-grain-with-flat-images.patch [bz#980771]
- kvm-qapi-Add-optional-field-compressed-to-ImageInfo.patch [bz#980771]
- kvm-vmdk-Only-read-cid-from-image-file-when-opening.patch [bz#980771]
- kvm-vmdk-Implment-bdrv_get_specific_info.patch [bz#980771]
- Resolves: bz#1004347
  (Backport qcow2 corruption prevention patches)
- Resolves: bz#1026524
  (Backport block layer error parameter patches)
- Resolves: bz#978402
  ([RFE] Add discard support to qemu-kvm layer)
- Resolves: bz#980771
  ([RFE]  qemu-img should be able to tell the compat version of a qcow2 image)

* Thu Nov 07 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-15.el7
- kvm-cow-make-reads-go-at-a-decent-speed.patch [bz#989646]
- kvm-cow-make-writes-go-at-a-less-indecent-speed.patch [bz#989646]
- kvm-cow-do-not-call-bdrv_co_is_allocated.patch [bz#989646]
- kvm-block-keep-bs-total_sectors-up-to-date-even-for-grow.patch [bz#989646]
- kvm-block-make-bdrv_co_is_allocated-static.patch [bz#989646]
- kvm-block-do-not-use-total_sectors-in-bdrv_co_is_allocat.patch [bz#989646]
- kvm-block-remove-bdrv_is_allocated_above-bdrv_co_is_allo.patch [bz#989646]
- kvm-block-expect-errors-from-bdrv_co_is_allocated.patch [bz#989646]
- kvm-block-Fix-compiler-warning-Werror-uninitialized.patch [bz#989646]
- kvm-qemu-img-always-probe-the-input-image-for-allocated-.patch [bz#989646]
- kvm-block-make-bdrv_has_zero_init-return-false-for-copy-.patch [bz#989646]
- kvm-block-introduce-bdrv_get_block_status-API.patch [bz#989646]
- kvm-block-define-get_block_status-return-value.patch [bz#989646]
- kvm-block-return-get_block_status-data-and-flags-for-for.patch [bz#989646]
- kvm-block-use-bdrv_has_zero_init-to-return-BDRV_BLOCK_ZE.patch [bz#989646]
- kvm-block-return-BDRV_BLOCK_ZERO-past-end-of-backing-fil.patch [bz#989646]
- kvm-qemu-img-add-a-map-subcommand.patch [bz#989646]
- kvm-docs-qapi-document-qemu-img-map.patch [bz#989646]
- kvm-raw-posix-return-get_block_status-data-and-flags.patch [bz#989646]
- kvm-raw-posix-report-unwritten-extents-as-zero.patch [bz#989646]
- kvm-block-add-default-get_block_status-implementation-fo.patch [bz#989646]
- kvm-block-look-for-zero-blocks-in-bs-file.patch [bz#989646]
- kvm-qemu-img-fix-invalid-JSON.patch [bz#989646]
- kvm-block-get_block_status-set-pnum-0-on-error.patch [bz#989646]
- kvm-block-get_block_status-avoid-segfault-if-there-is-no.patch [bz#989646]
- kvm-block-get_block_status-avoid-redundant-callouts-on-r.patch [bz#989646]
- kvm-qcow2-Restore-total_sectors-value-in-save_vmstate.patch [bz#1025740]
- kvm-qcow2-Unset-zero_beyond_eof-in-save_vmstate.patch [bz#1025740]
- kvm-qemu-iotests-Test-for-loading-VM-state-from-qcow2.patch [bz#1025740]
- kvm-apic-rename-apic-specific-bitopts.patch [bz#1001216]
- kvm-hw-import-bitmap-operations-in-qdev-core-header.patch [bz#1001216]
- kvm-qemu-help-Sort-devices-by-logical-functionality.patch [bz#1001216]
- kvm-devices-Associate-devices-to-their-logical-category.patch [bz#1001216]
- kvm-Mostly-revert-qemu-help-Sort-devices-by-logical-func.patch [bz#1001216]
- kvm-qdev-monitor-Group-device_add-help-and-info-qdm-by-c.patch [bz#1001216]
- kvm-qdev-Replace-no_user-by-cannot_instantiate_with_devi.patch [bz#1001216]
- kvm-sysbus-Set-cannot_instantiate_with_device_add_yet.patch [bz#1001216]
- kvm-cpu-Document-why-cannot_instantiate_with_device_add_.patch [bz#1001216]
- kvm-apic-Document-why-cannot_instantiate_with_device_add.patch [bz#1001216]
- kvm-pci-host-Consistently-set-cannot_instantiate_with_de.patch [bz#1001216]
- kvm-ich9-Document-why-cannot_instantiate_with_device_add.patch [bz#1001216]
- kvm-piix3-piix4-Clean-up-use-of-cannot_instantiate_with_.patch [bz#1001216]
- kvm-vt82c686-Clean-up-use-of-cannot_instantiate_with_dev.patch [bz#1001216]
- kvm-isa-Clean-up-use-of-cannot_instantiate_with_device_a.patch [bz#1001216]
- kvm-qdev-Do-not-let-the-user-try-to-device_add-when-it-c.patch [bz#1001216]
- kvm-rhel-Revert-unwanted-cannot_instantiate_with_device_.patch [bz#1001216]
- kvm-rhel-Revert-downstream-changes-to-unused-default-con.patch [bz#1001076]
- kvm-rhel-Drop-cfi.pflash01-and-isa-ide-device.patch [bz#1001076]
- kvm-rhel-Drop-isa-vga-device.patch [bz#1001088]
- kvm-rhel-Make-isa-cirrus-vga-device-unavailable.patch [bz#1001088]
- kvm-rhel-Make-ccid-card-emulated-device-unavailable.patch [bz#1001123]
- kvm-x86-fix-migration-from-pre-version-12.patch [bz#1005695]
- kvm-x86-cpuid-reconstruct-leaf-0Dh-data.patch [bz#1005695]
- kvm-kvmvapic-Catch-invalid-ROM-size.patch [bz#920021]
- kvm-kvmvapic-Enter-inactive-state-on-hardware-reset.patch [bz#920021]
- kvm-kvmvapic-Clear-also-physical-ROM-address-when-enteri.patch [bz#920021]
- kvm-block-optionally-disable-live-block-jobs.patch [bz#987582]
- kvm-rpm-spec-template-disable-live-block-ops-for-rhel-en.patch [bz#987582]
- kvm-migration-disable-live-block-migration-b-i-for-rhel-.patch [bz#1022392]
- kvm-Build-ceph-rbd-only-for-rhev.patch [bz#987583]
- kvm-spec-Disable-host-cdrom-RHEL-only.patch [bz#760885]
- kvm-rhel-Make-pci-serial-2x-and-pci-serial-4x-device-una.patch [bz#1001180]
- kvm-usb-host-libusb-Fix-reset-handling.patch [bz#980415]
- kvm-usb-host-libusb-Configuration-0-may-be-a-valid-confi.patch [bz#980383]
- kvm-usb-host-libusb-Detach-kernel-drivers-earlier.patch [bz#980383]
- kvm-monitor-Remove-pci_add-command-for-Red-Hat-Enterpris.patch [bz#1010858]
- kvm-monitor-Remove-pci_del-command-for-Red-Hat-Enterpris.patch [bz#1010858]
- kvm-monitor-Remove-usb_add-del-commands-for-Red-Hat-Ente.patch [bz#1010858]
- kvm-monitor-Remove-host_net_add-remove-for-Red-Hat-Enter.patch [bz#1010858]
- kvm-fw_cfg-add-API-to-find-FW-cfg-object.patch [bz#990601]
- kvm-pvpanic-use-FWCfgState-explicitly.patch [bz#990601]
- kvm-pvpanic-initialization-cleanup.patch [bz#990601]
- kvm-pvpanic-fix-fwcfg-for-big-endian-hosts.patch [bz#990601]
- kvm-hw-misc-make-pvpanic-known-to-user.patch [bz#990601]
- kvm-gdbstub-do-not-restart-crashed-guest.patch [bz#990601]
- kvm-gdbstub-fix-for-commit-87f25c12bfeaaa0c41fb857713bbc.patch [bz#990601]
- kvm-vl-allow-cont-from-panicked-state.patch [bz#990601]
- kvm-hw-misc-don-t-create-pvpanic-device-by-default.patch [bz#990601]
- kvm-block-vhdx-add-migration-blocker.patch [bz#1007176]
- kvm-qemu-kvm.spec-add-vhdx-to-the-read-only-block-driver.patch [bz#1007176]
- kvm-qemu-kvm.spec-Add-VPC-VHD-driver-to-the-block-read-o.patch [bz#1007176]
- Resolves: bz#1001076
  (Disable or remove other block devices we won't support)
- Resolves: bz#1001088
  (Disable or remove display devices we won't support)
- Resolves: bz#1001123
  (Disable or remove device ccid-card-emulated)
- Resolves: bz#1001180
  (Disable or remove devices pci-serial-2x, pci-serial-4x)
- Resolves: bz#1001216
  (Fix no_user or provide another way make devices unavailable with -device / device_add)
- Resolves: bz#1005695
  (QEMU should hide CPUID.0Dh values that it does not support)
- Resolves: bz#1007176
  (Add VPC and VHDX file formats as supported in qemu-kvm (read-only))
- Resolves: bz#1010858
  (Disable unused human monitor commands)
- Resolves: bz#1022392
  (Disable live-storage-migration in qemu-kvm (migrate -b/-i))
- Resolves: bz#1025740
  (Saving VM state on qcow2 images results in VM state corruption)
- Resolves: bz#760885
  (Disable host cdrom passthrough)
- Resolves: bz#920021
  (qemu-kvm segment fault when reboot guest after hot unplug device with option ROM)
- Resolves: bz#980383
  (The usb3.0 stick can't be returned back to host after shutdown guest with usb3.0 pass-through)
- Resolves: bz#980415
  (libusbx: error [_open_sysfs_attr] open /sys/bus/usb/devices/4-1/bConfigurationValue failed ret=-1 errno=2)
- Resolves: bz#987582
  (Initial Virtualization Differentiation for RHEL7 (Live snapshots))
- Resolves: bz#987583
  (Initial Virtualization Differentiation for RHEL7 (Ceph enablement))
- Resolves: bz#989646
  (Support backup vendors in qemu to access qcow disk readonly)
- Resolves: bz#990601
  (pvpanic device triggers guest bugs when present by default)

* Wed Nov 06 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-14.el7
- kvm-target-i386-remove-tabs-from-target-i386-cpu.h.patch [bz#928867]
- kvm-migrate-vPMU-state.patch [bz#928867]
- kvm-blockdev-do-not-default-cache.no-flush-to-true.patch [bz#1009993]
- kvm-virtio-blk-do-not-relay-a-previous-driver-s-WCE-conf.patch [bz#1009993]
- kvm-rng-random-use-error_setg_file_open.patch [bz#907743]
- kvm-block-mirror_complete-use-error_setg_file_open.patch [bz#907743]
- kvm-blockdev-use-error_setg_file_open.patch [bz#907743]
- kvm-cpus-use-error_setg_file_open.patch [bz#907743]
- kvm-dump-qmp_dump_guest_memory-use-error_setg_file_open.patch [bz#907743]
- kvm-savevm-qmp_xen_save_devices_state-use-error_setg_fil.patch [bz#907743]
- kvm-block-bdrv_reopen_prepare-don-t-use-QERR_OPEN_FILE_F.patch [bz#907743]
- kvm-qerror-drop-QERR_OPEN_FILE_FAILED-macro.patch [bz#907743]
- kvm-rhel-Drop-ivshmem-device.patch [bz#787463]
- kvm-usb-remove-old-usb-host-code.patch [bz#1001144]
- kvm-Add-rhel6-pxe-roms-files.patch [bz#997702]
- kvm-Add-rhel6-pxe-rom-to-redhat-rpm.patch [bz#997702]
- kvm-Fix-migration-from-rhel6.5-to-rhel7-with-ipxe.patch [bz#997702]
- kvm-pc-Don-t-prematurely-explode-QEMUMachineInitArgs.patch [bz#994490]
- kvm-pc-Don-t-explode-QEMUMachineInitArgs-into-local-vari.patch [bz#994490]
- kvm-smbios-Normalize-smbios_entry_add-s-error-handling-t.patch [bz#994490]
- kvm-smbios-Convert-to-QemuOpts.patch [bz#994490]
- kvm-smbios-Improve-diagnostics-for-conflicting-entries.patch [bz#994490]
- kvm-smbios-Make-multiple-smbios-type-accumulate-sanely.patch [bz#994490]
- kvm-smbios-Factor-out-smbios_maybe_add_str.patch [bz#994490]
- kvm-hw-Pass-QEMUMachine-to-its-init-method.patch [bz#994490]
- kvm-smbios-Set-system-manufacturer-product-version-by-de.patch [bz#994490]
- kvm-smbios-Decouple-system-product-from-QEMUMachine.patch [bz#994490]
- kvm-rhel-SMBIOS-type-1-branding.patch [bz#994490]
- kvm-Add-disable-rhev-features-option-to-configure.patch []
- Resolves: bz#1001144
  (Disable or remove device usb-host-linux)
- Resolves: bz#1009993
  (RHEL7 guests do not issue fdatasyncs on virtio-blk)
- Resolves: bz#787463
  (disable ivshmem (was: [Hitachi 7.0 FEAT] Support ivshmem (Inter-VM Shared Memory)))
- Resolves: bz#907743
  (qemu-ga: empty reason string for OpenFileFailed error)
- Resolves: bz#928867
  (Virtual PMU support during live migration - qemu-kvm)
- Resolves: bz#994490
  (Set per-machine-type SMBIOS strings)
- Resolves: bz#997702
  (Migration from RHEL6.5 host to RHEL7.0 host is failed with virtio-net device)

* Tue Nov 05 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-13.el7
- kvm-seabios-paravirt-allow-more-than-1TB-in-x86-guest.patch [bz#989677]
- kvm-scsi-prefer-UUID-to-VM-name-for-the-initiator-name.patch [bz#1006468]
- kvm-Fix-incorrect-rhel_rhev_conflicts-macro-usage.patch [bz#1017693]
- Resolves: bz#1006468
  (libiscsi initiator name should use vm UUID)
- Resolves: bz#1017693
  (incorrect use of rhel_rhev_conflicts)
- Resolves: bz#989677
  ([HP 7.0 FEAT]: Increase KVM guest supported memory to 4TiB)

* Mon Nov 04 2013 Michal Novotny <minovotn@redhat.com> - 1.5.3-12.el7
- kvm-vl-Clean-up-parsing-of-boot-option-argument.patch [bz#997817]
- kvm-qemu-option-check_params-is-now-unused-drop-it.patch [bz#997817]
- kvm-vl-Fix-boot-order-and-once-regressions-and-related-b.patch [bz#997817]
- kvm-vl-Rename-boot_devices-to-boot_order-for-consistency.patch [bz#997817]
- kvm-pc-Make-no-fd-bootchk-stick-across-boot-order-change.patch [bz#997817]
- kvm-doc-Drop-ref-to-Bochs-from-no-fd-bootchk-documentati.patch [bz#997817]
- kvm-libqtest-Plug-fd-and-memory-leaks-in-qtest_quit.patch [bz#997817]
- kvm-libqtest-New-qtest_end-to-go-with-qtest_start.patch [bz#997817]
- kvm-qtest-Don-t-reset-on-qtest-chardev-connect.patch [bz#997817]
- kvm-boot-order-test-New-covering-just-PC-for-now.patch [bz#997817]
- kvm-qemu-ga-execute-fsfreeze-freeze-in-reverse-order-of-.patch [bz#1019352]
- kvm-rbd-link-and-load-librbd-dynamically.patch [bz#989608]
- kvm-rbd-Only-look-for-qemu-specific-copy-of-librbd.so.1.patch [bz#989608]
- kvm-spec-Whitelist-rbd-block-driver.patch [bz#989608]
- Resolves: bz#1019352
  (qemu-guest-agent: "guest-fsfreeze-freeze" deadlocks if the guest have mounted disk images)
- Resolves: bz#989608
  ([7.0 FEAT] qemu runtime support for librbd backend (ceph))
- Resolves: bz#997817
  (-boot order and -boot once regressed since RHEL-6)

* Thu Oct 31 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-11.el7
- kvm-chardev-fix-pty_chr_timer.patch [bz#994414]
- kvm-qemu-socket-zero-initialize-SocketAddress.patch [bz#922010]
- kvm-qemu-socket-drop-pointless-allocation.patch [bz#922010]
- kvm-qemu-socket-catch-monitor_get_fd-failures.patch [bz#922010]
- kvm-qemu-char-check-optional-fields-using-has_.patch [bz#922010]
- kvm-error-add-error_setg_file_open-helper.patch [bz#922010]
- kvm-qemu-char-use-more-specific-error_setg_-variants.patch [bz#922010]
- kvm-qemu-char-print-notification-to-stderr.patch [bz#922010]
- kvm-qemu-char-fix-documentation-for-telnet-wait-socket-f.patch [bz#922010]
- kvm-qemu-char-don-t-leak-opts-on-error.patch [bz#922010]
- kvm-qemu-char-use-ChardevBackendKind-in-CharDriver.patch [bz#922010]
- kvm-qemu-char-minor-mux-chardev-fixes.patch [bz#922010]
- kvm-qemu-char-add-chardev-mux-support.patch [bz#922010]
- kvm-qemu-char-report-udp-backend-errors.patch [bz#922010]
- kvm-qemu-socket-don-t-leak-opts-on-error.patch [bz#922010]
- kvm-chardev-handle-qmp_chardev_add-KIND_MUX-failure.patch [bz#922010]
- kvm-acpi-piix4-Enable-qemu-kvm-compatibility-mode.patch [bz#1019474]
- kvm-target-i386-support-loading-of-cpu-xsave-subsection.patch [bz#1004743]
- Resolves: bz#1004743
  (XSAVE migration format not compatible between RHEL6 and RHEL7)
- Resolves: bz#1019474
  (RHEL-7 can't load piix4_pm migration section from RHEL-6.5)
- Resolves: bz#922010
  (RFE: support hotplugging chardev & serial ports)
- Resolves: bz#994414
  (hot-unplug chardev with pty backend caused qemu Segmentation fault)

* Thu Oct 17 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-10.el7
- kvm-xhci-fix-endpoint-interval-calculation.patch [bz#1001604]
- kvm-xhci-emulate-intr-endpoint-intervals-correctly.patch [bz#1001604]
- kvm-xhci-reset-port-when-disabling-slot.patch [bz#1001604]
- kvm-Revert-usb-hub-report-status-changes-only-once.patch [bz#1001604]
- kvm-target-i386-Set-model-6-on-qemu64-qemu32-CPU-models.patch [bz#1004290]
- kvm-pc-rhel6-doesn-t-have-APIC-on-pentium-CPU-models.patch [bz#918907]
- kvm-pc-RHEL-6-had-x2apic-set-on-Opteron_G-123.patch [bz#918907]
- kvm-pc-RHEL-6-don-t-have-RDTSCP.patch [bz#918907]
- kvm-scsi-Fix-scsi_bus_legacy_add_drive-scsi-generic-with.patch [bz#1009285]
- kvm-seccomp-fine-tuning-whitelist-by-adding-times.patch [bz#1004175]
- kvm-block-add-bdrv_write_zeroes.patch [bz#921465]
- kvm-block-raw-add-bdrv_co_write_zeroes.patch [bz#921465]
- kvm-rdma-export-qemu_fflush.patch [bz#921465]
- kvm-block-migration-efficiently-encode-zero-blocks.patch [bz#921465]
- kvm-Fix-real-mode-guest-migration.patch [bz#921465]
- kvm-Fix-real-mode-guest-segments-dpl-value-in-savevm.patch [bz#921465]
- kvm-migration-add-autoconvergence-documentation.patch [bz#921465]
- kvm-migration-send-total-time-in-QMP-at-completed-stage.patch [bz#921465]
- kvm-migration-don-t-use-uninitialized-variables.patch [bz#921465]
- kvm-pc-drop-external-DSDT-loading.patch [bz#921465]
- kvm-hda-codec-refactor-common-definitions-into-a-header-.patch [bz#954195]
- kvm-hda-codec-make-mixemu-selectable-at-runtime.patch [bz#954195]
- kvm-audio-remove-CONFIG_MIXEMU-configure-option.patch [bz#954195]
- kvm-pc_piix-disable-mixer-for-6.4.0-machine-types-and-be.patch [bz#954195]
- kvm-spec-mixemu-config-option-is-no-longer-supported-and.patch [bz#954195]
- Resolves: bz#1001604
  (usb hub doesn't work properly (win7 sees downstream port #1 only).)
- Resolves: bz#1004175
  ('-sandbox on'  option  cause  qemu-kvm process hang)
- Resolves: bz#1004290
  (Use model 6 for qemu64 and intel cpus)
- Resolves: bz#1009285
  (-device usb-storage,serial=... crashes with SCSI generic drive)
- Resolves: bz#918907
  (provide backwards-compatible RHEL specific machine types in QEMU - CPU features)
- Resolves: bz#921465
  (Migration can not finished even the "remaining ram" is already 0 kb)
- Resolves: bz#954195
  (RHEL machines <=6.4 should not use mixemu)

* Thu Oct 10 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-9.el7
- kvm-qxl-fix-local-renderer.patch [bz#1005036]
- kvm-spec-include-userspace-iSCSI-initiator-in-block-driv.patch [bz#923843]
- kvm-linux-headers-update-to-kernel-3.10.0-26.el7.patch [bz#1008987]
- kvm-target-i386-add-feature-kvm_pv_unhalt.patch [bz#1008987]
- kvm-warn-if-num-cpus-is-greater-than-num-recommended.patch [bz#1010881]
- kvm-char-move-backends-io-watch-tag-to-CharDriverState.patch [bz#1007222]
- kvm-char-use-common-function-to-disable-callbacks-on-cha.patch [bz#1007222]
- kvm-char-remove-watch-callback-on-chardev-detach-from-fr.patch [bz#1007222]
- kvm-block-don-t-lose-data-from-last-incomplete-sector.patch [bz#1017049]
- kvm-vmdk-fix-cluster-size-check-for-flat-extents.patch [bz#1017049]
- kvm-qemu-iotests-add-monolithicFlat-creation-test-to-059.patch [bz#1017049]
- Resolves: bz#1005036
  (When using “-vga qxl” together with “-display vnc=:5” or “-display  sdl” qemu displays  pixel garbage)
- Resolves: bz#1007222
  (QEMU core dumped when do hot-unplug virtio serial port during transfer file between host to guest with virtio serial through TCP socket)
- Resolves: bz#1008987
  (pvticketlocks: add kvm feature kvm_pv_unhalt)
- Resolves: bz#1010881
  (backport vcpu soft limit warning)
- Resolves: bz#1017049
  (qemu-img refuses to open the vmdk format image its created)
- Resolves: bz#923843
  (include userspace iSCSI initiator in block driver whitelist)

* Wed Oct 09 2013 Miroslav Rezanina <mrezanin@redhat.com> - qemu-kvm-1.5.3-8.el7
- kvm-vmdk-Make-VMDK3Header-and-VmdkGrainMarker-QEMU_PACKE.patch [bz#995866]
- kvm-vmdk-use-unsigned-values-for-on-disk-header-fields.patch [bz#995866]
- kvm-qemu-iotests-add-poke_file-utility-function.patch [bz#995866]
- kvm-qemu-iotests-add-empty-test-case-for-vmdk.patch [bz#995866]
- kvm-vmdk-check-granularity-field-in-opening.patch [bz#995866]
- kvm-vmdk-check-l2-table-size-when-opening.patch [bz#995866]
- kvm-vmdk-check-l1-size-before-opening-image.patch [bz#995866]
- kvm-vmdk-use-heap-allocation-for-whole_grain.patch [bz#995866]
- kvm-vmdk-rename-num_gtes_per_gte-to-num_gtes_per_gt.patch [bz#995866]
- kvm-vmdk-Move-l1_size-check-into-vmdk_add_extent.patch [bz#995866]
- kvm-vmdk-fix-L1-and-L2-table-size-in-vmdk3-open.patch [bz#995866]
- kvm-vmdk-support-vmfsSparse-files.patch [bz#995866]
- kvm-vmdk-support-vmfs-files.patch [bz#995866]
- Resolves: bz#995866
  (fix vmdk support to ESX images)

* Thu Sep 26 2013 Miroslav Rezanina <mrezanin@redhat.com> - qemu-kvm-1.5.3-7.el7
- kvm-spice-fix-display-initialization.patch [bz#974887]
- kvm-Remove-i82550-network-card-emulation.patch [bz#921983]
- kvm-Remove-usb-wacom-tablet.patch [bz#903914]
- kvm-Disable-usb-uas.patch [bz#903914]
- kvm-Disable-vhost-scsi.patch [bz#994642]
- kvm-Remove-no-hpet-option.patch [bz#947441]
- kvm-Disable-isa-parallel.patch [bz#1002286]
- kvm-xhci-implement-warm-port-reset.patch [bz#949514]
- kvm-usb-add-serial-bus-property.patch [bz#953304]
- kvm-rhel6-compat-usb-serial-numbers.patch [bz#953304]
- kvm-vmdk-fix-comment-for-vmdk_co_write_zeroes.patch [bz#995866]
- kvm-gluster-Add-image-resize-support.patch [bz#1007226]
- kvm-block-Introduce-bs-zero_beyond_eof.patch [bz#1007226]
- kvm-block-Produce-zeros-when-protocols-reading-beyond-en.patch [bz#1007226]
- kvm-gluster-Abort-on-AIO-completion-failure.patch [bz#1007226]
- kvm-Preparation-for-usb-bt-dongle-conditional-build.patch [bz#1001131]
- kvm-Remove-dev-bluetooth.c-dependency-from-vl.c.patch [bz#1001131]
- kvm-exec-Fix-Xen-RAM-allocation-with-unusual-options.patch [bz#1009328]
- kvm-exec-Clean-up-fall-back-when-mem-path-allocation-fai.patch [bz#1009328]
- kvm-exec-Reduce-ifdeffery-around-mem-path.patch [bz#1009328]
- kvm-exec-Simplify-the-guest-physical-memory-allocation-h.patch [bz#1009328]
- kvm-exec-Drop-incorrect-dead-S390-code-in-qemu_ram_remap.patch [bz#1009328]
- kvm-exec-Clean-up-unnecessary-S390-ifdeffery.patch [bz#1009328]
- kvm-exec-Don-t-abort-when-we-can-t-allocate-guest-memory.patch [bz#1009328]
- kvm-pc_sysfw-Fix-ISA-BIOS-init-for-ridiculously-big-flas.patch [bz#1009328]
- kvm-virtio-scsi-Make-type-virtio-scsi-common-abstract.patch [bz#903918]
- kvm-qga-move-logfiles-to-new-directory-for-easier-SELinu.patch [bz#1009491]
- kvm-target-i386-add-cpu64-rhel6-CPU-model.patch [bz#918907]
- kvm-fix-steal-time-MSR-vmsd-callback-to-proper-opaque-ty.patch [bz#903889]
- Resolves: bz#1001131
  (Disable or remove device usb-bt-dongle)
- Resolves: bz#1002286
  (Disable or remove device isa-parallel)
- Resolves: bz#1007226
  (Introduce bs->zero_beyond_eof)
- Resolves: bz#1009328
  ([RFE] Nicer error report when qemu-kvm can't allocate guest RAM)
- Resolves: bz#1009491
  (move qga logfiles to new /var/log/qemu-ga/ directory [RHEL-7])
- Resolves: bz#903889
  (The value of steal time in "top" command always is "0.0% st" after guest migration)
- Resolves: bz#903914
  (Disable or remove usb related devices that we will not support)
- Resolves: bz#903918
  (Disable or remove emulated SCSI devices we will not support)
- Resolves: bz#918907
  (provide backwards-compatible RHEL specific machine types in QEMU - CPU features)
- Resolves: bz#921983
  (Disable or remove emulated network devices that we will not support)
- Resolves: bz#947441
  (HPET device must be disabled)
- Resolves: bz#949514
  (fail to passthrough the USB3.0 stick to windows guest with xHCI controller under pc-i440fx-1.4)
- Resolves: bz#953304
  (Serial number of some USB devices must be fixed for older RHEL machine types)
- Resolves: bz#974887
  (the screen of guest fail to display correctly when use spice + qxl driver)
- Resolves: bz#994642
  (should disable vhost-scsi)
- Resolves: bz#995866
  (fix vmdk support to ESX images)

* Mon Sep 23 2013 Paolo Bonzini <pbonzini@redhat.com> - qemu-kvm-1.5.3-6.el7
- re-enable spice
- Related: #979953

* Mon Sep 23 2013 Paolo Bonzini <pbonzini@redhat.com> - qemu-kvm-1.5.3-5.el7
- temporarily disable spice until libiscsi rebase is complete
- Related: #979953

* Thu Sep 19 2013 Michal Novotny <minovotn@redhat.com> - qemu-kvm-1.5.3-4.el7
- kvm-block-package-preparation-code-in-qmp_transaction.patch [bz#1005818]
- kvm-block-move-input-parsing-code-in-qmp_transaction.patch [bz#1005818]
- kvm-block-package-committing-code-in-qmp_transaction.patch [bz#1005818]
- kvm-block-package-rollback-code-in-qmp_transaction.patch [bz#1005818]
- kvm-block-make-all-steps-in-qmp_transaction-as-callback.patch [bz#1005818]
- kvm-blockdev-drop-redundant-proto_drv-check.patch [bz#1005818]
- kvm-block-Don-t-parse-protocol-from-file.filename.patch [bz#1005818]
- kvm-Revert-block-Disable-driver-specific-options-for-1.5.patch [bz#1005818]
- kvm-qcow2-Add-refcount-update-reason-to-all-callers.patch [bz#1005818]
- kvm-qcow2-Options-to-enable-discard-for-freed-clusters.patch [bz#1005818]
- kvm-qcow2-Batch-discards.patch [bz#1005818]
- kvm-block-Always-enable-discard-on-the-protocol-level.patch [bz#1005818]
- kvm-qapi.py-Avoid-code-duplication.patch [bz#1005818]
- kvm-qapi.py-Allow-top-level-type-reference-for-command-d.patch [bz#1005818]
- kvm-qapi-schema-Use-BlockdevSnapshot-type-for-blockdev-s.patch [bz#1005818]
- kvm-qapi-types.py-Implement-base-for-unions.patch [bz#1005818]
- kvm-qapi-visit.py-Split-off-generate_visit_struct_fields.patch [bz#1005818]
- kvm-qapi-visit.py-Implement-base-for-unions.patch [bz#1005818]
- kvm-docs-Document-QAPI-union-types.patch [bz#1005818]
- kvm-qapi-Add-visitor-for-implicit-structs.patch [bz#1005818]
- kvm-qapi-Flat-unions-with-arbitrary-discriminator.patch [bz#1005818]
- kvm-qapi-Add-consume-argument-to-qmp_input_get_object.patch [bz#1005818]
- kvm-qapi.py-Maintain-a-list-of-union-types.patch [bz#1005818]
- kvm-qapi-qapi-types.py-native-list-support.patch [bz#1005818]
- kvm-qapi-Anonymous-unions.patch [bz#1005818]
- kvm-block-Allow-driver-option-on-the-top-level.patch [bz#1005818]
- kvm-QemuOpts-Add-qemu_opt_unset.patch [bz#1005818]
- kvm-blockdev-Rename-I-O-throttling-options-for-QMP.patch [bz#1005818]
- kvm-qemu-iotests-Update-051-reference-output.patch [bz#1005818]
- kvm-blockdev-Rename-readonly-option-to-read-only.patch [bz#1005818]
- kvm-blockdev-Split-up-cache-option.patch [bz#1005818]
- kvm-qcow2-Use-dashes-instead-of-underscores-in-options.patch [bz#1005818]
- kvm-qemu-iotests-filter-QEMU-version-in-monitor-banner.patch [bz#1006959]
- kvm-tests-set-MALLOC_PERTURB_-to-expose-memory-bugs.patch [bz#1006959]
- kvm-qemu-iotests-Whitespace-cleanup.patch [bz#1006959]
- kvm-qemu-iotests-Fixed-test-case-026.patch [bz#1006959]
- kvm-qemu-iotests-Fix-test-038.patch [bz#1006959]
- kvm-qemu-iotests-Remove-lsi53c895a-tests-from-051.patch [bz#1006959]
- Resolves: bz#1005818
  (qcow2: Backport discard command line options)
- Resolves: bz#1006959
  (qemu-iotests false positives)

* Thu Aug 29 2013 Miroslav Rezanina <mrezanin@redhat.com> - qemu-kvm-1.5.3-3.el7
- Fix rhel/rhev split

* Thu Aug 29 2013 Miroslav Rezanina <mrezanin@redhat.com> - qemu-kvm-1.5.3-2.el7
- kvm-osdep-add-qemu_get_local_state_pathname.patch [bz#964304]
- kvm-qga-determine-default-state-dir-and-pidfile-dynamica.patch [bz#964304]
- kvm-configure-don-t-save-any-fixed-local_statedir-for-wi.patch [bz#964304]
- kvm-qga-create-state-directory-on-win32.patch [bz#964304]
- kvm-qga-save-state-directory-in-ga_install_service-RHEL-.patch [bz#964304]
- kvm-Makefile-create-.-var-run-when-installing-the-POSIX-.patch [bz#964304]
- kvm-qemu-option-Fix-qemu_opts_find-for-null-id-arguments.patch [bz#980782]
- kvm-qemu-option-Fix-qemu_opts_set_defaults-for-corner-ca.patch [bz#980782]
- kvm-vl-New-qemu_get_machine_opts.patch [bz#980782]
- kvm-Fix-machine-options-accel-kernel_irqchip-kvm_shadow_.patch [bz#980782]
- kvm-microblaze-Fix-latent-bug-with-default-DTB-lookup.patch [bz#980782]
- kvm-Simplify-machine-option-queries-with-qemu_get_machin.patch [bz#980782]
- kvm-pci-add-VMSTATE_MSIX.patch [bz#838170]
- kvm-xhci-add-XHCISlot-addressed.patch [bz#838170]
- kvm-xhci-add-xhci_alloc_epctx.patch [bz#838170]
- kvm-xhci-add-xhci_init_epctx.patch [bz#838170]
- kvm-xhci-add-live-migration-support.patch [bz#838170]
- kvm-pc-set-level-xlevel-correctly-on-486-qemu32-CPU-mode.patch [bz#918907]
- kvm-pc-Remove-incorrect-rhel6.x-compat-model-value-for-C.patch [bz#918907]
- kvm-pc-rhel6.x-has-x2apic-present-on-Conroe-Penryn-Nehal.patch [bz#918907]
- kvm-pc-set-compat-CPUID-0x80000001-.EDX-bits-on-Westmere.patch [bz#918907]
- kvm-pc-Remove-PCLMULQDQ-from-Westmere-on-rhel6.x-machine.patch [bz#918907]
- kvm-pc-SandyBridge-rhel6.x-compat-fixes.patch [bz#918907]
- kvm-pc-Haswell-doesn-t-have-rdtscp-on-rhel6.x.patch [bz#918907]
- kvm-i386-fix-LAPIC-TSC-deadline-timer-save-restore.patch [bz#972433]
- kvm-all.c-max_cpus-should-not-exceed-KVM-vcpu-limit.patch [bz#996258]
- kvm-add-timestamp-to-error_report.patch [bz#906937]
- kvm-Convert-stderr-message-calling-error_get_pretty-to-e.patch [bz#906937]
- Resolves: bz#838170
  (Add live migration support for USB [xhci, usb-uas])
- Resolves: bz#906937
  ([Hitachi 7.0 FEAT][QEMU]Add a time stamp to error message (*))
- Resolves: bz#918907
  (provide backwards-compatible RHEL specific machine types in QEMU - CPU features)
- Resolves: bz#964304
  (Windows guest agent service failed to be started)
- Resolves: bz#972433
  ("INFO: rcu_sched detected stalls" after RHEL7 kvm vm migrated)
- Resolves: bz#980782
  (kernel_irqchip defaults to off instead of on without -machine)
- Resolves: bz#996258
  (boot guest with maxcpu=255 successfully but actually max number of vcpu is 160)

* Wed Aug 28 2013 Miroslav Rezanina <mrezanin@redhat.com> - 10:1.5.3-1
- Rebase to qemu 1.5.3

* Tue Aug 20 2013 Miroslav Rezanina <mrezanin@redhat.com> - 10:1.5.2-4
- qemu: guest agent creates files with insecure permissions in deamon mode [rhel-7.0] (rhbz 974444)
- update qemu-ga config & init script in RHEL7 wrt. fsfreeze hook (rhbz 969942)
- RHEL7 does not have equivalent functionality for __com.redhat_qxl_screendump (rhbz 903910)
- SEP flag behavior for CPU models of RHEL6 machine types should be compatible (rhbz 960216)
- crash command can not read the dump-guest-memory file when paging=false [RHEL-7] (rhbz 981582)
- RHEL 7 qemu-kvm fails to build on F19 host due to libusb deprecated API (rhbz 996469)
- Live migration support in virtio-blk-data-plane (rhbz 995030)
- qemu-img resize can execute successfully even input invalid syntax (rhbz 992935)

* Fri Aug 09 2013 Miroslav Rezanina <mrezanin@redhat.com> - 10:1.5.2-3
- query mem info from monitor would cause qemu-kvm hang [RHEL-7] (rhbz #970047)
- Throttle-down guest to help with live migration convergence (backport to RHEL7.0) (rhbz #985958)
- disable (for now) EFI-enabled roms (rhbz #962563)
- qemu-kvm "vPMU passthrough" mode breaks migration, shouldn't be enabled by default (rhbz #853101)
- Remove pending watches after virtserialport unplug (rhbz #992900)
- Containment of error when an SR-IOV device encounters an error... (rhbz #984604)

* Wed Jul 31 2013 Miroslav Rezanina <mrezanin@redhat.com> - 10:1.5.2-2
- SPEC file prepared for RHEL/RHEV split (rhbz #987165)
- RHEL guest( sata disk ) can not boot up (rhbz #981723)
- Kill the "use flash device for BIOS unless KVM" misfeature (rhbz #963280)
- Provide RHEL-6 machine types (rhbz #983991)
- Change s3/s4 default to "disable". (rhbz #980840)  
- Support Virtual Memory Disk Format in qemu (rhbz #836675)
- Glusterfs backend for QEMU (rhbz #805139)

* Tue Jul 02 2013 Miroslav Rezanina <mrezanin@redhat.com> - 10:1.5.2-1
- Rebase to 1.5.2

* Tue Jul 02 2013 Miroslav Rezanina <mrezanin@redhat.com> - 10:1.5.1-2
- Fix package package version info (bz #952996)
- pc: Replace upstream machine types by RHEL-7 types (bz #977864)
- target-i386: Update model values on Conroe/Penryn/Nehalem CPU model (bz #861210)
- target-i386: Set level=4 on Conroe/Penryn/Nehalem (bz #861210)

* Fri Jun 28 2013 Miroslav Rezanina <mrezanin@redhat.com> - 10:1.5.1-1
- Rebase to 1.5.1
- Change epoch to 10 to obsolete RHEL-6 qemu-kvm-rhev package (bz #818626)

* Fri May 24 2013 Miroslav Rezanina <mrezanin@redhat.com> - 3:1.5.0-2
- Enable werror (bz #948290)
- Enable nbd driver (bz #875871)
- Fix udev rules file location (bz #958860)
- Remove +x bit from systemd unit files (bz #965000)
- Drop unneeded kvm.modules on x86 (bz #963642)
- Fix build flags
- Enable libusb

* Thu May 23 2013 Miroslav Rezanina <mrezanin@redhat.com> - 3:1.5.0-1
- Rebase to 1.5.0

* Tue Apr 23 2013 Miroslav Rezanina <mrezanin@redhat.com> - 3:1.4.0-4
- Enable build of libcacard subpackage for non-x86_64 archs (bz #873174)
- Enable build of qemu-img subpackage for non-x86_64 archs (bz #873174)
- Enable build of qemu-guest-agent subpackage for non-x86_64 archs (bz #873174)

* Tue Apr 23 2013 Miroslav Rezanina <mrezanin@redhat.com> - 3:1.4.0-3
- Enable/disable features supported by rhel7
- Use qemu-kvm instead of qemu in filenames and pathes

* Fri Apr 19 2013 Daniel Mach <dmach@redhat.com> - 3:1.4.0-2.1
- Rebuild for cyrus-sasl

* Fri Apr 05 2013 Miroslav Rezanina <mrezanin@redhat.com> - 3:1.4.0-2
- Synchronization with Fedora 19 package version 2:1.4.0-8

* Wed Apr 03 2013 Daniel Mach <dmach@redhat.com> - 3:1.4.0-1.1
- Rebuild for libseccomp

* Thu Mar 07 2013 Miroslav Rezanina <mrezanin@redhat.com> - 3:1.4.0-1
- Rebase to 1.4.0

* Mon Feb 25 2013 Michal Novotny <minovotn@redhat.com> - 3:1.3.0-8
- Missing package qemu-system-x86 in hardware certification kvm testing (bz#912433)
- Resolves: bz#912433
  (Missing package qemu-system-x86 in hardware certification kvm testing)

* Fri Feb 22 2013 Alon Levy <alevy@redhat.com> - 3:1.3.0-6
- Bump epoch back to 3 since there has already been a 3 package release:
  3:1.2.0-20.el7 https://brewweb.devel.redhat.com/buildinfo?buildID=244866
- Mark explicit libcacard dependency on new enough qemu-img to avoid conflict
  since /usr/bin/vscclient was moved from qemu-img to libcacard subpackage.

* Wed Feb 13 2013 Michal Novotny <minovotn@redhat.com> - 2:1.3.0-5
- Fix patch contents for usb-redir (bz#895491)
- Resolves: bz#895491
  (PATCH: 0110-usb-redir-Add-flow-control-support.patch has been mangled on rebase !!)

* Wed Feb 06 2013 Alon Levy <alevy@redhat.com> - 2:1.3.0-4
- Add patch from f19 package for libcacard missing error_set symbol.
- Resolves: bz#891552

* Mon Jan 07 2013 Michal Novotny <minovotn@redhat.com> - 2:1.3.0-3
- Remove dependency on bogus qemu-kvm-kvm package [bz#870343]
- Resolves: bz#870343
  (qemu-kvm-1.2.0-16.el7 cant be installed)

* Tue Dec 18 2012 Michal Novotny <minovotn@redhat.com> - 2:1.3.0-2
- Rename qemu to qemu-kvm
- Move qemu-kvm to libexecdir

* Fri Dec 07 2012 Cole Robinson <crobinso@redhat.com> - 2:1.3.0-1
- Switch base tarball from qemu-kvm to qemu
- qemu 1.3 release
- Option to use linux VFIO driver to assign PCI devices
- Many USB3 improvements
- New paravirtualized hardware random number generator device.
- Support for Glusterfs volumes with "gluster://" -drive URI
- Block job commands for live block commit and storage migration

* Wed Nov 28 2012 Alon Levy <alevy@redhat.com> - 2:1.2.0-25
* Merge libcacard into qemu, since they both use the same sources now.

* Thu Nov 22 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-24
- Move vscclient to qemu-common, qemu-nbd to qemu-img

* Tue Nov 20 2012 Alon Levy <alevy@redhat.com> - 2:1.2.0-23
- Rewrite fix for bz #725965 based on fix for bz #867366
- Resolve bz #867366

* Fri Nov 16 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-23
- Backport --with separate_kvm support from EPEL branch

* Fri Nov 16 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-22
- Fix previous commit

* Fri Nov 16 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-21
- Backport commit 38f419f (configure: Fix CONFIG_QEMU_HELPERDIR generation,
  2012-10-17)

* Thu Nov 15 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-20
- Install qemu-bridge-helper as suid root
- Distribute a sample /etc/qemu/bridge.conf file

* Thu Nov  1 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.2.0-19
- Sync spice patches with upstream, minor bugfixes and set the qxl pci
  device revision to 4 by default, so that guests know they can use
  the new features

* Tue Oct 30 2012 Cole Robinson <crobinso@redhat.com> - 2:1.2.0-18
- Fix loading arm initrd if kernel is very large (bz #862766)
- Don't use reserved word 'function' in systemtap files (bz #870972)
- Drop assertion that was triggering when pausing guests w/ qxl (bz
  #870972)

* Sun Oct 28 2012 Cole Robinson <crobinso@redhat.com> - 2:1.2.0-17
- Pull patches queued for qemu 1.2.1

* Fri Oct 19 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-16
- add s390x KVM support
- distribute pre-built firmware or device trees for Alpha, Microblaze, S390
- add missing system targets
- add missing linux-user targets
- fix previous commit

* Thu Oct 18 2012 Dan Horák <dan[at]danny.cz> - 2:1.2.0-15
- fix build on non-kvm arches like s390(x)

* Wed Oct 17 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-14
- Change SLOF Requires for the new version number

* Thu Oct 11 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-13
- Add ppc support to kvm.modules (original patch by David Gibson)
- Replace x86only build with kvmonly build: add separate defines and
  conditionals for all packages, so that they can be chosen and
  renamed in kvmonly builds and so that qemu has the appropriate requires
- Automatically pick libfdt dependancy
- Add knob to disable spice+seccomp

* Fri Sep 28 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-12
- Call udevadm on post, fixing bug 860658

* Fri Sep 28 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.2.0-11
- Rebuild against latest spice-server and spice-protocol
- Fix non-seamless migration failing with vms with usb-redir devices,
  to allow boxes to load such vms from disk

* Tue Sep 25 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.2.0-10
- Sync Spice patchsets with upstream (rhbz#860238)
- Fix building with usbredir >= 0.5.2

* Thu Sep 20 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.2.0-9
- Sync USB and Spice patchsets with upstream

* Sun Sep 16 2012 Richard W.M. Jones <rjones@redhat.com> - 2:1.2.0-8
- Use 'global' instead of 'define', and underscore in definition name,
  n-v-r, and 'dist' tag of SLOF, all to fix RHBZ#855252.

* Fri Sep 14 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-4
- add versioned dependency from qemu-system-ppc to SLOF (BZ#855252)

* Wed Sep 12 2012 Richard W.M. Jones <rjones@redhat.com> - 2:1.2.0-3
- Fix RHBZ#853408 which causes libguestfs failure.

* Sat Sep  8 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.2.0-2
- Fix crash on (seamless) migration
- Sync usbredir live migration patches with upstream

* Fri Sep  7 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.2.0-1
- New upstream release 1.2.0 final
- Add support for Spice seamless migration
- Add support for Spice dynamic monitors
- Add support for usb-redir live migration

* Tue Sep 04 2012 Adam Jackson <ajax@redhat.com> 1.2.0-0.5.rc1
- Flip Requires: ceph >= foo to Conflicts: ceph < foo, so we pull in only the
  libraries which we need and not the rest of ceph which we don't.

* Tue Aug 28 2012 Cole Robinson <crobinso@redhat.com> 1.2.0-0.4.rc1
- Update to 1.2.0-rc1

* Mon Aug 20 2012 Richard W.M. Jones <rjones@redhat.com> - 1.2-0.3.20120806git3e430569
- Backport Bonzini's vhost-net fix (RHBZ#848400).

* Tue Aug 14 2012 Cole Robinson <crobinso@redhat.com> - 1.2-0.2.20120806git3e430569
- Bump release number, previous build forgot but the dist bump helped us out

* Tue Aug 14 2012 Cole Robinson <crobinso@redhat.com> - 1.2-0.1.20120806git3e430569
- Revive qemu-system-{ppc*, sparc*} (bz 844502)
- Enable KVM support for all targets (bz 844503)

* Mon Aug 06 2012 Cole Robinson <crobinso@redhat.com> - 1.2-0.1.20120806git3e430569.fc18
- Update to git snapshot

* Sun Jul 29 2012 Cole Robinson <crobinso@redhat.com> - 1.1.1-1
- Upstream stable release 1.1.1
- Fix systemtap tapsets (bz 831763)
- Fix VNC audio tunnelling (bz 840653)
- Don't renable ksm on update (bz 815156)
- Bump usbredir dep (bz 812097)
- Fix RPM install error on non-virt machines (bz 660629)
- Obsolete openbios to fix upgrade dependency issues (bz 694802)

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2:1.1.0-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jul 10 2012 Richard W.M. Jones <rjones@redhat.com> - 2:1.1.0-8
- Re-diff previous patch so that it applies and actually apply it

* Tue Jul 10 2012 Richard W.M. Jones <rjones@redhat.com> - 2:1.1.0-7
- Add patch to fix default machine options.  This fixes libvirt
  detection of qemu.
- Back out patch 1 which conflicts.

* Fri Jul  6 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.1.0-5
- Fix qemu crashing (on an assert) whenever USB-2.0 isoc transfers are used

* Thu Jul  5 2012 Richard W.M. Jones <rjones@redhat.com> - 2:1.1.0-4
- Disable tests since they hang intermittently.
- Add kvmvapic.bin (replaces vapic.bin).
- Add cpus-x86_64.conf.  qemu now creates /etc/qemu/target-x86_64.conf
  as an empty file.
- Add qemu-icon.bmp.
- Add qemu-bridge-helper.
- Build and include virtfs-proxy-helper + man page (thanks Hans de Goede).

* Wed Jul  4 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.1.0-1
- New upstream release 1.1.0
- Drop about a 100 spice + USB patches, which are all upstream

* Mon Apr 23 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.0-17
- Fix install failure due to set -e (rhbz #815272)

* Mon Apr 23 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.0-16
- Fix kvm.modules to exit successfully on non-KVM capable systems (rhbz #814932)

* Thu Apr 19 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.0-15
- Add a couple of backported QXL/Spice bugfixes
- Add spice volume control patches

* Fri Apr 6 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.0-12
- Add back PPC and SPARC user emulators
- Update binfmt rules from upstream

* Mon Apr  2 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.0-11
- Some more USB bugfixes from upstream

* Thu Mar 29 2012 Eduardo Habkost <ehabkost@redhat.com> - 2:1.0-12
- Fix ExclusiveArch mistake that disabled all non-x86_64 builds on Fedora

* Wed Mar 28 2012 Eduardo Habkost <ehabkost@redhat.com> - 2:1.0-11
- Use --with variables for build-time settings

* Wed Mar 28 2012 Daniel P. Berrange <berrange@redhat.com> - 2:1.0-10
- Switch to use iPXE for netboot ROMs

* Thu Mar 22 2012 Daniel P. Berrange <berrange@redhat.com> - 2:1.0-9
- Remove O_NOATIME for 9p filesystems

* Mon Mar 19 2012 Daniel P. Berrange <berrange@redhat.com> - 2:1.0-8
- Move udev rules to /lib/udev/rules.d (rhbz #748207)

* Fri Mar  9 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.0-7
- Add a whole bunch of USB bugfixes from upstream

* Mon Feb 13 2012 Daniel P. Berrange <berrange@redhat.com> - 2:1.0-6
- Add many more missing BRs for misc QEMU features
- Enable running of test suite during build

* Tue Feb 07 2012 Justin M. Forbes <jforbes@redhat.com> - 2:1.0-5
- Add support for virtio-scsi

* Sun Feb  5 2012 Richard W.M. Jones <rjones@redhat.com> - 2:1.0-4
- Require updated ceph for latest librbd with rbd_flush symbol.

* Tue Jan 24 2012 Justin M. Forbes <jforbes@redhat.com> - 2:1.0-3
- Add support for vPMU
- e1000: bounds packet size against buffer size CVE-2012-0029

* Fri Jan 13 2012 Justin M. Forbes <jforbes@redhat.com> - 2:1.0-2
- Add patches for USB redirect bits
- Remove palcode-clipper, we don't build it

* Wed Jan 11 2012 Justin M. Forbes <jforbes@redhat.com> - 2:1.0-1
- Add patches from 1.0.1 queue

* Fri Dec 16 2011 Justin M. Forbes <jforbes@redhat.com> - 2:1.0-1
- Update to qemu 1.0

* Tue Nov 15 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.15.1-3
- Enable spice for i686 users as well

* Thu Nov 03 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.15.1-2
- Fix POSTIN scriplet failure (#748281)

* Fri Oct 21 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.15.1-1
- Require seabios-bin >= 0.6.0-2 (#741992)
- Replace init scripts with systemd units (#741920)
- Update to 0.15.1 stable upstream
  
* Fri Oct 21 2011 Paul Moore <pmoore@redhat.com>
- Enable full relro and PIE (rhbz #738812)

* Wed Oct 12 2011 Daniel P. Berrange <berrange@redhat.com> - 2:0.15.0-6
- Add BR on ceph-devel to enable RBD block device

* Wed Oct  5 2011 Daniel P. Berrange <berrange@redhat.com> - 2:0.15.0-5
- Create a qemu-guest-agent sub-RPM for guest installation

* Tue Sep 13 2011 Daniel P. Berrange <berrange@redhat.com> - 2:0.15.0-4
- Enable DTrace tracing backend for SystemTAP (rhbz #737763)
- Enable build with curl (rhbz #737006)

* Thu Aug 18 2011 Hans de Goede <hdegoede@redhat.com> - 2:0.15.0-3
- Add missing BuildRequires: usbredir-devel, so that the usbredir code
  actually gets build

* Thu Aug 18 2011 Richard W.M. Jones <rjones@redhat.com> - 2:0.15.0-2
- Add upstream qemu patch 'Allow to leave type on default in -machine'
  (2645c6dcaf6ea2a51a3b6dfa407dd203004e4d11).

* Sun Aug 14 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.15.0-1
- Update to 0.15.0 stable release.

* Thu Aug 04 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.15.0-0.3.201108040af4922
- Update to 0.15.0-rc1 as we prepare for 0.15.0 release

* Thu Aug  4 2011 Daniel P. Berrange <berrange@redhat.com> - 2:0.15.0-0.3.2011072859fadcc
- Fix default accelerator for non-KVM builds (rhbz #724814)

* Thu Jul 28 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.15.0-0.1.2011072859fadcc
- Update to 0.15.0-rc0 as we prepare for 0.15.0 release

* Tue Jul 19 2011 Hans de Goede <hdegoede@redhat.com> - 2:0.15.0-0.2.20110718525e3df
- Add support usb redirection over the network, see:
  http://fedoraproject.org/wiki/Features/UsbNetworkRedirection
- Restore chardev flow control patches

* Mon Jul 18 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.15.0-0.1.20110718525e3df
- Update to git snapshot as we prepare for 0.15.0 release

* Wed Jun 22 2011 Richard W.M. Jones <rjones@redhat.com> - 2:0.14.0-9
- Add BR libattr-devel.  This caused the -fstype option to be disabled.
  https://www.redhat.com/archives/libvir-list/2011-June/thread.html#01017

* Mon May  2 2011 Hans de Goede <hdegoede@redhat.com> - 2:0.14.0-8
- Fix a bug in the spice flow control patches which breaks the tcp chardev

* Tue Mar 29 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.14.0-7
- Disable qemu-ppc and qemu-sparc packages (#679179)

* Mon Mar 28 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.14.0-6
- Spice fixes for flow control.

* Tue Mar 22 2011 Dan Horák <dan[at]danny.cz> - 2:0.14.0-5
- be more careful when removing the -g flag on s390

* Fri Mar 18 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.14.0-4
- Fix thinko on adding the most recent patches.

* Wed Mar 16 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.14.0-3
- Fix migration issue with vhost
- Fix qxl locking issues for spice

* Wed Mar 02 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.14.0-2
- Re-enable sparc and cris builds

* Thu Feb 24 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.14.0-1
- Update to 0.14.0 release

* Fri Feb 11 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.14.0-0.1.20110210git7aa8c46
- Update git snapshot
- Temporarily disable qemu-cris and qemu-sparc due to build errors (to be resolved shorly)

* Tue Feb 08 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.14.0-0.1.20110208git3593e6b
- Update to 0.14.0 rc git snapshot
- Add virtio-net to modules

* Wed Nov  3 2010 Daniel P. Berrange <berrange@redhat.com> - 2:0.13.0-2
- Revert previous change
- Make qemu-common own the /etc/qemu directory
- Add /etc/qemu/target-x86_64.conf to qemu-system-x86 regardless
  of host architecture.

* Wed Nov 03 2010 Dan Horák <dan[at]danny.cz> - 2:0.13.0-2
- Remove kvm config file on non-x86 arches (part of #639471)
- Own the /etc/qemu directory

* Mon Oct 18 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.13.0-1
- Update to 0.13.0 upstream release
- Fixes for vhost
- Fix mouse in certain guests (#636887)
- Fix issues with WinXP guest install (#579348)
- Resolve build issues with S390 (#639471)
- Fix Windows XP on Raw Devices (#631591)

* Tue Oct 05 2010 jkeating - 2:0.13.0-0.7.rc1.1
- Rebuilt for gcc bug 634757

* Tue Sep 21 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.13.0-0.7.rc1
- Flip qxl pci id from unstable to stable (#634535)
- KSM Fixes from upstream (#558281)

* Tue Sep 14 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.13.0-0.6.rc1
- Move away from git snapshots as 0.13 is close to release
- Updates for spice 0.6

* Tue Aug 10 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.13.0-0.5.20100809git25fdf4a
- Fix typo in e1000 gpxe rom requires.
- Add links to newer vgabios

* Tue Aug 10 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.13.0-0.4.20100809git25fdf4a
- Disable spice on 32bit, it is not supported and buildreqs don't exist.

* Mon Aug 9 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.13.0-0.3.20100809git25fdf4a
- Updates from upstream towards 0.13 stable
- Fix requires on gpxe
- enable spice now that buildreqs are in the repository.
- ksmtrace has moved to a separate upstream package

* Tue Jul 27 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.13.0-0.2.20100727gitb81fe95
- add texinfo buildreq for manpages.

* Tue Jul 27 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.13.0-0.1.20100727gitb81fe95
- Update to 0.13.0 upstream snapshot
- ksm init fixes from upstream

* Tue Jul 20 2010 Dan Horák <dan[at]danny.cz> - 2:0.12.3-8
- Add avoid-llseek patch from upstream needed for building on s390(x)
- Don't use parallel make on s390(x)

* Tue Jun 22 2010 Amit Shah <amit.shah@redhat.com> - 2:0.12.3-7
- Add vvfat hardening patch from upstream (#605202)

* Fri Apr 23 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.3-6
- Change requires to the noarch seabios-bin
- Add ownership of docdir to qemu-common (#572110)
- Fix "Cannot boot from non-existent NIC" error when using virt-install (#577851)

* Thu Apr 15 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.3-5
- Update virtio console patches from upstream

* Thu Mar 11 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.3-4
- Detect cdrom via ioctl (#473154)
- re add increased buffer for USB control requests (#546483)

* Wed Mar 10 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.3-3
- Migration clear the fd in error cases (#518032)

* Tue Mar 09 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.3-2
- Allow builds --with x86only
- Add libaio-devel buildreq for aio support

* Fri Feb 26 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.3-1
- Update to 0.12.3 upstream
- vhost-net migration/restart fixes
- Add F-13 machine type
- virtio-serial fixes

* Tue Feb 09 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.2-6
- Add vhost net support.

* Thu Feb 04 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.2-5
- Avoid creating too large iovecs in multiwrite merge (#559717)
- Don't try to set max_kernel_pages during ksm init on newer kernels (#558281)
- Add logfile options for ksmtuned debug.

* Wed Jan 27 2010 Amit Shah <amit.shah@redhat.com> - 2:0.12.2-4
- Remove build dependency on iasl now that we have seabios

* Wed Jan 27 2010 Amit Shah <amit.shah@redhat.com> - 2:0.12.2-3
- Remove source target for 0.12.1.2

* Wed Jan 27 2010 Amit Shah <amit.shah@redhat.com> - 2:0.12.2-2
- Add virtio-console patches from upstream for the F13 VirtioSerial feature

* Mon Jan 25 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.2-1
- Update to 0.12.2 upstream

* Sun Jan 10 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.1.2-3
- Point to seabios instead of bochs, and add a requires for seabios

* Mon Jan  4 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.1.2-2
- Remove qcow2 virtio backing file patch

* Mon Jan  4 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.1.2-1
- Update to 0.12.1.2 upstream
- Remove patches included in upstream

* Fri Nov 20 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-12
- Fix a use-after-free crasher in the slirp code (#539583)
- Fix overflow in the parallels image format support (#533573)

* Wed Nov  4 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-11
- Temporarily disable preadv/pwritev support to fix data corruption (#526549)

* Tue Nov  3 2009 Justin M. Forbes <jforbes@redhat.com> - 2:0.11.0-10
- Default ksm and ksmtuned services on.

* Thu Oct 29 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-9
- Fix dropped packets with non-virtio NICs (#531419)

* Wed Oct 21 2009 Glauber Costa <gcosta@redhat.com> - 2:0.11.0-8
- Properly save kvm time registers (#524229)

* Mon Oct 19 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-7
- Fix potential segfault from too small MSR_COUNT (#528901)

* Fri Oct  9 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-6
- Fix fs errors with virtio and qcow2 backing file (#524734)
- Fix ksm initscript errors on kernel missing ksm (#527653)
- Add missing Requires(post): getent, useradd, groupadd (#527087)

* Tue Oct  6 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-5
- Add 'retune' verb to ksmtuned init script

* Mon Oct  5 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-4
- Use rtl8029 PXE rom for ne2k_pci, not ne (#526777)
- Also, replace the gpxe-roms-qemu pkg requires with file-based requires

* Thu Oct  1 2009 Justin M. Forbes <jmforbes@redhat.com> - 2:0.11.0-3
- Improve error reporting on file access (#524695)

* Mon Sep 28 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-2
- Fix pci hotplug to not exit if supplied an invalid NIC model (#524022)

* Mon Sep 28 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-1
- Update to 0.11.0 release
- Drop a couple of upstreamed patches

* Wed Sep 23 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.92-5
- Fix issue causing NIC hotplug confusion when no model is specified (#524022)

* Wed Sep 16 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.92-4
- Fix for KSM patch from Justin Forbes

* Wed Sep 16 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.92-3
- Add ksmtuned, also from Dan Kenigsberg
- Use %%_initddir macro

* Wed Sep 16 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.92-2
- Add ksm control script from Dan Kenigsberg

* Mon Sep  7 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.92-1
- Update to qemu-kvm-0.11.0-rc2
- Drop upstreamed patches
- extboot install now fixed upstream
- Re-place TCG init fix (#516543) with the one gone upstream

* Mon Sep  7 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.91-0.10.rc1
- Fix MSI-X error handling on older kernels (#519787)

* Fri Sep  4 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.91-0.9.rc1
- Make pulseaudio the default audio backend (#519540, #495964, #496627)

* Thu Aug 20 2009 Richard W.M. Jones <rjones@redhat.com> - 2:0.10.91-0.8.rc1
- Fix segfault when qemu-kvm is invoked inside a VM (#516543)

* Tue Aug 18 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.91-0.7.rc1
- Fix permissions on udev rules (#517571)

* Mon Aug 17 2009 Lubomir Rintel <lkundrak@v3.sk> - 2:0.10.91-0.6.rc1
- Allow blacklisting of kvm modules (#517866)

* Fri Aug  7 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.91-0.5.rc1
- Fix virtio_net with -net user (#516022)

* Tue Aug  4 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.91-0.4.rc1
- Update to qemu-kvm-0.11-rc1; no changes from rc1-rc0

* Tue Aug  4 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.91-0.3.rc1.rc0
- Fix extboot checksum (bug #514899)

* Fri Jul 31 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.91-0.2.rc1.rc0
- Add KSM support
- Require bochs-bios >= 2.3.8-0.8 for latest kvm bios updates

* Thu Jul 30 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.91-0.1.rc1.rc0
- Update to qemu-kvm-0.11.0-rc1-rc0
- This is a pre-release of the official -rc1
- A vista installer regression is blocking the official -rc1 release
- Drop qemu-prefer-sysfs-for-usb-host-devices.patch
- Drop qemu-fix-build-for-esd-audio.patch
- Drop qemu-slirp-Fix-guestfwd-for-incoming-data.patch
- Add patch to ensure extboot.bin is installed

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2:0.10.50-14.kvm88
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jul 23 2009 Glauber Costa <glommer@redhat.com> - 2:0.10.50-13.kvm88
- Fix bug 513249, -net channel option is broken

* Thu Jul 16 2009 Daniel P. Berrange <berrange@redhat.com> - 2:0.10.50-12.kvm88
- Add 'qemu' user and group accounts
- Force disable xen until it can be made to build

* Thu Jul 16 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-11.kvm88
- Update to kvm-88, see http://www.linux-kvm.org/page/ChangeLog
- Package mutiboot.bin
- Update for how extboot is built
- Fix sf.net source URL
- Drop qemu-fix-ppc-softmmu-kvm-disabled-build.patch
- Drop qemu-fix-pcspk-build-with-kvm-disabled.patch
- Cherry-pick fix for esound support build failure

* Wed Jul 15 2009 Daniel Berrange <berrange@lettuce.camlab.fab.redhat.com> - 2:0.10.50-10.kvm87
- Add udev rules to make /dev/kvm world accessible & group=kvm (rhbz #497341)
- Create a kvm group if it doesn't exist (rhbz #346151)

* Tue Jul 07 2009 Glauber Costa <glommer@redhat.com> - 2:0.10.50-9.kvm87
- use pxe roms from gpxe, instead of etherboot package.

* Fri Jul  3 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-8.kvm87
- Prefer sysfs over usbfs for usb passthrough (#508326)

* Sat Jun 27 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-7.kvm87
- Update to kvm-87
- Drop upstreamed patches
- Cherry-pick new ppc build fix from upstream
- Work around broken linux-user build on ppc
- Fix hw/pcspk.c build with --disable-kvm
- Re-enable preadv()/pwritev() since #497429 is long since fixed
- Kill petalogix-s3adsp1800.dtb, since we don't ship the microblaze target

* Fri Jun  5 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-6.kvm86
- Fix 'kernel requires an x86-64 CPU' error
- BuildRequires ncurses-devel to enable '-curses' option (#504226)

* Wed Jun  3 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-5.kvm86
- Prevent locked cdrom eject - fixes hang at end of anaconda installs (#501412)
- Avoid harmless 'unhandled wrmsr' warnings (#499712)

* Thu May 21 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-4.kvm86
- Update to kvm-86 release
- ChangeLog here: http://marc.info/?l=kvm&m=124282885729710

* Fri May  1 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-3.kvm85
- Really provide qemu-kvm as a metapackage for comps

* Tue Apr 28 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-2.kvm85
- Provide qemu-kvm as a metapackage for comps

* Mon Apr 27 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-1.kvm85
- Update to qemu-kvm-devel-85
- kvm-85 is based on qemu development branch, currently version 0.10.50
- Include new qemu-io utility in qemu-img package
- Re-instate -help string for boot=on to fix virtio booting with libvirt
- Drop upstreamed patches
- Fix missing kernel/include/asm symlink in upstream tarball
- Fix target-arm build
- Fix build on ppc
- Disable preadv()/pwritev() until bug #497429 is fixed
- Kill more .kernelrelease uselessness
- Make non-kvm qemu build verbose

* Fri Apr 24 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-15
- Fix source numbering typos caused by make-release addition

* Thu Apr 23 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-14
- Improve instructions for generating the tarball

* Tue Apr 21 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-13
- Enable pulseaudio driver to fix qemu lockup at shutdown (#495964)

* Tue Apr 21 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-12
- Another qcow2 image corruption fix (#496642)

* Mon Apr 20 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-11
- Fix qcow2 image corruption (#496642)

* Sun Apr 19 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-10
- Run sysconfig.modules from %%post on x86_64 too (#494739)

* Sun Apr 19 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-9
- Align VGA ROM to 4k boundary - fixes 'qemu-kvm -std vga' (#494376)

* Tue Apr  14 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-8
- Provide qemu-kvm conditional on the architecture.

* Thu Apr  9 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-7
- Add a much cleaner fix for vga segfault (#494002)

* Sun Apr  5 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-6
- Fixed qcow2 segfault creating disks over 2TB. #491943

* Fri Apr  3 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-5
- Fix vga segfault under kvm-autotest (#494002)
- Kill kernelrelease hack; it's not needed
- Build with "make V=1" for more verbose logs

* Thu Apr 02 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-4
- Support botting gpxe roms.

* Wed Apr 01 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-2
- added missing patch. love for CVS.

* Wed Apr 01 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-1
- Include debuginfo for qemu-img
- Do not require qemu-common for qemu-img
- Explicitly own each of the firmware files
- remove firmwares for ppc and sparc. They should be provided by an external package.
  Not that the packages exists for sparc in the secondary arch repo as noarch, but they
  don't automatically get into main repos. Unfortunately it's the best we can do right
  now.
- rollback a bit in time. Snapshot from avi's maint/2.6.30
  - this requires the sasl patches to come back.
  - with-patched-kernel comes back.

* Wed Mar 25 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-0.12.kvm20090323git
- BuildRequires pciutils-devel for device assignment (#492076)

* Mon Mar 23 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.11.kvm20090323git
- Update to snapshot kvm20090323.
- Removed patch2 (upstream).
- use upstream's new split package.
- --with-patched-kernel flag not needed anymore
- Tell how to get the sources.

* Wed Mar 18 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.10.kvm20090310git
- Added extboot to files list.

* Wed Mar 11 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.9.kvm20090310git
- Fix wrong reference to bochs bios.

* Wed Mar 11 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.8.kvm20090310git
- fix Obsolete/Provides pair
- Use kvm bios from bochs-bios package.
- Using RPM_OPT_FLAGS in configure
- Picked back audio-drv-list from kvm package

* Tue Mar 10 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.7.kvm20090310git
- modify ppc patch

* Tue Mar 10 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.6.kvm20090310git
- updated to kvm20090310git
- removed sasl patches (already in this release)

* Tue Mar 10 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.5.kvm20090303git
- kvm.modules were being wrongly mentioned at %%install.
- update description for the x86 system package to include kvm support
- build kvm's own bios. It is still necessary while kvm uses a slightly different
  irq routing mechanism

* Thu Mar 05 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.4.kvm20090303git
- seems Epoch does not go into the tags. So start back here.

* Thu Mar 05 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.1.kvm20090303git
- Use bochs-bios instead of bochs-bios-data
- It's official: upstream set on 0.10

* Thu Mar  5 2009 Daniel P. Berrange <berrange@redhat.com> - 2:0.9.2-0.2.kvm20090303git
- Added BSD to license list, since many files are covered by BSD

* Wed Mar 04 2009 Glauber Costa <glommer@redhat.com> - 0.9.2-0.1.kvm20090303git
- missing a dot. shame on me

* Wed Mar 04 2009 Glauber Costa <glommer@redhat.com> - 0.92-0.1.kvm20090303git
- Set Epoch to 2
- Set version to 0.92. It seems upstream keep changing minds here, so pick the lowest
- Provides KVM, Obsoletes KVM
- Only install qemu-kvm in ix86 and x86_64
- Remove pkgdesc macros, as they were generating bogus output for rpm -qi.
- fix ppc and ppc64 builds

* Tue Mar 03 2009 Glauber Costa <glommer@redhat.com> - 0.10-0.3.kvm20090303git
- only execute post scripts for user package.
- added kvm tools.

* Tue Mar 03 2009 Glauber Costa <glommer@redhat.com> - 0.10-0.2.kvm20090303git
- put kvm.modules into cvs

* Tue Mar 03 2009 Glauber Costa <glommer@redhat.com> - 0.10-0.1.kvm20090303git
- Set Epoch to 1
- Build KVM (basic build, no tools yet)
- Set ppc in ExcludeArch. This is temporary, just to fix one issue at a time.
  ppc users (IBM ? ;-)) please wait a little bit.

* Tue Mar  3 2009 Daniel P. Berrange <berrange@redhat.com> - 1.0-0.5.svn6666
- Support VNC SASL authentication protocol
- Fix dep on bochs-bios-data

* Tue Mar 03 2009 Glauber Costa <glommer@redhat.com> - 1.0-0.4.svn6666
- use bios from bochs-bios package.

* Tue Mar 03 2009 Glauber Costa <glommer@redhat.com> - 1.0-0.3.svn6666
- use vgabios from vgabios package.

* Mon Mar 02 2009 Glauber Costa <glommer@redhat.com> - 1.0-0.2.svn6666
- use pxe roms from etherboot package.

* Mon Mar 02 2009 Glauber Costa <glommer@redhat.com> - 1.0-0.1.svn6666
- Updated to tip svn (release 6666). Featuring split packages for qemu.
  Unfortunately, still using binary blobs for the bioses.

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.1-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun Jan 11 2009 Debarshi Ray <rishi@fedoraproject.org> - 0.9.1-12
- Updated build patch. Closes Red Hat Bugzilla bug #465041.

* Wed Dec 31 2008 Dennis Gilmore <dennis@ausil.us> - 0.9.1-11
- add sparcv9 and sparc64 support

* Fri Jul 25 2008 Bill Nottingham <notting@redhat.com>
- Fix qemu-img summary (#456344)

* Wed Jun 25 2008 Daniel P. Berrange <berrange@redhat.com> - 0.9.1-10.fc10
- Rebuild for GNU TLS ABI change

* Wed Jun 11 2008 Daniel P. Berrange <berrange@redhat.com> - 0.9.1-9.fc10
- Remove bogus wildcard from files list (rhbz #450701)

* Sat May 17 2008 Lubomir Rintel <lkundrak@v3.sk> - 0.9.1-8
- Register binary handlers also for shared libraries

* Mon May  5 2008 Daniel P. Berrange <berrange@redhat.com> - 0.9.1-7.fc10
- Fix text console PTYs to be in rawmode

* Sun Apr 27 2008 Lubomir Kundrak <lkundrak@redhat.com> - 0.9.1-6
- Register binary handler for SuperH-4 CPU

* Wed Mar 19 2008 Daniel P. Berrange <berrange@redhat.com> - 0.9.1-5.fc9
- Split qemu-img tool into sub-package for smaller footprint installs

* Wed Feb 27 2008 Daniel P. Berrange <berrange@redhat.com> - 0.9.1-4.fc9
- Fix block device checks for extendable disk formats (rhbz #435139)

* Sat Feb 23 2008 Daniel P. Berrange <berrange@redhat.com> - 0.9.1-3.fc9
- Fix block device extents check (rhbz #433560)

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0.9.1-2
- Autorebuild for GCC 4.3

* Tue Jan  8 2008 Daniel P. Berrange <berrange@redhat.com> - 0.9.1-1.fc9
- Updated to 0.9.1 release
- Fix license tag syntax
- Don't mark init script as a config file

* Wed Sep 26 2007 Daniel P. Berrange <berrange@redhat.com> - 0.9.0-5.fc8
- Fix rtl8139 checksum calculation for Vista (rhbz #308201)

* Tue Aug 28 2007 Daniel P. Berrange <berrange@redhat.com> - 0.9.0-4.fc8
- Fix debuginfo by passing -Wl,--build-id to linker

* Tue Aug 28 2007 David Woodhouse <dwmw2@infradead.org> 0.9.0-4
- Update licence
- Fix CDROM emulation (#253542)

* Tue Aug 28 2007 Daniel P. Berrange <berrange@redhat.com> - 0.9.0-3.fc8
- Added backport of VNC password auth, and TLS+x509 cert auth
- Switch to rtl8139 NIC by default for linkstate reporting
- Fix rtl8139 mmio region mappings with multiple NICs

* Sun Apr  1 2007 Hans de Goede <j.w.r.degoede@hhs.nl> 0.9.0-2
- Fix direct loading of a linux kernel with -kernel & -initrd (bz 234681)
- Remove spurious execute bits from manpages (bz 222573)

* Tue Feb  6 2007 David Woodhouse <dwmw2@infradead.org> 0.9.0-1
- Update to 0.9.0

* Wed Jan 31 2007 David Woodhouse <dwmw2@infradead.org> 0.8.2-5
- Include licences

* Mon Nov 13 2006 Hans de Goede <j.w.r.degoede@hhs.nl> 0.8.2-4
- Backport patch to make FC6 guests work by Kevin Kofler
  <Kevin@tigcc.ticalc.org> (bz 207843).

* Mon Sep 11 2006 David Woodhouse <dwmw2@infradead.org> 0.8.2-3
- Rebuild

* Thu Aug 24 2006 Matthias Saou <http://freshrpms.net/> 0.8.2-2
- Remove the target-list iteration for x86_64 since they all build again.
- Make gcc32 vs. gcc34 conditional on %%{fedora} to share the same spec for
  FC5 and FC6.

* Wed Aug 23 2006 Matthias Saou <http://freshrpms.net/> 0.8.2-1
- Update to 0.8.2 (#200065).
- Drop upstreamed syscall-macros patch2.
- Put correct scriplet dependencies.
- Force install mode for the init script to avoid umask problems.
- Add %%postun condrestart for changes to the init script to be applied if any.
- Update description with the latest "about" from the web page (more current).
- Update URL to qemu.org one like the Source.
- Add which build requirement.
- Don't include texi files in %%doc since we ship them in html.
- Switch to using gcc34 on devel, FC5 still has gcc32.
- Add kernheaders patch to fix linux/compiler.h inclusion.
- Add target-sparc patch to fix compiling on ppc (some int32 to float).

* Thu Jun  8 2006 David Woodhouse <dwmw2@infradead.org> 0.8.1-3
- More header abuse in modify_ldt(), change BuildRoot:

* Wed Jun  7 2006 David Woodhouse <dwmw2@infradead.org> 0.8.1-2
- Fix up kernel header abuse

* Tue May 30 2006 David Woodhouse <dwmw2@infradead.org> 0.8.1-1
- Update to 0.8.1

* Sat Mar 18 2006 David Woodhouse <dwmw2@infradead.org> 0.8.0-6
- Update linker script for PPC

* Sat Mar 18 2006 David Woodhouse <dwmw2@infradead.org> 0.8.0-5
- Just drop $RPM_OPT_FLAGS. They're too much of a PITA

* Sat Mar 18 2006 David Woodhouse <dwmw2@infradead.org> 0.8.0-4
- Disable stack-protector options which gcc 3.2 doesn't like

* Fri Mar 17 2006 David Woodhouse <dwmw2@infradead.org> 0.8.0-3
- Use -mcpu= instead of -mtune= on x86_64 too
- Disable SPARC targets on x86_64, because dyngen doesn't like fnegs

* Fri Mar 17 2006 David Woodhouse <dwmw2@infradead.org> 0.8.0-2
- Don't use -mtune=pentium4 on i386. GCC 3.2 doesn't like it

* Fri Mar 17 2006 David Woodhouse <dwmw2@infradead.org> 0.8.0-1
- Update to 0.8.0
- Resort to using compat-gcc-32
- Enable ALSA

* Mon May 16 2005 David Woodhouse <dwmw2@infradead.org> 0.7.0-2
- Proper fix for GCC 4 putting 'blr' or 'ret' in the middle of the function,
  for i386, x86_64 and PPC.

* Sat Apr 30 2005 David Woodhouse <dwmw2@infradead.org> 0.7.0-1
- Update to 0.7.0
- Fix dyngen for PPC functions which end in unconditional branch

* Thu Apr  7 2005 Michael Schwendt <mschwendt[AT]users.sf.net>
- rebuilt

* Sun Feb 13 2005 David Woodhouse <dwmw2@infradead.org> 0.6.1-2
- Package cleanup

* Sun Nov 21 2004 David Woodhouse <dwmw2@redhat.com> 0.6.1-1
- Update to 0.6.1

* Tue Jul 20 2004 David Woodhouse <dwmw2@redhat.com> 0.6.0-2
- Compile fix from qemu CVS, add x86_64 host support

* Wed May 12 2004 David Woodhouse <dwmw2@redhat.com> 0.6.0-1
- Update to 0.6.0.

* Sat May 8 2004 David Woodhouse <dwmw2@redhat.com> 0.5.5-1
- Update to 0.5.5.

* Sun May 2 2004 David Woodhouse <dwmw2@redhat.com> 0.5.4-1
- Update to 0.5.4.

* Thu Apr 22 2004 David Woodhouse <dwmw2@redhat.com> 0.5.3-1
- Update to 0.5.3. Add init script.

* Thu Jul 17 2003 Jeff Johnson <jbj@redhat.com> 0.4.3-1
- Create.
