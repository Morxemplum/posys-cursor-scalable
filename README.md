# Posy's Cursor (Scalable)
![loading](https://github.com/user-attachments/assets/fa08756c-c0e3-4f39-ab1d-08fad391eca8)

This is a cursor theme that is based on [Posy's cursor](https://www.michieldb.nl/other/cursors/) by Michiel de Boer. Given that Michiel released a few SVGs of his cursor set, I used his SVGs (along with remaking designs myself and even making some of my own designs) and recreate his theme, entirely out of SVG.

## Why did I do this?
The main purpose behind this was to create a [hyprcursor](https://wiki.hyprland.org/Hypr-Ecosystem/hyprcursor/) theme, a new cursor utility that modernizes the ancient backbone behind cursors to address it's aging feature set. In addition to hyprcursor themes, there are also themes available for KDE Plasma.

I *really* love this cursor theme, so I decided to make it fully scalable so it'll look great on HiDPI monitors.

## How to use
The source SVGs behind the cursors are made using [Inkscape](https://inkscape.org/), so it is recommended you use this program if you want to tackle the source SVGs.

Alongside the source SVGs are preconfigured hyprcursor and KDE Plasma themes. I based the themes around how Posy distributes them on his website (minus some inconsistencies). 

### Procedures for KDE Plasma
> [!NOTE]
> You need KDE Plasma 6.2 or later to use this theme.

The themes in the repository are already pre-configured if you want an "SVG only" theme. All you have to do is copy and paste the folder into `.icons` or `~/.local/share/icons` folder. However, KDE Plasma will fall back to legacy XCursors if it comes across an application that doesn't support SVG Cursors, mainly GTK/adwaita applications or anything running under XWayland. In addition, aliases exist for alternative naming schemes or to fill in for unavailable designs, and these aren't included.

To add legacy XCursors and aliases to the theme, head into `plasma_themes/src/build_tools` and run `build.sh`. You are more than welcome to add additional size options by adding to the `SCALES` string, but the defaults should cover a variety of sizes. 

### Procedures for Hyprland
You can run `install_hyprcursor.sh` after cloning the repository and follow the instructions. It will build and install the hyprcursor theme for you. 

### From a tarball
Alternatively, you can download a prebuilt theme as a tarball from the [releases](https://github.com/Morxemplum/posys-cursor-scalable/releases) page. For KDE Plasma, the tarballs will include XCursor fallbacks and aliases for a better user experience.

1. Extract the top level folder from the tarball.
2. Move the folder into `.icons` or `~/.local/share/icons`.
#### For Hyprland
3. Update your `hyprland.conf` file with the following lines to apply the theme (changing the theme and size to your liking)
```conf
env = HYPRCURSOR_THEME,Posys-Cursor-Scalable
env = HYPRCURSOR_SIZE,24
```
Alternatively, you can also type the following in your terminal to instantly apply the cursor theme (may not be permanent)
```
hyprctl setcursor Posys-Cursor-Scalable 24
```
#### For KDE Plasma
3. Close any instances of KDE System Settings and open it. Navigate to `Colors & Themes > Cursors`.
4. Select your installed variant of Posy's Cursor (Scalable), and confirm by clicking "Apply"

## "Extra" cursors
Similar to the original Posy's cursors, this repository has the "extra" cursors that you can swap out some of the regular cursors with. These are completely optional cursors and only exist to offer a degree of customization. Some cursors will require a bit of hyprcursor knowledge in order to swap correctly, but these steps should be able to cover most of them.
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
Here's a quick preview of the preconfigured themes and what each theme should look like. Not all cursors are present, but should give you an idea of what you should expect.

### White (Default)
![default](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/white/hyprcursors/default/default.svg) ![hand](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/white/hyprcursors/hand/hand.svg) ![beam](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/white/hyprcursors/beam/beam.svg) ![move](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/white/hyprcursors/move/move.svg) ![forbidden](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/white/hyprcursors/forbidden/forbidden.svg) ![pen](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/white/hyprcursors/pen/pen.svg) ![size_EW](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/white/hyprcursors/size_EW/size_EW.svg) ![size_NeSw](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/white/hyprcursors/size_NeSw/size_NeSw.svg) ![size_NS](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/white/hyprcursors/size_NS/size_NS.svg) ![size_NwSe](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/white/hyprcursors/size_NwSe/size_NwSe.svg) ![precision](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/white/hyprcursors/precision/precision.svg) ![background](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/white/hyprcursors/background/background.svg)

### Black
![default](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/black/hyprcursors/default/default.svg) ![hand](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/black/hyprcursors/hand/hand.svg) ![beam](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/black/hyprcursors/beam/beam.svg) ![move](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/black/hyprcursors/move/move.svg) ![forbidden](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/black/hyprcursors/forbidden/forbidden.svg) ![pen](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/black/hyprcursors/pen/pen.svg) ![size_EW](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/black/hyprcursors/size_EW/size_EW.svg) ![size_NeSw](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/black/hyprcursors/size_NeSw/size_NeSw.svg) ![size_NS](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/black/hyprcursors/size_NS/size_NS.svg) ![size_NwSe](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/black/hyprcursors/size_NwSe/size_NwSe.svg) ![precision](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/black/hyprcursors/precision/precision.svg) ![background](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/black/hyprcursors/background/background.svg)

### Mono
![default](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/mono/hyprcursors/default/default.svg) ![hand](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/mono/hyprcursors/hand/hand.svg) ![beam](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/mono/hyprcursors/beam/beam.svg) ![move](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/mono/hyprcursors/move/move.svg) ![forbidden](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/mono/hyprcursors/forbidden/forbidden.svg) ![pen](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/mono/hyprcursors/pen/pen.svg) ![size_EW](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/mono/hyprcursors/size_EW/size_EW.svg) ![size_NeSw](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/mono/hyprcursors/size_NeSw/size_NeSw.svg) ![size_NS](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/mono/hyprcursors/size_NS/size_NS.svg) ![size_NwSe](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/mono/hyprcursors/size_NwSe/size_NwSe.svg) ![precision](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/mono/hyprcursors/precision/precision.svg) ![background](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/mono/hyprcursors/background/background.svg)

### Mono Black
![default](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/mono_black/hyprcursors/default/default.svg) ![hand](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/mono_black/hyprcursors/hand/hand.svg) ![beam](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/mono_black/hyprcursors/beam/beam.svg) ![move](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/mono_black/hyprcursors/move/move.svg) ![forbidden](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/mono_black/hyprcursors/forbidden/forbidden.svg) ![pen](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/mono_black/hyprcursors/pen/pen.svg) ![size_EW](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/mono_black/hyprcursors/size_EW/size_EW.svg) ![size_NeSw](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/mono_black/hyprcursors/size_NeSw/size_NeSw.svg) ![size_NS](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/mono_black/hyprcursors/size_NS/size_NS.svg) ![size_NwSe](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/mono_black/hyprcursors/size_NwSe/size_NwSe.svg) ![precision](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/mono_black/hyprcursors/precision/precision.svg) ![background](https://github.com/Morxemplum/posys-cursor-scalable/blob/main/hyprcursor_themes/mono_black/hyprcursors/background/background.svg)
