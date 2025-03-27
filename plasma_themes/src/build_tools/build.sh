#!/bin/bash
set -euo pipefail

BIN_DIR="$( dirname "${BASH_SOURCE[0]}" )"
THEMES_DIR="../.."
SRC_DIR="$THEMES_DIR/src"
# TODO: Make this easily interchangable with the different variants
VAR_DIR="$THEMES_DIR/posys_cursor_scalable"
CURSOR_DIR="$VAR_DIR/cursors_scalable"
ALIASES="$SRC_DIR/alias.list"

NOMINAL_SIZE=24
REAL_SIZE=32
FRAME_TIME=30
SCALES="50 75 100 125 150 175 200"

echo -ne "Checking Requirements...\\r"
if [[ ! -d "${CURSOR_DIR}" ]]; then
	echo -e "\\nFAIL: Missing cursor theme"
	exit 1
fi

if ! command -v inkscape > /dev/null ; then
	echo -e "\\nFAIL: Inkscape not found. Make sure you install inkscape through your package manager"
	exit 1
fi

if ! command -v xcursorgen > /dev/null ; then
	echo -e "\\nFAIL: xcursorgen not found. Make sure you install xcursorgen through your package manager"
	exit 1
fi

echo -e "\033[0KChecking Requirements... DONE"

echo -ne "Making Folders... \\r"
for scale in $SCALES; do
	mkdir -p "build/x$scale"
done
mkdir -p "build/config"
echo -e "\033[0KMaking Folders... DONE";

echo "Generating pixmaps..."
for SVG in `find $CURSOR_DIR -iname "*.svg"`; do
	BASENAME=${SVG##*/}
	BASENAME=${BASENAME%.*}
	genPixmaps="file-open:${SVG};"

	echo -ne "    $BASENAME...\\r"

	for scale in $SCALES; do
		DIR="build/x${scale}"
		if [[ "${DIR}/${BASENAME}.png" -ot ${SVG} ]]; then
			genPixmaps="${genPixmaps} export-width:$((${CURSOR_SIZE}*scale/100)); export-height:$((${CURSOR_SIZE}*scale/100)); export-filename:${DIR}/${BASENAME}.png; export-do;"
		fi
	done
	if [ "$genPixmaps" != "file-open:${SVG};" ]; then
		inkscape --shell < <(echo "${genPixmaps}") > /dev/null
	fi

	echo "    $BASENAME... DONE"
done
echo "Generating pixmaps... DONE"

echo "Generating cursor theme..."
OUTPUT="$VAR_DIR/cursors"
# python generate_cursors ../../posys_cursor_scalable/cursors_scalable build ../../posys_cursor_scalable/cursors 100
$BIN_DIR/generate_cursors ${CURSOR_DIR} "build" ${OUTPUT} ${SCALES}
echo "Generating cursor theme... DONE"

echo -ne "Generating shortcuts...\\r"
while read ALIAS ; do
	FROM=${ALIAS% *}
	TO=${ALIAS#* }

	if [[ -e "$OUTPUT/$FROM" ]]; then
		continue
	fi

	ln -s "$TO" "$OUTPUT/$FROM"
done < $ALIASES

while read ALIAS ; do
	FROM=${ALIAS% *}
	TO=${ALIAS#* }

	if [[ -e "$CURSOR_DIR/$FROM" ]]; then
		continue
	fi

	ln -s "$TO" "$CURSOR_DIR/$FROM"
done < $ALIASES
echo -e "\033[0KGenerating shortcuts... DONE"

echo "COMPLETE!"
