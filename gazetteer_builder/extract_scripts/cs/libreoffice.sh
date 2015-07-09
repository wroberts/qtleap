#!/bin/bash

URL=http://download.documentfoundation.org/libreoffice/src/4.4.0/libreoffice-translations-4.4.0.3.tar.xz
PACKED_FILE=${URL##*/}
PO_PATH=libreoffice-4.4.0.3/translations/source/cs

EN_GAZFILE=$1
OTHERLANG_GAZFILE=$2
ID_PREFIX=$3


#wget $URL
#tar -xvvJf $PACKED_FILE
find $PO_PATH -name '*.po' -exec cat {} \; | \
    ./po2gaz.pl $EN_GAZFILE $OTHERLANG_GAZFILE $ID_PREFIX

if [ "_$4" == "clean" ]; then
    rm $PACKED_FILE
    rm -rf ${PO_PATH%%/*}
fi
