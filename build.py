import argparse
import enum
from logging import INFO, DEBUG
from pathlib import Path
import json
import math
import os
import re
import shutil
import subprocess

import src.animated.hourglasses as hourglasses
from src.cursors_data import CursorManifest, KWinCursor, Compositor, CursorDesign, ThemeColor, ThemePalette, get_theme_palette, db
from src.format import Color8, Formats, TextFormat, init_logger

log_level = INFO
# If true, the program will continue running even if errors were produced by 
# any processes run. DO NOT SET TO TRUE UNLESS YOU KNOW WHAT YOU'RE DOING!
OVERRIDE_PROC_ERRORS: bool = False
procedure_cnt: int = 1
num_cursors: int = 0
NUM_ANIMATED_CURSORS = 2

class ArgConsts(argparse.Namespace):
    '''
    This class mainly exists to provide type definitions for the arguments
    provided by my argparse.
    '''
    compositor: str # pyright: ignore[reportUninitializedInstanceVariable]
    theme: str # pyright: ignore[reportUninitializedInstanceVariable]
    extras: list[str] # pyright: ignore[reportUninitializedInstanceVariable]
    tone: str # pyright: ignore[reportUninitializedInstanceVariable]
    skip_optional_prompts: bool # pyright: ignore[reportUninitializedInstanceVariable]
    install: bool # pyright: ignore[reportUninitializedInstanceVariable]
    debug: bool # pyright: ignore[reportUninitializedInstanceVariable]

class ConfirmationDefault(enum.IntEnum):
    '''
    Useful enum to have to intuitively understand values for Yes/No prompts
    '''
    NONE = 0
    YES = 1
    NO = 2

def print_procedure(s : str, current: int = 0, total: int = 0, newline: bool = True):
    '''
    Prefab print statement that applies text formatting that communicates
    program procedures, with an optional way to display progress through 
    numbers.

    If progress is used, the message will not show up in debug mode, as debug 
    mode provides more detailed insights.

    Parameters:
        s (str):
            The string that will be printed to the console
        current (int, Optional):
            A part of a progress bar that shows the current progress of the 
            task
        total (int, Optional):
            A part of the progress bar that shows how much the task needs to
            be performed before it is done. By default, this value is set to 0,
            which disables showing progress in the final print statement.
        newline (bool, Optional):
            After finishing the print statement, move to the next line if set 
            to True (which is the default value).
    '''
    fs: str = Formats.rich_txt(TextFormat.BOLD) + s
    if total > 0:
        if log_level == DEBUG:
            return
        fs += Formats.rich_txt(Color8.CYAN) + f" [{current}/{total}]"
    fs += Formats.RESET
    print(fs, end="\n" if newline else "")

def confirmation_prompt(prompt: str, default: ConfirmationDefault = ConfirmationDefault.NO) -> bool:
    '''
    A specific type of user prompt where the user must type "y" for yes or "n"
    for no.

    Parameters:
        prompt: The string of the prompt of which will be displayed to the user
        default: If the user chooses to not provide an answer, this answer will be
                 chosen by default. NONE means the user must provide an answer
    
    Returns:
        A boolean that reflects the user's decision.
    '''
    while True:
        answer = input(f"{prompt} [{"Y" if default == ConfirmationDefault.YES else "y"}/{"N" if default == ConfirmationDefault.NO else "n"}]: ").lower()
        match(answer):
            case "y":
                return True
            case "n":
                return False
            case _:
                if len(answer) == 0 or answer.isspace():
                    match(default):
                        case ConfirmationDefault.YES:
                            return True
                        case ConfirmationDefault.NO:
                            return False
                        case _:
                            error("\nThis prompt requires an answer!")
                else:
                    error("\nInvalid answer!")

def select_prompt(prompt: str, option_labels: list[str], default: int | None = None) -> int:
    '''
    A specific type of user prompt where a list of options are given, and user
    must give a numeric answer to indicate their selection.

    Parameters:
        prompt: 
            The string of the prompt of which will be displayed to the user
        option_labels: 
            The string labels that will be displayed next to their numbers for
            easier reading.
        default (Optional):
            If given, this will be the value returned when the user chooses to
            not offer an answer.
    Returns:
        The option selected by the user (or the default option, if one is given)
    '''
    while True:
        print(prompt)
        print()
        for i, label in enumerate(option_labels):
            print(f"{i + 1}. {label}")
        print()
        answer: str = input("Select your option: ")
        if (len(answer) == 0 or answer.isspace()):
            if default:
                return default
            else:
                error("An answer must be provided")
                continue
        if not answer.isnumeric():
            error(f"Insufficient answer \"{answer}\" (Answer must be numeric)")
            continue
        selection: int = int(answer)
        if selection <= 0 or selection > len(option_labels):
            error(f"Insufficient answer \"{selection}\" (Out of range)")
            continue
        return selection

def multiselect_prompt(prompt: str, option_labels: list[str]) -> set[int]:
    '''
    A specific type of user prompt where a list of options are given, and user
    is given fine-grain control on how they want to select their options, with
    a selection scheme similar to Yet Another Yogurt (yay).

    Unlike a regular selection prompt, this prompt allows for multiple choices
    to be selected, or even no options.

    Parameters:
        prompt: 
            The string of the prompt of which will be displayed to the user
        option_labels: 
            The string labels that will be displayed next to their numbers for
            easier reading.
    
    Returns:
        A set of the options selected by the user
    '''
    while True:
        print(prompt)
        print()
        for i, label in enumerate(option_labels):
            print(f"{i + 1}. {label}")
        print()
        # TODO: Support exclusion? (e.g. "^3", everything except 3)
        print("Select your options: (eg: \"1 2 3\", \"1-3\")")
        print("Or, simply press Enter to select no options.")
        answer: str = input("> ")
        if len(answer) == 0 or answer.isspace():
            break
        items: list[str] = answer.split(" ")
        options: set[int] = set[int]()
        errors: int = 0
        for item in items:
            if item.isnumeric():
                option: int = int(item)
                if option > len(option_labels) or option <= 0:
                    error(f"Insufficient answer \"{option}\" (Out of range)")
                    errors += 1
                else:
                    options.add(option)
                continue
            
            if isinstance(re.search("[a-zA-Z]", item), re.Match):
                error(f"Insufficient answer \"{item}\" (Contains letters)")
                errors += 1
                continue

            if isinstance(re.search(r"^\d+-\d+$", item), re.Match):
                start, end = item.split("-")
                s: int = int(start)
                e: int = int(end)
                if s > e:
                    error(f"Insufficient answer \"{item}\" (Bad range: start > end)")
                    errors += 1
                    continue
                for i in range(s, e + 1):
                    options.add(i)
                continue

            error(f"Insufficient option \"{item}\". Please check your formatting and try again.")
            errors += 1
        if errors > 0:
            continue
        return options

    return set()

def dependency_check():
    '''
    Function that goes over all of the dependencies needed by the program. Any
    missing dependencies should immediately error and terminate the program.
    '''
    inkscape: str | None = shutil.which("inkscape")
    if not inkscape:
        raise OSError("Inkscape not installed")
    scour: str | None = shutil.which("scour")
    if not scour:
        raise OSError("Scour not installed")

def bimi_dependency_check():
    '''
    If the user is planning on making a theme for KDE Plasma (KWin), an
    additional dependency check needs to be run to ensure that the program
    needed to make SVGs Qt compatible is installed.

    Considering most users are not going to have this program installed, it's
    better that we ask the user if we want to install the program locally on
    their behalf.
    '''
    svgtinyps: str | None = "./svgtinyps" if os.path.exists("./svgtinyps") else None
    if svgtinyps:
        return
    print("KDE Plasma (KWin) themes require an additional dependency to ensure SVGs are compatible with Qt.")
    print("\"svgtinyps\" can not be found in the directory.")
    print("If you made your own installation, please ensure that the program name is stripped down to \"svgtinyps\".\n")
    install_svgtinyps: bool = confirmation_prompt("Install \"svgtinyps\" for the current user? (Requires curl)", ConfirmationDefault.YES)
    if not install_svgtinyps:
        raise OSError("Unable to create KWin theme (missing svgtinyps dependency)")
    curl: str | None = shutil.which("curl")
    if not curl:
        raise OSError("curl not installed")
    result = subprocess.run(["curl", "-L", "https://github.com/SRWieZ/svgtinyps-cli/releases/download/v1.4.0/svgtinyps-linux-x86_64", "-o", "./svgtinyps"])
    # If an error occurs in installing svgtinyps, error out of the program
    try:
        result.check_returncode()
    except subprocess.CalledProcessError:
        error("An error has occurred while trying to install svgtinyps!")
        error(result.stderr)
        exit(1)
    else:
        info("svgtinyps has been installed successfully!")
        # Mark the newly installed program as runnable
        _ = subprocess.run(["chmod", "a+x", "./svgtinyps"])

def is_animated(cursor: CursorDesign) -> bool:
    '''
    Checks if the cursor implements the two attributes needed for it to be an
    animated cursor.

    cursor (CursorDesign):
        The cursor to assess
    
    Return:
        Whether the cursor has the metadata to suggest it is animated
    '''
    return ("total_frames" in cursor) and ("animation_speed" in cursor)

def format_title_tags() -> str:
    '''
    Observes all of the tags within the database and uses them to format a
    string that will be inserted into the title of the theme's manifest file.

    When somebody views the theme in a GUI theming / settings manager, they 
    will get a very concise description of what type of cursor theme it is, so
    if multiple variants of the same theme are installed, they can 
    differentiate them.

    Returns:
        A formatted string that outlines the important descriptors of the
        cursor theme.
    '''
    title_tags: list[str] = []
    tags = db["manifest"]["tags"]

    # First, check the color / variant of the theme. If it is anything other than white, specify it.
    if db["theme"] != ThemeColor.WHITE:
        match(db["theme"]):
            case ThemeColor.BLACK:
                title_tags.append("Black")
            case ThemeColor.MONO:
                title_tags.append("Mono")
            case ThemeColor.MONO_BLACK:
                title_tags.append("Mono Black")
    
    if (len(tags) == 0 and len(title_tags) == 0):
        return ""
    
    # For extra cursors, there is a specific order we want to go in and only certain extras are worthy of distinction
    
    # The first extra is the skin tone cursors.
    # They override the overall color / variant on the hand cursors, so they should be specified.
    if ("tone_light" in tags) or ("tone_medium" in tags) or ("tone_dark" in tags):
        title_tags.append("Skinned")

    # The second extra is the refreshed (V2) cursor designs. 
    # Michiel de Boer (Posy) later on made a revisit to some of his old cursors and made changes to their designs.
    # However, he classifies his redesigns as extras and not standard, so it might be best to specify if themes
    # use the refreshed designs.
    if "v2" in tags:
        title_tags.append("Refreshed")

    return f"[{", ".join(title_tags)}]"

def describe_modifications() -> str:
    '''
    Observes all of the tags within the database and uses them to format a
    string that will be inserted into the description of the theme's manifest
    file.

    Similar to format_title_tags, this is meant to inform users who are viewing
    the theme in a GUI theming / settings manager. Unlike that function, this
    function is more exhaustive on stating how the theme was modified.

    Returns:
        A formatted string that outlines how the cursor theme has been
        modified.
    '''
    modifications: list[str] = []
    tags = db["manifest"]["tags"]
    fulltext_theme = "white"
    
    if db["theme"] != ThemeColor.WHITE:
        match(db["theme"]):
            case ThemeColor.BLACK:
                fulltext_theme = "black"
            case ThemeColor.MONO:
                fulltext_theme = "mono"
            case ThemeColor.MONO_BLACK:
                fulltext_theme = "mono black"
    
    if len(tags) == 0:
        return f"This is the {fulltext_theme} variant of the theme."
    
    if "v2" in tags:
        modifications.append("Posy's refreshed (V2) designs")
    
    if "tone_light" in tags:
        modifications.append("Light skin tones")
    elif "tone_medium" in tags:
        modifications.append("Medium skin tones")
    elif "tone_dark" in tags:
        modifications.append("Dark skin tones")

    if "colored_help" in tags:
        modifications.append("Colored help cursor")
    
    if "wrong_finger" in tags:
        modifications.append("Wrong finger click")

    if "xerox" in tags:
        modifications.append("Alternative default cursor (Early Xerox)")
    
    if "social" in tags:
        modifications.append("Additional social cursors")

    return f"This is the {fulltext_theme} variant of the theme. This theme has been modified from the original to include the following: {", ".join(modifications)}."

def create_hyprland_metadata(directory: str, cursor: str):
    '''
    Writes a metadata file for a cursor following the Hyprcursor metadata
    format.

    Parameters:
        directory (str):
            The file path to the directory of our scalable cursor
        cursor (str):
            The direct name of the cursor that correlates to a key in the
            database
    '''
    data: CursorDesign = db['cursors'][cursor]
    with open(f"{directory}/meta.hl", "w") as f:
        # We link to the cursor file through defining size
        _ = f.write(f"define_size = 0, {data.get("out_file", cursor)}.svg\n")

        # With hyprcursor, this is a vector-only theme. We don't care about resize algorithm
        _ = f.write("resize_algorithm = none\n")

        # Write hotspot values
        hotspot: tuple[float, float] = data.get("hotspot", (0, 0))
        _ = f.write(f"hotspot_x = {hotspot[0]}\n")
        _ = f.write(f"hotspot_y = {hotspot[1]}\n\n")

        # Write out all of the cursor's aliases
        aliases: list[str] = data.get("aliases", [])
        for alias in aliases:
            _ = f.write(f"define_override = {alias}\n")

def create_hyprland_manifest():
    '''
    Writes the theme manifest following the Hyprcursor manifest format.
    '''
    manifest: CursorManifest = db["manifest"]
    with open("./build/hyprland/manifest.hl", "w") as f:
        _ = f.write(f"name = {manifest.get("name")} {format_title_tags()}\n")
        _ = f.write(f"description = {manifest.get("description")} {describe_modifications()}\n")
        _ = f.write(f"author = {", ".join(manifest.get("authors"))}\n")
        _ = f.write(f"version = {manifest.get("version")}\n")
        _ = f.write("cursors_directory = hyprcursors\n")

def create_kwin_metadata(directory: str, cursor: str):
    '''
    Writes a metadata file for a cursor following the KDE metadata format.

    Parameters:
        directory (str):
            The file path to the directory of our scalable cursor
        cursor (str):
            The direct name of the cursor that correlates to a key in the
            database
    '''
    data: CursorDesign = db["cursors"][cursor]
    nominal_size: int = db["nominal_size"]
    hotspot: tuple[float, float] = data.get("hotspot", (0, 0))
    # Translate our data into a dictionary following JSON and KDE's formatting
    staging: KWinCursor = {
        "filename": f"{data.get("out_file", cursor)}.svg",
        "nominal_size": nominal_size,
        "hotspot_x": round(hotspot[0] * nominal_size, 2),
        "hotspot_y": round(hotspot[1] * nominal_size, 2),
    }
    with open(f"{directory}/metadata.json", "w") as f:
        json.dump([staging], f)

def create_kwin_manifest():
    '''
    Writes the theme manifest following the KDE theming format.
    '''
    manifest: CursorManifest = db["manifest"]
    with open("./build/plasma/index.theme", "w") as f:
        _ = f.write(f"[Icon Theme]\n")
        _ = f.write(f"Name={manifest.get("name")} {format_title_tags()}\n")
        _ = f.write(f"Comment={manifest.get("description")} Version {manifest.get("version")}. Created by {", ".join(manifest.get("authors"))}. {describe_modifications()}\n")

def create_metadata_file(compositor: Compositor, directory: str, cursor: str):
    '''
    General function that will create the metadata file for a cursor
    '''
    match(compositor):
        case Compositor.HYPRLAND:
            create_hyprland_metadata(directory, cursor)
        case Compositor.KWIN:
            create_kwin_metadata(directory, cursor)
        case _:
            raise Exception("No compositor mentioned or the compositor is unsupported")

def count_buildable_cursors() -> int:
    '''
    Counts how many cursors in the database are buildable. Animated cursors are
    excluded from this count.

    Returns:
        The total number of buildable cursors (excluding animated cursors)
    '''
    count = 0
    for _, cursor in db["cursors"].items():
        if cursor["build"]:
            count += 1
    return count

def setup_theme_directories(theme_dir: str, compositor: Compositor):
    '''
    Compositors will have their own way of structuring their themes. This
    function creates all of the prerequisite folders to establish theme
    structure.

    Parameters:
        theme_dir (str):
            The file path to the folder that will be holding our cursor theme
        compositor (Compositor enum):
            The compositor for which the theme will be structured around
    '''
    match(compositor):
        case Compositor.HYPRLAND:
            os.makedirs(f"{theme_dir}/hyprcursors", exist_ok=True)
        case Compositor.KWIN:
            os.makedirs(f"{theme_dir}/cursors", exist_ok=True)
            os.makedirs(f"{theme_dir}/cursors_scalable", exist_ok=True)
        case _:
            pass

def create_cursor_metadatas(theme_dir: str, compositor: Compositor):
    '''
    Creates all of the metadata files for the cursors that will be built with
    the theme.

    Parameters:
        theme_dir (str):
            The file path to the folder that will be holding our cursor theme
        compositor (Compositor enum):
            The compositor for which the theme is structured around
    '''
    count: int = 1
    for name, cursor in db["cursors"].items():
        if not cursor["build"]:
            continue
        fin_name: str = cursor.get("out_file", name)
        output_dir: str
        match(compositor):
            case Compositor.HYPRLAND:
                output_dir = f"{theme_dir}/hyprcursors/{fin_name}"
            case Compositor.KWIN:
                output_dir = f"{theme_dir}/cursors_scalable/{fin_name}"
            case _:
                output_dir = f"{theme_dir}/{fin_name}"
        
        if (log_level != DEBUG):
            print_procedure(Formats.clear_line() +
            f"{procedure_cnt}. Generating metadata files for static cursors", count, num_cursors, False)
        debug(f"Generating metadata for {name}")

        os.makedirs(output_dir, exist_ok=True)
        create_metadata_file(compositor, output_dir, name)
        count += 1
    if (log_level != DEBUG):
        print()

def query_svg(source_path: str) -> list[str]:
    '''
    Using the query-all flag, fetches and filters a list of all the object IDs
    within a source SVG through the usage of inkscape. The header SVG object is
    filtered immediately, along with layers that start with "GROUP" and "NOOP",
    leaving with IDs that suggest that they link to paths.

    Parameters:
        source_path (str):
            The full relative path and file name of the template SVG (with 
            extension)

    Returns:
        A list of all the names of path layer IDs in the SVGs.
    '''
    results = subprocess.run(["inkscape", "--query-all", source_path], capture_output=True)
    
    raw_lines = results.stdout.decode("utf-8").splitlines()
    ids: list[str] = []
    for i in range(1, len(raw_lines)):
        line = raw_lines[i]
        if line.startswith("GROUP") or line.startswith("NOOP"):
            continue
        elements = line.split(",")
        if len(elements) == 0:
            continue
        ids.append(elements[0])
    return ids

def invert_color(c: str) -> str:
    '''
    Given an input RGB color (in hexadecimal format), inverts the color to an
    output color 

    Parameters:
        c (str):
            The input color string (in hexadecimal RGB)
    
    Returns:
        An RGB color in hexadecimal, inverted
    '''
    r = int(c[0:2], base=16)
    g = int(c[2:4], base=16)
    b = int(c[4:], base=16)

    r = 255 - r
    g = 255 - g
    b = 255 - b

    return f"#{hex(b + (g << 8) + (r << 16))[2:]}"

def theme_layer(id: str, palette: ThemePalette) -> list[str]:
    '''
    Observes the formatted ID name of a layer and creates the Inkscape actions
    that would modify the layer to match the theme's palette.

    Parameters:
        id (str):
            The full ID of the layer named in the SVG to apply theming to. ID
            must follow a specific format for the theming to work.
        palette (ThemePalette):
            The color palette that reflects the cursor's theme wanted
    
    Returns:
        A sequential list of Inkscape actions that, when ran, will change the
        layer to reflect the colors in the palette
    '''
    components = id.split(".")
    # Required elements are missing for theming to properly apply
    if len(components) < 3:
        print(f"Error: Required elements are missing to apply theming on layer {id}")
        return []

    fill = components[1]
    fill_c = ""
    stroke = components[2]
    stroke_c = ""
    actions: list[str] = [f"select-by-id:{id}"]

    debug(f"\tUID: {components[0]}, FILL: {fill}, STROKE: {stroke}")

    optionals: list[str] = []
    if len(components) > 3:
        optionals = components[3:]
        if (log_level == DEBUG):
            fulltext_optionals: list[str] = []
            if "sk" in optionals:
                if "tone" in palette:
                    fulltext_optionals.append("Skinned (Enabled)")
                else:
                    fulltext_optionals.append("Skinned (Disabled)")
            if "fmi" in optionals:
                fulltext_optionals.append("Fill mono inverse")
            if "smi" in optionals:
                fulltext_optionals.append("Stroke mono inverse")
            debug(f"\t\tOPTIONALS: {", ".join(fulltext_optionals)}")
    
    if ("sk" in optionals and "tone" in palette):
        fill_c = palette["tone"]
    elif (not "fmi" in optionals):
        match(fill):
            case "p":
                fill_c = palette["primary"]
            case "s":
                fill_c = palette["secondary"]
            case "t":
                fill_c = "none"
            case "mb":
                if palette["mono"]:
                    fill_c = "#000000"
            case "mw":
                if palette["mono"]:
                    fill_c = "#ffffff"
            case text if re.match(r"o\d+$", text):
                index = int(fill[1:]) - 1
                fill_c = palette["overrides"][index]
            case _:
                pass

    if not ("smi" in optionals and palette["mono"]):
        match(stroke):
            case "p":
                stroke_c = palette["primary"]
            case "s":
                stroke_c = palette["secondary"]
            case "t":
                stroke_c = "none"
            case "mb":
                if palette["mono"]:
                    stroke_c = "#000000"
            case "mw":
                if palette["mono"]:
                    stroke_c = "#ffffff"
            case text if re.match(r"o\d+$", text):
                index = int(stroke[1:])
                stroke_c = palette["overrides"][index]
            case _:
                pass
    else:
        stroke_c = invert_color(fill_c[1:])
    
    if ("fmi" in optionals and len(fill_c) == 0 and palette["mono"]):
        fill_c = invert_color(stroke_c[1:])
    
    if len(fill_c) > 0:
        actions.append(f"object-set-property:fill, {fill_c}")
    
    if len(stroke_c) > 0:
        actions.append(f"object-set-property:stroke, {stroke_c}")

    actions.append(f"unselect-by-id:{id}")
    return actions

def create_plain_svgs(theme_dir: str, compositor: Compositor):
    '''
    Creates all of the Plain SVGs from the Inkscape/Source SVGs, stripping
    Inkscape data and applying theming to the user's preference.

    Parameters:
        theme_dir (str):
            The file path to the folder that will be holding our cursor theme
        compositor (Compositor enum):
            The compositor for which the theme is structured around
    '''
    err: bool = False
    palette = get_theme_palette(db["theme"])
    # Surely there's a cleaner way to write this?
    has_tone: bool = ("tone_light" in db["manifest"]["tags"]) or \
                ("tone_medium" in db["manifest"]["tags"]) or \
                ("tone_dark" in db["manifest"]["tags"])
    if has_tone:
        palette["tone"] = "#eed9ca" if "tone_light" in db["manifest"]["tags"] else \
                        "#caae99" if "tone_medium" in db["manifest"]["tags"] else \
                        "#906545" if "tone_dark" in db["manifest"]["tags"] else "#000000"
    
    debug("Retrieved Palette")
    debug(f"\tPRIMARY: {palette["primary"]}")
    debug(f"\tSECONDARY: {palette["secondary"]}")
    debug(f"\tMONO: {palette["mono"]}")
    debug(f"\tNUMBER OF OVERRIDES: {len(palette["overrides"])}")
    if has_tone:
        assert("tone" in palette)
        debug(f"\tTONE: {palette["tone"]}")
    else:
        debug(f"\tTONE: None!")

    count: int = 1
    for name, cursor in db["cursors"].items():
        if not cursor["build"]:
            continue
        fin_name: str = cursor.get("out_file", name)
        input_file_name: str = f"{cursor.get("src_file", name)}.svg"
        output_file_name: str = f"{fin_name}-plain.svg"
        file_path: str = f"./src/{input_file_name}"
        if cursor.get("extra", False):
            file_path = f"./src/extra/{input_file_name}"
        output_dir: str
        match(compositor):
            case Compositor.HYPRLAND:
                output_dir = f"{theme_dir}/hyprcursors/{fin_name}"
            case Compositor.KWIN:
                output_dir = f"{theme_dir}/cursors_scalable/{fin_name}"
            case _:
                output_dir = f"{theme_dir}/{fin_name}"

        # Live update the counter for each cursor we are creating metadatas for
        if (log_level != DEBUG):
            print_procedure(Formats.clear_line() + 
            f"{procedure_cnt}. Generating plain SVGs for static cursors", count, num_cursors, False)
        debug(f"Generating Plain SVG for {name}")

        os.makedirs(output_dir, exist_ok=True)
        results: subprocess.CompletedProcess[bytes]
        if (db["theme"] == ThemeColor.WHITE and not has_tone) or cursor.get("skip_theming", False):
            results = subprocess.run(["inkscape", "--export-type=svg", "--export-plain-svg", f"--export-filename={f"{output_dir}/{output_file_name}"}", file_path], capture_output=True)
        else:
            actions: list[str] = []
            ids = query_svg(file_path)
            for id in ids:
                if id.find(".") < 0:
                    continue
                actions.extend(theme_layer(id, palette))
            actions.append("export-type:svg")
            actions.append("export-plain-svg")
            actions.append(f"export-filename:{f"{output_dir}/{output_file_name}"}")
            actions.append("export-do")
            results = subprocess.run(["inkscape", f"--actions={";".join(actions)}", file_path], capture_output=True)
        
        # Inkscape CLI, even if you run into a fatal error, will still return a 0 exit code. We must look at stderr's len to determine failure.
        if len(results.stderr) > 0:
            err = True
            # Convert the raw string into a formatted string, then print it.
            error(str(results.stderr).encode("utf-8").decode("unicode_escape"))
        count += 1

    if err and not OVERRIDE_PROC_ERRORS:
        critical("One or more errors have occurred while making the Plain SVGs. Can not continue with building until errors have been resolved.")
        exit(1)
    if (log_level != DEBUG):
        print()

def optimize_plain_svgs(theme_dir: str, compositor: Compositor, bimi_required: bool):
    '''
    Takes all of the Plain SVGs and optimizes them using the Scour program.
    Applies aggressive optimizations to try and ensure the lowest file size
    possible.

    Parameters:
        theme_dir (str):
            The file path to the folder that will be holding our cursor theme
        compositor (Compositor enum):
            The compositor for which the theme is structured around
        bimi_required (bool):
            Whether BIMI conversion will be done later. If true, the output
            file name will be appended to be considered a temp file.
    '''
    err: bool = False
    count = 1
    for name, cursor in db["cursors"].items():
        if not cursor["build"]:
            continue
        fin_name: str = cursor.get("out_file", name)
        plain_svg: str = f"{fin_name}-plain.svg"
        output_file_name = f"{fin_name}{"-optimized" if bimi_required and not cursor.get("skip_bimi", False) else ""}.svg"
        dir: str
        match(compositor):
            case Compositor.HYPRLAND:
                dir = f"{theme_dir}/hyprcursors/{fin_name}"
            case Compositor.KWIN:
                dir = f"{theme_dir}/cursors_scalable/{fin_name}"
            case _:
                dir = f"{theme_dir}/{fin_name}"

        if (log_level != DEBUG):
            print_procedure(Formats.clear_line() + 
            f"{procedure_cnt}. Optimizing SVGs for static cursors", count, num_cursors, False)

        result = subprocess.run(
            ["scour", f"{dir}/{plain_svg}", f"{dir}/{output_file_name}", 
            "--set-precision=4", "--strip-xml-prolog", "--remove-titles", 
            "--remove-description", "--remove-metadata", "--remove-descriptive-elements", 
            "--enable-comment-stripping", "--indent=tab", "--no-line-breaks", 
            "--strip-xml-space", "--enable-id-stripping", "--shorten-ids"],
            capture_output=(log_level != DEBUG))
        if (result.returncode != 0):
            err = True
        count += 1
    if err and not OVERRIDE_PROC_ERRORS:
        critical("One or more errors have occurred while optimizing the Plain SVGs. Can not continue with building until errors have been resolved.")
        exit(1)
    if (log_level != DEBUG):
        print()

def hourglass_cursors(theme_dir: str, compositor: Compositor):
    '''
    Utilizes an external generation script to create the animated hourglass
    cursors, given the preferances in the database. Then, moves build artifacts
    into final theme.

    Parameters:
        theme_dir (str):
            The file path to the folder that will be holding our cursor theme
        compositor (Compositor enum):
            The compositor for which the theme is structured around
    '''
    # It'll be faster and convenient to directly list the cursors that will be generated
    names : list[str] = ["wait", "progress"]

    path: str
    match(compositor):
        case Compositor.HYPRLAND:
            path = f"{theme_dir}/hyprcursors"
        case Compositor.KWIN:
            path = f"{theme_dir}/cursors_scalable"
        case _:
            path = f"{theme_dir}"

    for name in names:
        cursor: CursorDesign = db["cursors"][name]
        assert("total_frames" in cursor)
        assert("animation_speed" in cursor)
        print_procedure(f"        {Formats.branch(1)} Generating {name}")
        os.makedirs(f"{path}/{name}", exist_ok=True)
        hourglasses.generate_cursor(path, name, cursor["total_frames"], cursor["animation_speed"], compositor, (db["theme"] == ThemeColor.MONO) or (db["theme"] == ThemeColor.MONO_BLACK))

def convert_to_qt(theme_dir: str):
    '''
    KWin uses Qt for its graphics framework. Qt does not support the full SVG
    specification, but a subset of it called "1.2 Tiny". This function utilizes
    a program called "svgtinyps", which checks and applies changes to SVGs to
    follow SVG P/S, a stricter subset that is valid 1.2 Tiny.

    Keep in mind that cursors that have "skip_bimi" set to True will ignore this
    conversion.

    Parameters:
        theme_dir (str):
            The file path to the folder that will be holding our cursor theme
    '''
    err: bool = False
    count = 1
    for name, cursor in db["cursors"].items():
        if (not cursor["build"] and not is_animated(cursor)) or cursor.get("skip_bimi", False):
            if cursor.get("skip_bimi", False):
                count += 1 # Otherwise the count will be inaccurate
            continue
        fin_name: str = cursor.get("out_file", name)
        dir = f"{theme_dir}/cursors_scalable/{fin_name}"

        if (log_level != DEBUG and not err):
            print_procedure(Formats.clear_line() + 
            f"{procedure_cnt}. Making SVGs Qt compatible.", count, num_cursors + NUM_ANIMATED_CURSORS, False)

        if (not is_animated(cursor)):
            optimized_svg: str = f"{fin_name}-optimized.svg"
            output_file = f"{fin_name}.svg"

            debug(f"Converting SVG: {optimized_svg}")
            result = subprocess.run(["./svgtinyps", "convert", f"{dir}/{optimized_svg}", f"{dir}/{output_file}", f"--title=\"{db['manifest']['name']}\""])
            if (result.returncode != 0):
                err = True
                print()
                error(f"Failed to convert static cursor {fin_name}")
        else:
            file = f"{fin_name}.svg"
            staging_file = f"{fin_name}-c.svg"

            debug(f"Converting Animated SVG: {file}")
            result = subprocess.run(["./svgtinyps", "convert", f"{dir}/{file}", f"{dir}/{staging_file}", f"--title=\"{db['manifest']['name']}\""])
            if (result.returncode != 0):
                err = True
                print()
                error(f"Failed to convert animated cursor {fin_name}")
            # For animated cursors, we'll automatically clean up the artifacts as they are more numerous
            os.remove(f"{dir}/{file}")
            os.rename(f"{dir}/{staging_file}", f"{dir}/{file}")

            assert("total_frames" in cursor)
            frames = cursor["total_frames"]
            digits = int(math.log10(frames) + 1)
            for i in range(1, frames):
                fi = str(i).zfill(digits)
                file = f"{fin_name}-{fi}.svg"
                staging_file = f"{fin_name}-{fi}-c.svg"

                debug(f"\tConverting frame {fi}")
                result = subprocess.run(["./svgtinyps", "convert", f"{dir}/{file}", f"{dir}/{staging_file}", f"--title=\"{db['manifest']['name']}\""])
                if (result.returncode != 0):
                    err = True
                    print()
                    error(f"Failed to convert animated cursor {fin_name} on frame {i}")
                    break # For animated cursors, don't complete conversion
                os.remove(f"{dir}/{file}")
                os.rename(f"{dir}/{staging_file}", f"{dir}/{file}")
            if err:
                break
        count += 1

    if err and not OVERRIDE_PROC_ERRORS:
        critical("Errors have occurred while converting the optimized SVGs. Can not continue with building until errors have been resolved.")
        exit(1)
    if (log_level != DEBUG):
        print()

def clean_up_artifacts(theme_dir: str, compositor: Compositor, bimi_converted: bool):
    '''
    Cleans up all of the temporary SVGs that were created in the process of
    creating the final SVGs for the theme, deleting them permanently.

    Parameters:
        theme_dir (str):
            The file path to the folder that is holding our cursor theme
        compositor (Compositor enum):
            The compositor for which the theme is structured around
        bimi_converted (bool):
            Whether BIMI conversion was done. If True, it will clean up
            optimized, but unconverted SVGs (except if it has been flagged to
            skip the conversion).
    '''
    for name, cursor in db["cursors"].items():
        if not cursor["build"]:
            continue
        fin_name: str = cursor.get("out_file", name)
        plain_svg = f"{fin_name}-plain.svg"
        match(compositor):
            case Compositor.HYPRLAND:
                dir = f"{theme_dir}/hyprcursors/{fin_name}"
            case Compositor.KWIN:
                dir = f"{theme_dir}/cursors_scalable/{fin_name}"
            case _:
                dir = f"{theme_dir}/{fin_name}"
        
        debug(f"Deleting {plain_svg}")
        _ = subprocess.run(["rm", f"{dir}/{plain_svg}"])
        if bimi_converted and not cursor.get("skip_bimi", False):
            optimized_svg = f"{fin_name}-optimized.svg"
            debug(f"Deleting {optimized_svg}")
            _ = subprocess.run(["rm", f"{dir}/{optimized_svg}"])

def create_alias_sym_links(theme_dir: str):
    '''
    KDE Themes do not have their aliases listed in the metadata files, but
    rather through symbolic links. This function runs the processes to create
    the symbolic links for the aliases.

    Parameters:
        theme_dir (str):
            The file path to the folder that is holding our cursor theme
    '''
    for name, cursor in db["cursors"].items():
        if (not cursor["build"] and not is_animated(cursor)) or (not "aliases" in cursor):
            continue
        fin_name: str = cursor.get("out_file", name)
        # Path should be relative to where the symlink is
        rel_dir: str = f"./{fin_name}"
        for alias in cursor["aliases"]:
            sym_link: str = f"{theme_dir}/cursors_scalable/{alias}"
            # Do not recreate the symlink if it already exists, otherwise we will get errors
            if os.path.islink(sym_link):
                debug(f"Alias \"{alias}\" for \"{fin_name}\" already exists. Skipping.")
                continue
            debug(f"Creating alias \"{alias}\" for \"{fin_name}\"")
            _ = subprocess.run(["ln", "-s", rel_dir, sym_link])

def extra_refreshed_designs():
    '''
    Applies Posy's Refreshed Designs (V2) extra
    '''
    cursors = db["cursors"]
    db["manifest"]["tags"].append("v2")
    cursors["beam"]["build"] = False
    cursors["precision"]["build"] = False

    cursors["beam-v2"]["build"] = True
    cursors["precision-v2"]["build"] = True

def extra_xerox():
    '''
    Applies the early Xerox cursor design extra
    '''
    cursors = db["cursors"]
    db["manifest"]["tags"].append("xerox")
    cursors["default"]["build"] = False

    cursors["alt"]["build"] = True

def extra_wrong_finger():
    '''
    Applies the middle finger hand cursor extra
    '''
    cursors = db["cursors"]
    db["manifest"]["tags"].append("wrong_finger")
    cursors["hand"]["build"] = False

    cursors["wrong-finger"]["build"] = True

def extra_colored_help():
    '''
    Applies the colored help extra
    '''
    cursors = db["cursors"]
    db["manifest"]["tags"].append("colored_help")
    cursors["help"]["build"] = False

    cursors["winhelp"]["build"] = True

def extra_social():
    '''
    Applies the social extra, including map-pin and social-person
    '''
    cursors = db["cursors"]
    db["manifest"]["tags"].append("social")
    cursors["social-person"]["build"] = True
    cursors["map-pin"]["build"] = True

def extra_toned_hands():
    '''
    Applies the skin tone extra. If a tone is not provided through args, the
    user will be prompted for one.
    '''
    if (args.tone):
        db["manifest"]["tags"].append(f"tone_{args.tone}")
    else:
        tone_opt = select_prompt("Which skin tone would you like to choose?", ["Light", "Medium", "Dark"])
        match(tone_opt):
            case 1:
                db["manifest"]["tags"].append("tone_light")
            case 2:
                db["manifest"]["tags"].append("tone_medium")
            case 3:
                db["manifest"]["tags"].append("tone_dark")
            case _:
                pass

def apply_extras_args():
    '''
    A separate function that is dedicated to applying selected extras to the
    cursor theme. Instead of reading from a provided list and set, the options
    are read through the argparser.
    '''
    mono = db["theme"] == ThemeColor.MONO or db["theme"] == ThemeColor.MONO_BLACK
    if args.extras and len(args.extras) > 0:
        for extra in args.extras:
            match(extra):
                case "v2":
                    extra_refreshed_designs()
                case "xerox":
                    extra_xerox()
                case "wrong-finger":
                    extra_wrong_finger()
                case "winhelp":
                    if not mono:
                        extra_colored_help()
                    else:
                        warning("Attempted to apply \"winhelp\" extra while the theme is mono. Ignoring.")
                case "social":
                    extra_social()
                case _:
                    pass
    
    if args.tone:
        if not mono:
            extra_toned_hands()
        else:
            warning("Attempted to apply \"tone\" extra while the theme is mono. Ignoring.")

def apply_extras_prompt(option_labels : list[str], selected: set[int]):
    '''
    A separate function that is dedicated to applying selected extras to the
    cursor theme

    Parameters:
        option_labels (list[str]):
            The option names in plain English
        selected (set[int]):
            The set of all selected options by the user
    '''
    if len(selected) == 0:
        return
    
    for selection in selected:
        option = option_labels[selection - 1]
        match(option):
            case "Posy's Refreshed Cursors (V2 Designs)":
                extra_refreshed_designs()
            case "Early Xerox default cursor":
                extra_xerox()
            case "Wrong finger click":
                extra_wrong_finger()
            case "Winhelp (Colored Help)":
                extra_colored_help()
            case "Social cursors (person & pin)":
                extra_social()
            case "Skin toned hands":
                extra_toned_hands()
            case _:
                pass

def install_theme(theme_dir: str, compositor: Compositor):
    '''
    Given the built theme, will install the theme locally onto the user's
    system by moving (and renaming) the built theme into the icons folder.

    Parameters:
        theme_dir (str):
            The built theme directory that will be installed
        compositor (Compositor):
            The Wayland compositor the theme was built for. This is used
            to help name the installed theme
    '''
    theme = ""
    if db["theme"] != ThemeColor.WHITE:
        match(db["theme"]):
            case ThemeColor.BLACK:
                theme = "_black"
            case ThemeColor.MONO:
                theme = "_mono"
            case ThemeColor.MONO_BLACK:
                theme = "_mono_black"
    installed_name = f"{Compositor.theme_name(compositor)}_posys_cursor_scalable{theme}"
    install_dir = f"{Path.home()}/.local/share/icons"

    if os.path.exists(f"{install_dir}/{installed_name}"):
        overwrite = False
        if (not args.install):
            overwrite = confirmation_prompt("A copy of the theme is already installed on your system. Replace the installation?")
        if args.install or overwrite:
            shutil.rmtree(f"{install_dir}/{installed_name}")
        else:
            return
    
    try:           
        _ = shutil.move(theme_dir, f"{install_dir}/{installed_name}")
        info("Theme has successfully installed")
    except:
        error("An error occurred while installing the theme")
    
def main():
    comp : Compositor
    global procedure_cnt
    global num_cursors

    dependency_check()

    print("Welcome to the install script for Posy's cursors.")
    print(Formats.rich_txt(TextFormat.BOLD, Color8.YELLOW) +
        "Disclaimer: " +
        Formats.rich_txt(TextFormat.UNDERLINE) +
        "This build script and theme are not responsible for any damage done to your system or hardware." +
        Formats.RESET)
    print()
    debug("If you're seeing this, debug is enabled.")

    folder_name: str = ""
    if (args.compositor):
        folder_name = args.compositor
        comp = Compositor(args.compositor)
        if comp == Compositor.KWIN:
            bimi_dependency_check()
    else:
        comp_opt: int = select_prompt("For which compositor will you be building this theme for?", ["Hyprland", "KDE Plasma (KWin)"])
        match(comp_opt):
            case 1:
                folder_name = "hyprland"
                comp = Compositor.HYPRLAND
            case 2:
                folder_name = "plasma"
                comp = Compositor.KWIN
                bimi_dependency_check()
            case _:
                comp= Compositor.UNSUPPORTED
        print()

    if (args.theme):
        match(args.theme):
            case "white":
                db["theme"] = ThemeColor.WHITE
            case "black":
                db["theme"] = ThemeColor.BLACK
            case "mono":
                db["theme"] = ThemeColor.MONO
            case "mono-black":
                db["theme"] = ThemeColor.MONO_BLACK
            case _:
                pass
    else:
        theme_opt = select_prompt("Choose which theme you would like for your cursors (or just press Enter for \"White\")", ["White", "Black", "Mono", "Mono Black"], 1)
        db["theme"] = ThemeColor(theme_opt - 1)
    
    available_extras: list[str] = ["Posy's Refreshed Cursors (V2 Designs)", "Early Xerox default cursor", "Wrong finger click", "Winhelp (Colored Help)", "Social cursors (person & pin)", "Skin toned hands"]
    if (db["theme"] == ThemeColor.MONO or db["theme"] == ThemeColor.MONO_BLACK):
        # Mono themes change fundamental properties of the hourglass cursors, so we must apply those changes
        db["cursors"]["wait"]["skip_bimi"] = True
        db["cursors"]["wait"]["total_frames"] = 22
        db["cursors"]["progress"]["skip_bimi"] = True
        db["cursors"]["progress"]["total_frames"] = 22

        # Remove incompatible extra options (Skin tones, winhelp)
        available_extras.remove("Skin toned hands")
        available_extras.remove("Winhelp (Colored Help)")

    if (args.extras or args.tone):
        apply_extras_args()
    elif (not args.skip_optional_prompts):
        extra_opts: set[int] = multiselect_prompt("This theme offers extra cursors and alternatives on top of the regular selection. Here is a list of all the available extra cursors.", available_extras)
        apply_extras_prompt(available_extras, extra_opts)
    num_cursors = count_buildable_cursors()

    print_procedure(f"{procedure_cnt}. Creating appropriate theme directories")
    theme_dir: str = f"./build/{folder_name}"
    os.makedirs(theme_dir, exist_ok=True)
    setup_theme_directories(theme_dir, comp)
    procedure_cnt += 1

    print_procedure(f"{procedure_cnt}. Writing manifest")

    # Write theme manifest file
    match(comp):
        case Compositor.HYPRLAND:
            create_hyprland_manifest()
        case Compositor.KWIN:
            create_kwin_manifest()
        case _:
            # Realistically, this case should never run.
            pass
    procedure_cnt += 1

    print_procedure(f"{procedure_cnt}. Generating metadata files for static cursors", 0, 0, log_level == DEBUG)
    create_cursor_metadatas(theme_dir, comp)
    procedure_cnt += 1

    print_procedure(f"{procedure_cnt}. Generating plain SVGs for static cursors", 0, 0, log_level == DEBUG)
    create_plain_svgs(theme_dir, comp)
    procedure_cnt += 1

    bimi: bool = (comp == Compositor.KWIN)
    print_procedure(f"{procedure_cnt}. Optimizing SVGs for static cursors", 0, 0, log_level == DEBUG)
    optimize_plain_svgs(theme_dir, comp, bimi)
    procedure_cnt += 1

    print_procedure(f"{procedure_cnt}. Generating animated cursors")
    print_procedure(f"   {Formats.branch(1)} Hourglass cursors")
    hourglass_cursors(theme_dir, comp)
    procedure_cnt += 1

    if bimi:
        print_procedure(f"{procedure_cnt}. Making SVGs Qt compatible.", 0, 0, log_level == DEBUG)
        convert_to_qt(theme_dir)
        procedure_cnt += 1

    print_procedure(f"{procedure_cnt}. Removing intermediate SVGs")
    clean_up_artifacts(theme_dir, comp, bimi)
    procedure_cnt += 1

    if comp == Compositor.KWIN:
        print_procedure(f"{procedure_cnt}. Generating aliases with symbolic links")
        create_alias_sym_links(theme_dir)
        procedure_cnt += 1
    
    print()
    install = False
    if (not args.skip_optional_prompts and not args.install):
        install = confirmation_prompt("Install the built cursor theme to user?", ConfirmationDefault.YES)
    if install or args.install:
        install_theme(theme_dir, comp)

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Main build script for the Posy's Cursors Scalable theme. For most command line arguments, providing them avoids their associated interactive prompt."
    )
    _ = parser.add_argument("-c", "--compositor", type=str, choices=["hyprland", "plasma"], 
        help="The compositor that the metadata and manifest will be written in, which will use the theme.")
    _ = parser.add_argument("-t", "--theme", type=str, choices=["white", "black", "mono", "mono-black"], 
        help="The color/theme that will be applied to the cursor, affecting overall appearance.")
    _ = parser.add_argument("-e", "--extras", nargs="+", type=str, choices=["v2", "xerox", "wrong-finger", "winhelp", "social"],
        help="Modifies the theme built by swapping or adding different cursor variants. Some extras are not available on mono themes and will be ignored.")
    _ = parser.add_argument("--tone", type=str, choices=["light", "medium", "dark"],
        help="Modifies all hand cursors by applying a pigmented color to reflect a skin tone. This flag is ignored on mono themes.")
    _ = parser.add_argument("--install", action="store_true", 
        help="After building the theme, will install the theme directly to the user through `~/.local/share/icons` directory so it can be used. " +
        "WARNING: While the interactive mode will prompt for an overwrite, this flag ALWAYS overwrites any previous installations, so be careful!")
    _ = parser.add_argument("--skip-optional-prompts", action="store_true", 
        help="Skips the optional interaction prompts, which are the extra and installation prompts")
    _ = parser.add_argument("--debug", action="store_true",
        help="Enables debug logging and more verbose output, including output from external processes like Inkscape and Scour.")
    args: ArgConsts = parser.parse_args(namespace=ArgConsts())

    if (args.debug):
        log_level = DEBUG
    logger = init_logger(log_level, "build_main")

    # Create aliases that will make calling our logging functions easier
    debug = logger.debug
    info = logger.info
    warning = logger.warning
    error = logger.error
    critical = logger.critical

    main()