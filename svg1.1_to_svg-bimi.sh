#!/usr/bin/env bash

# For KDE Plasma, the SVGs for the scalable cursors must follow SVG Tiny 1.2
# as the Qt framework only uses Tiny 1.2. This script takes advantage of a
# program that converts a Plain SVG (which is SVG 1.1 Full) to a profile called
# BIMI P/S. BIMI P/S is valid Tiny 1.2 as BIMI P/S is a subset of Tiny 1.2.

# Get the program here: https://github.com/SRWieZ/svgtinyps-cli


CURRENT_DIR=`pwd`
SVG_DIR=$CURRENT_DIR
CURSOR_DIR="${CURRENT_DIR}/plasma_themes/posys_cursor_scalable/cursors_scalable"

if [ ! -d "$CURSOR_DIR" ]; then
    echo "ERROR: Cursor Directory does not exist."
    exit 1
fi

EXE="${SVG_DIR}/svgtinyps"
for svg in `find $CURSOR_DIR -iname "*.svg"`; do
    FILE_NAME="${svg%.*}"
    $EXE convert $svg $FILE_NAME-final.svg --title="Posy's Cursor"
    rm $svg
    mv $FILE_NAME-final.svg $svg
done