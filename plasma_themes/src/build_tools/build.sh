#!/bin/bash
set -euo pipefail

BIN_DIR="$( dirname "${BASH_SOURCE[0]}" )"
THEMES_DIR="../.."
SRC_DIR="$THEMES_DIR/src"
# TODO: Make this easily interchangable with the different variants
VAR_DIR="$THEMES_DIR/posys_cursor_scalable"
CURSOR_DIR="$VAR_DIR/cursors_scalable"
ALIASES="$SRC_DIR/alias.list"

CURSOR_SIZE=24
# Certain cursors employ an additional sprite in place of the default tail.
# These enlargen the canvas size by 33%. So these cursors will be larger to
# ensure the cursor size is consistent.
TAIL_CURSORS=("alias" "context-menu" "copy" "help" "no-drop" "progress")
TAIL_ICON_SIZE=32
SCALES="100 125 150 175 200"

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

	ACTUAL_SIZE=$CURSOR_SIZE
	# Match cursor name with tail cursors
	for tail in "${TAIL_CURSORS[@]}"; do
		if [[ ${BASENAME} == ${tail} ]]; then
			ACTUAL_SIZE=$TAIL_ICON_SIZE
		fi
	done

	for scale in $SCALES; do
		DIR="build/x${scale}"
		if [[ "${DIR}/${BASENAME}.png" -ot ${SVG} ]]; then
			genPixmaps="${genPixmaps} export-width:$((${ACTUAL_SIZE}*scale/100)); export-height:$((${ACTUAL_SIZE}*scale/100)); export-filename:${DIR}/${BASENAME}.png; export-do;"
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
if [[ ! -d "${OUTPUT}" ]]; then
	mkdir $OUTPUT
fi
$BIN_DIR/generate_cursors ${CURSOR_DIR} "build" ${OUTPUT} ${SCALES}
echo "Generating cursor theme... DONE"

echo -ne "Generating shortcuts...\\r"
while read ALIAS ; do
	# Skip comments (#)
	if [[ $ALIAS =~ ^#.* ]]; then
		continue
	fi
	TO=${ALIAS% *}
	FROM=${ALIAS#* }

	# Skip empty lines
	if [[ $FROM == "" ]] || [[ $TO == "" ]]; then
		continue
	fi

	# echo "FROM: ${FROM} TO: ${TO}"

	if [[ -e "$OUTPUT/$TO" ]]; then
		continue
	fi

	ln -s "$FROM" "$OUTPUT/$TO"
done < $ALIASES

while read ALIAS ; do
	# Skip comments (#)
	if [[ $ALIAS =~ ^#.* ]]; then
		continue
	fi
	TO=${ALIAS% *}
	FROM=${ALIAS#* }

	# Skip empty lines
	if [[ $FROM == "" ]] || [[ $TO == "" ]]; then
		continue
	fi

	if [[ -e "$CURSOR_DIR/$TO" ]]; then
		continue
	fi

	ln -s "$FROM" "$CURSOR_DIR/$TO"
done < $ALIASES
echo -e "\033[0KGenerating shortcuts... DONE"

echo "COMPLETE!"
