{ stdenv
, fetchFromGitHub
, cmake
, pkgconfig
, shapelib
, libpng
, gdal
, qgis
, qtbase
, qtdeclarative
, qtquickcontrols
, qtgraphicaleffects
, qtlocation
, qtwebsockets
, qtwebchannel
, wrapQtAppsHook
}:

stdenv.mkDerivation rec {
  pname = "rb-road-network";
  version = "unstable-2023-03-24";

  src = fetchFromGitHub {
    owner = "RockyBranches";
    repo = "rb-road-network";
  };

  nativeBuildInputs = [ cmake pkgconfig wrapQtAppsHook ];
  buildInputs = [ shapelib libpng gdal qgis qtbase qtdeclarative qtquickcontrols qtgraphicaleffects qtlocation qtwebsockets qtwebchannel ];

  cmakeFlags = [ "-DWITH_QT=ON" ];

  meta = with stdenv.lib; {
    homepage = "https://github.com/RockyBranches/rb-road-network";
    description = "GIS toolkit for creating market area reports, including: US county demographics, road-distance market area maps";
    license = licenses.gpl3Plus;
    platforms = platforms.linux;
    maintainers = with maintainers; [ cstrahan ];
  };
}
