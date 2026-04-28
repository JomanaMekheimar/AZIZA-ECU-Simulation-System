# ============================================================
# AZIZA - Distributed Automotive ECU Simulation
# ecu/sensor_ecu.py — Sensor ECU (speed, temperature, brake)
# ============================================================

import random
import math
from config import (
    LOG_PREFIX,
    CAN_ID_TEMPERATURE, CAN_ID_SPEED, CAN_ID_BRAKE,
    SENSOR_SPEED_MIN, SENSOR_SPEED_MAX,
    SENSOR_TEMP_MIN, SENSOR_TEMP_MAX,
    SENSOR_BRAKE_MIN, SENSOR_BRAKE_MAX,
)


class SensorECU:
    """
    AZIZA Sensor ECU.

    Simulates physical vehicle sensors and publishes readings
    onto the CAN bus. All values are deterministic with smooth
    realistic transitions — no random jumps.

    CAN IDs published:
        0x101 → engine temperature (°C)
        0x102 → vehicle speed (km/h)
        0x201 → brake pressure (0.0–1.0)
    """

    def __init__(self, can_bus):
        self.can_bus = can_bus

        # Internal state — smooth simulation
        self._speed: float = 0.0
        self._temperature: float = 80.0
        self._brake: float = 0.0

        # Simulation trajectory helpers
        self._target_speed: float = 60.0
        self._cycle: int = 0

        print(f"{LOG_PREFIX['SENSOR']} SensorECU initialized.")

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def read_and_publish(self) -> dict:
        """
        Sample all sensors, publish to CAN bus, and return raw readings.
        Called once per main loop cycle.
        """
        self._cycle += 1
        self._update_speed()
        self._update_temperature()
        self._update_brake()

        readings = {
            "speed":       round(self._speed, 1),
            "temperature": round(self._temperature, 1),
            "brake":       round(self._brake, 2),
        }

        # Publish to CAN bus
        self.can_bus.send(CAN_ID_TEMPERATURE, {"temp": readings["temperature"]})
        self.can_bus.send(CAN_ID_SPEED,       {"speed": readings["speed"]})
        self.can_bus.send(CAN_ID_BRAKE,       {"brake": readings["brake"]})

        print(
            f"{LOG_PREFIX['SENSOR']} "
            f"Speed={readings['speed']} km/h  "
            f"Temp={readings['temperature']} °C  "
            f"Brake={readings['brake']}"
        )

        return readings

    @property
    def speed(self) -> float:
        return round(self._speed, 1)

    @property
    def temperature(self) -> float:
        return round(self._temperature, 1)

    @property
    def brake(self) -> float:
        return round(self._brake, 2)

    # ------------------------------------------------------------------
    # Private simulation helpers
    # ------------------------------------------------------------------

    def _update_speed(self) -> None:
        """
        Smooth speed simulation: gradually accelerate / decelerate toward
        a target speed. Target changes periodically to simulate driving.
        """
        # Change target speed every ~15 cycles
        if self._cycle % 15 == 0:
            self._target_speed = random.uniform(
                SENSOR_SPEED_MIN + 10,
                SENSOR_SPEED_MAX - 10
            )

        delta = self._target_speed - self._speed
        self._speed += delta * 0.15 + random.uniform(-0.5, 0.5)
        self._speed = max(SENSOR_SPEED_MIN, min(SENSOR_SPEED_MAX, self._speed))

    def _update_temperature(self) -> None:
        """
        Temperature rises with speed/load, cools slowly.
        Injects occasional spikes to trigger AI anomaly detection.
        """
        load_factor = self._speed / SENSOR_SPEED_MAX
        natural_heat = load_factor * 0.8
        cooling = 0.3 if self._temperature > 90 else 0.0

        # Occasional thermal spike every ~40 cycles
        spike = 4.0 if (self._cycle % 40 == 0) else 0.0

        self._temperature += natural_heat - cooling + spike + random.uniform(-0.2, 0.2)
        self._temperature = max(SENSOR_TEMP_MIN, min(SENSOR_TEMP_MAX, self._temperature))

    def _update_brake(self) -> None:
        """
        Simulate brake events: brief, random brake applications.
        Every ~10 cycles there is a chance of braking.
        """
        if self._cycle % 10 == 0 and random.random() < 0.3:
            # Brake event
            self._brake = random.uniform(0.3, 0.9)
        else:
            # Release brake gradually
            self._brake = max(0.0, self._brake - 0.15)
        self._brake = max(SENSOR_BRAKE_MIN, min(SENSOR_BRAKE_MAX, self._brake))
