import argparse
import math
import json
import subprocess
import sys
from copy import deepcopy
from collections import deque
from logging import debug
from os import remove, rename
from pathlib import Path

# The data module is in the parent directory, so we need to modify the path accordingly
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))
from cursors_data import KWinCursor, KWinAnimatedCursor

REVERSE = True # Posy's animation goes in the opposite direction of the gradient
subprocess_output = False
# Dict that directly names all hourglass cursors and maps their template SVG files
CURSORS = {
    "progress" : "background-template.svg", 
    "wait" : "hourglass-template.svg"
}
MONO_CURSORS = {
    "progress" : "background-mono-template.svg", 
    "wait" : "mono-template.svg"
}

class ArgConsts(argparse.Namespace):
    '''
    This class mainly exists to provide type definitions for the arguments
    provided by my argparse.
    '''
    duration: int # pyright: ignore[reportUninitializedInstanceVariable]
    frame_rate: int # pyright: ignore[reportUninitializedInstanceVariable]
    compositor: str # pyright: ignore[reportUninitializedInstanceVariable]
    mono: bool | None # pyright: ignore[reportUninitializedInstanceVariable]
    cursor: str | None # pyright: ignore[reportUninitializedInstanceVariable]

parser = argparse.ArgumentParser(description="Individual generation script for the hourglass animated cursors (wait & process)")
_ = parser.add_argument("duration", type=int, help="How long the animation of the cursor will last (in milliseconds)")
_ = parser.add_argument("frame_rate", type=int, help="How many frames will be made per second of animation. Delays will be calculated from this value.")
_ = parser.add_argument("compositor", type=str, help="The Wayland compositor that the cursors will be made for (hyprland, kwin)")
_ = parser.add_argument("--mono", action="store_true", help="If used, the monotone variants will be generated instead of the colorfuls")
_ = parser.add_argument("--cursor", type=str, help="Picks a specific hourglass cursor to generate. If not present, all cursors will be generated.")
args: ArgConsts = parser.parse_args(namespace=ArgConsts())

# TODO: Read cursor attributes directly from db?
def create_hyprland_metadata(cursor: str, frames: int, rate: int, delay: int):
    '''
    Writes metadata files for the cursors following the Hyprcursor metadata
    format.

    Parameters:
        cursor (str):
            The direct name of the cursor that correlates to a key in the
            database
        frames (int):
            The total number of frames present in the animation
        rate (int):
            The suggested frame rate of the cursor. Since delays only accept
            integers, we intentionally truncate the value and as a result, lose
            precision on our duration. By providing the frame rate, we
            calculate when to round up so the cursor is much closer to our
            intended duration.
        delay (int):
            The delay between each frame, in milliseconds
    '''
    num_digits = int(math.log10(frames) + 1)
    denom = round(1/((1000 / rate) - delay), 4)
    ins_buffer = 1
    frame_list = range(1, frames)
    with open(f"{cursor}/meta.hl", "w") as f:
        _ = f.write("resize_algorithm = none\n")
        _ = f.write("hotspot_x = 0\n")
        _ = f.write("hotspot_y = 0\n")
        match(cursor):
            case "progress":
                _ = f.write("define_override = watch\n")
            case "wait":
                _ = f.write("define_override = half_busy\n")
                _ = f.write("define_override = left_ptr_watch\n")
                _ = f.write("define_override = background\n")
            case _:
                pass
        # Write reference SVG
        _ = f.write(f"define_size = 0, {cursor}.svg, {delay}\n")
        for i in frame_list:
            fi = str(i).zfill(num_digits)
            final_delay = delay
            ins_buffer += 1
            if (ins_buffer >= denom):
                ins_buffer -= denom
                final_delay += 1
            _ = f.write(f"define_size = 0, {cursor}-{fi}.svg, {final_delay}\n")

def create_kwin_metadata(cursor: str, frames: int, rate: int, delay: int):
    '''
    Writes metadata files for the cursors following the KDE metadata format.

    Parameters:
        cursor (str):
            The direct name of the cursor that correlates to a key in the
            database
        frames (int):
            The total number of frames present in the animation
        rate (int):
            The suggested frame rate of the cursor. Since delays only accept
            integers, we intentionally truncate the value and as a result, lose
            precision on our duration. By providing the frame rate, we
            calculate when to round up so the cursor is much closer to our
            intended duration.
        delay (int):
            The delay between each frame, in milliseconds
    '''
    num_digits = int(math.log10(frames) + 1)
    denom = round(1/((1000 / rate) - delay), 4)
    ins_buffer = 1
    frame_list = range(1, frames)

    frame_dict: KWinCursor = {
        "filename": f"{cursor}.svg",
        "nominal_size": 24,
        "hotspot_x": 0,
        "hotspot_y": 0,
        "delay": delay
    }
    animated_cursor: KWinAnimatedCursor = {
        "frames": [frame_dict]
    }
    for i in frame_list:
        final_delay = delay
        ins_buffer += 1
        if (ins_buffer >= denom):
            ins_buffer -= denom
            final_delay += 1
        new_frame = deepcopy(frame_dict)
        new_frame["filename"] = f"{cursor}-{str(i).zfill(num_digits)}.svg"
        new_frame["delay"] = final_delay
        animated_cursor["frames"].append(new_frame)
    with open(f"{cursor}/metadata.json", "w") as f:
        _ = f.write(json.dumps(animated_cursor["frames"]))

colors = [  
    "c000ff", # purple 
    "0066ff", # blue
    "00baff", # turquoise
    "46f609", # green
    "fffc00", # yellow
    "fea002", # orange
    "ff0030" # red
]

def generate_frames(cursor: str, total_frames : int):
    '''
    Given a cursor, generates all of the individual frames that will make up
    the animation.

    Parameters:
        cursor (str):
            The direct name of the cursor that correlates to a key in the
            database
        total_frames (int):
            The total number of frames present in the animation
    '''
    export_statements = ["export-plain-svg", "export-do", "file-close"]
    delimiter = ";"
    num_digits = int(math.log10(total_frames) + 1)
    start = 1
    end = len(colors) + 2

    template = CURSORS[cursor]
    overflow = 0
    if REVERSE:
        start -= 1
        end -= 1
        overflow = 8

    segment_length: float
    hypotenuse: float
    match(cursor):
        case "progress":
            hypotenuse = 10.67
            segment_length = hypotenuse / 7
        case "wait":
            segment_length = 3.43
            hypotenuse = segment_length * 7
        case _:
            return
    
    begin_statements = [f"select-by-id:layer{overflow}", f"select-by-id:hourglass{overflow}", "delete"]

    for i in range(0, total_frames):
        debug(f"\t\tGenerating frame {str(i).zfill(num_digits)}")
        statements = deepcopy(begin_statements)
        t_amount = i/total_frames * hypotenuse
        
        # Recolor to appropriate areas
        if t_amount > segment_length:
            cycles = int(t_amount // segment_length)
            color_copy = deque(colors)
            if REVERSE:
                for _ in range(0, cycles):
                    color_copy.appendleft(color_copy.pop())
            else:
                for _ in range(0, cycles):
                    color_copy.append(color_copy.popleft())

            for j in range(1, len(color_copy) + 1):
                statements.append(f"select-by-id:layer{j}")
                statements.append(f"object-set-attribute: style, fill:#{color_copy[j - 1]}")
                statements.append(f"unselect-by-id:layer{j}")

            # Overflow layer will mirror the first/last color, depending on the direction.
            if REVERSE:
                statements.append("select-by-id:layer0")
                statements.append(f"object-set-attribute: style, fill:#{color_copy[-1]}")
                statements.append("unselect-by-id:layer0")
            else:
                statements.append("select-by-id:layer8")
                statements.append(f"object-set-attribute: style, fill:#{color_copy[0]}")
                statements.append("unselect-by-id:layer8")
    
        shift_amount = t_amount % segment_length
        # Translate by remainder
        for j in range(start, end):
            statements.append(f"select-by-id:layer{j}")
            if REVERSE:
                statements.append(f"transform-translate:{shift_amount},-{shift_amount}")
            else:
                statements.append(f"transform-translate:-{shift_amount},{shift_amount}")
            statements.append(f"unselect-by-id:layer{j}")

        # Perform intersections
        for j in range(start, end):
            statements.append(f"select-by-id:layer{j}")
            statements.append(f"select-by-id:hourglass{j}")
            statements.append("path-intersection")
            statements.append(f"unselect-by-id:layer{j}")

        if i > 0:
            statements.append(f"export-filename:./{cursor}/{cursor}-{str(i).zfill(num_digits)}.svg")
        else:
            statements.append(f"export-filename:./{cursor}/{cursor}.svg")
        statements += export_statements

        _ = subprocess.run(["inkscape", f"--actions={delimiter.join(statements)}", template], check=True, capture_output=(not subprocess_output))

def generate_frames_mono(cursor: str, total_frames: int):
    '''
    Given a cursor, generates all of the individual frames that will make up
    the animation. Similar to generate_frames, but this function has slightly
    tweaked procedures that fit the file structure and needs of the mono
    versions of the cursor.

    Parameters:
        cursor (str):
            The direct name of the cursor that correlates to a key in the
            database
        total_frames (int):
            The total number of frames present in the animation
    '''
    export_statements = ["export-plain-svg", "export-do", "file-close"]
    delimiter = ";"
    num_digits = int(math.log10(total_frames) + 1)
    start = 1
    k_start = start + 1
    end = 8

    template = MONO_CURSORS[cursor]

    overflow = 0
    if REVERSE:
        k_start = start - 1
        end -= 1
        overflow = 8
    
    segment_length: float
    hypotenuse: float
    match(cursor):
        case "progress":
            hypotenuse = 10.67
            segment_length = hypotenuse / 7
        case "wait":
            segment_length = 3.43
            hypotenuse = segment_length * 7
        case _:
            return

    begin_statements = [f"select-by-id:layer{overflow}", f"select-by-id:hourglass{overflow}", "delete"]
    mono_hypotenuse = hypotenuse * (2/7)

    for i in range(0, total_frames):
        debug(f"\t\tGenerating frame {str(i).zfill(num_digits)}")
        statements = deepcopy(begin_statements)
        t_amount = i/total_frames * mono_hypotenuse

        cull_layers = range(start, end + 1, 2)
        keep_layers = range(k_start, end + 1, 2)

        # Detemine the layers to be culled
        if t_amount >= segment_length:
            cull_layers, keep_layers = keep_layers, cull_layers
        
        # Cull the extra layers
        for j in cull_layers:
            statements.append(f"select-by-id:layer{j}")
            statements.append(f"select-by-id:hourglass{j}")
            statements.append("delete")
        
        shift_amount = t_amount % segment_length
        # Translate by remainder
        for j in keep_layers:
            statements.append(f"select-by-id:layer{j}")
            if REVERSE:
                statements.append(f"transform-translate:{shift_amount},-{shift_amount}")
            else:
                statements.append(f"transform-translate:-{shift_amount},{shift_amount}")
            statements.append(f"unselect-by-id:layer{j}")

        # Perform intersections
        for j in keep_layers:
            statements.append(f"select-by-id:layer{j}")
            statements.append(f"select-by-id:hourglass{j}")
            statements.append("path-intersection")
            statements.append(f"unselect-by-id:layer{j}")

        # When performing in Reverse, Inkscape-CLI has a bug where the layer0 intersection will move the layer below hourglass_fill, making the intersection not visible
        # I can not reproduce this issue in the GUI. Performing the intersection in the GUI will keep the resulting layer above hourglass_fill
        # To get around this, we're going to manually select hourglass_fill and push it to the bottom of the stack.
        if REVERSE:
            statements.append("select-by-id:hourglass_fill")    
            statements.append("selection-bottom")
        
        if i > 0:
            statements.append(f"export-filename:./{cursor}/{cursor}-{str(i).zfill(num_digits)}.svg")
        else:
            statements.append(f"export-filename:./{cursor}/{cursor}.svg")
        statements += export_statements

        _ = subprocess.run(["inkscape", f"--actions={delimiter.join(statements)}", template], check=True, capture_output=(not subprocess_output))
        
def optimize_frames(cursor: str, total_frames: int):
    '''
    Takes all of the Plain SVGs and optimizes them using the Scour program.
    Applies aggressive optimizations to try and ensure the lowest file size
    possible.

    Parameters:
        cursor (str):
            The direct name of the cursor that correlates to a key in the
            database
        frames (int):
            The total number of frames present in the animation
    '''
    num_digits = int(math.log10(total_frames) + 1)
    scour = ["scour", f"./{cursor}/{cursor}.svg", f"./{cursor}/{cursor}-o.svg", "--set-precision=4", 
    "--strip-xml-prolog", "--remove-titles", "--remove-description",
    "--remove-metadata", "--remove-descriptive-elements", 
    "--enable-comment-stripping", "--no-line-breaks", "--strip-xml-space", 
    "--enable-id-stripping", "--shorten-ids"]

    _ = subprocess.run(scour, check=True, capture_output=(not subprocess_output))
    remove(f"./{cursor}/{cursor}.svg")
    rename(f"./{cursor}/{cursor}-o.svg", f"./{cursor}/{cursor}.svg")

    for i in range(1, total_frames):
        fi = str(i).zfill(num_digits)
        scour[1] = f"./{cursor}/{cursor}-{fi}.svg"
        scour[2] = f"./{cursor}/{cursor}-{fi}o.svg"
        _ = subprocess.run(scour, check=True, capture_output=(not subprocess_output))
        remove(f"./{cursor}/{cursor}-{fi}.svg")
        rename(f"./{cursor}/{cursor}-{fi}o.svg", f"./{cursor}/{cursor}-{fi}.svg")

def generate_cursor(cursor: str, total_frames: int, rate: int):
    '''
    Given the cursor name, total number of frames, and the suggested frame 
    rate, procedures will be run to generate the animated cursor, all the way
    up to optimizing the SVG file size.

    Parameters:
        cursor (str):
            The direct name of the cursor that correlates to a key in the
            database
        total_frames (int):
            The total number of frames present in the animation
        rate (int):
            The suggested frame rate of the cursor, in frames per second.
    '''
    if args.mono:
        generate_frames_mono(cursor, total_frames)
    else:
        generate_frames(cursor, total_frames)

    debug("\tWriting to metadata file")
    delay: int = math.floor(1000 / rate)
    match(args.compositor):
        case "hyprland":    
            create_hyprland_metadata(cursor, total_frames, rate, delay)
        case "kwin":
            create_kwin_metadata(cursor, total_frames, rate, delay)
        case _:
            pass
    debug("\tOptimizing SVG files")
    
    optimize_frames(cursor, total_frames)

def main():
    '''
    WARNING: This function only runs when someone wants to run this script 
    standalone. The main build script doesn't call this function!
    '''
    total_frames: int = math.ceil(args.duration * args.frame_rate / 1000)
    
    print("Frames to generate:", total_frames)

    if args.cursor:
        if args.cursor in CURSORS:
            print(f"Generating selected cursor")
            generate_cursor(args.cursor, total_frames, args.frame_rate)
        else:
            print("ERROR: Invalid cursor name. Accepted values are: wait, progress.")
    else: 
        for cursor in CURSORS.keys():
            print(f"Generating {cursor}")
            generate_cursor(cursor, total_frames, args.frame_rate)

if __name__ == "__main__":
    main()