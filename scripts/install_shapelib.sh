#!/usr/bin/env sh

install_deps() {
    sudo apt install -yq \
        libtool \
        libtool-bin \
        pkg-config \
        wget \
        ca-certificates
}

install_deps

install_shapelib() {
    wget https://github.com/OSGeo/shapelib/archive/refs/tags/v1.5.0.tar.gz && \
        tar -zxf ./v1.5.0.tar.gz && \
    cd shapelib-1.5.0 && \
    ./autogen.sh && \
    ./configure && \
    make && \
    sudo make install && \
    cd .. && \
    rm -rf shapelib-1.5.0 && \
    rm -f v1.5.0.tar.gz
}

install_shapelib
