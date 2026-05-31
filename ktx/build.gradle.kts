plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.mavenPublish)
}

android {
    namespace = "io.github.tdlibandroid.ktx"
    compileSdk = libs.versions.compileSdk.get().toInt()
    defaultConfig {
        minSdk = libs.versions.minSdk.get().toInt()
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    api(project(":core"))
    implementation(libs.kotlinx.coroutines)
}

mavenPublishing {
    publishToMavenCentral(com.vanniktech.maven.publish.SonatypeHost.CENTRAL_PORTAL)
    signAllPublications()
    coordinates(
        groupId = "io.github.tdlib-android",
        artifactId = "ktx",
        version = File(rootDir, "VERSION").readText().trim()
    )
    pom {
        name.set("tdlib-android-ktx")
        description.set("Kotlin Coroutines + Flow wrapper for TDLib Android. Suspend send() + Flow<Update>.")
        inceptionYear.set("2026")
        url.set("https://github.com/tdlib-android/tdlib-android")
        licenses {
            license {
                name.set("Apache-2.0")
                url.set("https://www.apache.org/licenses/LICENSE-2.0.txt")
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
