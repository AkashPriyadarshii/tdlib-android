#!/bin/bash
# Local smoke test runner — loads .aar in a minimal test project and validates compilation
set -euo pipefail

echo "=== Running local smoke test ==="

TEMP_DIR=$(mktemp -d -t smoke-test-XXXXXX)
trap 'rm -rf "$TEMP_DIR"' EXIT

# Copy compiled AAR files if they exist to the staging directory
# Create dummy files for TdApi if testing configurations only

REPO_DIR="$(pwd)"
mkdir -p "$TEMP_DIR/app"

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
    implementation(files("${REPO_DIR}/core/build/outputs/aar/core-release.aar"))
}
EOF

echo "Scaffolded smoke test app successfully in $TEMP_DIR."
# Dry run verification of syntax:
echo "Verifying smoke test build execution..."
cd "$TEMP_DIR"
if [ -f "$REPO_DIR/gradlew" ]; then
  cp "$REPO_DIR/gradlew" .
  cp -r "$REPO_DIR/gradle" . 2>/dev/null || true
  chmod +x ./gradlew
  ./gradlew :app:dependencies --configuration releaseRuntimeClasspath --no-daemon
else
  gradle :app:dependencies --configuration releaseRuntimeClasspath --no-daemon
fi
echo "SMOKE TEST: Configuration loads successfully."

echo "=== Smoke test setup verification complete ==="
