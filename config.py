# ============================================================
# AZIZA - Distributed Automotive ECU Simulation
# config.py — Central configuration for the AZIZA system
# ============================================================

PROJECT_NAME = "AZIZA"

# --- Blynk ---
BLYNK_AUTH_TOKEN = "YOUR_BLYNK_TOKEN_HERE"  # Replace with your Blynk token
BLYNK_SERVER = "blynk.cloud"
BLYNK_PORT = 80

# --- Simulation ---
SIMULATION_CYCLE_SECONDS = 1.0   # Sleep between each main loop cycle
SIMULATION_DURATION = None        # None = run forever

# --- CAN Message IDs ---
CAN_ID_TEMPERATURE = 0x101
CAN_ID_SPEED       = 0x102
CAN_ID_BRAKE       = 0x201

# --- Sensor Ranges ---
SENSOR_SPEED_MIN        = 0
SENSOR_SPEED_MAX        = 150      # km/h
SENSOR_TEMP_MIN         = 70
SENSOR_TEMP_MAX         = 130      # °C
SENSOR_BRAKE_MIN        = 0.0
SENSOR_BRAKE_MAX        = 1.0

# --- Engine Thresholds ---
ENGINE_TEMP_WARN        = 100      # °C — throttle reduction
ENGINE_TEMP_LIMIT       = 120      # °C — engine LIMITED

# --- Safety Thresholds ---
SAFETY_MAX_SPEED        = 150      # km/h hard cap
SAFETY_MAX_TEMP         = 125      # °C hard cap
SAFETY_MIN_BRAKE        = 0.0

# --- AI Risk Scoring ---
AI_TEMP_RISE_THRESHOLD  = 5        # °C rise per cycle to flag
AI_HIGH_SPEED_THRESHOLD = 100      # km/h — relevant for brake+speed check
AI_RISK_CRITICAL        = 5
AI_RISK_SUSPICIOUS      = 2

# --- LIN Bus ---
LIN_MASTER_ID = "BODY_MASTER"

# --- Blynk Virtual Pins ---
VPIN_SPEED         = "V0"
VPIN_TEMPERATURE   = "V1"
VPIN_BRAKE         = "V2"
VPIN_ENGINE_STATE  = "V3"
VPIN_AI_RISK       = "V4"
VPIN_CRUISE_TOGGLE = "V5"

# --- Logging ---
LOG_PREFIX = {
    "CAN":    "[CAN]   ",
    "LIN":    "[LIN]   ",
    "ENGINE": "[ENGINE]",
    "BRAKE":  "[BRAKE] ",
    "SENSOR": "[SENSOR]",
    "BODY":   "[BODY]  ",
    "SAFETY": "[SAFETY]",
    "AI":     "[AI]    ",
    "BLYNK":  "[BLYNK] ",
    "AZIZA":  "[AZIZA] ",
}
