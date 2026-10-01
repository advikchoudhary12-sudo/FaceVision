#include <Arduino.h>
#include <WiFi.h>
#include "blind_stick_secrets.h"
#include <BlynkSimpleEsp32.h>
// ============================================================
// PIN CONFIGURATION
// ============================================================

const int TRIG_PIN   = 9;
const int ECHO_PIN   = 10;
const int BUZZER_PIN = 7;

const int BLIND_STICK_PIN = V10;


// ============================================================
// CONFIGURATION
// ============================================================

const float OBSTACLE_DISTANCE_CM = 100.0f;

const unsigned long OBSTACLE_CLEAR_TIME_MS = 1000;
const unsigned long TRIGGER_COOLDOWN_MS = 3000;
const unsigned long SENSOR_SAMPLE_INTERVAL_MS = 60;
const unsigned long ECHO_TIMEOUT_US = 30000;

// Print distance every 250 ms instead of flooding
// the Serial Monitor every 60 ms.
const unsigned long SERIAL_DISTANCE_INTERVAL_MS = 250;


// ============================================================
// STATE
// ============================================================

bool obstacleLatched = false;
bool clearTiming = false;
bool hasTriggered = false;

unsigned long lastTriggerAt = 0;
unsigned long clearStartedAt = 0;
unsigned long lastSensorSampleAt = 0;
unsigned long lastSerialDistanceAt = 0;


// ============================================================
// ULTRASONIC DISTANCE
// ============================================================

float measureDistanceCm() {

    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);

    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);

    digitalWrite(TRIG_PIN, LOW);

    unsigned long echoDuration =
        pulseIn(ECHO_PIN, HIGH, ECHO_TIMEOUT_US);

    if (echoDuration == 0) {
        return -1.0f;
    }

    return (float)echoDuration * 0.0343f / 2.0f;
}


// ============================================================
// OBSTACLE DETECTION
// ============================================================

bool obstacleDetected(float distanceCm) {

    return distanceCm > 0.0f &&
           distanceCm <= OBSTACLE_DISTANCE_CM;
}


// ============================================================
// ACTIVE BUZZER
// ============================================================

void setBuzzer(bool enabled) {

    digitalWrite(
        BUZZER_PIN,
        enabled ? HIGH : LOW
    );
}


// ============================================================
// BLYNK STATE
// ============================================================

void publishObstacleState(bool detected) {

    if (Blynk.connected()) {

        Blynk.virtualWrite(
            BLIND_STICK_PIN,
            detected ? 1 : 0
        );

        Serial.printf(
            "[BLYNK] V10 -> %s\n",
            detected ? "HIGH" : "LOW"
        );
    }
    else {

        Serial.println(
            "[BLYNK] Not connected; state not sent."
        );
    }
}


// ============================================================
// BLYNK CONNECTED
// ============================================================

BLYNK_CONNECTED() {

    Serial.println();
    Serial.println("[BLYNK] Connected!");

    publishObstacleState(obstacleLatched);
}


// ============================================================
// WIFI EVENTS
// ============================================================

void printConnectionInfo() {

    Serial.println();
    Serial.println("------------- CONNECTION -------------");

    Serial.print("[WIFI] SSID: ");
    Serial.println(WiFi.SSID());

    Serial.print("[WIFI] IP: ");
    Serial.println(WiFi.localIP());

    Serial.print("[WIFI] RSSI: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");

    Serial.println("--------------------------------------");
    Serial.println();
}


// ============================================================
// SETUP
// ============================================================

void setup() {

    Serial.begin(115200);

    // Give Serial Monitor time to open
    delay(500);

    Serial.println();
    Serial.println();
    Serial.println("========================================");
    Serial.println("        FACEVISION BLIND STICK");
    Serial.println("========================================");
    Serial.println();

    Serial.println("[SYSTEM] Initializing...");

    // --------------------------------------------------------
    // GPIO
    // --------------------------------------------------------

    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    pinMode(BUZZER_PIN, OUTPUT);

    digitalWrite(TRIG_PIN, LOW);
    setBuzzer(false);

    Serial.println("[GPIO] TRIG   = GPIO 9");
    Serial.println("[GPIO] ECHO   = GPIO 10");
    Serial.println("[GPIO] BUZZER = GPIO 7");


    // --------------------------------------------------------
    // Configuration
    // --------------------------------------------------------

    Serial.println();
    Serial.println("[CONFIG] Obstacle threshold: 100 cm");
    Serial.println("[CONFIG] Clear time: 1000 ms");
    Serial.println("[CONFIG] Trigger cooldown: 3000 ms");
    Serial.println("[CONFIG] Sensor interval: 60 ms");


    // --------------------------------------------------------
    // Wi-Fi / Blynk
    // --------------------------------------------------------

    Serial.println();
    Serial.println("[WIFI] Connecting to Wi-Fi...");
    Serial.print("[WIFI] SSID: ");
    Serial.println(WIFI_SSID);

    Blynk.begin(
        BLYNK_AUTH_TOKEN,
        WIFI_SSID,
        WIFI_PASSWORD
    );

    Serial.println("[WIFI] Connected.");

    printConnectionInfo();


    // --------------------------------------------------------
    // Initial Blynk state
    // --------------------------------------------------------

    publishObstacleState(false);

    Serial.println();
    Serial.println("[SYSTEM] Blind Stick READY.");
    Serial.println("[SYSTEM] Serial telemetry active.");
    Serial.println();
}


// ============================================================
// MAIN LOOP
// ============================================================

void loop() {

    // Keep Blynk alive
    Blynk.run();

    unsigned long now = millis();


    // ========================================================
    // SENSOR SAMPLE RATE
    // ========================================================

    if (now - lastSensorSampleAt <
        SENSOR_SAMPLE_INTERVAL_MS) {

        delay(1);
        return;
    }

    lastSensorSampleAt = now;


    // ========================================================
    // MEASURE DISTANCE
    // ========================================================

    float distanceCm = measureDistanceCm();

    bool detected =
        obstacleDetected(distanceCm);


    // ========================================================
    // SERIAL DISTANCE TELEMETRY
    // ========================================================

    if (now - lastSerialDistanceAt >=
        SERIAL_DISTANCE_INTERVAL_MS) {

        lastSerialDistanceAt = now;

        if (distanceCm < 0.0f) {

            Serial.println(
                "[ULTRASONIC] No echo"
            );
        }
        else {

            Serial.printf(
                "[ULTRASONIC] Distance: %.1f cm | Detection: %s | Latched: %s\n",
                distanceCm,
                detected ? "YES" : "NO",
                obstacleLatched ? "YES" : "NO"
            );
        }
    }


    // ========================================================
    // NEW OBSTACLE DETECTED
    // ========================================================

    if (detected && !obstacleLatched) {

        obstacleLatched = true;

        clearTiming = false;

        hasTriggered = true;

        lastTriggerAt = now;


        // Buzzer ON
        setBuzzer(true);


        // Blynk HIGH
        publishObstacleState(true);


        Serial.println();
        Serial.println("******** OBSTACLE DETECTED ********");

        Serial.printf(
            "[OBSTACLE] Distance: %.1f cm\n",
            distanceCm
        );

        Serial.println(
            "[BUZZER] ON"
        );

        Serial.println(
            "[SYSTEM] Obstacle state LATCHED"
        );

        Serial.println(
            "***********************************"
        );
        Serial.println();

        return;
    }


    // ========================================================
    // NO OBSTACLE LATCHED
    // ========================================================

    if (!obstacleLatched) {

        setBuzzer(false);

        return;
    }


    // ========================================================
    // OBSTACLE STILL PRESENT
    // ========================================================

    if (detected) {

        // Cancel clear timer
        if (clearTiming) {

            clearTiming = false;

            Serial.println(
                "[OBSTACLE] Obstacle returned; clear timer cancelled."
            );
        }

        // Keep buzzer ON
        setBuzzer(true);

        return;
    }


    // ========================================================
    // OBSTACLE DISAPPEARED
    // ========================================================

    if (!clearTiming) {

        clearTiming = true;

        clearStartedAt = now;

        Serial.println();
        Serial.println(
            "[OBSTACLE] Obstacle disappeared."
        );

        Serial.println(
            "[CLEAR] Starting 1-second clear timer..."
        );
    }


    // ========================================================
    // CHECK CLEAR TIME
    // ========================================================

    unsigned long currentTime = millis();

    unsigned long clearElapsed =
        currentTime - clearStartedAt;

    bool clearLongEnough =
        clearElapsed >= OBSTACLE_CLEAR_TIME_MS;


    // ========================================================
    // CHECK COOLDOWN
    // ========================================================

    bool triggerCooldownExpired =
        !hasTriggered ||
        currentTime - lastTriggerAt >=
        TRIGGER_COOLDOWN_MS;


    // ========================================================
    // CLEAR TIMER TELEMETRY
    // ========================================================

    static unsigned long lastClearPrint = 0;

    if (clearTiming &&
        currentTime - lastClearPrint >= 250) {

        lastClearPrint = currentTime;

        Serial.printf(
            "[CLEAR] Clear for %lu / %lu ms\n",
            clearElapsed,
            OBSTACLE_CLEAR_TIME_MS
        );
    }


    // ========================================================
    // RESET OBSTACLE STATE
    // ========================================================

    if (clearLongEnough &&
        triggerCooldownExpired) {

        obstacleLatched = false;

        clearTiming = false;


        // Buzzer OFF
        setBuzzer(false);


        // Blynk LOW
        publishObstacleState(false);


        Serial.println();
        Serial.println("******** OBSTACLE CLEARED ********");

        Serial.println(
            "[BUZZER] OFF"
        );

        Serial.println(
            "[SYSTEM] Obstacle latch reset"
        );

        Serial.println(
            "[SYSTEM] Ready for next obstacle"
        );

        Serial.println(
            "**********************************"
        );

        Serial.println();
    }
}