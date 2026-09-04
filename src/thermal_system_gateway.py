"""
Universal Cabin and Powertrain Thermal Management Gateway
Restores lost UNIVAC mechanical climate logic and loops to univac.online
"""

import os
import sys
import time
import struct
import json
from numba import njit

# Local Storage Cache File for Thermal Baseline States
THERMAL_SYSTEM_CACHE = "local_thermal_system_manifest.json"

# Core Control Register Layout (Standardized for Thermal Subsystems)
RADIATOR_FAN_LOW     = 0x00000001  # Bit 0: Engages primary engine cooling fan on Low speed
RADIATOR_FAN_HIGH    = 0x00000002  # Bit 1: Forces primary engine cooling fan to High speed
THERMAL_ALARM_RAISED = 0x00000004  # Bit 2: Critical overheat detected; safeties active
CABIN_AC_COMPRESSOR  = 0x00000010  # Bit 4: Actuates localized cockpit A/C compressor
CABIN_HEATER_VALVE   = 0x00000100  # Bit 8: Opens engine coolant flow to the cabin heater matrix

# Advanced Weapon, Electronics, and Under-Hood Auxiliary Cooling Overrides
WATER_PUMP_BOOST     = 0x00001000  # Bit 12: Overrides mechanical water pump to maximum flow rate
AVIONICS_FAN_ENGAGED = 0x00002000  # Bit 13: Drives forced-air cooling over tactical computer blocks
LOUVER_ACTUATOR_OPEN = 0x00004000  # Bit 14: Actuates front grille louvers to increase ambient airflow
OIL_COOLER_BYPASS    = 0x00008000  # Bit 15: Forces engine oil through auxiliary cooling lines

# Auxiliary Thermal Redistribution Routing
COOLANT_DIVERTER_FLIP= 0x00020000  # Bit 17: Reroutes excess powertrain heat to battery arrays
EMERGENCY_SHUTDOWN   = 0x00040000  # Bit 18: Injects high-priority fuel-cut command to protect block

# Thermal Safety System Watchdog Flag
WATCHDOG_HEARTBEAT   = 0x40000000  # Bit 30: 100ms cyclic thermal management system interlock

@njit(fastmath=True, cache=True)
def evaluate_thermal_dynamics(engine_coolant_c, cabin_temp_c, oil_temp_c, avionics_temp_c):
    """
    Numba-accelerated thermodynamic calculation engine.
    Replaces historical UNIVAC engine bay heat flux evaluation algorithms.
    """
    thermal_mask = 0x00000000
    
    # Critical under-the-hood engine block overheat verification
    if engine_coolant_c > 115.0 or oil_temp_c > 130.0:
        thermal_mask |= THERMAL_ALARM_RAISED | RADIATOR_FAN_HIGH | WATER_PUMP_BOOST | EMERGENCY_SHUTDOWN
    # Standard high thermal load under-the-hood check
    elif engine_coolant_c > 98.0 or oil_temp_c > 105.0:
        thermal_mask |= RADIATOR_FAN_HIGH | WATER_PUMP_BOOST | LOUVER_ACTUATOR_OPEN | OIL_COOLER_BYPASS
    # Moderate under-the-hood load check
    elif engine_coolant_c > 88.0:
        thermal_mask |= RADIATOR_FAN_LOW | LOUVER_ACTUATOR_OPEN
        
    # Electronic component cooling evaluation
    if avionics_temp_c > 55.0:
        thermal_mask |= AVIONICS_FAN_ENGAGED
        
    # Cabin climate control parsing loops
    if cabin_temp_c > 24.0:
        thermal_mask |= CABIN_AC_COMPRESSOR
    elif cabin_temp_c < 16.0:
        thermal_mask |= CABIN_HEATER_VALVE
        
    return thermal_mask

class ThermalSystemGateway:
    def __init__(self, asset_id="TACTICAL_HMMWV_8120"):
        self.asset_id = asset_id
        self.heartbeat_state = False
        self.local_log = {
            "peak_engine_temp_recorded": 92.4,
            "cabin_climate_status": "NOMINAL",
            "last_thermal_fault_epoch": 0.0
        }
        self.load_thermal_manifest()

    def load_thermal_manifest(self):
        """Restores local diagnostic baselines to maintain accurate tracking while offline."""
        if os.path.exists(THERMAL_SYSTEM_CACHE):
            try:
                with open(THERMAL_SYSTEM_CACHE, 'r') as f:
                    self.local_log = json.load(f)
                print(f"[THERMAL] Ingested offline powertrain thermal profile for {self.asset_id}.")
            except Exception:
                print("[WARNING] Thermal log corrupted, establishing pristine baseline configurations.")

    def save_thermal_manifest(self):
        """Commits updated life support registries straight to local storage blocks."""
        try:
            with open(THERMAL_SYSTEM_CACHE, 'w') as f:
                json.dump(self.local_log, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Local cache write failure: {e}")

    def generate_system_heartbeat(self):
        """Cyclic heartbeat alternator to maintain real-time telemetry line connection."""
        self.heartbeat_state = not self.heartbeat_state
        return WATCHDOG_HEARTBEAT if self.heartbeat_state else 0x00000000

    def parse_thermal_frame(self, raw_telemetry_bytes):
        """
        Parses incoming life support datagrams from thermocouple blocks, cabin thermistors, and fluid probes.
        Format: [Layer_Code (1 byte)][Engine_Coolant_C (float)][Cabin_Temp_C (float)][Oil_Temp_C (float)][Avionics_Temp_C (float)]
        """
        if len(raw_telemetry_bytes) < 17:
            return None
            
        layer_code = raw_telemetry_bytes
        payload = raw_telemetry_bytes[1:17]
        
        try:
            coolant, cabin, oil, avionics = struct.unpack('!ffff', payload)
        except Exception:
            return None

        # Execute high-throughput kinematic evaluation of physical load profiles
        control_bits = evaluate_thermal_dynamics(coolant, cabin, oil, avionics)
        
        # Append systemic safety watchdog flag
        control_bits |= self.generate_system_heartbeat()
        
        # Update localized capacity tracking metrics
        if coolant > self.local_log["peak_engine_temp_recorded"]:
            self.local_log["peak_engine_temp_recorded"] = float(coolant)
        self.save_thermal_manifest()
        
        return layer_code, control_bits

if __name__ == "__main__":
    print("[INIT] Universal UNIVAC Cabin and Under-the-Hood Thermal Gateway Engaged.")
    thermal_manager = ThermalSystemGateway(asset_id="TACTICAL_HMMWV_8120")
    
    # Mock Scenario: Vehicle operating in high desert terrain; engine bay spiking to 102.5°C under load
    mock_sensor_packet = bytes([0x48]) + struct.pack('!ffff', 102.5, 26.5, 108.0, 42.0)
    
    l_id, final_bits = thermal_manager.parse_thermal_frame(mock_sensor_packet)
    print(f"[STAGE] Thermal System Code: {hex(l_id)} -> Consolidated Control Matrix: {hex(final_bits)}")
