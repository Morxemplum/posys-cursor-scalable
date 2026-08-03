'''
This module holds all the metadata regarding various cursor designs that can be
easily read for my scripts, by not bothering with a cross-language data format
and just storing the data as direct Python structures.

These structures should have all the information needed to construct metadata
files for all the cursor designs for various compositors.
'''

import enum
from typing import NotRequired, TypedDict

class KWinCursor(TypedDict):
    '''
    This dictionary resembles a cursor structure that is meant to mimic the
    KDE Theming formatting for their metadata files.
    '''
    filename: str
    nominal_size: int
    hotspot_x: float
    hotspot_y: float
    delay: NotRequired[int]

class KWinAnimatedCursor(TypedDict):
    '''
    This dictionary resembles a cursor structure that mimics the KDE Theming
    formatting for metadata files regarding animated cursors (which is a list
    of different cursor metadatas)
    '''
    frames: list[KWinCursor]

class CursorDesign(TypedDict):
    '''
    This is the internal data structure that I use to contain various metadata
    to help structure and construct data for the cursors. This formatting 
    structure is meant to be compositor-agnostic.

    Attributes:
        src_file (str, Optional):
            If the name of the Inkscape SVG file does not match the design 
            name, put the file name here (omitting file extension)
        out_file (str, Optional):
            If you wish the final SVG to have a different file name than
            the design, put the file name here (omitting file extension)
        extra (bool, Optional):
            If true, tells the program this cursor is not within the default
            set of cursors and should look into the "extras" directory for
            the cursor.
        aliases (list[str], Optional):
            The same cursor may be referred to different names by various
            programs or environments, or you want to fill in a design with
            an existing one. This list of strings should be all the names
            the cursor should alias.
        
        hotspot (tuple[float, float], Optional):
            An XY value with values from 0-1 that are indicative of where in
            the cursor should the actual mouse point be. If no value is
            provided, this value will default to (0, 0).
        size (tuple[int, int]):
            The size of the cursor, in logical pixels.
        build (bool):
            Informs the build script whether this cursor is going to be built
            into the final theme or not.
        skip_bimi (bool, Optional):
            If set to True, will skip conversion for Qt compatibility. Defaults
            to False. 
            
            WARNING: Do not have cursors skip BIMI conversion unless you can
            verify that the SVG files are compliant with 1.2 Tiny. This should
            be treated as a last resort!
        skip_theming (bool, Optional):
            If set to True, this will skip theming procedures on the cursor.
            Defaults to False. This attribute is meant as a slight performance
            optimization for the few designs that remain the same throughout
            all different themes.

        total_frames (int, optional):
            If this is an animated cursor, this functionally lists how many
            frames will be in the cursor
        animated_speed (int, optional):
            If this is an animated cursor, this specifies a fixed framerate for
            the cursor, in frames per second. 
    '''
    src_file: NotRequired[str]
    out_file: NotRequired[str]
    extra: NotRequired[bool]
    aliases: NotRequired[list[str]]

    hotspot: NotRequired[tuple[float, float]]
    size: tuple[int, int]
    build: bool
    skip_bimi: NotRequired[bool]
    skip_theming: NotRequired[bool]

    total_frames: NotRequired[int]
    animation_speed: NotRequired[int]

class CursorManifest(TypedDict):
    '''
    This is the internal data structure that is to be used to give all the info
    about the cursor theme. This information is used when accessing and
    applying themes for the user.

    Attributes:
        name (str):
            The name of the theme itself
        tags (list[str]):
            The list of tags that disclose what has been modified about the 
            theme from its stock settings.
        description (str):
            Description of what the theme is about.
        authors (list[str]):
            List of authors involved in making the cursor theme.
        version (str):
            A simplistic string detailing the version of the theme. Reminder
            that this theme doesn't receive frequent updates, so semantic 
            versioning is not a requirement.
    '''
    name: str
    tags: list[str]
    description: str
    authors: list[str]
    version: str

class ThemeColor(enum.IntEnum):
    '''
    This enum is useful for distinguishing the different variants (or colors)
    offered by this theme.
    '''
    WHITE = 0
    BLACK = 1
    MONO = 2
    MONO_BLACK = 3

class ThemePalette(TypedDict):
    '''
    The palette full of RGB colors (in hex format) that will be used to apply
    the colors to SVGs to fall in line with the dictated theme
    '''
    primary: str
    secondary: str
    mono: bool
    tone: NotRequired[str]
    overrides: list[str]

class Compositor(enum.Enum):
    '''
    This includes all of the Wayland compositors that support vector cursors.
    '''
    UNSUPPORTED = ""
    HYPRLAND = "hyprland"
    KWIN = "plasma"

    @staticmethod
    def from_str(s : str) -> Compositor:
        match(s.lower()):
            case "hyprland":
                return Compositor.HYPRLAND
            case "kwin":
                return Compositor.KWIN
            case "plasma":
                return Compositor.KWIN
            case _:
                return Compositor.UNSUPPORTED

class CursorCollection(TypedDict):
    '''
    Structure for the overall cursor database.

    Attributes:
        manifest (CursorManifest):
            The manifest of the theme
        cursors (dict[str, CursorDesign]):
            The full collection of cursor design information, keyed to their 
            design name
        theme (ThemeColor):
            The color of the theme.
    '''
    manifest: CursorManifest
    cursors: dict[str, CursorDesign]
    theme: ThemeColor

def get_theme_palette(theme: ThemeColor) -> ThemePalette:
    match(theme):
        case ThemeColor.WHITE | ThemeColor.MONO:
            return {
                "primary": "#ffffff",
                "secondary": "#000000",
                "mono": theme == ThemeColor.MONO,
                "overrides": ["#ffffff"]
            }
        case ThemeColor.BLACK | ThemeColor.MONO_BLACK:
            return {
                "primary": "#000000",
                "secondary": "#ffffff",
                "mono": theme == ThemeColor.MONO_BLACK,
                "overrides": ["#3f3f3f"]
            }

def kwin_nominal_size(cursor: str) -> int:
    '''
    A helper function that specifically takes the size attribute and crushes it
    to a singular number for the KWin compositor.

    Parameters:
        cursor: The name of the cursor to get the size of

    Returns:
        The largest number in the size attribute 
    '''
    if not cursor in db["cursors"]:
        return -1
    return max(db["cursors"][cursor]["size"])

# Some attributes will be later modified by scripts to tailor user preferences
db : CursorCollection = {
    "manifest": {
        "name": "Posy's Cursors Scalable",
        "tags": [],
        "description": "Posy's infamous cursors, containing unrasterized and additional cursors for the Linux user",

        "authors": ["Michiel De Boer", "Synth Morxemplum"],
        "version": "1.4"
    },
    
    "theme": ThemeColor.WHITE,

    "cursors": {
        "default": {
            "build": True,
            "size": (24, 24),
            "aliases": ["arrow", "left_ptr"]
        },

        "hand": {
            "build": True,
            "hotspot": (0.296, 0),
            "size": (24, 24),
            "aliases": ["pointer", "hand1", "hand2", "pointing_hand", "9d800788f1b08800ae810202380a0822", "e29285e634086352946a0e7090d73106"]
        },

        "grab": {
            "build": True,
            "hotspot": (0.523, 0.5),
            "size": (24, 24),
            "aliases": ["openhand"]
        },

        "grabbing": {
            "build": True,
            "hotspot": (0.523, 0.5),
            "size": (24, 24),
            "aliases": ["closedhand"]
        },

        "beam": {
            "build": True,
            "skip_theming": True,
            "hotspot": (0.5, 0.5),
            "size": (24, 24),
            "aliases": ["text", "ibeam", "xterm"]
        },

        "vertical-text": {
            "build": True,
            "src_file": "hbeam",
            "skip_theming": True,
            "hotspot": (0.5, 0.5),
            "size": (24, 24),
            "aliases": ["vertical_text", "hbeam"]
        },

        "forbidden": {
            "build": True,
            "hotspot": (0.5, 0.5),
            "size": (24, 24),
            "aliases": ["not-allowed", "crossed_circle", "pirate", "x-cursor", "X_cursor", "unavailable"]
        },

        "move": {
            "build": True,
            "hotspot": (0.5, 0.5),
            "size": (24, 24),
            # Michiel intentionally merges all-scroll with move. I will respect this decision.
            "aliases": ["size_all", "all-scroll", "pointer-move", "fleur", "dnd-move"]
        },

        "precision": {
            "build": True,
            "skip_theming": True,
            # The gradients in this design are 1.2 Tiny compliant. <stop> is allowed in 1.2 Tiny
            # BIMI for some stupid reason doesn't allow <stop>, making gradients completely pointless.
            "skip_bimi": True,
            "hotspot": (0.5, 0.5),
            "size": (24, 24),
            "aliases": ["cross", "cross_reverse", "diamond_cross", "tcross", "crosshair"]
        },

        "help": {
            "build": True,
            "size": (32, 32),
            "aliases": ["question_arrow", "left_ptr_help", "whats_this", "dnd-ask", "5c6cd98b3f3ebcb1f9c7f1c204630408", "d9ce0ab605698f320427677b458ad60b"]
        },

        "alias": {
            "build": True,
            "src_file": "dnd-alias",
            "size": (32, 32),
            "aliases": ["dnd-alias", "DnD_alias", "link", "640fb0e74195791501fd1ed57b41487f", "a2a266d0498c3104214a47bd64ab0fc8", "3085a0e285430894940527032f8b26df"]
        },

        "copy": {
            "build": True,
            "src_file": "dnd-copy",
            "size": (32, 32),
            "aliases": ["dnd-copy", "DnD_copy", "1081e37283d90000800003c07f3ef6bf", "6407b0e94181790501fd1e167b474872", "b66166c04f8c3109214a4fbd64a50fc8"]
        },

        "nodrop": {
            "build": True,
            "src_file": "dnd-nodrop",
            "size": (32, 32),
            "aliases": ["dnd-no-drop", "dnd-nodrop", "DnD_nodrop", "no-drop"]
        },

        "context-menu": {
            "build": True,
            "size": (32, 32)
        },

        "zoom-in": {
            "build": True,
            "size": (24, 24)
        },

        "zoom-out": {
            "build": True,
            "size": (24, 24)
        },

        "pen": {
            "build": True,
            "size": (24, 24),
            "aliases": ["pencil"]
        },

        "cell": {
            "build": True,
            "size": (24, 24),
            "aliases": ["plus"]
        },

        "col-resize": {
            "build": True,
            "size": (24, 24),
            "aliases": ["col_resize"]
        },

        "row-resize": {
            "build": True,
            "size": (24, 24),
            "aliases": ["row_resize"]
        },

        "e-resize": {
            "build": True,
            "src_file": "resize-E",
            "size": (24, 24),
            "aliases": ["size_E"]
        },

        "n-resize": {
            "build": True,
            "src_file": "resize-N",
            "size": (24, 24),
            "aliases": ["size_N"]
        },

        "ne-resize": {
            "build": True,
            "src_file": "resize-Ne",
            "size": (24, 24),
            "aliases": ["size_Ne"]
        },

        "nw-resize": {
            "build": True,
            "src_file": "resize-Nw",
            "size": (24, 24),
            "aliases": ["size_Nw"]
        },

        "s-resize": {
            "build": True,
            "src_file": "resize-S",
            "size": (24, 24),
            "aliases": ["size_S"]
        },

        "se-resize": {
            "build": True,
            "src_file": "resize-Se",
            "size": (24, 24),
            "aliases": ["size_Se"],
        },

        "sw-resize": {
            "build": True,
            "src_file": "resize-Sw",
            "size": (24, 24),
            "aliases": ["size_Sw"]
        },

        "w-resize": {
            "build": True,
            "src_file": "resize-W",
            "size": (24, 24),
            "aliases": ["size_W"]
        },

        "ew-resize": {
            "build": True,
            "src_file": "resize-EW",
            "size": (24, 24),
            "aliases": ["split_v", "sb_v_double_arrow", "size_hor", "size-hor", "v_double_arrow", "size_EW"]
        },

        "nesw-resize": {
            "build": True,
            "src_file": "resize-NeSw",
            "size": (24, 24),
            "aliases": ["fb_double_arrow", "size_bdiag", "size_NeSw"]
        },

        "ns-resize": {
            "build": True,
            "src_file": "resize-NS",
            "size": (24, 24),
            "aliases": ["split_h", "h_double_arrow", "sb_h_double_arrow", "size_ver", "size-ver", "size_NS"]
        },

        "nwse-resize": {
            "build": True,
            "src_file": "resize-NwSe",
            "size": (24, 24),
            "aliases": ["size_fdiag", "size_NwSe"]
        },

        "right_ptr": {
            "build": True,
            "hotspot": (1, 0),
            "size": (24, 24)
        },

        "center_ptr": {
            "build": True,
            "hotspot": (0.5, 0),
            "size": (24, 24)
        },

        ### ANIMATED CURSORS
        # Build for animated cursors is always set to False, as animated cursors have custom building procedures.

        "wait": {
            "build": False,
            "skip_bimi": False, # If mono, this should be True
            "size": (24, 24),
            "aliases": ["half_busy", "left_ptr_watch", "background"],
            "total_frames": 75, # Mono is 22
            "animation_speed": 30
        },

        "progress": {
            "build": False,
            "skip_bimi": False, # If mono, this should be True
            "size": (32, 32),
            "aliases": ["watch"],
            "total_frames": 75, # Mono is 22
            "animation_speed": 30
        },

        ### ALTERNATIVE CURSORS

        "alt": {
            "build": False,
            "extra": True,
            "out_file": "default",
            "size": (24, 24),
            "aliases": ["arrow", "left_ptr"]
        },

        "wrong-finger": {
            "build": False,
            "extra": True,
            "out_file": "hand",
            "hotspot": (0.432, 0),
            "size": (24, 24),
            "aliases": ["pointer", "hand1", "hand2", "pointing_hand", "9d800788f1b08800ae810202380a0822", "e29285e634086352946a0e7090d73106"]
        },

        "beam-v2": {
            "build": False,
            "extra": True,
            "skip_theming": True,
            "out_file": "beam",
            "size": (24, 24),
            "aliases": ["text", "ibeam", "xterm"]
        },

        "precision-v2": {
            "build": False,
            "extra": True,
            "skip_theming": True,
            "out_file": "precision",
            "hotspot": (0.5, 0.5),
            "size": (24, 24),
            "aliases": ["cross", "cross_reverse", "diamond_cross", "tcross", "crosshair"]
        },

        "winhelp": {
            "build": False,
            "extra": True,
            "out_file": "help",
            "size": (32, 32),
            "aliases": ["question_arrow", "left_ptr_help", "whats_this", "dnd-ask", "5c6cd98b3f3ebcb1f9c7f1c204630408", "d9ce0ab605698f320427677b458ad60b"]
        },

        ### EXTRA CURSORS

        "social-person": {
            "build": False,
            "extra": True,
            "out_file": "person",
            "hotspot": (0.221, 0),
            "size": (32, 32)
        },

        "map-pin": {
            "build": False,
            "extra": True,
            "out_file": "pin",
            "hotspot": (0.221, 0),
            "size": (32, 32)
        }
    }
}