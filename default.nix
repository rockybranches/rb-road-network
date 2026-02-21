with import <nixpkgs> { };

let
  pkgs = import <nixpkgs> { };
in
pkgs.stdenv.mkDerivation rec {
  pname = "rb-road-network";
  version = "0.1.0";

  # Source directory
  src = ./.;

  # Build dependencies
  nativeBuildInputs = [
    pkgs.cmake
    pkgs.pkg-config
  ];

  # Runtime dependencies
  buildInputs = [
    pkgs.gnumake
    pkgs.gcc
    pkgs.shapelib
    pkgs.libpng
    pkgs.gdal
    pkgs.wget
    pkgs.jq
    pkgs.gtk3
    pkgs.glew
    pkgs.freetype
    pkgs.cairo
    pkgs.libxml2
    pkgs.spdlog
  ];

  # Build phase
  buildPhase = ''
    runHook preBuild

    mkdir -p $out/bin

    # Compile justPop binary
    make clean && \
      make build

    # Compile roadsrb binary
    g++ -std=gnu++2a -fconcepts \
      -I${src}/include \
      -o $out/bin/roadsrb \
      ${src}/src/roadsrb.cc ${src}/src/lodepng.cpp \
      -lshp -pthread -lstdc++fs \
      $(pkg-config --cflags --libs gtk+-3.0) \
      $(pkg-config --cflags --libs gmodule-export-2.0) \
      -lcairo -lxml2

    runHook postBuild
  '';

  # Install phase
  installPhase = ''
    runHook preInstall

    # Copy resources
    mkdir -p $out/share/rb-road-network
    cp -r ${src}/resources/* $out/share/rb-road-network/ 2>/dev/null || true

    # Copy scripts
    mkdir -p $out/libexec/rb-road-network
    cp -r ${src}/scripts/* $out/libexec/rb-road-network/ 2>/dev/null || true

    runHook postInstall
  '';

  # Metadata
  meta = with pkgs.lib; {
    homepage = "https://github.com/rocapp/rb-road-network";
    description = "GIS toolkit for creating market area reports, including: US county demographics, road-distance market area maps";
    platforms = platforms.linux;
  };
}
