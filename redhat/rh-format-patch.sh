#!/bin/bash

# RH Patch formatting and sending script
# Run without parameters to see currently supported options. This version
# also supports parameters passthrough directly to git-format-patch.

# Formatting string for the subject prefix, it can use substitutions:
#    %PRODUCT% translates to product name (e.g. RHEL-6.2)
#    %PACKAGE% translates to package/component name (e.g. qemu-kvm)
#    %VERSION% translates to the version of the patch/series (defaults to 1 but putting it to prefix is ignored in this case)
FORMAT="PATCH %VERSION%%PRODUCT% %PACKAGE%"

# Feel free to comment LISTADDRESS line not to send patches automatically
LISTADDRESS="rhvirt-patches@redhat.com"

# Default editor when in interactive mode
DEFAULT_EDITOR="vim"

if [ -z "$EDITOR" ]; then
    EDITOR=$DEFAULT_EDITOR
fi

# Global variables for communication with functions
passthru_params=( )
debug=0
skip_query=0
send=0
is_series=0
interactive=0
version=1
cl_has_bz=0
cl_has_upstream=0
cl_has_brew_id=0

bail()
{
    echo "Error: $1"
    exit 1
}

check_bugzilla_number()
{
    egrep -i "(Bugzilla|BZ).*$bz" "$1" > /dev/null
}

check_upstream_relationship()
{
    egrep -ie cherry \
            -e '^Upstream( status:| relationship:| commit:)?' "$1" \
         > /dev/null
}

check_brew_id()
{
    grep -i Brew "$1" > /dev/null
}

askuser_bool()
{
    local ret ret2 opts a1 a2
    local question=$1
    local default=$2

    if [ "$default" = y ]; then
        a1=n
        a2=no
        ret=1
        ret2=0
        opts=Y/n
    else
        a1=y
        a2=yes
        ret=0
        ret2=1
        opts=y/N
    fi

    read -p "$question ($opts) " ui
    if [ "$ui" = $a1 ] || [ "$ui" = $a2 ]; then
        return $ret
    else
        return $ret2
    fi
}

check_patch_part()
{
    local file=$1
    local funcname=$2
    local part=$3
    local suffix=$4
    local cl=0
    local cl_has_info=0

    if [ $is_series = 1 ]; then
        # Read relevant information if series
        eval cl_has_info=$(echo \$cl_has_$suffix)
    fi

    # Check whether file is a cover-letter
    if grep -i "^Subject: .*PATCH[^]]*00*/" $file > /dev/null; then
        cl=1
    fi

    if ! $funcname "$file"; then
        if [ $is_series = 1 ]; then
            if [ $cl = 1 ] || [ $cl_has_info = 1 ]; then
                return 0
            fi
            echo "... missing $part (not in cover letter)"
        else
            echo "... missing $part"
        fi

        if [ $interactive = 0 ]; then
            return 1
        fi
        if ! askuser_bool "Do you want to manually edit the file?" "y"; then
            return 1
        fi
        $EDITOR $file
        check_patch $file
    else
        if [ $is_series = 1 ]; then
            if [ $cl = 1 ]; then
                eval cl_has_$suffix=1
            fi
        fi
        return 0
    fi
}

check_patch()
{
    local file=$1
    local was_error=0

    check_patch_part $file "check_bugzilla_number" "bugzilla number" "bz" || was_error=1
    if test $interactive = 1 && test $was_error = 1; then return 1; fi

    check_patch_part $file "check_upstream_relationship" "upstream relationship" "upstream" || was_error=1
    if test $interactive = 1 && test $was_error = 1; then return 1; fi

    check_patch_part $file "check_brew_id" "brew information" "brew_id" || was_error=1
    return $was_error
}

get_component_git()
{
     component_git=`git config -l | sed '
         /engineering/! d;
         s,.*/,,
         s,-rhel.*,,
         q
     ' `
}

get_subject_prefix()
{
    local tag=false
    local product=false
    local package=false
    local ver=$1
    local top_commit=$2

    tag=$(git describe $top_commit --tags --match '*.el*'  | awk '{ split($0, a, "el"); split(a[2], b, "-"); print a[1]"el"b[1] }')
    product=`echo $tag | sed '
        s,.*el,RHEL-,;                 # remove package name
        s,\..*,,;                      # remove z-stream version
        s,RHEL-\(.\)[_-],RHEL-\1.,;    # change minor version separator to .
        s,-g[0-9a-f]*$,,' `            # remove trailing junk

    get_component_git

    subject_prefix=${FORMAT//%PACKAGE%/$component_git}
    subject_prefix=${subject_prefix//%PRODUCT%/$product}
    if [ "$ver" -gt 1 ]; then
        subject_prefix=${subject_prefix//%VERSION%/"v$ver "}
    else
        subject_prefix=${subject_prefix//%VERSION%/}
    fi
}

access_pbz()
{
    local bug=$1
    local ver=$2

    tmp=$(bugzilla query --oneline --bug_id=$bug | awk '/#/ { split($0, a, " "); if (substr(a[9], 0, 4) == "rhel") print a[4],"|",substr(a[9], 6, 10); }')
    if [ -z "$tmp" ]; then
        return
    fi

    tmpArr=(${tmp//|/ })

    bzcomp=${tmpArr[0]}
    bzproduct=${tmpArr[1]}

    major=`echo $bzproduct | awk '{ split($0, x, "."); print x[1] }'`
    minor=`echo $bzproduct | awk '{ split($0, x, "."); print x[2] }'`
    is_zstream=`echo $bzproduct | awk '{ split($0, x, "."); print match(x[3], '/z/') }'`

    if [ $is_zstream = 1 ]; then
        append=.z
    fi

    product=RHEL-$major.$minor$append
    subject_prefix=${FORMAT//%PACKAGE%/$bzcomp}
    subject_prefix=${subject_prefix//%PRODUCT%/$product}
    if [ $ver -gt 1 ]; then
        subject_prefix=${subject_prefix//%VERSION%/"v$ver "}
    else
        subject_prefix=${subject_prefix//%VERSION%/}
    fi

    echo $subject_prefix
}

access_bz_login()
{
    local bz=$1

    config=$HOME/.rh-bugzilla-login
    if [ ! -f $config ]; then
        echo "Cannot read bugzilla config file ($config)"

        if [ "x$interactive" != "x1" ]; then
            bail "You have to set up your bugzilla username and password in the interactive mode (run with --interactive flag)"
        fi

        if askuser_bool "Do you want to create it?" "n"; then
            echo -e "url=https://bugzilla.redhat.com\nusername=<your-bugzilla-username>\npassword=<your-password>" > $config
            $EDITOR $config
        else
            bail "Not creating bugzilla config file"
        fi
    fi
}

access_dbz()
{
    local bz=$1
    local ver=$2

    access_bz_login "$1"

    url=`cat $config | awk '/url=/ { split($0, x, "="); print x[2] }'`
    username=`cat $config | awk '/username=/ { split($0, x, "="); print x[2] }'`
    password=`cat $config | awk '/password=/ { split($0, x, "="); print x[2] }'`

    tmpfile=$(mktemp)
    input="<?xml version=\"1.0\"?><methodCall><methodName>Bug.get_bugs</methodName><params><param><value><struct><member><name>Bugzilla_login</name><value><string>$username</string></value></member><member><name>Bugzilla_password</name><value><string>$password</string></value></member><member><name>ids</name><value><array><data><value><int>$bug</int></value></data></array></value></member></struct></value></param></params></methodCall>"

    curl --silent -o $tmpfile "$url/xmlrpc.cgi" -d "$input" -H "Content-Type: text/xml"
    component_bz=$(xpath $tmpfile "string(//methodResponse/params/param/value/struct/member[name='bugs']/value/array/data/value/struct/member[name='component']/value/array/data/value/string)" 2> /dev/null);

    input="<?xml version=\"1.0\"?><methodCall><methodName>Flag.get</methodName><params><param><value><struct><member><name>Bugzilla_login</name><value><string>$username</string></value></member><member><name>Bugzilla_password</name><value><string>$password</string></value></member><member><name>ids</name><value><array><data><value><int>$bug</int></value></data></array></value></member></struct></value></param></params></methodCall>"
    curl --silent -o $tmpfile "$url/xmlrpc.cgi" -d "$input" -H "Content-Type: text/xml"
    bzproduct=$(xpath $tmpfile "string(//methodResponse/params/param/value/struct/member[name='bugs']/value/struct/member/value/struct/member[name='bug']/value/array/data/value/struct/member[name='flags']/value/array/data/value/struct/member/value[starts-with(string, 'rhel-')" 2> /dev/null)

    bzproduct=$(echo $bzproduct | awk '{ split($0, x, "-"); print x[2] }')

    major=$(echo $bzproduct | awk '{ split($0, x, "."); print x[1] }')
    minor=$(echo $bzproduct | awk '{ split($0, x, "."); print x[2] }')
    is_zstream=$(echo $bzproduct | awk '{ split($0, x, "."); print match(x[3], '/z/') }')

    get_component_git
    if [ "x$component_git" != "x$component_bz" ]; then
        bail "Bug $bz refers to component $component_bz but git repository says it's for $component_git."
    fi

    if [ $is_zstream = 1 ]; then
        append=.z
    fi

    product=RHEL-$major.$minor$append

    rm -f $tmpfile

    subject_prefix=${FORMAT//%PACKAGE%/$component_bz}
    subject_prefix=${subject_prefix//%PRODUCT%/$product}
    if [ "$ver" -gt 1 ]; then
        subject_prefix=${subject_prefix//%VERSION%/"v$ver "}
    else
        subject_prefix=${subject_prefix//%VERSION%/}
    fi
    echo $subject_prefix
}

has_python_bugzilla() {
    command -v bugzilla >/dev/null
}

access_bz()
{
    local bug=$1
    local ver=$2

    if has_python_bugzilla; then
        func=access_pbz
    else
        func=access_dbz
    fi

    if [ ! -z "$func" ]; then
        echo $($func "$bug" "$ver")
    fi
}

get_bz_info()
{
    local bz=$1
    local ver=$2

    echo "Accessing bugzilla information. This may take some time..."
    subject_prefix=$(access_bz "$bz" "$ver")
}

check_patch_count()
{
    local num=$1

    if ! askuser_bool "Detected patch count is $num. Is that correct?" "y"; then
        read -p "Please enter a valid number (q for quit): " num

        if [ "$num" = q ]; then
            bail "Terminated by user"
        fi

        let "num=$num+0"
        patch_count_override=$num
    fi
}

usage()
{
    b=$(basename $0)
    echo "RH Patch sender script"
    echo
    echo "Valid parameters:"
    echo "    --bug <number>             - accesses information for bug number to generate subject prefix"
    echo "    --interactive              - turns on interactive mode"
    echo "    --skip-bugzilla-query      - avoids querying bugzilla for information to check integrity (enabled by default)"
    echo "    --debug                    - turns on the debugging messages"
    echo "    --send                     - this will automatically send the patches, meant to be used with --validate-file option"
    echo "    --validate-file <filename> - validates that file <filename> contains all required information"
    echo "    --version <version-number> - override the version to be <version-number> instead of 1"
    echo
    echo "    any other argument is being passed directly to git (parameters passthrough)"
    echo
    echo "Examples:"
    echo "    '$b --bug <bug-number> rhel6/master' gets the bugzilla number of XXXXXX and all commits new to current branch"
    echo "         in comparison to rhel6/master branch."
    echo "    '$b --send --validate-file test.patch' validates file test.patch for all necessary information like BZ number,"
    echo "         upstream relationship, testing statement and brew build location/information. Returns error code 0"
    echo "         on successful validation or error code 1 on error, also auto-send."
    echo "    '$b --interactive rhel6/master' ask for all user information on the terminal. No need to combine with"
    echo "         other flags except the git branch to check again (like rhel6/master in the first example) or number"
    echo "         of patches from the branch's HEAD (e.g. -3 for last 3 patches), can use commit hash too."
    echo "    '$b --skip-bugzilla-query' skips querying the bugzilla for information. If the queries are being skipped then"
    echo "         you don't have to have bugzilla username and password however the checks for target release version,"
    echo "         component and dynamic bugzilla-based subject-prefix generation are disabled and therefore it's not"
    echo "         recommended to use this option"
    echo "    '$b --bug <bug-number> --debug rhel6/master' is the same like first example except there's also debugging enabled"
    echo "         which also saves the information about bugzilla output files for debugging the bugzilla queries"
    echo "    '$b --bug <bug-number> <branch-to-compare-to>' - compares the current branch with the <branch-to-compare-to>"
    echo "         branch and formats the new patches between current branch and the <branch-to-compare-to> branch"
    echo "    '$b --bug <bug-number> <first-branch>..<second-branch>' - compares <first-branch> with <second-branch>"
    echo "         and formats the new patches between them"
    echo "    '$b --bug <bug-number> <first-branch>..<second-branch> --version 3' -- formats patches as above however"
    echo "         the subject prefix is having information about version 3 of the patch series"
    echo "    '$b --interactive rhel6/master' - this will format the new patches between current branch and rhel6/master"
    echo "         branch in the interactive mode"
    echo
    exit 0
}

parse_params()
{
    local array=( "$@" )
    local idarray=( )
    local num=0
    local inc=0
    local min=0

    total_params=${#array[@]}
    while [ $num -lt $total_params ]; do
        var=${array[$num]}
        param=${array[$num+1]}

        inc=1
        case $var in
        --bug)
            bz=$param
            inc=2 ;;
        --validate-file)
            validate_file=( )
            let num=$num+1;
            while [ $num -lt $total_params ]; do
                next=${array[$num]}
                validate_file=( "${validate_file[@]}" "$next" )
                let num=$num+1;
            done
            if test "${#validate_file[@]}" = 0; then
              bail "Missing argument for --validate-file"
            fi
            continue ;;
        --interactive)
            interactive=1 ;;
        --version)
            version=$param
            inc=2 ;;
        --skip-bugzilla-query)
            skip_query=1 ;;
        --debug)
            debug=1 ;;
        --send)
            send=1 ;;
        --help)
            usage ;;
        *)
            passthru_params=( "${idarray[@]}" "$var" ) ;;
        esac

        let num=$num+$inc
        if [ $num -gt $total_params ]; then
            usage
        fi
    done
}

send_patches()
{
    local tempdir=$1
    local files=$2
    local dryrun=

    if [ $send = 0 ]; then
        dryrun=--dry-run
    fi
    if [ -z "$LISTADDRESS" ]; then
        git send-email $files --suppress-cc=all --no-format-patch $dryrun
    else
        git send-email $files --suppress-cc=all --no-format-patch $dryrun \
          --to=$LISTADDRESS
    fi

    if [ "x$?" != "x0" ]; then
        bail "Error while sending patches"
    fi

    if [ $send = 0 ]; then
        if [ -n "$tempdir" ]; then
            rm -rf $tempdir
        fi

        echo "Messages sent to $LISTADDRESS."
    else
        if [ -n "$tempdir" ]; then
            echo "All OK. Message files saved to $tempdir"
        fi
    fi
}

validate_files() {
   local tempdir=$1
   local files=$2
   local was_error=0

   for file in $files
   do
     echo "Validating $file ..."
     if ! [ -f "$file" ]; then
       bail "... does not exist!"
     fi
     if check_patch $file; then
         echo "... ok"
     else
         echo "... errors!"
         was_error=1
     fi
   done

   if [ $was_error != 0 ]; then
     echo "Errors occurred while validating files. Please fix them first"
     return 1
   else
     send_patches "$tempdir" "$files"
   fi
}

parse_params "$@"

if [ $debug = 1 ]; then
    echo "Passthru params: ${passthru_params[@]}"
    echo "Interactive: $interactive"
    echo "Bugzilla: $bz"
    echo "Send: $send"
    echo "Params: $params"
    echo "Subject prefix: $subject_prefix"
fi

if [ $total_params = 0 ]; then
    usage
fi

# Validate file(s)
if test "${#validate_file[@]}" -gt 0; then
   if test "${#validate_file[@]}" -gt 1; then
     is_series=1
   fi

   validate_files "" "${validate_file[*]}"
   exit $?
fi

num_patches=$(git format-patch --stdout ${passthru_params[@]} |  grep -c '^From [^:]* [0-9][0-9]:[0-9][0-9]:[0-9][0-9] [0-9][0-9][0-9]')
top_commit=$(git format-patch --cover-letter --stdout ${passthru_params[@]} | awk 'NR==1{print $2}')
if [ $debug = 1 ]; then
    echo "Num patches: $num_patches"
fi

# Check for patch series
if [ $num_patches -gt 1 ]; then
    params="--numbered --cover-letter"
    is_series=1
fi

if [ $interactive = 1 ]; then
    if [ -z "$bz" ]; then
        read -p "Enter bugzilla number: " bz

        let "bz=$bz+0"
        if [ $bz = 0 ]; then
            bail "Invalid bugzilla number"
        fi
    else
        echo "Bug number: $bz"
    fi

    if ! askuser_bool "Do you want to query bugzilla for information?" "y"; then
        skip_query=1
    fi

    read -p "Enter the patch version (def. to 1): " version
    if [ -z "$version" ]; then
        version=1
    fi
fi

if [ -z "$bz" ] && [ $skip_query != 1 ]; then
    get_bz_info $bz $version
fi

if [ -z "$subject_prefix" ]; then
    get_subject_prefix $version $top_commit
fi

if [ $interactive = 1 ]; then
    check_patch_count $num_patches

    if [ -n "$patch_count_override" ]; then
        num_patches=$patch_count_override
    fi
fi

if [ "$num_patches" -lt 1 ]; then
    bail "Invalid number of patches. Patch count have to be positive number higher than 0!"
fi

tempdir=$(mktemp -d)

files=$(git format-patch --subject-prefix="$subject_prefix" $params --output-directory=$tempdir -$num_patches $top_commit)
cd $tempdir

if [ $is_series = 1 ]; then
    # For series, force interactive mode from now on since they have to edit
    # the cover letter anyway
    interactive=1
fi

echo "Opening editor ($EDITOR) for cover-letter"
tmp=( $files )
$EDITOR ${tmp[0]}

validate_files "$tempdir" "$files"
