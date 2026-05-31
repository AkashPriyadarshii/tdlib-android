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
        // Flat dir for the local AARs built in tdlib-android/core/build/outputs/aar/
        flatDir {
            dirs("../core/build/outputs/aar", "../ktx/build/outputs/aar")
        }
    }
}

rootProject.name = "telegram-storage-mvp"
include(":app")
