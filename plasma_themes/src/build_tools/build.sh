#!/usr/bin/env bash
echo "Select a cursor theme to generate rasters and aliases:"
echo ""
echo "1. Default (White)"
echo "2. Black"
echo "3. Mono"
echo "4. Mono Black"
echo ""
echo -n "Answer (1 2 3 4): "
MIN=1
MAX=4
read THEME
if (($THEME < $MIN || $THEME > $MAX)); then
        echo "invalid input"
        exit 1
fi
THEME=$(expr $THEME - 1)
./buildVariant.sh $THEME
