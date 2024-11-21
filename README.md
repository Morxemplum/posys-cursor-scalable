# Posy's Cursor (Scalable)
![Scale Showcase](https://github.com/user-attachments/assets/ceb1c365-c883-4732-bd62-94110213d688)

This is a cursor theme that is based on [Posy's cursor](https://www.michieldb.nl/other/cursors/) by Michiel de Boer. Given that Michiel released a few SVGs of his cursor set, I used his SVGs (along with remaking some designs myself) and recreate his theme, entirely out of SVG. No more rasters. Looking sharp on HiDPI monitors.

## Why did I do this?
The main purpose behind this was to create a [hyprcursor](https://wiki.hyprland.org/Hypr-Ecosystem/hyprcursor/) theme, a new cursor utility that modernizes the ancient backbone behind cursors to address it's aging feature set, alongside introducing nifty features, such as SVG Support!

Seeing as nobody has managed to do this so far, I decided to go out of my way to make the theme myself because of how much I love this cursor theme.

## How to use
The source SVGs behind the cursors are made using [Inkscape](https://inkscape.org/), so it is recommended you use this program if you want to tackle the source SVGs.

Alongside the source SVGs are preconfigured hyprcursor themes. I based the themes around how Posy distributes them on his website (minus some inconsistencies). 
### Procedures for Hyprland
You can run ``install_hyprcursor.sh`` after cloning the repository and follow the instructions. It will build and install the hyprcursor theme for you.
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
## To Do List
This theme has feature parity with the original Posy's Cursors (minus some themes and "extra" cursors). I'd say most of the work is done, but if I am feeling up for it, there's probably a couple of things that I could do to really flesh out this theme.
- Add "extra" cursors (Though if you wanna use these, make sure to export to Plain SVG to save file size)
- Add alias, copy, and no-drop cursors to make the theme fully compliant with the [Freedesktop cursor spec](https://www.freedesktop.org/wiki/Specifications/cursor-spec/). This would involve me creating new designs, which would take some time.
- If KDE Plasma goes forward with adopting SVG cursors, I may offer a KDE Plasma version.
