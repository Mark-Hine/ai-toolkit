plugins {
    id("com.android.application")
    kotlin("android")
}

android {
    namespace = "com.example.rewards"
    compileSdk = 36
    defaultConfig { minSdk = 26 }
}

dependencies {
    testImplementation("org.junit.jupiter:junit-jupiter:5.11.4")
    testImplementation("io.kotest:kotest-assertions-core:5.9.1")
}

tasks.withType<Test> { useJUnitPlatform() }
