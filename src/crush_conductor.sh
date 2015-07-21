#!/bin/bash
set -e

CEPH=ceph
CRUSHTOOL=crushtool

TMP_OLD_CRUSH_BIN=/tmp/crush.bin
TMP_OLD_CRUSH_TXT=/tmp/crush.txt

TMP_OSD_TREE_TXT=$(tempfile -p 'osd_tree.json')

TMP_NEW_CRUSH_TXT=$(tempfile -p 'crush.txt')
TMP_NEW_CRUSH_BIN=$(tempfile -p 'crush.bin')

# backup
${CEPH} osd getcrushmap -o ${TMP_OLD_CRUSH_BIN}
${CRUSHTOOL} -d ${TMP_OLD_CRUSH_BIN} -o ${TMP_OLD_CRUSH_TXT}

# getting data
${CEPH} osd tree -f json-pretty -o ${TMP_OSD_TREE_TXT}

# conversion
${CEPH} osd set noout
${CEPH} tell osd.\* injectargs '--osd-max-backfills 1'
${CEPH} tell osd.\* injectargs '--osd-recovery-max-active 1'

mv -f ${TMP_OSD_TREE_TXT} /tmp/hier.txt
python ./crush_converter.py > ${TMP_NEW_CRUSH_TXT}
${CRUSHTOOL} -c ${TMP_NEW_CRUSH_TXT} -o ${TMP_NEW_CRUSH_BIN}

# injecting
${CEPH} osd setcrushmap -i ${TMP_NEW_CRUSH_BIN}
${CEPH} osd unset noout

# cleaning
rm -f   ${TMP_OSD_TREE_TXT}     \
        ${TMP_OLD_CRUSH_BIN}    \
        ${TMP_OLD_CRUSH_TXT}    \
        ${TMP_NEW_CRUSH_BIN}    \
        ${TMP_NEW_CRUSH_TXT}
