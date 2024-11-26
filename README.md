# Posy's Cursor (Scalable)
![loading](https://github.com/user-attachments/assets/fa08756c-c0e3-4f39-ab1d-08fad391eca8)

This is a cursor theme that is based on [Posy's cursor](https://www.michieldb.nl/other/cursors/) by Michiel de Boer. Given that Michiel released a few SVGs of his cursor set, I used his SVGs (along with remaking some designs myself) and recreate his theme, entirely out of SVG. No more rasters. Looking sharp on HiDPI monitors.

## Why did I do this?
The main purpose behind this was to create a [hyprcursor](https://wiki.hyprland.org/Hypr-Ecosystem/hyprcursor/) theme, a new cursor utility that modernizes the ancient backbone behind cursors to address it's aging feature set, alongside introducing nifty features, such as SVG Support!

Seeing as nobody has managed to do this so far, I decided to go out of my way to make the theme myself because of how much I love this cursor theme.

## How to use
The source SVGs behind the cursors are made using [Inkscape](https://inkscape.org/), so it is recommended you use this program if you want to tackle the source SVGs.

Alongside the source SVGs are preconfigured hyprcursor themes. I based the themes around how Posy distributes them on his website (minus some inconsistencies). 
### Procedures for Hyprland
You can run ``install_hyprcursor.sh`` after cloning the repository and follow the instructions. It will build and install the hyprcursor theme for you. Alternatively, you can download a prebuilt theme as a tarball from the [releases](https://github.com/Morxemplum/posys-cursor-scalable/releases) page.
#### From a tarball
1. Extract the "theme_" folder from the tarball.
2. Move the theme folder into your `.icons` or `~/.local/share/icons` folder.
3. Update your `hyprland.conf` file with the following lines to apply the theme (changing the theme and size to your liking)
```conf
env = HYPRCURSOR_THEME,Posys-Cursor-Scalable
env = HYPRCURSOR_SIZE,24
```
Alternatively, you can also type the following in your terminal to instantly apply the cursor theme (may not be permanent)
```
hyprctl setcursor Posys-Cursor-Scalable 24
```
#### "Extra" cursors
Similar to the original Posy's cursors, this repository has the "extra" cursors that you can swap out some of the regular cursors with. These are completely optional cursors and only exist to offer a degree of customization. Some cursors will require a bit of hyprcursor knowledge in order to swap correctly, but these steps should be able to cover most of them.
1. Open up the extra cursor that you want to swap out in Inkscape or a sufficient alternative.
2. If it doesn't exist, create a new folder in the theme you want to modify and name it after the cursor you'll be exporting
3. Export the cursor as a "Plain SVG" (Inkscape SVGs have additional metadata and information that need to be stripped out for file size)
4. If needed, modify and copy over the meta file for the corresponding custom cursor (otherwise it should be taken care of for you)

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
