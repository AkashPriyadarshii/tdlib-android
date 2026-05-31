plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.mavenPublish)
}

android {
    namespace = "io.github.tdlibandroid.core"
    compileSdk = libs.versions.compileSdk.get().toInt()
    defaultConfig {
        minSdk = libs.versions.minSdk.get().toInt()
        ndk { abiFilters += listOf("arm64-v8a", "armeabi-v7a", "x86_64", "x86") }
        consumerProguardFiles("consumer-rules.pro")
    }
    packaging {
        jniLibs.keepDebugSymbols.add("**/*.so")
    }
    sourceSets {
        getByName("main") {
            jniLibs.srcDirs("src/main/jniLibs")
        }
    }
}

dependencies {
    compileOnly("androidx.annotation:annotation:1.8.0")
}

mavenPublishing {
    publishToMavenCentral(com.vanniktech.maven.publish.SonatypeHost.CENTRAL_PORTAL)
    signAllPublications()
    coordinates(
        groupId = "io.github.tdlib-android",
        artifactId = "core",
        version = File(rootDir, "VERSION").readText().trim()
    )
    pom {
        name.set("tdlib-android-core")
        description.set("Community-maintained TDLib prebuilt AAR for Android. Auto-updated. Zero build steps.")
        inceptionYear.set("2026")
        url.set("https://github.com/tdlib-android/tdlib-android")
        licenses {
            license {
                name.set("Boost Software License 1.0")
                url.set("https://www.boost.org/LICENSE_1_0.txt")
            }
        }
        developers {
            developer {
                id.set("AkashPriyadarshii")
                name.set("Akash Priyadarshi")
                url.set("https://github.com/AkashPriyadarshii")
            }
        }
        scm {
            url.set("https://github.com/tdlib-android/tdlib-android")
            connection.set("scm:git:git://github.com/tdlib-android/tdlib-android.git")
            developerConnection.set("scm:git:ssh://git@github.com/tdlib-android/tdlib-android.git")
        }
    }
}
