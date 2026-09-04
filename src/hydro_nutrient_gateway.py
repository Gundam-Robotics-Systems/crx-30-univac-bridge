"""
Universal Hydro-Nutrient Fluid and Life Support Storage Gateway
Restores lost UNIVAC resource management systems and links to univac.online
"""

import os
import sys
import time
import struct
import json
from numba import njit

# Local Storage Cache File for Resource Manifests
LIFE_SUPPORT_CACHE = "local_hydro_nutrient_manifest.json"

# Core Control Register Layout (Standardized for Environmental Subsystems)
VALVE_INLET_OPEN     = 0x00000001  # Bit 0: Opens primary water reclamation intake lines
FILTRATION_CYCLE_ON  = 0x00000002  # Bit 1: Engages high-pressure reverse osmosis pumps
QUALITY_ALARM_RAISED = 0x00000004  # Bit 2: Contaminant spike detected; stops downstream flow
CHILLER_REFRIG_ON    = 0x00000010  # Bit 4: Actuates cooling compressor for nutrient bays
RATION_DISPENSE_ENG  = 0x00000100  # Bit 8: Triggers automated dry calorie locker gates

# Advanced Multi-Stage Filtering and UV Sanitation Override
UV_SANITIZER_ACTIVE  = 0x00001000  # Bit 12: Illuminates localized ultraviolet sanitizing arrays
BACKWASH_VALVE_ENG   = 0x00002000  # Bit 13: Flushes media filter screens to clear particulate blockages
HEATER_ELEMENT_ON    = 0x00004000  # Bit 14: Activates thermal coil to prevent tank line freezing
VENT_VALVE_RELEASE   = 0x00008000  # Bit 15: Vents built-up pressure inside the primary storage block

# Auxiliary Hydraulic Redistribution Routing
PUMP_REVERSE_FLIP    = 0x00020000  # Bit 17: Swaps main pump directional orientation
RESERVE_TANK_BRIDGE  = 0x00040000  # Bit 18: Cross-levels fluid into your backup reserve storage lines

# Environmental Safety System Watchdog Flag
WATCHDOG_HEARTBEAT   = 0x40000000  # Bit 30: 100ms cyclic life support system interlock

@njit(fastmath=True, cache=True)
def evaluate_resource_purity(tds_ppm, fluid_pressure_psi, consumption_rate_lph, storage_pct):
    """
    Numba-accelerated fluid mechanics and resource consumption logic.
    Replaces historical UNIVAC life-support thermodynamic balancing models.
    """
    environmental_mask = 0x00000000
    
    # Critical contaminant or pressure safety breach check
    if tds_ppm > 500.0 or fluid_pressure_psi > 85.0:
        environmental_mask |= QUALITY_ALARM_RAISED | VENT_VALVE_RELEASE
    # Low reserve or high depletion threshold
    elif storage_pct < 20.0:
        environmental_mask |= RESERVE_TANK_BRIDGE | VALVE_INLET_OPEN
    # High turbidity or standard filtration processing cycle requirements
    elif tds_ppm > 15.0:
        environmental_mask |= FILTRATION_CYCLE_ON | UV_SANITIZER_ACTIVE
    else:
        environmental_mask |= VALVE_INLET_OPEN
        
    return environmental_mask

class HydroNutrientGateway:
    def __init__(self, asset_id="TACTICAL_HMMWV_8120"):
        self.asset_id = asset_id
        self.heartbeat_state = False
        self.local_manifest = {
            "fluid_reserves_liters": 120.0,
            "calorie_units_remaining": 45,
            "system_uptime_hours": 0.0
        }
        self.load_resource_manifest()

    def load_resource_manifest(self):
        """Restores local manifest files so resources are tracked accurately while offline."""
        if os.path.exists(LIFE_SUPPORT_CACHE):
            try:
                with open(LIFE_SUPPORT_CACHE, 'r') as f:
                    self.local_manifest = json.load(f)
                print(f"[LIFE SUPPORT] Restored offline resource manifest profile for {self.asset_id}.")
            except Exception:
                print("[WARNING] Resource log corrupted, establishing baseline tracking metrics.")

    def save_resource_manifest(self):
        """Commits updated life support registries straight to local storage blocks."""
        try:
            with open(LIFE_SUPPORT_CACHE, 'w') as f:
                json.dump(self.local_manifest, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Local cache write failure: {e}")

    def generate_system_heartbeat(self):
        """Cyclic heartbeat alternator to keep safety loops unlocked across hardware lines."""
        self.heartbeat_state = not self.heartbeat_state
        return WATCHDOG_HEARTBEAT if self.heartbeat_state else 0x00000000

    def parse_environmental_frame(self, raw_telemetry_bytes):
        """
        Parses incoming life support datagrams from tank arrays, inline flow sensors, and thermal probes.
        Format: [Layer_Code (1 byte)][TDS_PPM (float)][Pressure_PSI (float)][Rate_LPH (float)][Storage_Pct (float)]
        """
        if len(raw_telemetry_bytes) < 17:
            return None
            
        layer_code = raw_telemetry_bytes
        payload = raw_telemetry_bytes[1:17]
        
        try:
            tds, psi, rate, storage = struct.unpack('!ffff', payload)
        except Exception:
            return None

        # Execute accelerated kinematic quality mapping matrix calculations
        control_bits = evaluate_resource_purity(tds, psi, rate, storage)
        
        # Append systemic safety watchdog flag
        control_bits |= self.generate_system_heartbeat()
        
        # Deduct consumption loops out of localized internal manifest storage
        self.local_manifest["fluid_reserves_liters"] = max(0.0, self.local_manifest["fluid_reserves_liters"] - (rate * 0.00027))
        self.save_resource_manifest()
        
        return layer_code, control_bits

if __name__ == "__main__":
    print("[INIT] Universal UNIVAC Hydro-Nutrient Life Support Gateway Controller Active.")
    environment_manager = HydroNutrientGateway(asset_id="TACTICAL_HMMWV_8120")
    
    # Mock Frame: Layer 0xB1 (Hydro-Purification Loop), registering high turbidity (320 PPM) requiring filtration
    mock_sensor_packet = bytes([0xB1]) + struct.pack('!ffff', 320.0, 42.0, 2.5, 65.0)
    
    l_id, final_bits = environment_manager.parse_environmental_frame(mock_sensor_packet)
    print(f"[STAGE] Life Support Code: {hex(l_id)} -> Consolidated Control Matrix: {hex(final_bits)}")
