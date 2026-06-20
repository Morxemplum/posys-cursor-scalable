import enum
from logging import debug
import json
import os
import shutil
import subprocess
from src.cursors_data import CursorManifest, KWinCursor, Compositor, CursorDesign, kwin_nominal_size, db

class ConfirmationDefault(enum.IntEnum):
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
    manifest: CursorManifest = db["manifest"]
    with open("./build/hyprcursor/manifest.hl", "w") as f:
        # TODO: Incorporate tags into the name
        _ = f.write(f"name = {manifest.get("name")}\n")
        _ = f.write(f"description = {manifest.get("description")}\n")
        _ = f.write(f"author = {", ".join(manifest.get("authors"))}\n")
        _ = f.write(f"version = {manifest.get("version")}\n")
        _ = f.write("cursors_directory = hyprcursors\n")

def create_kwin_metadata(directory: str, cursor: str):
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
    manifest: CursorManifest = db["manifest"]
    with open("./build/plasma/index.theme", "w") as f:
        _ = f.write(f"[Icon Theme]\n")
        # TODO: Incorporate tags into the name
        _ = f.write(f"Name={manifest.get("name")}\n")
        _ = f.write(f"Comment={manifest.get("description")}. Version {manifest.get("version")}. Created by {", ".join(manifest.get("authors"))}.\n")

def create_metadata_file(compositor: Compositor, directory: str, cursor: str):
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
    for name, cursor in db["cursors"].items():
        if not cursor["build"]:
            continue
        output_dir: str
        match(compositor):
            case Compositor.HYPRLAND:
                output_dir = f"{theme_dir}/hyprcursors/{name}"
            case Compositor.KWIN:
                output_dir = f"{theme_dir}/cursors_scalable/{name}"
            case _:
                output_dir = f"{theme_dir}/{name}"

        debug(f"Generating metadata for {name}")
        os.makedirs(output_dir, exist_ok=True)
        create_metadata_file(compositor, output_dir, name)

def create_plain_svgs(theme_dir: str, compositor: Compositor):
    for name, cursor in db["cursors"].items():
        if not cursor["build"]:
            continue
        input_file_name: str = f"{cursor.get("src_file", name)}.svg"
        output_file_name: str = f"{cursor.get("out_file", name)}-plain.svg"
        file_path: str = f"./src/{input_file_name}"
        output_dir: str
        match(compositor):
            case Compositor.HYPRLAND:
                output_dir = f"{theme_dir}/hyprcursors/{name}"
            case Compositor.KWIN:
                output_dir = f"{theme_dir}/cursors_scalable/{name}"
            case _:
                output_dir = f"{theme_dir}/{name}"

        debug(f"Generating Plain SVG for {name}")
        os.makedirs(output_dir, exist_ok=True)
        _ = subprocess.run(["inkscape", "--export-type=svg", "--export-plain-svg", f"--export-filename={f"{output_dir}/{output_file_name}"}", file_path])

def optimize_plain_svgs(theme_dir: str, compositor: Compositor, bimi_required: bool):
    for name, cursor in db["cursors"].items():
        if not cursor["build"]:
            continue
        plain_svg: str = f"{cursor.get("out_file", name)}-plain.svg"
        output_file_name = f"{cursor.get("out_file", name)}{"-optimized" if bimi_required and not cursor.get("skip_bimi", False) else ""}.svg"
        dir: str
        match(compositor):
            case Compositor.HYPRLAND:
                dir = f"{theme_dir}/hyprcursors/{name}"
            case Compositor.KWIN:
                dir = f"{theme_dir}/cursors_scalable/{name}"
            case _:
                dir = f"{theme_dir}/{name}"
        
        debug(f"Optimizing SVG: {plain_svg}")
        _ = subprocess.run(["scour", f"{dir}/{plain_svg}", f"{dir}/{output_file_name}", "--set-precision=4", "--strip-xml-prolog", "--remove-titles", "--remove-description", "--remove-metadata", "--remove-descriptive-elements", "--enable-comment-stripping", "--indent=tab", "--no-line-breaks", "--strip-xml-space", "--enable-id-stripping", "--shorten-ids"])

def convert_to_qt(theme_dir: str):
    for name, cursor in db["cursors"].items():
        if not cursor["build"] or cursor.get("skip_bimi", False):
            continue
        optimized_svg: str = f"{cursor.get("out_file", name)}-optimized.svg"
        output_file_name = f"{cursor.get("out_file", name)}.svg"
        dir = f"{theme_dir}/cursors_scalable/{name}"
        
        debug(f"Converting SVG: {optimized_svg}")
        _ = subprocess.run(["./svgtinyps", "convert", f"{dir}/{optimized_svg}", f"{dir}/{output_file_name}", f"--title=\"{db['manifest']['name']}\""])

def clean_up_artifacts(theme_dir: str, compositor: Compositor, bimi_converted: bool):
    for name, cursor in db["cursors"].items():
        if not cursor["build"]:
            continue
        plain_svg = f"{cursor.get("out_file", name)}-plain.svg"
        match(compositor):
            case Compositor.HYPRLAND:
                dir = f"{theme_dir}/hyprcursors/{name}"
            case Compositor.KWIN:
                dir = f"{theme_dir}/cursors_scalable/{name}"
            case _:
                dir = f"{theme_dir}/{name}"
        
        debug(f"Deleting {plain_svg}")
        _ = subprocess.run(["rm", f"{dir}/{plain_svg}"])
        if bimi_converted and not cursor.get("skip_bimi", False):
            optimized_svg = f"{cursor.get("out_file", name)}-optimized.svg"
            debug(f"Deleting {optimized_svg}")
            _ = subprocess.run(["rm", f"{dir}/{optimized_svg}"])

def create_alias_sym_links(theme_dir: str):
    for name, cursor in db["cursors"].items():
        if not cursor["build"] or (not "aliases" in cursor):
            continue
        abs_proc = subprocess.run(["realpath", f"{theme_dir}/cursors_scalable/{name}"], capture_output=True, text=True)
        abs_dir: str = abs_proc.stdout.strip()
        for alias in cursor["aliases"]:
            sym_link: str = f"{theme_dir}/cursors_scalable/{alias}"
            debug(f"Creating alias \"{alias}\" for \"{cursor}\"")
            _ = subprocess.run(["ln", "-s", abs_dir, sym_link])

def main():
    comp : Compositor
    procedure_cnt: int = 1

    dependency_check()

    print("Welcome to the install script for Posy's cursors.")
    print("WARNING: THIS SCRIPT IS CURRENTLY A WORK IN PROGRESS AND NOT YET COMPLETE.")
    print("This script will ask you a few questions to build the theme so it best fits your preferences.\n")

    print("For which compositor will you be building this theme for?")
    print("\t1. Hyprland\n\t2. KDE Plasma (KWin)\n")

    folder_name: str = ""
    while True:
        option: int = int(input("Option: "))
        match(option):
            case 1:
                folder_name = "hyprcursor"
                comp = Compositor.HYPRLAND
                break
            case 2:
                folder_name = "plasma"
                comp = Compositor.KWIN
                bimi_dependency_check()
                break
            case _:
                print("Invalid option!\n")

    # TODO: Support theming
    # print("\nChoose which theme you would like for your cursors")
    # print("\n1. White\n2. Black\n3. Mono\n4. Mono Black\n")
 
    # theme_option: str = input("Option (default=1): ")
    # if theme_option.isspace():
    #     option = 1
    # else:
    #     option = int(theme_option)

    # TODO: Make it easy for users to select extra cursors they want to include in their theme
    
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