{
  description = "rb-road-network: GIS toolkit for creating market area reports based on road network analysis";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    let
      overlay = final: prev: {
        rb-road-network = final.callPackage ./default.nix { };
      };
    in
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ overlay ];
        };
      in
      {
        packages = {
          rb-road-network = pkgs.rb-road-network;
          default = pkgs.rb-road-network;
        };

        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            cmake
            pkg-config
            gdal
            shapelib
            libpng
            wget
            jq
            gtk3
            glew
            freetype
            cairo
            libxml2
            spdlog
            python312
            python312Packages.pip
            python312Packages.virtualenv
          ];

          pythonPath = with pkgs.python312Packages; [
            aria2p
            click
            gdal
            geopandas
            geopy
            ipython
            jupyter
            matplotlib
            numpy
            openpyxl
            pandas
            plotly
            pyproj
            python-dotenv
            requests
            scipy
          ];

          shellHook = ''
            export RB_SRC=${self}
            export RB_PATH=$RB_SRC
            export XDG_DATA_DIRS=$RB_PATH/share/
          '';
        };
      }
    );
}
