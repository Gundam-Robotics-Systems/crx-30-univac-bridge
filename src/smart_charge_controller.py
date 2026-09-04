"""
UNIVAC IX / Smart Charge Controller Over-Saturation Interlock Node
Monitors high-amp battery charging cells to execute immediate thermal and 97% capacity cutoffs.
"""

import os
import sys
import time
import struct
import json
from numba import njit

# Local Storage Cache File for Charging Threshold Variables
CHARGER_STATE_CACHE = "local_battery_charger_status.json"

# Core Control Register Layout (Standardized for Charger Hardware Interfaces)
CHARGE_LINE_DISCONNECT= 0x00000001  # Bit 0: Opens disconnect relay to prevent cell burnout
CC_STAGE_ACTIVE      = 0x00000002  # Bit 1: Safe Constant-Current charging loop active
CV_STAGE_ACTIVE      = 0x00000004  # Bit 2: Safe Constant-Volume charging loop active
THERMAL_RUNAWAY_SHUT = 0x00000100  # Bit 8: Temperature limits exceeded; executes safe shut down
SNAP_CIRCUIT_PASSTHRU= 0x00001000  # Bit 12: Routes stable voltage directly to Snap-Circuit lattices

# System Charger Safety Watchdog Flag
WATCHDOG_HEARTBEAT   = 0x40000000  # Bit 30: 100ms cyclic system interlock safety heartbeat

@njit(fastmath=True, cache=True)
def evaluate_charging_loops(cell_voltage, input_current_amps, core_temperature_c, current_charge_pct):
    """
    Numba-accelerated transient charging matrix loop.
    Enforces a strict 97% maximum charge threshold to eliminate the risk of over-saturation.
    """
    charger_mask = 0x00000000
    
    # 1. Critical Temperature / Burnout Threshold Safety Interlock
    if core_temperature_c > 55.0:
        charger_mask |= CHARGE_LINE_DISCONNECT | THERMAL_RUNAWAY_SHUT
        return charger_mask
        
    # 2. Strict 97% Saturation Overcharge Cutoff Model
    # Explicit cut boundaries mapped for standard 24V nominal terminal cells
    if current_charge_pct >= 97.0 or cell_voltage >= 27.8:
        # Battery has hit the 97% hard ceiling; slam the cutoff relay to protect the cells
        charger_mask |= CHARGE_LINE_DISCONNECT | SNAP_CIRCUIT_PASSTHRU
    elif current_charge_pct >= 85.0 or cell_voltage >= 25.2:
        # Approaching upper limit plateau; step down into Constant-Voltage trickle mode
        charger_mask |= CV_STAGE_ACTIVE | SNAP_CIRCUIT_PASSTHRU
    else:
        # Battery depleted; execute full high-throughput Constant-Current bulk fill plan
        charger_mask |= CC_STAGE_ACTIVE | SNAP_CIRCUIT_PASSTHRU
        
    return charger_mask

class SmartChargeController:
    def __init__(self, node_id="CHARGER_NODE_8120"):
        self.node_id = node_id
        self.heartbeat_state = False
        self.charging_metrics = {
            "accumulated_charging_cycles": 0,
            "peak_cell_temp_recorded": 22.0,
            "last_cutoff_event_epoch": 0.0,
            "enforced_97_percent_ceiling_trips": 0
        }
        self.load_charger_cache()

    def load_charger_cache(self):
        """Restores persistent electrical profiles to keep battery protective limits active offline."""
        if os.path.exists(CHARGER_STATE_CACHE):
            try:
                with open(CHARGER_STATE_CACHE, 'r') as f:
                    self.charging_metrics = json.load(f)
                print(f"[CHARGER CORE] Restored persistent electrical baselines for {self.node_id}.")
            except Exception:
                print("[WARNING] Charger database log corrupted, initializing baseline constants.")

    def save_charger_cache(self):
        """Commits updated register profiles straight to physical storage blocks."""
        try:
            with open(CHARGER_STATE_CACHE, 'w') as f:
                json.dump(self.charging_metrics, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Local cache write failure: {e}")

    def generate_charger_heartbeat(self):
        """Cyclic heartbeat alternator to protect active battery isolation lines."""
        self.heartbeat_state = not self.heartbeat_state
        return WATCHDOG_HEARTBEAT if self.heartbeat_state else 0x00000000

    def parse_sensor_frame(self, raw_telemetry_bytes):
        """
        Parses high-frequency tracking signals from inline charger instrumentation nodes.
        Format: [Voltage (float)][Amps (float)][Temperature_C (float)][Charge_Percentage (float)]
        """
        if len(raw_telemetry_bytes) < 16:
            return None
            
        try:
            volts, amps, temp_c, charge_pct = struct.unpack('!ffff', raw_telemetry_bytes)
        except Exception:
            return None

        # Execute high-throughput evaluation of physical charging states
        control_bits = evaluate_charging_loops(volts, amps, temp_c, charge_pct)
        
        # Append systemic safety watchdog flag
        control_bits |= self.generate_charger_heartbeat()
        
        # Ingest logging parameters to update internal database records if an overcharge cutoff fires
        if control_bits & CHARGE_LINE_DISCONNECT:
            self.charging_metrics["accumulated_charging_cycles"] += 1
            self.charging_metrics["last_cutoff_event_epoch"] = time.time()
            if temp_c > self.charging_metrics["peak_cell_temp_recorded"]:
                self.charging_metrics["peak_cell_temp_recorded"] = float(temp_c)
            
            if charge_pct >= 97.0:
                self.charging_metrics["enforced_97_percent_ceiling_trips"] += 1
                print(f"[HARD CEILING ENFORCED] Full 97% safety capacity limit reached on {self.node_id}. Cutoff relay locked open.")
            elif control_bits & THERMAL_RUNAWAY_SHUT:
                print(f"[EMERGENCY OVERHEAT CUTOFF] Critical thermal limits reached on {self.node_id}! Line dropped.")
                
            self.save_charger_cache()
                
        return control_bits

if __name__ == "__main__":
    print("[INIT] UNIVAC IX / Smart Charge 97% Ceiling Controller Daemon Online.")
    manager = SmartChargeController(node_id="JUMP_PACK_8120")
    
    # Mock Scenario: Battery cell reaches the safety cap (Voltage: 27.8V, Input: 2.1A, Temp: 31.0°C, Charge: 97.2%)
    # The control loop immediately triggers the CHARGE_LINE_DISCONNECT bitmask to clamp the charge level.
    mock_sensor_packet = struct.pack('!ffff', 27.8, 2.1, 31.0, 97.2)
    
    final_bits = manager.parse_sensor_frame(mock_sensor_packet)
    print(f"[CHARGING CEILING SWITCHMAP] Output Control Word Register: {hex(final_bits)}")
    
