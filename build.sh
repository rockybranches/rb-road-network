#!/usr/bin/env bash

# rb-road-network/build.sh : build the binary for the specified architecture

set -e

src=$RB_SRC/src/$1
src=$(realpath -ms $src)
includes=$RB_SRC/include/
includes=$(realpath -ms $includes)
arch=${3:-linux}

echo "ARCH=$arch"
echo "RB_SRC=$RB_SRC"
echo "SRC=$src"
echo "INCLUDE_PATH=$includes"

LIBS=" -lshp -pthread -lstdc++fs "
CFLAGS=""
RB_DEBUG=${RB_DEBUG:-true} # Set debug flag

echo "RB_DEBUG=${RB_DEBUG}"

determine_compiler() {
    export -p CXX=g++
}

perform_compile() {
    g++ $@
}

if [ "$arch" = "linux" ]
then
    CFLAGS+="-std=gnu++2a -fconcepts"
    if [[ $src == *"GL"* ]]; then # OpenGL graphics backend
	LIBS+=$(pkg-config --libs glew)" "$(pkg-config --libs freetype2)" -L/usr/lib "
	CFLAGS+=$(pkg-config --cflags glew)" "$(pkg-config --cflags freetype2)" -D_USEGL "
	includes+=" -I/usr/include "
    fi
    if [[ $src = *"test"* ]] || [[ $src = *"justPop"* ]]; then
	CFLAGS+=" -D_TESTRB " # removes dependencies on GTK if set
	echo "TEST FLAG SET (remove GTK dependencies)"
    fi
    if [[ "$RB_DEBUG" = true ]]; then
	CFLAGS+=" -D_RB_DEBUG " # set debug flag -- sets breakpoints with std::raise(SIGINT)
	echo 'DEBUG FLAG SET -- Use breakpoints set with `rbtypes.hpp::insert_breakpoint()`'
    fi
    if [[ "$THRUST_RB" = true ]]; then
	CFLAGS+=" "$(pkg-config --cflags cudart-8.0)" "
	LIBS+=" "$(pkg-config --libs cudart-8.0)" "
	CFLAGS+=" -D_THRUSTRB " # set Thrust flag -- include CUDA OOP Thrust library
	echo 'Thrust FLAG SET -- use CUDA Thrust'
	THRUST_ARGS=" -I${includes} -c $RB_SRC/src/testThrust_cuda.cu "
    else
	CFLAGS+=" -o $2.exe "
    fi
    CFLAGS+=" -o $2.exe " # remember this !! !! *******
    echo "CFLAGS=$CFLAGS"
    echo "LIBS=$LIBS"
    if [[ "$THRUST_RB" != true ]]; then
	export -p COMPILE_ARGS="-Wall -rdynamic -g -I${includes} ${CFLAGS} $src.cc $RB_SRC/src/lodepng.cpp ${LIBS} -std=gnu++2a"
	echo "COMPILE_ARGS=${COMPILE_ARGS}"
	perform_compile $COMPILE_ARGS
    else
	determine_compiler
	export -p COMPILE_ARGS="-Wall -rdynamic -g -I${includes} ${CFLAGS} $src.cc $RB_SRC/src/lodepng.cpp ${LIBS} -std=gnu++2a"
	echo "COMPILE_ARGS=${COMPILE_ARGS}"
	$CXX $COMPILE_ARGS
    fi
    
elif [ "$arch" = "win" ]
then
    cp -v $RB_SRC/resources/* $RB_SRC/dist/resources/ # copy resources -> dist
    cp -v $RB_SRC/version.txt $RB_SRC/dist/ # copy version info -> dist
    cp -v -r $RB_SRC/data/ $RB_SRC/dist/ # copy data files -> dist
    export XDG_DATA_DIRS=$RB_SRC/share/
    CXX=x86_64-w64-mingw32-g++
    PKGCONFIG=x86_64-w64-mingw32-pkg-config
    CFLAGS=$($PKGCONFIG gtk+-3.0 --cflags)$($PKGCONFIG gtk+-3.0 --cflags)$($PKGCONFIG shapelib --cflags)
    CFLAGS+=" -g -Wall -mms-bitfields -mwindows -std=c++2a -Wl,--export-all-symbols -static-libgcc -static-libstdc++ "
    LIBS=$($PKGCONFIG gtk+-3.0 --libs)$($PKGCONFIG gmodule-export-2.0 --libs)$($PKGCONFIG shapelib --libs)
    LIBS+=" -lcairo -pthread -lxml2"
    if [[ $src == *"test"* ]]; then
	CFLAGS+=" -D_TESTRB "
    fi
    if [[ $src == *"GL"* ]]; then
	LIBS+=$($PKG_CONFIG --libs glew)" "$($PKG_CONFIG --libs freetype2)" "
	CFLAGS+=$($PKG_CONFIG --cflags glew)" "$($PKG_CONFIG --cflags freetype2)" "
	CFLAGS+=" -D_USEGL "
    fi
    echo "CFLAGS=$CFLAGS"
    echo "LIBS=$LIBS"
    $CXX $CFLAGS -L$RB_SRC/dist/bin -I$includes $src.cc $RB_SRC/src/lodepng.cpp -o $RB_SRC/dist/bin/$2_$arch.exe $LIBS
fi
