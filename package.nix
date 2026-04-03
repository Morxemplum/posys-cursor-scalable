{
  lib,
  stdenvNoCC,
  inkscape,
  xcursorgen,
  makeFontsConf,
  python3,
}:
stdenvNoCC.mkDerivation {
  pname = "posy-cursors-scalable";
  version = "1.3";

  src = with lib.fileset;
    toSource {
      root = ./.;
      fileset = ./plasma_themes;
    };

  env = {
    FONTCONFIG_FILE = makeFontsConf {fontDirectories = [];};
  };

  patchPhase = ''
    patchShebangs ./plasma_themes/src/build_tools
  '';

  buildInputs = [python3 inkscape xcursorgen];

  buildPhase = ''
    runHook preBuild
    export HOME=$(mktemp -d)
    # build each variant
    cd plasma_themes/src/build_tools
    ./buildVariant.sh 0
    ./buildVariant.sh 1
    ./buildVariant.sh 2
    ./buildVariant.sh 3
    cd ../../..
    runHook postBuild
  '';

  installPhase = ''
    runHook preInstall
    mkdir -p $out/share/icons
    cp -r plasma_themes/posys_* $out/share/icons
    runHook postInstall
  '';

  meta = {
    description = "Posy's Improved Cursors for Hyprcursor";
    homepage = "https://github.com/Morxemplum/posys-cursor-scalable";
    platforms = lib.platforms.unix;
    license = lib.licenses.cc-by-nc-40;
  };
}
