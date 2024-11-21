#!/usr/bin/env bash

# The directory that your built cursor theme is going to.
# You can change this to whatever directory is necessary, such as ~/.icons.
# It is not recommended to go outside userspace!
INSTALL_DIR="$(xdg-user-dir)/.local/share/icons"
THEMES_DIR="./hyprcursor_themes"

theme=""
themes=("Posys-Cursor-Scalable" "Posys-Cursor-Scalable-Black" "Posys-Cursor-Scalable-Mono" "Posys-Cursor-Scalable-Mono-Black")
directories=("white" "black" "mono" "mono_black")

function program_check() {
    if ! command -v hyprcursor-util > /dev/null 2>&1; then
        echo "ERROR: hyprcursor-util is not detected. It is either not installed or it is not in your PATH."
        exit 1
    fi
}

function prompt_user() {
    echo "Select a cursor theme to build:"
    echo ""
    echo "1. Default (White)"
    echo "2. Black"
    echo "3. Mono"
    echo "4. Mono Black"
    echo ""
    echo -n "Answer (1 2 3 4): "
    read theme
    theme=$(expr $theme - 1)
}

function build_hyprcursor() {
    theme_dir="theme_${themes[$theme]}"
    echo "Building $theme_dir"
    if [ ! -d "$THEMES_DIR" ]; then
        echo "ERROR: Hyprcursor themes directory missing!"
        exit 1
    fi
    if [ ! -d "$THEMES_DIR/${directories[$theme]}" ]; then
        echo "ERROR: Theme \"${directories[$theme]}\" is missing!"
        exit 1
    fi
    hyprcursor-util --create $THEMES_DIR/${directories[$theme]}
    if [ -d $INSTALL_DIR/$theme_dir ]; then
        echo "Removing existing installation"
        rm -rdf $INSTALL_DIR/$theme_dir
    fi
    echo "Installing theme"
    if [ ! -d "$INSTALL_DIR" ]; then
	  mkdir "$INSTALL_DIR"
	  if [ ! -d "$INSTALL_DIR" ]; then
		  echo "Could not install hyprcursor theme (Invalid installation directory)"
          echo "You can configure this script and change the installation directory"
		  exit 1
	  fi
    fi
    mv $THEMES_DIR/$theme_dir $INSTALL_DIR/$theme_dir
    echo "Theme now in $INSTALL_DIR. Update your hyprland.conf with the following to use the theme."
    echo ""
    echo "env = HYPRCURSOR_THEME,${themes[$theme]}"
}

program_check
prompt_user
build_hyprcursor