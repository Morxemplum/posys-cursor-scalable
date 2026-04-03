{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };
  outputs = {
    self,
    nixpkgs,
  }: let
    system = "x86_64-linux";
    pkgs = import nixpkgs {
      inherit system;
      config.allowUnfree = true;
    };
  in {
    packages.${system}.default = pkgs.callPackage ./package.nix {
      inherit
        (pkgs)
        lib
        stdenvNoCC
        inkscape
        xcursorgen
        makeFontsConf
        python3
        ;
    };
    # TODO: overlays.default = ...?
  };
}
