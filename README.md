# Posy's Cursor (Scalable)
![Scale Showcase](https://github.com/user-attachments/assets/ceb1c365-c883-4732-bd62-94110213d688)

This is a cursor theme that is based on [Posy's cursor](https://www.michieldb.nl/other/cursors/) by Michiel de Boer. Given that Michiel released a few SVGs of his cursor set, I used his SVGs (along with remaking some designs myself) and recreate his theme, entirely out of SVG. No more rasters.

## Why did I do this?
The main purpose behind this was to create a [hyprcursor](https://wiki.hyprland.org/Hypr-Ecosystem/hyprcursor/) theme, a new cursor utility that modernizes the ancient backbone behind cursors to address it's aging feature set, alongside introducing nifty features, such as SVG Support!

Seeing as nobody has managed to do this so far, I decided to go out of my way to make the theme myself because of how much I love this cursor theme.

## How to use
The source SVGs behind the cursors are made using [Inkscape](https://inkscape.org/), so it is recommended you use this program if you want to tackle the source SVGs.

Alongside the source SVGs are preconfigured hyprcursor themes. I based the themes around how Posy distributes them on his website (minus some inconsistencies). 
### Procedures for Hyprland
1. Use `hyprcursor-util` to build the theme or download a prebuilt tarball from the releases. If using the tarball, make sure to extract the "theme_" folder.
2. Move the theme folder into your `.icons` or `~/.local/share/icons` folder.
3. Update your `hyprland.conf` file with the following lines to apply the theme (changing the theme and size to your liking)
```conf
env = HYPRCURSOR_THEME,Posys-Cursor-Scalable
env = HYPRCURSOR_SIZE,24
```
## To Do List
A lot of the basics are complete, but there's still work that needs to be done
- Animate the watch (Rainbow Hourglass) sprite
  - (I have a setup that will make this programmable)
- Create an install script to simplify the Hyprcursor building process
- Add additional cursors?
