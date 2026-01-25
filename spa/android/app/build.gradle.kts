import java.io.FileInputStream
import java.util.Properties
import org.gradle.api.GradleException

plugins {
    id("com.android.application")
    id("kotlin-android")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
    id("com.google.gms.google-services")
}

// Загружаем ключи подписи из key.properties (если файл существует)
val keystorePropertiesFile = rootProject.file("key.properties")
val keystoreProperties = Properties()
val hasReleaseKeystore = keystorePropertiesFile.exists()
if (hasReleaseKeystore) {
    keystoreProperties.load(FileInputStream(keystorePropertiesFile))
} else {
    println("⚠️  key.properties не найден. Release сборка будет недоступна, пока не настроена подпись. См. spa/android/SETUP_SIGNING.md")
}

android {
    namespace = "ru.prirodaspa.app"
    compileSdk = flutter.compileSdkVersion
    ndkVersion = flutter.ndkVersion

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }

    kotlinOptions {
        jvmTarget = JavaVersion.VERSION_11.toString()
    }

    defaultConfig {
        applicationId = "ru.prirodaspa.app"
        minSdk = flutter.minSdkVersion
        targetSdk = flutter.targetSdkVersion
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    signingConfigs {
        if (hasReleaseKeystore) {
            create("release") {
                keyAlias = keystoreProperties["keyAlias"] as String
                keyPassword = keystoreProperties["keyPassword"] as String
                storeFile = file(keystoreProperties["storeFile"] as String)
                storePassword = keystoreProperties["storePassword"] as String
            }
        }
    }

    buildTypes {
        release {
            // Для debug-сборок (flutter run) не ломаем билд, даже если подпись не настроена.
            // Если же собирается именно release (appbundle/release apk) — требуем keystore.
            val isReleaseTask = gradle.startParameter.taskNames.any { it.lowercase().contains("release") }
            if (isReleaseTask) {
                if (!hasReleaseKeystore) {
                    throw GradleException(
                        "Release signing не настроен. Создай key.properties и keystore (см. spa/android/SETUP_SIGNING.md)"
                    )
                }
                signingConfig = signingConfigs.getByName("release")
            } else if (hasReleaseKeystore) {
                // Если keystore есть, используем его и для других билдов при желании
                signingConfig = signingConfigs.getByName("release")
            }
            isMinifyEnabled = false
            isShrinkResources = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}

flutter {
    source = "../.."
}
