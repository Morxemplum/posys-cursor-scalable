import math

# In milliseconds
DURATION = 2500 # 715 for Mono (2/7 the duration)
# Higher will lead to smoother appearance, at cost of efficiency and file size
FRAME_RATE = 30
REVERSE = True # Posy's animation goes in the opposite direction of the gradient
CURSOR_NAME = "watch"
MONO = False

colors = [ "ff0030", # red
            "fea002", # orange
            "fffc00", # yellow
            "46f609", # green
            "00baff", # turquoise
            "0066ff", # blue
            "c000ff" # purple 
        ]
shades = [ "ffffff",
            "000000"
]

# Positions are in denominations of 7
def generate_positions():
    stops = []
    if MONO:
        for i in range(14):
            stops.append([shades[math.floor(i/2) % 2], math.ceil(i/2)/7])
    else:
        for i in range(14):
            stops.append([colors[math.floor(i/2)], math.ceil(i/2)/7])
    return stops

def generate_xml_stop(stop):
    color, position = stop
    return '''<stop
    style="stop-color:#{};stop-opacity:1;"
    offset="{}" />
    '''.format(color, position)

def transform_stops(stops, amount):
    transformed_stops = []
    for stop in stops:
        t_pos = stop[1] + amount
        while t_pos < 0:
            t_pos += 1
        while t_pos > 1:
            t_pos -= 1
        transformed_stops.append( [stop[0], t_pos] )
    return transformed_stops

def is_sorted(l):
    if len(l) < 2:
        return True
    for i in range(1, len(l)):
        prev = l[i-1][1]
        curr = l[i][1]
        if (prev > curr):
            return False
    return True

# In SVG, out of order stops will not be displayed. So we need to pop them back to the start
def pop_stops(stops):
    if is_sorted(stops):
        return
    index = -2
    previous = stops[-1][1]
    current = stops[-2][1]
    while (current <= previous and index > -len(stops)):
        stops.insert(0, stops.pop())
        previous = stops[-1][1]
        current = stops[-2][1]
        index -= 1
    previous = stops[0][1]
    current = stops[-1][1]
    if (current <= previous):
        stops.insert(0, stops.pop())

# Mono is a special case where the ends are the same color. We need to reapply the shades so there's no repeat
def reapply_shades(stops):
    count = 0
    flipped = False
    for i in range(len(stops) - 2, -1, -1):
        if (stops[i+1][0] == stops[i][0]):
            count += 1
        else:
            count = 0
        if (count > 1 or flipped):
            # Use XOR to flip the position
            stops[i][0] = shades[shades.index(stops[i][0]) ^ 1]
            flipped = True

# Unfortunately, with this programmable method, the gradient stops will have aliasing (stair-stepping) when rasterized 
# But by shifting one of the stops a very small amount, we can achieve anti-aliasing.
# (Should work well for the limited range we have. Only remove if you're making a REALLY big raster)
def fix_aliasing(stops):
    for i in range(1, len(stops) + 1, 2):
        stops[i][1] -= 0.001

def generate_frames(stops, total_frames, pre, post):
    for i in range(1, total_frames):
        print("Generating frame", i)
        t_amount = i/total_frames
        if MONO:
            t_amount *= (2/7)
        transformed = transform_stops(stops, t_amount)
        for stop in transformed:
            stop[1] = round(stop[1], 3)
        fix_aliasing(transformed)
        pop_stops(transformed)
        if MONO:
            reapply_shades(transformed)
        with open(CURSOR_NAME + "-" + str(i) + ".svg", "w") as f:
            for line in pre:
                f.write(line)
            for stop in transformed:
                f.write(generate_xml_stop(stop))
            for line in post:
                f.write(line)

# Helper function to find the "stop" XML tag to address an issue in background.svg, where the first linearGradient is not the one we're looking for
def find_stop(lines):
    for line in lines:
        if "<stop" in line:
            return True
    return False

def copy_svg_data(file_name):
    contents = []
    with open(file_name, "r") as f:
        contents = f.readlines()
    pre_stops = []
    post_stops = []
    gradient_found = False
    i = 0
    j = 0
    for line in contents:
        # Inkscape exports the Plain SVG by attaching an id for some reason, usually the line after
        if ("<linearGradient" in line and find_stop(contents[i:i+3])):
            gradient_found = True
            i += 1
            pre_stops = contents[:i + 1]
            # Inkscape is wildly inconsistent with its formatting, so we have to clear any garbage text
            pre_stops[-1] = pre_stops[-1][:(pre_stops[-1].find(">") + 1)] + "\n"
        if (gradient_found):
            if ("</linearGradient>" in line):
                post_stops = contents[j:]
                post_stops[0] = post_stops[0][(post_stops[0].find("<")):]
                return (pre_stops, post_stops)
        else:
            i += 1
        j += 1
    if (gradient_found):
        raise IOError("End of gradient expected, got EOF")
    else:
        raise Exception("No gradient is in the target SVG")

headers = {
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

def write_metadata(total_frames, delay):
    # We will insert milliseconds in between frames to make up for lost time and get closer to our declared duration
    denom = round(1/((1000 / FRAME_RATE) - delay), 4)
    ins_buffer = 1
    frame_list = range(1, total_frames)
    header = ""
    if REVERSE:
        frame_list = range(total_frames - 1, 0, -1)
    if (not CURSOR_NAME in headers):
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

def main():
    original = generate_positions()
    total_frames = math.ceil(DURATION * FRAME_RATE / 1000)
    delay = math.floor(1000 / FRAME_RATE)
    print("Frames to generate:", total_frames)
    print("Calculated delay:", delay)

    pre_stops, post_stops = copy_svg_data(CURSOR_NAME + ".svg")
    generate_frames(original, total_frames, pre_stops, post_stops)

    print("Writing to metadata file")
    write_metadata(total_frames, delay)

main()