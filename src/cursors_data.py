'''
This module holds all the metadata regarding various cursor designs that can be
easily read for my scripts, by not bothering with a cross-language data format
and just storing the data as direct Python structures.

These structures should have all the information needed to construct metadata
files for all the cursor designs for various compositors.
'''

from ast import alias
import enum
from typing import NotRequired, TypedDict

class KWinCursor(TypedDict):
    filename: str
    nominal_size: int
    hotspot_x: float
    hotspot_y: float
    delay: NotRequired[int]

class KWinAnimatedCursor(TypedDict):
    frames: list[KWinCursor]

class CursorDesign(TypedDict):
    src_file: NotRequired[str]
    out_file: NotRequired[str]
    aliases: NotRequired[list[str]]

    hotspot: NotRequired[tuple[float, float]]
    size: tuple[int, int]
    build: bool
    skip_bimi: NotRequired[bool]

    total_frames: NotRequired[int]
    animation_speed: NotRequired[int]

class CursorManifest(TypedDict):
    name: str
    tags: list[str]
    description: str
    authors: list[str]
    version: str

class ThemeColor(enum.IntEnum):
    WHITE = 0
    BLACK = 1
    MONO = 2
    MONO_BLACK = 3

class Compositor(enum.Enum):
    UNSUPPORTED = ""
    HYPRLAND = "hyprland"
    KWIN = "plasma"

class CursorCollection(TypedDict):
    manifest: CursorManifest
    cursors: dict[str, CursorDesign]
    theme: ThemeColor

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
            "hotspot": (0.5, 0.5),
            "size": (24, 24),
            "aliases": ["text", "ibeam", "xterm"]
        },

        "vertical-text": {
            "build": True,
            "src_file": "hbeam",
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

        ### ALTERNATIVE CURSORS

        "alt": {
            "build": False,
            "out_file": "default",
            "size": (24, 24),
            "aliases": ["arrow", "left_ptr"]
        },

        "wrong-finger": {
            "build": False,
            "out_file": "hand",
            "hotspot": (0.432, 0),
            "size": (24, 24),
            "aliases": ["pointer", "hand1", "hand2", "pointing_hand", "9d800788f1b08800ae810202380a0822", "e29285e634086352946a0e7090d73106"]
        },

        "beam-v2": {
            "build": False,
            "out_file": "beam",
            "size": (24, 24),
            "aliases": ["text", "ibeam", "xterm"]
        },

        "precision-v2": {
            "build": False,
            "out_file": "precision",
            "hotspot": (0.5, 0.5),
            "size": (24, 24),
            "aliases": ["cross", "cross_reverse", "diamond_cross", "tcross", "crosshair"]
        },

        "winhelp": {
            "build": False,
            "out_file": "help",
            "size": (32, 32),
            "aliases": ["question_arrow", "left_ptr_help", "whats_this", "dnd-ask", "5c6cd98b3f3ebcb1f9c7f1c204630408", "d9ce0ab605698f320427677b458ad60b"]
        },

        # TODO: As part of theming, skin tones will be integrated directly in the original designs where they apply

        ### EXTRA CURSORS

        "person": {
            "build": False,
            "hotspot": (0.253, 0),
            "size": (32, 32)
        },

        "pin": {
            "build": False,
            "hotspot": (0.253, 0),
            "size": (32, 32)
        }
    }
}