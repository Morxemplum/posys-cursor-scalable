import math
import json
import subprocess
from copy import deepcopy
from collections import deque
from os import remove, rename

# In milliseconds
DURATION = 2500 # 715 for Mono (2/7 the duration)
# Higher will lead to smoother appearance, at cost of efficiency and file size
FRAME_RATE = 30
REVERSE = True # Posy's animation goes in the opposite direction of the gradient
CURSOR_NAME = "progress"
# MONO = False
ENVIRONMENT = "plasma"

colors = [  "c000ff", # purple 
            "0066ff", # blue
            "00baff", # turquoise
            "46f609", # green
            "fffc00", # yellow
            "fea002", # orange
            "ff0030" # red
        ]
shades = [ "ffffff",
            "000000"
]

segment_length = 3.43
hypotenuse = segment_length * 7

# In the progress template, the hourglass is significantly smaller and the measurements have to be adjusted
if CURSOR_NAME == "progress":
    hypotenuse = 10.67
    segment_length = hypotenuse / 7
    
hypr_headers = {
"watch":'''resize_algorithm = none
hotspot_x = 0
hotspot_y = 0
define_override = wait

''',
"background":'''resize_algorithm = none
hotspot_x = 0
hotspot_y = 0
define_override = half_busy
define_override = left_ptr_watch
define_override = progress

'''}

def generate_frames(total_frames):
    export_statements = ["export-plain-svg", "export-do", "file-close"]
    delimiter = ";"
    start = 1
    end = len(colors) + 2

    template = "hourglass-template.svg"
    if CURSOR_NAME == "progress":
        template = "background-template.svg"

    overflow = 0
    if REVERSE:
        start -= 1
        end -= 1
        overflow = 8
    
    begin_statements = [f"select-by-id:layer{overflow}", f"select-by-id:hourglass{overflow}", "delete"]

    for i in range(0, total_frames):
        print("Generating frame", i)
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
            statements.append(f"export-filename:{CURSOR_NAME}-{i}.svg")
        else:
            statements.append(f"export-filename:{CURSOR_NAME}.svg")
        statements += export_statements

        subprocess.run(["inkscape", f"--actions={delimiter.join(statements)}", template], check=True)

def write_metadata(total_frames, delay):
    # We will insert milliseconds in between frames to make up for lost time and get closer to our declared duration
    denom = round(1/((1000 / FRAME_RATE) - delay), 4)
    ins_buffer = 1
    frame_list = range(1, total_frames)
    header = ""
    if (ENVIRONMENT == "hyprland"):
        if (not CURSOR_NAME in hypr_headers):
            raise Exception("Invalid cursor. Make sure you have defined the header info")
        with open("meta.hl", "w") as f:
            f.write(headers[CURSOR_NAME])
            # Write reference SVG first
            f.write("define_size = 0, " + CURSOR_NAME + ".svg, " + str(delay) +"\n")
            for i in frame_list:
                final_delay = delay
                ins_buffer += 1
                if (ins_buffer >= denom):
                    ins_buffer -= denom
                    final_delay += 1
                f.write("define_size = 0, " + CURSOR_NAME + "-" + str(i) + ".svg, " + str(final_delay) +"\n")
    elif (ENVIRONMENT == "plasma"):
        frame_dict = {
            "filename": f"{CURSOR_NAME}.svg",
            "nominal_size": 24,
            "hotspot_x": 0,
            "hotspot_y": 0,
            "delay": delay
        }
        frames = [frame_dict]
        for i in frame_list:
            final_delay = delay
            ins_buffer += 1
            if (ins_buffer >= denom):
                ins_buffer -= denom
                final_delay += 1
            new_frame = deepcopy(frame_dict)
            new_frame["filename"] = f"{CURSOR_NAME}-{i}.svg"
            new_frame["delay"] = final_delay
            frames.append(new_frame)
        with open("metadata.json", "w") as f:
            f.write(json.dumps(frames))
        
def optimize_frames(total_frames):
    scour = ["scour", f"{CURSOR_NAME}.svg", f"{CURSOR_NAME}-o.svg", "--set-precision=4", 
    "--strip-xml-prolog", "--remove-titles", "--remove-description",
    "--remove-metadata", "--remove-descriptive-elements", 
    "--enable-comment-stripping", "--no-line-breaks", "--strip-xml-space", 
    "--enable-id-stripping", "--shorten-ids"]

    subprocess.run(scour, check=True)
    remove(f"{CURSOR_NAME}.svg")
    rename(f"{CURSOR_NAME}-o.svg", f"{CURSOR_NAME}.svg")

    for i in range(1, total_frames):
        scour[1] = f"{CURSOR_NAME}-{i}.svg"
        scour[2] = f"{CURSOR_NAME}-{i}o.svg"
        subprocess.run(scour, check=True)
        remove(f"{CURSOR_NAME}-{i}.svg")
        rename(f"{CURSOR_NAME}-{i}o.svg", f"{CURSOR_NAME}-{i}.svg")

def convert_to_svg_tiny(total_frames):
    SVGTINYPS_PATH = "../../svgtinyps"
    svgtinyps = [SVGTINYPS_PATH, "convert", f"{CURSOR_NAME}.svg", f"{CURSOR_NAME}-b.svg", "--title=\"Posy's Cursor\""]
    
    subprocess.run(svgtinyps, check=True)
    remove(f"{CURSOR_NAME}.svg")
    rename(f"{CURSOR_NAME}-b.svg", f"{CURSOR_NAME}.svg")

    for i in range(1, total_frames):
        svgtinyps[2] = f"{CURSOR_NAME}-{i}.svg"
        svgtinyps[3] = f"{CURSOR_NAME}-{i}b.svg"
        subprocess.run(svgtinyps, check=True)
        remove(f"{CURSOR_NAME}-{i}.svg")
        rename(f"{CURSOR_NAME}-{i}b.svg", f"{CURSOR_NAME}-{i}.svg")

def main():
    total_frames = math.ceil(DURATION * FRAME_RATE / 1000)
    delay = math.floor(1000 / FRAME_RATE)
    print("Frames to generate:", total_frames)
    print("Calculated delay:", delay)

    generate_frames(total_frames)
    
    print("Writing to metadata file")
    write_metadata(total_frames, delay)

    print("Optimizing SVG files")
    optimize_frames(total_frames)

    if (ENVIRONMENT == "plasma"):
        print("Converting frames to SVG Tiny 1.2 (BIMI P/S)")
        convert_to_svg_tiny(total_frames)

main()