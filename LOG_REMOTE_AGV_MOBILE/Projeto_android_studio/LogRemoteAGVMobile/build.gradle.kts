buildscript {
    dependencies {
        classpath 'com.google.gms:google-services:4.4.1' // versão obrigatória
    }
    repositories {
        google()
        mavenCentral()
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}
