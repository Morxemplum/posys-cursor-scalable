#!/usr/bin/env bash
set -uo pipefail

BIN_DIR="$( dirname "${BASH_SOURCE[0]}" )"
THEMES_DIR="../.."
SRC_DIR="$THEMES_DIR/src"
THEME=""
THEMES=("posys_cursor_scalable" "posys_cursor_scalable_black" "posys_cursor_scalable_mono" "posys_cursor_scalable_mono_black")
VARIANTS=("white" "black" "mono" "mono_black")
ALIASES="$SRC_DIR/alias.list"

CURSOR_SIZE=24
# Certain cursors employ an additional sprite in place of the default tail.
# These enlargen the canvas size by 33%. So these cursors will be larger to
# ensure the cursor size is consistent.
TAIL_CURSORS=("alias" "context-menu" "copy" "help" "no-drop" "progress")
TAIL_ICON_SIZE=32
SCALES="75 100 125 150 175"

## START OF SCRIPT
echo "Select a cursor theme to generate rasters and aliases:"
echo ""
echo "1. Default (White)"
echo "2. Black"
echo "3. Mono"
echo "4. Mono Black"
echo ""
echo -n "Answer (1 2 3 4): "
read THEME
THEME=$(expr $THEME - 1)

VAR_DIR="$THEMES_DIR/${THEMES[$THEME]}"
CURSOR_DIR="$VAR_DIR/cursors_scalable"
VARIANT="${VARIANTS[$THEME]}"

echo -ne "Checking Requirements...\\r"
if [[ ! -d "${CURSOR_DIR}" ]]; then
	echo -e "\\nFAIL: Missing \"${VARIANT}\" cursor theme"
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
	mkdir -p "build_${VARIANT}/x$scale"
done
mkdir -p "build_${VARIANT}/config"
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
		if [[ ${BASENAME} == ${tail}* ]]; then
			ACTUAL_SIZE=$TAIL_ICON_SIZE
		fi
	done

	for scale in $SCALES; do
		DIR="build_${VARIANT}/x${scale}"
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

# TODO: In rare situations, Inkscape can crash when generating the pixmaps. Perhaps we should add a verification process to remove corrupted pixmaps.

echo "Generating cursor theme..."
OUTPUT="$VAR_DIR/cursors"
if [[ ! -d "${OUTPUT}" ]]; then
	mkdir $OUTPUT
fi
$BIN_DIR/generate_cursors ${CURSOR_DIR} "build_${VARIANT}" ${OUTPUT} ${SCALES}
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
