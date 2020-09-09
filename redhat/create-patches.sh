#! /bin/sh

MARKER=$1
SOURCES=$2
SPECFILE=$3
PKGRELEASE=$4

# BUILD* are legacy variables: please use PKGRELEASE instead
PREBUILD=$5
BUILD=$6
RHEV=$7
ZRELEASE=$8
BUILDID=$9

PATCHF="$SOURCES/Patch.include"
patchf="$SOURCES/patch.include"
SERIESF="$SOURCES/series"
clogf="$SOURCES/changelog"
# hide [redhat] entries from changelog
HIDE_REDHAT=1;
# include "From <commit> <commit-date>" line on patches
PRINT_COMMITLINE=1;
# add an extra empty line between headers and "meta" data
META_EXTRALINE=1;
# prefix for all patch files:
PATCHPREFIX='kvm-';
# strips all redhat/ and .gitignore patches
# This was requested in order to avoid the contents of the redhat/ directory
# to be included on the packages (arozansk, orders of lwang)
STRIP_REDHAT=1;
# override LC_TIME to avoid date conflicts when building the srpm
LC_TIME=
SUBLEVEL=$(echo $MARKER | cut -f 2 -d '-')
#RCREV := $(shell echo $(MARKER) | cut -f 2 -d '-' -s | sed -e "s/rc//")
RCREV= 
GITREV=$(echo $MARKER | cut -f 3 -d '-' -s | sed -e "s/git//")
LASTCOMMIT=$(cat lastcommit);
#STAMP=$(echo $MARKER | cut -f 1 -d '-' | sed -e "s/v//");
STAMP=$(echo $MARKER | cut -f 2 -d '-')
if [ -n "$RCREV" ]; then
	RELEASED_KERNEL="0";
	SUBLEVEL=$(($SUBLEVEL - 1));
else
	RELEASED_KERNEL="1";
	RCREV=0;
fi
if [ -z "$GITREV" ]; then
	GITREV=0;
fi
RPM_VERSION="$STAMP-$PREBUILD$PKGRELEASE.el7_9.$ZRELEASE$BUILDID";

touch $PATCHF $patchf
echo >$clogf

total="$(git log --first-parent --pretty=oneline $MARKER.. |wc -l)"
git format-patch --first-parent --no-renames --no-binary -k --stdout $MARKER..|tee debug0 | awk '
BEGIN{TYPE="PATCHJUNK"; count=1; dolog=0; pnum=1000}

	#convert subject line to a useable filename
	function subj_to_name(subject)
	{
		#strip off "Subject: "
		subject = substr(subject, 10);

		#need to get first word
		split(subject, a);
		pre = a[1];

		#if word matches foo: or [foo], then the patch is
		#good, otherwise stick a misc in front of it
		if (! match(pre, /:$|^\[.*\]$/)) {
			subject = "misc " subject;
		}

		name = subject;
		#keep cvs name all lower case, I forgot why
		if (SPECFILE == "") { name = tolower(name); }

		#do the actual filename conversion
		gsub(/[^a-zA-Z0-9_-]/,"-", name);
		gsub(/--*/, "-", name);
                gsub(/^[.-]*/, "", name);
                gsub(/[.-]*$/, "", name);

		if (!match(name, "^" PATCHPREFIX)) {
			name = PATCHPREFIX name;
		}

		#check for duplicate files and append a number to it
		patchname=name;
		num=2;
		while (! system("test -f " SOURCES "/" patchname ".patch")) {
			patchname=name "-" num;
			num=num+1;
        	}
		patchname = patchname ".patch";
	}

	# add an entry to changelog
	function changelog(subjectline, nameline)
	{
		subj = substr(subjectline, 10);
		gsub(/%/, "", subj)
		name = substr(nameline, 7);
		pos=match(name, /</);
		name=substr(name,1,pos-2);
		if ( HIDE_REDHAT == 1 ) {
			if ( subj ~ /^[\[]?redhat[:\]]/ ) {
				if ( COMMIT == LASTCOMMIT ) {
					dolog = 1;
				}
				return;
			}
			if ( subj ~ /^Revert/ ) {
				if ( COMMIT == LASTCOMMIT ) {
					dolog = 1;
				}
				return;
			}
			# keep Fedora on the patch name but not on the changelog
			if ( subj ~ /^\[Fedora\]/ ) {
				gsub(/\[Fedora\] /, "", subj)
			}
		}
		bz=substr(BZ,11);
		meta = "";
		if (bz != "") {
			meta = " [" bz "]";
		}
		cve = substr(CVE, 6);
		if (cve != "") {
			if (meta != "") {
				meta = meta " {" cve "}";
			} else {
				meta = " {" cve "}";
			}
		}
		if ( COMMIT == LASTCOMMIT ) {
			dolog=1;
		} else {
			if (dolog == 1) {
				clog = "- " subj " (" name ")" meta;
				print clog >> CLOGF;
			}
		}
	}

	#special separator, close previous patch
	/^From / { if (TYPE=="PATCHJUNK") {
			COMMIT=substr($0, 6, 40);
			SEPLINE=$0;
			TYPE="HEADER";
			close(OUTF);
			next;
		} }

	#interesting header stuff
	/^From: / { if (TYPE=="HEADER") {
			namestr=$0;
			#check for mime encoding on the email headers
			#git uses utf-8 q encoding
			if ( $0 ~ /=\?utf-8\?q/ ) {
				#get rid of the meta utf-8 junk
				gsub(/=\?utf-8\?q\?/, "");
				gsub(/\?=/, "");

				#translate each char
				n=split($0, a, "=");
				namestr = sprintf("%s", a[1]);
				for (i = 2; i <= n; ++i) {
					utf = substr(a[i], 0, 2);
					c = strtonum("0x" utf);
					namestr = sprintf("%s%c%s", namestr, c, substr(a[i],3));
				}
			}
			NAMELINE=namestr; next;
		    }
	    }
	/^Date: / {if (TYPE=="HEADER") {DATELINE=$0; next; } }
	/^Subject: / { if (TYPE=="HEADER") {SUBJECTLINE=$0; next; } }
	/^Bugzilla: / { if (TYPE=="META") {BZ=$0; } }
	/^CVE: / { if (TYPE=="META") {CVE=$0; } }

	#blank line triggers end of header and to begin processing
	/^$/ { 
	    if (TYPE=="META") {
		#create the dynamic changelog entry
		changelog(SUBJECTLINE, NAMELINE);
		#reset cve values because they do not always exist
		CVE="";
		BZ="";
		TYPE="BODY";
	    }
	    if (TYPE=="HEADER") {
		subj_to_name(SUBJECTLINE);
		OUTF= SOURCES "/" patchname;

		if ((pnum!=1647)&&(pnum!=1657)&&(pnum!=1666)&&(pnum!=1667)&&(pnum!=1668)&&(pnum!=1669)&&(pnum!=1670) \
			&&(pnum!=1671)&&(pnum!=1672)&&(pnum!=1673)&&(pnum!=1674)&&(pnum!=1675) \
			&&(pnum!=1676)&&(pnum!=1677)&&(pnum!=1678)&&(pnum!=1679)&&(pnum!=1726)) {
			#output patch commands for specfile
			print "Patch" pnum": " patchname >> PATCHF;
			#print "ApplyPatch " patchname >> patchf;
			print "%patch" pnum  " -p1" >> patchf;
		}
		pnum=pnum+1;

		if (SPECFILE == "") { print patchname >> SERIESF; }

		printf "Creating qemu-kvm patches - (" count "/" total ")\r";
		count=count+1;

		printf "" > OUTF;
		if (PRINT_COMMITLINE == 1)
			print SEPLINE >> OUTF;
		print NAMELINE >> OUTF;
		print DATELINE >> OUTF;
		print SUBJECTLINE >> OUTF;
		if (META_EXTRALINE == 1)
			print >> OUTF;
		TYPE="META"; next;
	    }
	}

	#in order to handle overlapping keywords, we keep track of each
	#section of the patchfile and only process keywords in the correct section
	/^---$/ {
		if (TYPE=="META") {
			# no meta data found, just use the subject line to fill
			# the changelog
			changelog(SUBJECTLINE, NAMELINE);
			#reset cve values because they do not always exist
			CVE="";
			BZ="";
			TYPE="BODY";
		}
		if (TYPE=="BODY") {
			TYPE="PATCHSEP";
		}
	}
	/^diff --git/ { if (TYPE=="PATCHSEP") {print "" >> OUTF; TYPE="PATCH"; } }
	/^-- $/ { if (TYPE=="PATCH") { TYPE="PATCHJUNK"; } }

	#filter out stuff we do not care about
	{ if (TYPE == "PATCHSEP") { next; } }
	{ if (TYPE == "PATCHJUNK") { next; } }
	{ if (TYPE == "HEADER") { next; } }

	#print the rest
	{ print $0 >> OUTF; }
' SOURCES=$SOURCES PATCHF=$PATCHF patchf=$patchf SPECFILE=$SPECFILE \
	SERIESF=$SERIESF CLOGF=$clogf total=$total LASTCOMMIT=$LASTCOMMIT \
	HIDE_REDHAT=$HIDE_REDHAT STRIP_REDHAT=$STRIP_REDHAT \
	PRINT_COMMITLINE=$PRINT_COMMITLINE PATCHPREFIX=$PATCHPREFIX \
	META_EXTRALINE=$META_EXTRALINE

echo cp $clogf debug > debug1
cp $clogf debug
# strip all redhat/ code
if [ $STRIP_REDHAT = 1 ]; then
	which filterdiff >/dev/null 2>&1;
	if [ ! $? = 0 ]; then
		echo "patchutils is required (filterdiff)" >&2;
		exit 1;
	fi
	which lsdiff >/dev/null 2>&1;
	if [ ! $? = 0 ]; then
		echo "patchutils is required (lsdiff)" >&2;
		exit 1;
	fi
	for patch in $(find $SOURCES/ -name \*.patch); do
		filterdiff -x '*redhat/*' -x '*/.gitignore' -x '*/makefile' $patch >$SOURCES/.tmp;
		diff $patch $SOURCES/.tmp > /dev/null
		if [ $? = 1 ]; then
			filterdiff -i '*' $SOURCES/.tmp > $patch;
		fi
		if [ -z "$(lsdiff $patch)" ]; then
			pnum=`grep -e "^Patch.*: $(basename $patch)$" $PATCHF| sed -e "s/^Patch//" | sed -e "s/:.*//"`
			grep -v -e "^Patch.*: $(basename $patch)$" $PATCHF >$SOURCES/.tmp;
			mv $SOURCES/.tmp $PATCHF;
			grep -v -e "^%patch$pnum -p1$" $patchf >$SOURCES/.tmp;
			mv $SOURCES/.tmp $patchf;
			rm -f $patch;
		fi
	done
	if [ ! "$(cat $PATCHF | wc -l)" = "$(cat $patchf | wc -l)" ]; then
		echo "Internal error: different number of patches between two lists" >&2;
		exit 1;
	fi
fi

#CONFIGS=configs/config.include
#CONFIGS2=configs/config2.include
#find configs/ -mindepth 1 -maxdepth 1 -name config-\* | grep -v merged | cut -f 2 -d '/' >$CONFIGS;
## Set this to a nice high starting point
#count=50;
#rm -f $CONFIGS2;
#for i in $(cat $CONFIGS); do
#	echo "Source$count: $i" >>$CONFIGS2;
#	count=$((count+1));
#done

printf "Creating qemu-kvm patches - Done.    \n"

#the changelog was created in reverse order
#also remove the blank on top, if it exists
#left by the 'print version\n' logic above
cname="$(git var GIT_COMMITTER_IDENT |sed 's/>.*/>/')"
cdate="$(date +"%a %b %d %Y")"
cversion="[$RPM_VERSION]";
tac $clogf | sed "1{/^$/d; /^- /i\
* $cdate $cname $cversion
	}" > $clogf.rev

test -n "$SPECFILE" &&
        sed -i -e "/%%PATCH_LIST%%/r $PATCHF
        /%%PATCH_LIST%%/d
	/%%CONFIGS%%/r $CONFIGS2
	/%%CONFIGS%%/d
        /%%PATCH_APPLICATION%%/r $patchf
        /%%PATCH_APPLICATION%%/d
	/%%CHANGELOG%%/r $clogf.rev
	/%%CHANGELOG%%/d
	s/%%PREBUILD%%/$PREBUILD/
	s/%%BUILD%%/$BUILD/
	s/%%ZRELEASE%%/$ZRELEASE/
	s/%%BUILDID%%/$BUILDID/
	s/%%PKGRELEASE%%/$PKGRELEASE/
	s/%%SUBLEVEL%%/$SUBLEVEL/
	s/%%RCREV%%/$RCREV/
	s/%%GITREV%%/$GITREV/
        s/%%RHEV_FLAG%%/$RHEV/
	s/%%RELEASED_KERNEL%%/$RELEASED_KERNEL/" $SPECFILE
if [ -n "$BUILDID" ]; then
	sed -i -e "s/# % define buildid .local/%define buildid $BUILDID/" $SPECFILE;
fi

rm $PATCHF $patchf $clogf $clogf.rev $CONFIGS $CONFIGS2;

