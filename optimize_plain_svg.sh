#!/usr/bin/env bash

CURRENT_DIR=`pwd`
CURSOR_DIR="${CURRENT_DIR}/plasma_themes/posys_cursor_scalable/cursors_scalable/"

if [ ! -d "$CURSOR_DIR" ]; then
    echo "ERROR: Cursor Directory does not exist."
    exit 1
fi

for svg in `find $CURSOR_DIR -iname "*.svg"`; do
    FILE_NAME="${svg%.*}"
    scour $svg $FILE_NAME-optimized.svg --set-precision=4 --strip-xml-prolog \
    --remove-titles --remove-description --remove-metadata --remove-descriptive-elements \
    --enable-comment-stripping --indent=tab --no-line-breaks --strip-xml-space \
    --enable-id-stripping --shorten-ids
    rm $svg
    mv $FILE_NAME-optimized.svg $svg
done