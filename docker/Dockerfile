FROM buildpack-deps:bookworm as rb-roads

# dependencies
RUN apt-get update && \
    apt-get upgrade -yq && \
    apt-get install -yq --no-install-recommends \
    build-essential \
    cmake \
    gfortran \
    libatlas-base-dev \
    liblapack-dev \
    libblas-dev \
    wget \
    make \
    libtool \
    libtool-bin \
    ca-certificates \
    ca-certificates-mono \
    jq \
    sudo

# Download, install correct version of shapelib (v1.5.0)
RUN \
    wget https://github.com/OSGeo/shapelib/archive/refs/tags/v1.5.0.tar.gz && \
    tar -zxf ./v1.5.0.tar.gz && \
    cd shapelib-1.5.0 && \
    ./autogen.sh && ./configure && \
    make && \
    make install

# setup non-root user
RUN groupadd -r -g 1000 appuser \
    && useradd -m -r -u 1000 -g appuser appuser \
    && echo 'appuser ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers \
    && chown -R appuser:appuser /home/appuser
USER appuser

# setup build environment variables
ENV USER=appuser
ENV RB_SRC=/home/appuser/rb_app
ENV RB_DATA=/home/appuser/rb_data
ENV LD_LIBRARY_PATH=/usr/local/lib
WORKDIR $RB_SRC

# copy build files
COPY ./ $RB_SRC/

# mount data volume
RUN mkdir -p $RB_DATA
VOLUME $RB_DATA

# setup build environment, then build justPop.exe
RUN sudo -E /bin/bash -c "$(realpath ${RB_SRC}/scripts/_prebuild_setup.sh) && src=justPop exe=justPop make arch=linux" && \
    sudo -E /bin/bash -c "chown -R appuser:appuser ${RB_SRC} && chmod ug+x ${RB_SRC}/justPop.exe"

# set entrypoint, cmd defaults
# ref: https://docs.docker.com/engine/reference/builder/#understand-how-cmd-and-entrypoint-interact
ENTRYPOINT [ "/bin/bash", "-c" ]
CMD ["echo 'Container is running....' && read -p 'Press any key to open a shell...' && echo 'Key pressed. Opening shell...' && /bin/bash", "/bin/bash" ]
