#!/bin/bash
# Wraps Docker build for a single ABI and extracts .so files + TdApi.java
# Usage: ./scripts/build-tdlib.sh <abi> <version>
set -euo pipefail

ABI="${1:?Usage: build-tdlib.sh <abi> <version>}"
TDLIB_VERSION="${2:?Usage: build-tdlib.sh <abi> <version>}"
NDK_VERSION="27.2.12479018"

echo "=== Building TDLib for ABI: $ABI (Version: $TDLIB_VERSION) ==="

# 3 build attempts with 30s backoff
for attempt in 1 2 3; do
    echo "Build attempt $attempt..."
    if docker build \
      --build-arg TDLIB_INTERFACE=Java \
      --build-arg ANDROID_NDK_VERSION="$NDK_VERSION" \
      --build-arg COMMIT_HASH="master" \
      --build-arg CACHEBUST="$(date +%s)" \
      --build-arg TDLIB_ABI="$ABI" \
      --output tdlib_output \
      ./docker/; then
        echo "Docker build succeeded on attempt $attempt"
        break
    fi
    if [ $attempt -eq 3 ]; then
        echo "ERROR: Docker build failed after 3 attempts."
        exit 1
    fi
    echo "Attempt $attempt failed. Retrying in 30s..."
    sleep 30
done

# Extract outputs
mkdir -p "artifacts/$ABI"
cp tdlib_output/libs/"$ABI"/libtdjni.so "artifacts/$ABI/"

mkdir -p "artifacts/java"
cp -r tdlib_output/java/. "artifacts/java/"

echo "=== Build and extraction complete for ABI: $ABI ==="
