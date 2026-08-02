import enum
from logging import basicConfig, debug, INFO, DEBUG
import json
import math
import os
import re
import shutil
import subprocess

import src.animated.hourglasses as hourglasses
from src.cursors_data import CursorManifest, KWinCursor, Compositor, CursorDesign, ThemeColor, ThemePalette, get_theme_palette, kwin_nominal_size, db

LOG_LEVEL = INFO
basicConfig(level=LOG_LEVEL)
# If true, the program will continue running even if errors were produced by 
# any processes run. DO NOT SET TO TRUE UNLESS YOU KNOW WHAT YOU'RE DOING!
OVERRIDE_PROC_ERRORS: bool = False

class ConfirmationDefault(enum.IntEnum):
    '''
    Useful enum to have to intuitively understand values for Yes/No prompts
    '''
    NONE = 0
    YES = 1
    NO = 2

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
                            print("\nThis prompt requires an answer!")
                else:
                    print("\nInvalid answer!")

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
                print("An answer must be provided")
                continue
        if not answer.isnumeric():
            print(f"Insufficient answer \"{answer}\" (Answer must be numeric)")
            continue
        selection: int = int(answer)
        if selection <= 0 or selection > len(option_labels):
            print(f"Insufficient answer \"{selection}\" (Out of range)")
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
                    print(f"Insufficient answer \"{option}\" (Out of range)")
                    errors += 1
                else:
                    options.add(option)
                continue
            
            if isinstance(re.search("[a-zA-Z]", item), re.Match):
                print(f"Insufficient answer \"{item}\" (Contains letters)")
                errors += 1
                continue

            if isinstance(re.search(r"^\d+-\d+$", item), re.Match):
                start, end = item.split("-")
                s: int = int(start)
                e: int = int(end)
                if s > e:
                    print(f"Insufficient answer \"{item}\" (Bad range: start > end)")
                    errors += 1
                    continue
                for i in range(s, e + 1):
                    options.add(i)
                continue

            print(f"Insufficient option \"{item}\". Please check your formatting and try again.")
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
        print("An error has occurred while trying to install svgtinyps!")
        print(result.stderr)
        exit(1)
    else:
        print("svgtinyps has been installed successfully!")
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
    with open("./build/hyprcursor/manifest.hl", "w") as f:
        # TODO: Incorporate tags into the name
        _ = f.write(f"name = {manifest.get("name")}\n")
        _ = f.write(f"description = {manifest.get("description")}\n")
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
    data: CursorDesign = db['cursors'][cursor]
    nominal_size: int = kwin_nominal_size(cursor)
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
        # TODO: Incorporate tags into the name
        _ = f.write(f"Name={manifest.get("name")}\n")
        _ = f.write(f"Comment={manifest.get("description")}. Version {manifest.get("version")}. Created by {", ".join(manifest.get("authors"))}.\n")

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

        debug(f"Generating metadata for {name}")
        os.makedirs(output_dir, exist_ok=True)
        create_metadata_file(compositor, output_dir, fin_name)

def query_svg(source_svg: str) -> list[str]:
    '''
    Using the query-all flag, fetches and filters a list of all the object IDs
    within a source SVG through the usage of inkscape. The header SVG object is
    filtered immediately, along with layers that start with "GROUP" and "NOOP",
    leaving with IDs that suggest that they link to paths.

    Parameters:
        source_svg (str):
            The file name of the template SVG (Must be in the "src" folder)

    Returns:
        A list of all the names of path layer IDs in the SVGs.
    '''
    svg = f"./src/{source_svg}"
    results = subprocess.run(["inkscape", "--query-all", svg], capture_output=True)
    
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
    stroke = components[2]
    actions: list[str] = [f"select-by-id:{id}"]

    # TODO: Implement optional attributes that would change fill and stroke (skin tone, mono inverse)

    match(fill):
        case "p":
            actions.append(f"object-set-property:fill, {palette["primary"]}")
        case "s":
            actions.append(f"object-set-property:fill, {palette["secondary"]}")
        case "t":
            actions.append(f"object-set-property:fill, none")
        case "mb":
            if palette["mono"]:
                actions.append("object-set-property:fill, #000000")
        case "mw":
            if palette["mono"]:
                actions.append("object-set-property:fill, #ffffff")
        case text if re.match(r"o\d+$", text):
            index = int(fill[1:]) - 1
            actions.append(f"object-set-property:fill, {palette["overrides"][index]}")
        case _:
            pass
    
    match(stroke):
        case "p":
            actions.append(f"object-set-property:stroke, {palette["primary"]}")
        case "s":
            actions.append(f"object-set-property:stroke, {palette["secondary"]}")
        case "t":
            actions.append(f"object-set-property:stroke, none")
        case "mb":
            if palette["mono"]:
                actions.append("object-set-property:stroke, #000000")
        case "mw":
            if palette["mono"]:
                actions.append("object-set-property:stroke, #ffffff")
        case text if re.match(r"o\d+$", text):
            index = int(stroke[1:])
            actions.append(f"object-set-property:stroke, {palette["overrides"][index]}")
        case _:
            pass
    
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
    error: bool = False

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

        debug(f"Generating Plain SVG for {name}")
        os.makedirs(output_dir, exist_ok=True)
        results: subprocess.CompletedProcess[bytes]
        if (db["theme"] == ThemeColor.WHITE):
            results = subprocess.run(["inkscape", "--export-type=svg", "--export-plain-svg", f"--export-filename={f"{output_dir}/{output_file_name}"}", file_path], capture_output=True)
        else:
            actions: list[str] = []
            ids = query_svg(input_file_name)
            palette = get_theme_palette(db["theme"])
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
            error = True
            # Convert the raw string into a formatted string, then print it.
            print(str(results.stderr).encode("utf-8").decode("unicode_escape"))

    if error and not OVERRIDE_PROC_ERRORS:
        print("One or more errors have occurred while making the Plain SVGs. Can not continue with building until errors have been resolved.")
        exit(1)

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
    error: bool = False
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
        
        debug(f"Optimizing SVG: {plain_svg}")
        result = subprocess.run(
            ["scour", f"{dir}/{plain_svg}", f"{dir}/{output_file_name}", 
            "--set-precision=4", "--strip-xml-prolog", "--remove-titles", 
            "--remove-description", "--remove-metadata", "--remove-descriptive-elements", 
            "--enable-comment-stripping", "--indent=tab", "--no-line-breaks", 
            "--strip-xml-space", "--enable-id-stripping", "--shorten-ids"],
            capture_output=(LOG_LEVEL != DEBUG)) # pyright: ignore[reportUnnecessaryComparison]
        if (result.returncode != 0):
            error = True
    if error and not OVERRIDE_PROC_ERRORS:
        print("One or more errors have occurred while optimizing the Plain SVGs. Can not continue with building until errors have been resolved.")
        exit(1)

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
        print(f"\t\tGenerating {name}")
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
    error: bool = False
    for name, cursor in db["cursors"].items():
        if (not cursor["build"] and not is_animated(cursor)) or cursor.get("skip_bimi", False):
            continue
        fin_name: str = cursor.get("out_file", name)
        dir = f"{theme_dir}/cursors_scalable/{fin_name}"
        if (not is_animated(cursor)):
            optimized_svg: str = f"{fin_name}-optimized.svg"
            output_file = f"{fin_name}.svg"

            debug(f"Converting SVG: {optimized_svg}")
            result = subprocess.run(["./svgtinyps", "convert", f"{dir}/{optimized_svg}", f"{dir}/{output_file}", f"--title=\"{db['manifest']['name']}\""])
            if (result.returncode != 0):
                error = True
        else:
            file = f"{fin_name}.svg"
            staging_file = f"{fin_name}-c.svg"

            debug(f"Converting SVG: {file}")
            result = subprocess.run(["./svgtinyps", "convert", f"{dir}/{file}", f"{dir}/{staging_file}", f"--title=\"{db['manifest']['name']}\""])
            if (result.returncode != 0):
                error = True
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
                    error = True
                    break # For animated cursors, don't complete conversion
                os.remove(f"{dir}/{file}")
                os.rename(f"{dir}/{staging_file}", f"{dir}/{file}")

    if error and not OVERRIDE_PROC_ERRORS:
        print("One or more errors have occurred while converting the optimized SVGs. Can not continue with building until errors have been resolved.")
        exit(1)

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
        abs_proc = subprocess.run(["realpath", f"{theme_dir}/cursors_scalable/{fin_name}"], capture_output=True, text=True)
        abs_dir: str = abs_proc.stdout.strip()
        for alias in cursor["aliases"]:
            sym_link: str = f"{theme_dir}/cursors_scalable/{alias}"
            # Do not recreate the symlink if it already exists, otherwise we will get errors
            if os.path.islink(sym_link):
                continue
            debug(f"Creating alias \"{alias}\" for \"{cursor}\"")
            _ = subprocess.run(["ln", "-s", abs_dir, sym_link])

def main():
    comp : Compositor
    procedure_cnt: int = 1

    dependency_check()

    print("Welcome to the install script for Posy's cursors.")
    print("WARNING: THIS SCRIPT IS CURRENTLY A WORK IN PROGRESS AND NOT YET COMPLETE.")
    print("This script will ask you a few questions to build the theme so it best fits your preferences.\n")

    comp_opt: int = select_prompt("For which compositor will you be building this theme for?", ["Hyprland", "KDE Plasma (KWin)"])

    folder_name: str = ""
    match(comp_opt):
        case 1:
            folder_name = "hyprcursor"
            comp = Compositor.HYPRLAND
        case 2:
            folder_name = "plasma"
            comp = Compositor.KWIN
            bimi_dependency_check()
        case _:
            comp= Compositor.UNSUPPORTED

    print()

    # TODO: Some extras are incompatible with a mono theme. Refine the extra cursor selection process to remove such options if a mono theme is selected.
    available_extras: list[str] = ["Posy's Refreshed Cursors (V2 Designs)", "Early Xerox default cursor", "Wrong finger click", "Winhelp (Colored Help)", "Social cursors (person & pin)", "Skin toned hands"]

    theme_opt = select_prompt("Choose which theme you would like for your cursors (or just press Enter for \"White\")", ["White", "Black", "Mono", "Mono Black"], 1)
    match(theme_opt):
        case 1:
            db["theme"] = ThemeColor.WHITE
        case 2:
            db["theme"] = ThemeColor.BLACK
        case 3:
            db["theme"] = ThemeColor.MONO
        case 4:
            db["theme"] = ThemeColor.MONO_BLACK
        case _:
            pass
    
    # Mono themes change fundamental properties of the hourglass cursors, so we must apply those changes
    if (db["theme"] == ThemeColor.MONO or db["theme"] == ThemeColor.MONO_BLACK):
        db["cursors"]["wait"]["skip_bimi"] = True
        db["cursors"]["wait"]["total_frames"] = 22
        db["cursors"]["progress"]["skip_bimi"] = True
        db["cursors"]["progress"]["total_frames"] = 22

    extra_opts: set[int] = multiselect_prompt("This theme offers extra cursors and alternatives on top of the regular selection. Here is a list of all the available extra cursors.", available_extras)

    # Refreshed Cursors
    if 1 in extra_opts:
        db["cursors"]["beam"]["build"] = False
        db["cursors"]["precision"]["build"] = False

        db["cursors"]["beam-v2"]["build"] = True
        db["cursors"]["precision-v2"]["build"] = True

    # Early Xerox cursor (up arrow)
    if 2 in extra_opts:
        db["cursors"]["default"]["build"] = False

        db["cursors"]["alt"]["build"] = True

    # Wrong finger (middle finger click)
    if 3 in extra_opts:
        db["cursors"]["hand"]["build"] = False

        db["cursors"]["wrong-finger"]["build"] = True
    
    # Winhelp (Colored Help cursor)
    if 4 in extra_opts:
        db["cursors"]["help"]["build"] = False

        db["cursors"]["winhelp"]["build"] = True
    
    # Social cursors (person & pin)
    if 5 in extra_opts:
        db["cursors"]["social-person"]["build"] = True
        db["cursors"]["map-pin"]["build"] = True
    
    # Skin toned hands
    if 6 in extra_opts:
        print("Skin tones has not yet been implemented! Stay tuned")

    
    print(f"{procedure_cnt}. Creating appropriate theme directories")
    theme_dir: str = f"./build/{folder_name}"
    os.makedirs(theme_dir, exist_ok=True)
    setup_theme_directories(theme_dir, comp)
    procedure_cnt += 1

    print(f"{procedure_cnt}. Writing manifest")

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

    print(f"{procedure_cnt}. Generating metadata files for static cursors")
    create_cursor_metadatas(theme_dir, comp)
    procedure_cnt += 1

    print(f"{procedure_cnt}. Generating plain SVGs for static cursors")
    create_plain_svgs(theme_dir, comp)
    procedure_cnt += 1

    bimi: bool = (comp == Compositor.KWIN)
    print(f"{procedure_cnt}. Optimizing SVGs for static cursors")
    optimize_plain_svgs(theme_dir, comp, bimi)
    procedure_cnt += 1

    print(f"{procedure_cnt}. Generating animated cursors")
    print("\tHourglass cursors")
    hourglass_cursors(theme_dir, comp)
    procedure_cnt += 1

    if bimi:
        print(f"{procedure_cnt}. Making SVGs Qt compatible.")
        convert_to_qt(theme_dir)
        procedure_cnt += 1

    print(f"{procedure_cnt}. Removing intermediate SVGs")
    clean_up_artifacts(theme_dir, comp, bimi)
    procedure_cnt += 1

    if comp == Compositor.KWIN:
        print(f"{procedure_cnt}. Generating aliases with symbolic links")
        create_alias_sym_links(theme_dir)
        procedure_cnt += 1
    
    print("All done!")

    
if __name__ == "__main__":
    main()