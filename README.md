# Posy's Cursor (Scalable)
![loading](https://github.com/user-attachments/assets/fa08756c-c0e3-4f39-ab1d-08fad391eca8)

This is a cursor theme based on [Posy's cursor](https://www.michieldb.nl/other/cursors/) by Michiel de Boer. Ever since he released a few SVGs of his cursor set, I used his SVGs to remake his theme entirely out of SVG, so it'll look great on a variety of HiDPI monitors. I also decided to make my own cursors on top of his, cursors for the Linux user.

## Why did I do this?

Originally, I did this to create a [hyprcursor](https://wiki.hyprland.org/Hypr-Ecosystem/hyprcursor/) theme, Hyprland's implementation of drawing the mouse cursor that abandons the XCursor used throughout the [X Window System](https://en.wikipedia.org/wiki/X_Window_System), switching from raster pixel maps to vector graphics. With the increasing adoption of higher resolutions, continuing to use XCursor introduces some big problems:

* To account for various monitor sizes and increasing cursor sizes, multiple raster pixel maps of the same cursor have to be made and stored in a single XCursor.
* These rasters are *uncompressed*. Even PNG offers lossless compression to save file space. Each pixel map is essentially storing a bitmap image.
* This gets worse when the cursor is animated. For example, Posy's infamous rainbow hourglass consists of 75 unique frames. Each frame must be a separate pixel map, and that includes all the various sizes.

This snowballs into XCursor themes having *huge* file sizes that become noticable when entering the megabyte territory. Nobody likes wasted storage, especially for underlying system files like mouse cursors. By replacing the outdated XCursor format with a cursor implementation that uses vector graphics, only one vector map has to be made per cursor (or frame of an animation). Since vector graphics are infinitely scalable, not only can we cover all of the sizes previously possible, but newer sizes that would be difficult to accommodate with rasters.

I based the themes around how Posy distributes them on his website (minus some inconsistencies). As adoption of vector cursors continues, I will be glad to expand support for more compositors.

## Building and Installing The Theme

The source SVGs behind the cursors are made using [Inkscape](https://inkscape.org/), so it is recommended you use this program if you want to edit them.

### Using the Build Script

> [!NOTE]
> If you are on KDE Plasma, you must be running 6.2 or later to use this theme.

Through Python, you can easily run a script that will build the theme (and install it) for you. Just simply clone the repository and run `build.py`, and follow the instructions. Currently supported compositors are **Hyprland** and **KDE Plasma**.

### Clarifications for KDE Plasma

If you want an "SVG only" theme, run the build script and you'll be good to go. However, KDE Plasma will fall back to legacy XCursors if it comes across an application that doesn't support vector cursors, mainly GTK/adwaita applications or anything running under XWayland. The build script does not support XCursor fallbacks *yet*. To add legacy XCursors and aliases to the theme, head into `plasma_themes/src/build_tools` and run `build.sh`, and you'll have a completed theme in the folder of your chosen theme. You are more than welcome to add additional size options by adding to the `SCALES` string, but the defaults should cover a variety of sizes. 

### From a tarball
Alternatively, you can download a prebuilt theme as a tarball from the [releases](https://github.com/Morxemplum/posys-cursor-scalable/releases) page. For KDE Plasma, the tarballs will include XCursor fallbacks and aliases for a better user experience.

1. Extract the top level folder from the tarball.
2. Move the folder into `.icons` or `~/.local/share/icons`.

### Using the Nix Flake

> [!CAUTION]
> Due to the rewrite of the building process, the Nix Flake may no longer work as intended and needs to be updated. I am hoping this will be resolved before 1.4's release.

For Nix users this repo provides a consumable flake.

Add this repo to your `flake.nix` inputs:

```nix
{
    inputs = {
        nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
        posy-cursor = {
            url = "github:Morxemplum/posys-cursor-scalable";
            inputs.nixpkgs.follows = "nixpkgs";
        };
        # ...
    };

    # ...
}
```

Then apply the provided overlay to your nixpkgs, which will make `pkgs.posy-scalable` available for you to use. This can then be set however you prefer, the example below will be using [Home Manager](https://github.com/nix-community/home-manager)'s `home.pointerCursor` option.

```nix
{ inputs, pkgs, ... }: {
    nixpkgs.overlays = [inputs.posy-cursor.overlays.default];
    home.pointerCursor = {
        enable = true;
        package = pkgs.posy-scalable;
        name = "posys_cursor_scalable"; # For White (Default)
        # name = "posys_cursor_scalable_black"; # For Black variant
        # name = "posys_cursor_scalable_mono"; # For Mono variant
        # name = "posys_cursor_scalable_mono_black"; For Mono Black variant
    };
}
```

## Post-installation 

### Hyprland
Update your `hyprland.conf` file with the following lines to apply the theme (changing the theme and size to your liking)
```conf
env = HYPRCURSOR_THEME,hyprcursor_posys_cursor_scalable
env = HYPRCURSOR_SIZE,24
```
Alternatively, you can also type the following in your terminal to instantly apply the cursor theme (may not be permanent)
```
hyprctl setcursor hyprcursor_posys_cursor_scalable 24
```
### KDE Plasma
1. Close any instances of KDE System Settings and open it. Navigate to `Colors & Themes > Cursors`.
2. Select your installed variant of Posy's Cursor Scalable, and confirm by clicking "Apply"

## "Extra" cursors
Similar to the original Posy's cursors, this repository has the "extra" cursors that you can swap out some of the regular cursors with. These are completely optional cursors and only exist to offer a degree of customization. You can easily swap or add in extra cursors through the build script, making it easy to tailor the theme to your liking.

## Building A Cursor Manually
0. If needed, modify and copy over the metadata file for the corresponding custom cursor (otherwise it should be taken care of for you)
1. Open up the extra cursor that you want to swap out in Inkscape or a sufficient alternative.
2. If it doesn't exist, create a new folder in the theme you want to modify and name it after the cursor you'll be exporting
3. Export the cursor as a "Plain SVG" (Inkscape SVGs have additional metadata and information that need to be stripped out for file size)
4. We want to further optimize the file size by using [scour](https://github.com/scour-project/scour), an application that is available on most distros. On a terminal, navigate to the directory your plain SVG is in, and type in `scour [plain svg name].svg [a slightly different name].svg`. This is to get the file size as small as possible.

    a. If you want to avoid using the terminal / command line, you can access a GUI version of it in Inkscape through `File > Save a Copy`, and selecting "Optimized SVG" from the file type dropdown menu. *Be careful as this method may not always work.*

    b. For the most optimal results, you can use the following flags below
    ```
    --set-precision=4 --strip-xml-prolog --remove-titles --remove-description --remove-metadata --remove-descriptive-elements --enable-comment-stripping --indent=tab --no-line-breaks --strip-xml-space --enable-id-stripping --shorten-ids
    ```
5. **(KDE Plasma Users Only)** Inkscape exports SVGs in SVG 1.1. However, Qt SVGs use 1.2 Tiny, a slight update of SVG that strips out more advanced features (e.g. clipping, masking). BIMI P/S is a profile that further strips away features (like JavaScript execution) for security purposes, but is valid Tiny 1.2. [svgtinyps-cli](https://github.com/SRWieZ/svgtinyps-cli/releases/tag/v1.4.0) is a program that allows us to convert our SVG to BIMI P/S.

    a. Install a binary and rename it to ``svgtinyps``, and move it to the same directory as our SVG to simplify the process. 
    
    b. With the terminal, type in `./svgtinyps convert [optimized svg name].svg [either a different name, or the initial svg name].svg --title="Posy's Cursor"`. This will give us our final SVG.

    c. If you chose a different name, make sure to swap names with the original SVG so our converted SVG will take place.

    d. Delete other SVGs so only the converted SVG remains

## Preview
Here's a quick preview of the preconfigured themes and what each theme should look like. Animated cursors are presented as still images rather than their fully animated counterparts

### White (Default)
![default](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable/cursors_scalable/default/default.svg) ![pointer](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable/cursors_scalable/pointer/pointer.svg) ![text](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable/cursors_scalable/text/text.svg) ![vertical-text](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable/cursors_scalable/vertical-text/vertical-text.svg) ![all-scroll](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable/cursors_scalable/all-scroll/all-scroll.svg) ![pen](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable/cursors_scalable/pen/pen.svg) ![ew-resize](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable/cursors_scalable/ew-resize/ew-resize.svg) ![nesw-resize](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable/cursors_scalable/nesw-resize/nesw-resize.svg) ![ns-resize](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable/cursors_scalable/ns-resize/ns-resize.svg) ![nwse-resize](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable/cursors_scalable/nwse-resize/nwse-resize.svg) ![row-resize](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable/cursors_scalable/row-resize/row-resize.svg) ![col-resize](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable/cursors_scalable/col-resize/col-resize.svg) ![crosshair](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable/cursors_scalable/crosshair/crosshair.svg) ![not-allowed](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable/cursors_scalable/not-allowed/not-allowed.svg) ![wait](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable/cursors_scalable/wait/wait.svg) ![progress](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable/cursors_scalable/progress/progress.svg) ![alias](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable/cursors_scalable/alias/alias.svg) ![copy](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable/cursors_scalable/copy/copy.svg) ![no-drop](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable/cursors_scalable/no-drop/no-drop.svg) ![context-menu](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable/cursors_scalable/context-menu/context-menu.svg) ![help](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable/cursors_scalable/help/help.svg)

### Black
![default](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_black/cursors_scalable/default/default.svg) ![pointer](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_black/cursors_scalable/pointer/pointer.svg) ![text](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_black/cursors_scalable/text/text.svg) ![vertical-text](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_black/cursors_scalable/vertical-text/vertical-text.svg) ![all-scroll](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_black/cursors_scalable/all-scroll/all-scroll.svg) ![pen](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_black/cursors_scalable/pen/pen.svg) ![ew-resize](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_black/cursors_scalable/ew-resize/ew-resize.svg) ![nesw-resize](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_black/cursors_scalable/nesw-resize/nesw-resize.svg) ![ns-resize](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_black/cursors_scalable/ns-resize/ns-resize.svg) ![nwse-resize](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_black/cursors_scalable/nwse-resize/nwse-resize.svg) ![row-resize](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_black/cursors_scalable/row-resize/row-resize.svg) ![col-resize](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_black/cursors_scalable/col-resize/col-resize.svg) ![crosshair](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_black/cursors_scalable/crosshair/crosshair.svg) ![not-allowed](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_black/cursors_scalable/not-allowed/not-allowed.svg) ![wait](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_black/cursors_scalable/wait/wait.svg) ![progress](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_black/cursors_scalable/progress/progress.svg) ![alias](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_black/cursors_scalable/alias/alias.svg) ![copy](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_black/cursors_scalable/copy/copy.svg) ![no-drop](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_black/cursors_scalable/no-drop/no-drop.svg) ![context-menu](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_black/cursors_scalable/context-menu/context-menu.svg) ![help](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_black/cursors_scalable/help/help.svg)

### Mono
![default](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono/cursors_scalable/default/default.svg) ![pointer](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono/cursors_scalable/pointer/pointer.svg) ![text](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono/cursors_scalable/text/text.svg) ![vertical-text](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono/cursors_scalable/vertical-text/vertical-text.svg) ![all-scroll](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono/cursors_scalable/all-scroll/all-scroll.svg) ![pen](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono/cursors_scalable/pen/pen.svg) ![ew-resize](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono/cursors_scalable/ew-resize/ew-resize.svg) ![nesw-resize](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono/cursors_scalable/nesw-resize/nesw-resize.svg) ![ns-resize](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono/cursors_scalable/ns-resize/ns-resize.svg) ![nwse-resize](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono/cursors_scalable/nwse-resize/nwse-resize.svg) ![row-resize](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono/cursors_scalable/row-resize/row-resize.svg) ![col-resize](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono/cursors_scalable/col-resize/col-resize.svg) ![crosshair](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono/cursors_scalable/crosshair/crosshair.svg) ![not-allowed](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono/cursors_scalable/not-allowed/not-allowed.svg) ![wait](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono/cursors_scalable/wait/wait.svg) ![progress](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono/cursors_scalable/progress/progress.svg) ![alias](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono/cursors_scalable/alias/alias.svg) ![copy](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono/cursors_scalable/copy/copy.svg) ![no-drop](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono/cursors_scalable/no-drop/no-drop.svg) ![context-menu](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono/cursors_scalable/context-menu/context-menu.svg) ![help](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono/cursors_scalable/help/help.svg)

### Mono Black
![default](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono_black/cursors_scalable/default/default.svg) ![pointer](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono_black/cursors_scalable/pointer/pointer.svg) ![text](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono_black/cursors_scalable/text/text.svg) ![vertical-text](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono_black/cursors_scalable/vertical-text/vertical-text.svg) ![all-scroll](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono_black/cursors_scalable/all-scroll/all-scroll.svg) ![pen](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono_black/cursors_scalable/pen/pen.svg) ![ew-resize](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono_black/cursors_scalable/ew-resize/ew-resize.svg) ![nesw-resize](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono_black/cursors_scalable/nesw-resize/nesw-resize.svg) ![ns-resize](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono_black/cursors_scalable/ns-resize/ns-resize.svg) ![nwse-resize](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono_black/cursors_scalable/nwse-resize/nwse-resize.svg) ![row-resize](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono_black/cursors_scalable/row-resize/row-resize.svg) ![col-resize](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono_black/cursors_scalable/col-resize/col-resize.svg) ![crosshair](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono_black/cursors_scalable/crosshair/crosshair.svg) ![not-allowed](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono_black/cursors_scalable/not-allowed/not-allowed.svg) ![wait](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono_black/cursors_scalable/wait/wait.svg) ![progress](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono_black/cursors_scalable/progress/progress.svg) ![alias](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono_black/cursors_scalable/alias/alias.svg) ![copy](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono_black/cursors_scalable/copy/copy.svg) ![no-drop](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono_black/cursors_scalable/no-drop/no-drop.svg) ![context-menu](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono_black/cursors_scalable/context-menu/context-menu.svg) ![help](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/plasma_themes/posys_cursor_scalable_mono_black/cursors_scalable/help/help.svg)
