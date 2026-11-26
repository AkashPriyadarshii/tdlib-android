FROM ubuntu:24.04 AS build

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -yq default-jdk g++ git gperf make perl php-cli unzip wget && rm -rf /var/lib/apt/lists/*

WORKDIR /home

ARG TDLIB_ABI
ENV TDLIB_ABI=$TDLIB_ABI

ARG ANDROID_NDK_VERSION=27.2.12479018
COPY ./check-environment.sh ./fetch-sdk.sh ./
RUN ./fetch-sdk.sh SDK "$ANDROID_NDK_VERSION"

ARG OPENSSL_VERSION=openssl-3.5.9
ARG OPENSSL_SHA256=796831ec533bf41998eaaee9d632d921b8a69f57394fa4086ff01a941113d26d
ARG BUILD_SHARED_OPENSSL_LIBS=
COPY ./build-openssl.sh ./
RUN ./build-openssl.sh SDK "$ANDROID_NDK_VERSION" openssl "$OPENSSL_VERSION" "$BUILD_SHARED_OPENSSL_LIBS" "$OPENSSL_SHA256"

ARG CACHEBUST=1
ARG TDLIB_VERSION=master
RUN git clone https://github.com/tdlib/td.git && cd td && \
    (git checkout "$TDLIB_VERSION" 2>/dev/null || git checkout "v${TDLIB_VERSION#v}" 2>/dev/null || git checkout master)

# Copy our custom, parallelized and ABI-filtered build script to override the default one from cloned td
COPY ./build-tdlib.sh td/example/android/build-tdlib.sh

ARG ANDROID_STL=c++_static
ARG TDLIB_INTERFACE=Java
RUN td/example/android/build-tdlib.sh SDK "$ANDROID_NDK_VERSION" openssl "$ANDROID_STL" "$TDLIB_INTERFACE" && rm -rf td/example/android/build-*


FROM scratch

COPY --from=build /home/td/example/android/tdlib/ /
