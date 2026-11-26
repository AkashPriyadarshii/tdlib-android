#!/bin/bash
# Verify all 4 required ABIs are present and have correct architectures
# Usage: ./scripts/verify-abi-count.sh <artifacts_dir>
set -euo pipefail

ARTIFACTS_DIR="${1:?Usage: verify-abi-count.sh <artifacts_dir>}"
FAILED=0

# Define mappings from ABI to expected readelf Machine architecture string
declare -A EXPECTED_ARCHS
EXPECTED_ARCHS=(
    ["arm64-v8a"]="AArch64"
    ["armeabi-v7a"]="ARM"
    ["x86_64"]="X86-64"
    ["x86"]="80386"
)

for ABI in "${!EXPECTED_ARCHS[@]}"; do
    SO_PATH="$ARTIFACTS_DIR/$ABI/libtdjni.so"
    if [ ! -f "$SO_PATH" ]; then
        echo "ERROR: Missing libtdjni.so for ABI: $ABI (expected at $SO_PATH)"
        FAILED=1
    else
        # Verify architecture using readelf -h
        ARCH_INFO=$(readelf -h "$SO_PATH" | grep "Machine:" || echo "")
        EXPECTED="${EXPECTED_ARCHS[$ABI]}"
        
        if [[ -z "$ARCH_INFO" ]]; then
            echo "ERROR: Could not read ELF headers for $SO_PATH"
            FAILED=1
        elif [[ "$ARCH_INFO" != *"$EXPECTED"* ]]; then
            echo "ERROR: Architecture mismatch for $ABI!"
            echo "Expected machine: $EXPECTED"
            echo "Found machine header: $ARCH_INFO"
            FAILED=1
        else
            echo "OK: $ABI verified matches ELF machine: $EXPECTED"
        fi

        # Verify 16KB (0x4000) LOAD segment alignment for 64-bit ABIs
        if [[ "$ABI" == "arm64-v8a" || "$ABI" == "x86_64" ]]; then
            LOAD_ALIGNS=$(readelf -lW "$SO_PATH" | awk '$1 == "LOAD" { print $NF }' || echo "")
            if [[ -z "$LOAD_ALIGNS" ]]; then
                echo "ERROR: Could not read LOAD segments for $SO_PATH"
                FAILED=1
            else
                ALIGN_OK=1
                for ALIGN in $LOAD_ALIGNS; do
                    if (( ALIGN < 0x4000 || ALIGN % 0x4000 != 0 )); then
                        echo "ERROR: $ABI LOAD segment alignment $ALIGN is not 16KB (0x4000) aligned!"
                        ALIGN_OK=0
                        FAILED=1
                    fi
                done
                if [ $ALIGN_OK -eq 1 ]; then
                    echo "OK: $ABI verified 16KB (0x4000) LOAD segment alignment"
                fi
            fi
        fi
    fi
done

if [ $FAILED -eq 1 ]; then
    echo "FATAL: ABI validation failed. Aborting build."
    exit 1
fi

echo "ABI successfully verified with readelf."
