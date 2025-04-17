THEMES_DIR="../.."
VAR_DIR="$THEMES_DIR/posys_cursor_scalable"
SCALABLE_CURSORS="$VAR_DIR/cursors_scalable"
RASTER_CURSORS="$VAR_DIR/cursors"

if [ ! -d "$VAR_DIR" ]; then
    echo "ERROR: Theme directory does not exist."
    exit 1
fi

if [ ! -d "$SCALABLE_CURSORS" ]; then
    echo "ERROR: Scalable cursors directory does not exist."
    exit 1
fi

if [ -d "$RASTER_CURSORS" ]; then
    for folder in `ls ${RASTER_CURSORS}`; do
        FILE=${RASTER_CURSORS}/${folder}
        if [ -L $FILE ]; then
            rm $FILE
        fi
    done
fi

for folder in `ls ${SCALABLE_CURSORS}`; do
    FILE=${SCALABLE_CURSORS}/${folder}
    if [ -L $FILE ]; then
        rm $FILE
    fi
done