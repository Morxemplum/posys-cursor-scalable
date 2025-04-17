THEMES_DIR="../.."
THEMES=("posys_cursor_scalable" "posys_cursor_scalable_black" "posys_cursor_scalable_mono" "posys_cursor_scalable_mono_black")
THEME=""

function prompt_user() {
    echo "Select a cursor theme to delete aliases:"
    echo ""
    echo "1. Default (White)"
    echo "2. Black"
    echo "3. Mono"
    echo "4. Mono Black"
    echo "5. All"
    echo ""
    echo -n "Answer (1 2 3 4 5): "
    read THEME
    THEME=$(expr $THEME - 1)
}

function delete_aliases() {
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
}

prompt_user

if [[ $THEME == 4 ]]; then
    for theme in "${THEMES[@]}"; do
        VAR_DIR="$THEMES_DIR/$theme"
        SCALABLE_CURSORS="$VAR_DIR/cursors_scalable"
        RASTER_CURSORS="$VAR_DIR/cursors"

        echo "Deleting aliases for $theme"
        delete_aliases
    done
else
    VAR_DIR="$THEMES_DIR/${THEMES[$THEME]}"
    SCALABLE_CURSORS="$VAR_DIR/cursors_scalable"
    RASTER_CURSORS="$VAR_DIR/cursors"

    delete_aliases
fi
