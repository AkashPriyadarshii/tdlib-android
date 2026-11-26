#!/bin/bash
# Local smoke test runner — loads .aar in a minimal test project and validates compilation
set -euo pipefail

echo "=== Running local smoke test ==="

TEMP_DIR=$(mktemp -d -t smoke-test-XXXXXX)
trap 'rm -rf "$TEMP_DIR"' EXIT

# Copy compiled AAR files if they exist to the staging directory
# Create dummy files for TdApi if testing configurations only

REPO_DIR="$(pwd)"
AAR_PATH="${REPO_DIR}/core/build/outputs/aar/core-release.aar"
if [ ! -f "$AAR_PATH" ]; then
    echo "ERROR: $AAR_PATH not found." >&2
    exit 1
fi

unzip -p "$AAR_PATH" classes.jar > "$TEMP_DIR/classes.jar"
if ! jar tf "$TEMP_DIR/classes.jar" | grep -q '^org/drinkless/tdlib/TdApi\.class$'; then
    echo "ERROR: classes.jar in $AAR_PATH does not contain org/drinkless/tdlib/TdApi.class" >&2
    exit 1
fi
echo "Verified classes.jar contains org/drinkless/tdlib/TdApi.class."

mkdir -p "$TEMP_DIR/app/src/main/java/io/github/tdlibandroid/smoke"

# Scaffold build.gradle.kts for smoke test
cat > "$TEMP_DIR/build.gradle.kts" << EOF
plugins {
    id("com.android.application") version "8.4.0" apply false
    id("org.jetbrains.kotlin.android") version "2.0.0" apply false
}
EOF

cat > "$TEMP_DIR/settings.gradle.kts" << EOF
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
include(":app")
EOF

cat > "$TEMP_DIR/app/build.gradle.kts" << EOF
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}
android {
    namespace = "io.github.tdlibandroid.smoke"
    compileSdk = 36
    defaultConfig {
        applicationId = "io.github.tdlibandroid.smoke"
        minSdk = 26
        targetSdk = 36
    }
}
dependencies {
    // Add local core release dependency using absolute repository path
    implementation(files("${AAR_PATH}"))
}
EOF

cat > "$TEMP_DIR/app/src/main/java/io/github/tdlibandroid/smoke/SmokeTest.kt" << 'EOF'
package io.github.tdlibandroid.smoke

import org.drinkless.tdlib.Client
import org.drinkless.tdlib.TdApi

object SmokeTest {
    fun check(): TdApi.Object = TdApi.GetAuthorizationState()
    fun clientClass(): Class<*> = Client::class.java
}
EOF

echo "Scaffolded smoke test app successfully in $TEMP_DIR."
echo "Compiling smoke test against TdApi..."
cd "$TEMP_DIR"
if [ -f "$REPO_DIR/gradlew" ]; then
  cp "$REPO_DIR/gradlew" .
  cp -r "$REPO_DIR/gradle" . 2>/dev/null || true
  chmod +x ./gradlew
  ./gradlew :app:compileReleaseKotlin --no-daemon
else
  gradle :app:compileReleaseKotlin --no-daemon
fi
echo "SMOKE TEST: TdApi reference compiled successfully."

echo "=== Smoke test setup verification complete ==="
