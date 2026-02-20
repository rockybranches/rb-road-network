{
  stdenv,
  cmake,
  pkg-config,
  shapelib,
  libpng,
  gdal,
  wget,
  jq,
  gtk3,
  glew,
  freetype,
  cairo,
  libxml2,
  spdlog,
}:

stdenv.mkDerivation rec {
  pname = "rb-road-network";
  version = "0.1.0";

  src = ./.;

  nativeBuildInputs = [
    cmake
    pkg-config
  ];

  buildInputs = [
    shapelib
    libpng
    gdal
    wget
    jq
    gtk3
    glew
    freetype
    cairo
    libxml2
    spdlog
  ];

  buildPhase = ''
    runHook preBuild

    mkdir -p $out/bin

    g++ -std=gnu++2a -fconcepts -D_TESTRB \
      -I${src}/include \
      -o $out/bin/justPop \
      ${src}/src/justPop.cc ${src}/src/lodepng.cpp \
      -lshp -pthread -lstdc++fs -std=gnu++2a

    g++ -std=gnu++2a -fconcepts \
      -I${src}/include \
      -o $out/bin/roadsrb \
      ${src}/src/roadsrb.cc ${src}/src/lodepng.cpp \
      -lshp -pthread -lstdc++fs \
      $(pkg-config --cflags --libs gtk+-3.0) \
      $(pkg-config --cflags --libs gmodule-export-2.0) \
      -lcairo -lxml2 -std=gnu++2a

    runHook postBuild
  '';

  installPhase = ''
    runHook preInstall

    mkdir -p $out/share/rb-road-network
    cp -r ${src}/resources/* $out/share/rb-road-network/ 2>/dev/null || true

    mkdir -p $out/libexec/rb-road-network
    cp -r ${src}/scripts/* $out/libexec/rb-road-network/ 2>/dev/null || true

    runHook postInstall
  '';

  meta = with stdenv.lib; {
    homepage = "https://github.com/rocapp/rb-road-network";
    description = "GIS toolkit for creating market area reports, including: US county demographics, road-distance market area maps";
    platforms = platforms.linux;
  };
}
