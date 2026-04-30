# ============================================================
# AZIZA - Car Control ECU (Body Control Module Simulation)
# Handles: windows, lights, door locks (LIN domain)
# ============================================================

class CarControlECU:
    def __init__(self, can_bus, lin_bus):
        self.can_bus = can_bus
        self.lin_bus = lin_bus

        # --- Vehicle state from CAN ---
        self.vehicle_speed = 0.0

        # --- Windows (0 = closed, 100 = fully open) ---
        self.windows = {
            "positions": {0: 0, 1: 0, 2: 0, 3: 0},  # FL, FR, RL, RR
            "targets":   {0: 0, 1: 0, 2: 0, 3: 0}
        }

        # --- Lights ---
        self.lights = {
            "headlights": "OFF",
            "interior":   "OFF",
            "hazard":     "OFF",
            "fog":        "OFF",
        }

        # --- Door locks ---
        self.door_locks = {
            "FL": True,
            "FR": True,
            "RL": True,
            "RR": True,
            "all_locked": True,
        }

        # --- Commands from external system (server / UI) ---
        self._commands = []

    # ========================================================
    # CAN MESSAGE PROCESSING
    # ========================================================
    def process_can_messages(self, messages):
        for msg in messages:
            if hasattr(msg, "msg_id"):
                msg_id = msg.msg_id
            elif hasattr(msg, "id"):
                msg_id = msg.id
            elif hasattr(msg, "arbitration_id"):            
                msg_id = msg.arbitration_id
            else:
                continue  # unknown format

            if hasattr(msg, "data"):
                data = msg.data
            elif hasattr(msg, "payload"):
                data = msg.payload
            else:
                continue

        # --- YOUR LOGIC ---
            if msg_id == 0x102:
                self.vehicle_speed = data

    # ========================================================
    # EXTERNAL COMMAND INTERFACE (called by server)
    # ========================================================
    def apply_command(self, command: dict):
        """
        Example commands:
        {"type": "window", "index": 0, "target": 100}
        {"type": "lock", "action": "unlock_all"}
        {"type": "light", "name": "headlights", "value": "ON"}
        """
        self._commands.append(command)

    # ========================================================
    # UPDATE LOOP
    # ========================================================
    def update(self, vehicle_speed=None):
        if vehicle_speed is not None:
            self.vehicle_speed = vehicle_speed

        # 1) Apply external commands
        self._process_commands()

        # 2) Automatic behaviors (realistic features)
        self._auto_lock_doors()
        self._auto_lights()

        # 3) Update actuators (LIN simulation)
        self._update_windows()

        return {
            "windows": self.windows,
            "lights": self.lights,
            "door_locks": self.door_locks
        }

    # ========================================================
    # COMMAND HANDLING
    # ========================================================
    def _process_commands(self):
        while self._commands:
            cmd = self._commands.pop(0)

            if cmd["type"] == "window":
                idx = cmd.get("index", 0)
                target = max(0, min(100, cmd.get("target", 0)))
                self.windows["targets"][idx] = target

            elif cmd["type"] == "lock":
                if cmd.get("action") == "lock_all":
                    self._set_all_locks(True)
                elif cmd.get("action") == "unlock_all":
                    self._set_all_locks(False)

            elif cmd["type"] == "light":
                name = cmd.get("name")
                value = cmd.get("value", "OFF")
                if name in self.lights:
                    self.lights[name] = value

    # ========================================================
    # AUTOMATIC LOGIC (REALISTIC BEHAVIOR)
    # ========================================================
    def _auto_lock_doors(self):
        # Lock all doors if speed > 20 km/h
        if self.vehicle_speed > 20 and not self.door_locks["all_locked"]:
            self._set_all_locks(True)

    def _auto_lights(self):
        # Simple rule: headlights ON if speed > 0 (simulate driving)
        if self.vehicle_speed > 0:
            self.lights["headlights"] = "ON"
        else:
            self.lights["headlights"] = "OFF"

    # ========================================================
    # WINDOW CONTROL (SIMULATED MOTOR)
    # ========================================================
    def _update_windows(self):
        for idx in self.windows["positions"]:
            current = self.windows["positions"][idx]
            target  = self.windows["targets"][idx]

            if current < target:
                current += 5
            elif current > target:
                current -= 5

            self.windows["positions"][idx] = max(0, min(100, current))

            # Simulate sending command over LIN
            self.lin_bus_request(f"window_{idx}", current)

    # ========================================================
    # DOOR LOCK HELPERS
    # ========================================================
    def _set_all_locks(self, locked: bool):
        self.door_locks["FL"] = locked
        self.door_locks["FR"] = locked
        self.door_locks["RL"] = locked
        self.door_locks["RR"] = locked
        self.door_locks["all_locked"] = locked

    # ========================================================
    # LIN BUS SIMULATION
    # ========================================================
    def lin_bus_request(self, device, value):
        """
        Simulate sending command to LIN slave device
        """
        try:
            self.lin_bus.request(device, value)
        except Exception:
            pass