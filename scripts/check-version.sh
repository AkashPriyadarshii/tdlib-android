#!/bin/bash
# Polls upstream TDLib version and outputs comparison results
# Usage: ./scripts/check-version.sh
set -euo pipefail

LOCAL_VERSION=$(cat VERSION 2>/dev/null || echo "0.0.0")
echo "Local VERSION: $LOCAL_VERSION"

# Fetch upstream CMakeLists.txt version field via GitHub API
UPSTREAM_VERSION=$(curl -s "https://api.github.com/repos/tdlib/td/contents/CMakeLists.txt" \
    | jq -r '.content' | base64 -d \
    | grep -oP 'set\(TDLib_VERSION \K[0-9]+\.[0-9]+\.[0-9]+' || echo "")

if [ -z "$UPSTREAM_VERSION" ]; then
    echo "ERROR: Could not fetch upstream TDLib version."
    exit 1
fi

echo "Upstream VERSION: $UPSTREAM_VERSION"

if [ "$LOCAL_VERSION" != "$UPSTREAM_VERSION" ]; then
    echo "VERSION_CHANGED=true"
    echo "NEW_VERSION=$UPSTREAM_VERSION"
    echo "OLD_VERSION=$LOCAL_VERSION"
else
    echo "VERSION_CHANGED=false"
fi
