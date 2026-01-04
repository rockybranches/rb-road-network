{ stdenv
, fetchFromGitHub
, cmake
, pkgconfig
, shapelib
, libpng
, gdal
, wget
, jq
}:

stdenv.mkDerivation rec {
  pname = "rb-road-network";

  src = fetchFromGitHub {
    owner = "rocapp";
    repo = "rb-road-network";
  };
  buildInputs = [
    shapelib
    libpng
    gdal
    wget
    jq
    cmake
    pkgconfig
  ];

  meta = with stdenv.lib; {
    homepage = "https://github.com/rocapp/rb-road-network";
    description = "GIS toolkit for creating market area reports, including: US county demographics, road-distance market area maps";
    platforms = platforms.linux;
  };
}
