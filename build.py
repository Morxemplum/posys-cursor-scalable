import enum
from logging import debug
import json
import os
import re
import shutil
import subprocess
from src.cursors_data import CursorManifest, KWinCursor, Compositor, CursorDesign, kwin_nominal_size, db

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

def select_prompt(prompt: str, option_labels: list[str]) -> int:
    '''
    A specific type of user prompt where a list of options are given, and user
    must give a numeric answer to indicate their selection.

    Parameters:
        prompt: 
            The string of the prompt of which will be displayed to the user
        option_labels: 
            The string labels that will be displayed next to their numbers for
            easier reading.
    
    Returns:
        The option selected by the user
    '''
    while True:
        print(prompt)
        print()
        for i, label in enumerate(option_labels):
            print(f"{i + 1}. {label}")
        print()
        answer: str = input("Select your option: ")
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

def create_plain_svgs(theme_dir: str, compositor: Compositor):
    '''
    Creates all of the Plain SVGs from the Inkscape/Source SVGs, stripping
    Inkscape data and (soon) applying theming to the user's preference.

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
        _ = subprocess.run(["inkscape", "--export-type=svg", "--export-plain-svg", f"--export-filename={f"{output_dir}/{output_file_name}"}", file_path])

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
        _ = subprocess.run(["scour", f"{dir}/{plain_svg}", f"{dir}/{output_file_name}", "--set-precision=4", "--strip-xml-prolog", "--remove-titles", "--remove-description", "--remove-metadata", "--remove-descriptive-elements", "--enable-comment-stripping", "--indent=tab", "--no-line-breaks", "--strip-xml-space", "--enable-id-stripping", "--shorten-ids"])

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
    for name, cursor in db["cursors"].items():
        if not cursor["build"] or cursor.get("skip_bimi", False):
            continue
        fin_name: str = cursor.get("out_file", name)
        optimized_svg: str = f"{fin_name}-optimized.svg"
        output_file_name = f"{fin_name}.svg"
        dir = f"{theme_dir}/cursors_scalable/{fin_name}"
        
        debug(f"Converting SVG: {optimized_svg}")
        _ = subprocess.run(["./svgtinyps", "convert", f"{dir}/{optimized_svg}", f"{dir}/{output_file_name}", f"--title=\"{db['manifest']['name']}\""])

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
        if not cursor["build"] or (not "aliases" in cursor):
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

    available_extras: list[str] = ["Posy's Refreshed Cursors (V2 Designs)", "Early Xerox default cursor", "Wrong finger click", "Winhelp (Colored Help)", "Social cursors (person & pin)", "Skin toned hands"]

    # TODO: Support theming
    # print("\nChoose which theme you would like for your cursors")
    # print("\n1. White\n2. Black\n3. Mono\n4. Mono Black\n")
 
    # theme_option: str = input("Option (default=1): ")
    # if theme_option.isspace():
    #     option = 1
    # else:
    #     option = int(theme_option)

    # TODO: Make it easy for users to select extra cursors they want to include in their theme
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

    # TODO: When we incorporate animated cursors, it'll be done here.

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