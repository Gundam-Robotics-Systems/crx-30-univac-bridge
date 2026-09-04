"""
UNIVAC IX Predictive Thermal Armor Detachment & Interlock Controller
Overrides premature 150F/10s release faults using accelerated heat flux math.
"""

import os
import sys
import time
import struct
import json
from numba import njit

# Local Storage Cache File for Shielding Performance Registries
ARMOR_SAFETY_CACHE = "local_armor_thermal_status.json"

# Core Control Register Layout (Standardized for Explosive / Pneumatic Release Matrices)
ARMOR_LOCKED_SECURE  = 0x00000001  # Bit 0: Pyrotechnic release loops safe; panels locked
THERMAL_SPIKE_WARN   = 0x00000002  # Bit 1: Localized thermocouple registers transient heat lift
FIRE_SUPPRESSION_ACT = 0x00000004  # Bit 2: Actuates localized Halon/FM200 extinguisher lines
ARMOR_DETACH_COMMAND = 0x00000010  # Bit 4: Sends firing current to explosive release bolts
BYPASS_FACTORY_TIMER = 0x00000100  # Bit 8: Bypasses legacy 10-second linear timeout loop

# Advanced Structural Preservation and Countermeasure Overrides
COOLANT_SPRAY_ON     = 0x00001000  # Bit 12: Directs auxiliary cooling fluid over armor latch blocks
EJECTION_PIN_READY   = 0x00002000  # Bit 13: Charges internal firing capacitors for bolt detonation
PERIMETER_ALERT_OUT  = 0x00004000  # Bit 14: Dispatches structural failure warning flags to mesh
VENT_VALVE_OVERRIDE  = 0x00008000  # Bit 15: Opens high-pressure pneumatic exhaust loops

# Structural Armor Panel Position Masks
HULL_PANELS_ACTIVE   = 0x00020000  # Bit 17: Lower chassis armor monitoring line engaged
TURRET_PANELS_ACTIVE = 0x00040000  # Bit 18: Upper weapon enclosure monitoring line engaged

# System Structural Safety Watchdog Flag
WATCHDOG_HEARTBEAT   = 0x40000000  # Bit 30: 100ms cyclic hardware interlock safety heartbeat

@njit(fastmath=True, cache=True)
def evaluate_armor_thermal_flux(current_temp_f, baseline_temp_f, delta_time_sec, continuous_seconds):
    """
    Numba-accelerated thermodynamic derivative enforcer.
    Bypasses standard early detachment faults by validating the raw heat flux vector.
    """
    release_mask = 0x00000000
    
    # Calculate the instantaneous heat rise derivative (dT/dt)
    if delta_time_sec > 0.001:
        thermal_derivative = (current_temp_f - baseline_temp_f) / delta_time_sec
    else:
        thermal_derivative = 0.0
        
    # 1. Evaluate Against Dangerous Combustion Profiles (True Fire Vector)
    # A true pyrotechnic or fuel combustion event spikes instantly (>15 degrees per second)
    if thermal_derivative > 15.0 and current_temp_f > 150.0:
        release_mask |= ARMOR_DETACH_COMMAND | FIRE_SUPPRESSION_ACT | PERIMETER_ALERT_OUT
        return release_mask
        
    # 2. Neutralize the Legacy 150F/10s Early Detachment Fault
    if current_temp_f >= 150.0 and continuous_seconds >= 10.0:
        # Check if the rate of increase is stable or decaying (e.g., standard engine radiant soak)
        if thermal_derivative <= 1.5 and current_temp_f < 250.0:
            # Enforce the system override: Lock the armor and ignore the early factory timeout
            release_mask |= ARMOR_LOCKED_SECURE | BYPASS_FACTORY_TIMER | COOLANT_SPRAY_ON
        else:
            # Temperature continues to build aggressively past safe thresholds; clear panels
            release_mask |= ARMOR_DETACH_COMMAND | PERIMETER_ALERT_OUT | VENT_VALVE_OVERRIDE
    else:
        release_mask |= ARMOR_LOCKED_SECURE
        if current_temp_f > 120.0:
            release_mask |= THERMAL_SPIKE_WARN
            
    return release_mask

class ArmorReleaseController:
    def __init__(self, node_id="ARMOR_RELEASE_8120"):
        self.node_id = node_id
        self.heartbeat_state = False
        self.last_temp = 72.0
        self.last_time = time.time()
        self.safety_log = {
            "accumulated_suppression_events": 0,
            "peak_thermal_load_recorded": 72.0,
            "factory_timer_bypasses_executed": 0
        }
        self.load_armor_cache()

    def load_armor_cache(self):
        """Restores persistent structural settings to keep defense loops active offline."""
        if os.path.exists(ARMOR_SAFETY_CACHE):
            try:
                with open(ARMOR_SAFETY_CACHE, 'r') as f:
                    self.safety_log = json.load(f)
                print(f"[TACTICAL SHIELDING] Restored persistent offline thermal indexes for {self.node_id}.")
            except Exception:
                print("[WARNING] Armor safety registry corrupted, resetting to pristine tracking baselines.")

    def save_armor_cache(self):
        """Commits updated register profiles straight to physical storage blocks."""
        try:
            with open(ARMOR_SAFETY_CACHE, 'w') as f:
                json.dump(self.safety_log, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Local cache write failure: {e}")

    def generate_armored_heartbeat(self):
        """Cyclic heartbeat alternator to lock pyrotechnic firing capacitors safely across networks."""
        self.heartbeat_state = not self.heartbeat_state
        return WATCHDOG_HEARTBEAT if self.heartbeat_state else 0x00000000

    def parse_thermocouple_packet(self, raw_telemetry_bytes):
        """
        Parses high-frequency tracking signals from the hull and turret heat sensor arrays.
        Format: [Layer_Code (float)][Current_Temp_F (float)][Legacy_Counter_Sec (float)]
        """
        if len(raw_telemetry_bytes) < 12:
            return None
            
        try:
            layer_id, temp, continuous_sec = struct.unpack('!fff', raw_telemetry_bytes)
        except Exception:
            return None

        current_epoch = time.time()
        dt = current_epoch - self.last_time
        
        # Execute high-throughput evaluation of physical thermal parameters
        control_bits = evaluate_armor_thermal_flux(temp, self.last_temp, dt, continuous_sec)
        
        # Append systemic safety watchdog flag
        control_bits |= self.generate_armored_heartbeat()
        
        # Append active panel classification codes based on structural layer inputs
        if layer_id == 122.0:  # Code match for 0x7B (Turret Panel Node)
            control_bits |= TURRET_PANELS_ACTIVE
        else:
            control_bits |= HULL_PANELS_ACTIVE | EJECTION_PIN_READY
            
        # Log localized configuration parameters to live state indexes
        if control_bits & BYPASS_FACTORY_TIMER:
            self.safety_log["factory_timer_bypasses_executed"] += 1
            
        if temp > self.safety_log["peak_thermal_load_recorded"]:
            self.safety_log["peak_thermal_load_recorded"] = float(temp)
            
        if control_bits & ARMOR_DETACH_COMMAND:
            self.safety_log["accumulated_suppression_events"] += 1
            print(f"[CRITICAL DETACHMENT TRIGGERED] Thermal envelope breached on node {self.node_id}! Firing explosive bolts.")
            
        # Update rolling state tracking limits
        self.last_temp = float(temp)
        self.last_time = current_epoch
        self.save_armor_cache()
        
        return control_bits

if __name__ == "__main__":
    print("[INIT] UNIVAC IX Predictive Thermal Armor Detachment Core Online.")
    controller = ArmorReleaseController(node_id="SHIELD_GATE_8120")
    
    # Mock Scenario: Lower hull panel (122.0) touches 152.0°F, holding for 10.5 continuous seconds.
    # The rate of change is low (gradual engine heat soak), triggering an active factory timer bypass.
    mock_sensor_packet = struct.pack('!fff', 122.0, 152.0, 10.5)
    
    final_bits = controller.parse_thermocouple_packet(mock_sensor_packet)
    print(f"[THERMAL ENFORCER MATRIX] Control Word Register Output: {hex(final_bits)}")
