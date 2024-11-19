# Posy's Cursor (Scalable)
This is a cursor theme that is based on [Posy's cursor](https://www.michieldb.nl/other/cursors/) by Michiel de Boer. Given that Michiel released a few SVGs of his cursor set, I decided to go forward and use his SVGs (along with remaking some of the designs myself) and recreate his theme, entirely out of SVG.

## Why did I do this?
The main purpose behind this was to create a [hyprcursor](https://wiki.hyprland.org/Hypr-Ecosystem/hyprcursor/) theme, a new cursor utility that is meant to modernize the ancient backbone behind cursor themes to address many shortcomings, alongside introducing nifty features, such as SVG Support!

Seeing as nobody has managed to do this so far, I decided to go out of my way to make the theme myself because of how much I love this cursor theme.

## How to use
The source SVGs behind the sprites are made using [Inkscape](https://inkscape.org/), so it is recommended you use this program if you want to tackle the source SVGs.

Alongside the source SVGs are preconfigured hyprcursor themes. I based the themes around how Posy distributes them on his websites (minus some inconsistencies). All you have to do is run `hyprcursor-util` to build the themes, then just simply put the theme in your `.icons` or `~/local/share/icons` folder and update your configuration file to utilize the new theme

## To Do List
As of writing this, this is a bare bones publish of the theme and more work needs to be done.
- Generate additional themes (Black, Mono, Black Mono)
- Animate the watch (Rainbow Hourglass) sprite
- Create an install script to simplify the Hyprcursor building process
- Add additional cursors?
