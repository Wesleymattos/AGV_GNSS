plugins {
    id 'com.android.application'
    id 'kotlin-android'
    id 'com.google.gms.google-services' // Firebase plugin
}

android {
    namespace 'com.exemplo.logremote'
    compileSdk 34

    defaultConfig {
        applicationId "com.exemplo.logremote"
        minSdk 24
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }

    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}

dependencies {
    implementation "org.jetbrains.kotlin:kotlin-stdlib:1.9.0"
    implementation 'com.google.firebase:firebase-database-ktx:20.3.0'
    implementation 'com.google.firebase:firebase-analytics-ktx:21.5.0'
}
