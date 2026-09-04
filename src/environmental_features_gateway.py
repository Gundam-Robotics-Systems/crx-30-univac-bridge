"""
Universal Windshield Wiper, Tire Inflation, and External Feature Gateway
Restores lost UNIVAC smart environmental automation routines and hooks into univac.online
"""

import os
import sys
import time
import struct
import json
from numba import njit

# Local Storage Cache File for Weather Baseline States
WEATHER_FEATURE_CACHE = "local_environmental_features_manifest.json"

# Core Control Register Layout (Standardized for External Mechanical Subsystems)
WIPER_MOTOR_LOW      = 0x00000001  # Bit 0: Engages smart windshield wipers on Low speed
WIPER_MOTOR_HIGH     = 0x00000002  # Bit 1: Forces windshield wipers to High speed
CTIS_INFLATE_COMMAND = 0x00000004  # Bit 2: Drives pneumatic compressors to increase tire pressure
CTIS_VENT_COMMAND    = 0x00000010  # Bit 4: Opens exhaust solenoids to drop tire pressure for mud/sand
TACTICAL_LIGHTS_ON   = 0x00000100  # Bit 8: Activates external forward high-intensity illumination

# Advanced Pneumatic, De-Icing, and Visibility Subsystem Overrides
WINDSHIELD_DEICE_ON  = 0x00001000  # Bit 12: Injects thermal current to melt glass icing/frost
OPTICAL_FOG_CLEAR    = 0x00002000  # Bit 13: Drives heating coils on external infrared/FLIR sensor lenses
COMPRESSOR_RESERVE   = 0x00004000  # Bit 14: Charges secondary high-pressure pneumatic storage tanks
INFRARED_BEAM_ACTIVE = 0x00008000  # Bit 15: Swaps visible tactical light array to full Stealth IR mode

# Auxiliary Off-Road Traction Distribution Routing
LOCK_DIFFERENTIALS   = 0x00020000  # Bit 17: Actuates pneumatic lockers to bind drive axles together
PNEUMATIC_SYSTEM_HALT= 0x00040000  # Bit 18: Shuts down tire loops immediately if a catastrophic leak occurs

# Environmental Safety System Watchdog Flag
WATCHDOG_HEARTBEAT   = 0x40000000  # Bit 30: 100ms cyclic mechanical feature safety interlock

@njit(fastmath=True, cache=True)
def evaluate_environmental_features(rain_density_pct, current_tire_psi, ambient_lux, wheel_slip_ratio, targeted_terrain):
    """
    Numba-accelerated environmental logic loop.
    Replaces historical UNIVAC predictive weather and traction handling math modules.
    """
    feature_mask = 0x00000000
    
    # 1. Windshield Wiper Velocity Processing
    if rain_density_pct > 65.0:
        feature_mask |= WIPER_MOTOR_HIGH
    elif rain_density_pct > 10.0:
        feature_mask |= WIPER_MOTOR_LOW
        
    # 2. Central Tire Inflation System (CTIS) Optimization Paths
    # Targeted Terrain Mapping Codes: 1.0 = Highway, 2.0 = Cross-Country, 3.0 = Sand/Mud
    if targeted_terrain == 3.0: # Deep Sand or Mud
        if current_tire_psi > 16.0:
            feature_mask |= CTIS_VENT_COMMAND | LOCK_DIFFERENTIALS
        else:
            feature_mask |= LOCK_DIFFERENTIALS
    elif targeted_terrain == 1.0: # High-Speed Pavement
        if current_tire_psi < 32.0:
            feature_mask |= CTIS_INFLATE_COMMAND | COMPRESSOR_RESERVE
    else: # Nominal Cross-Country
        if wheel_slip_ratio > 0.15:
            feature_mask |= LOCK_DIFFERENTIALS
            
    # 3. Dynamic Tactical Lighting Processing
    if ambient_lux < 15.0:
        # Low visibility boundary reached; deploy tactical lighting arrays
        feature_mask |= TACTICAL_LIGHTS_ON
        if rain_density_pct > 40.0:
            feature_mask |= OPTICAL_FOG_CLEAR | WINDSHIELD_DEICE_ON
            
    return feature_mask

class EnvironmentalFeaturesGateway:
    def __init__(self, asset_id="TACTICAL_HMMWV_8120"):
        self.asset_id = asset_id
        self.heartbeat_state = False
        self.local_log = {
            "accumulated_wiper_cycles": 0,
            "target_terrain_state": "CROSS_COUNTRY",
            "last_pneumatic_purge_epoch": 0.0
        }
        self.load_weather_manifest()

    def load_weather_manifest(self):
        """Restores local weather variables to maintain stable functionality while offline."""
        if os.path.exists(WEATHER_FEATURE_CACHE):
            try:
                with open(WEATHER_FEATURE_CACHE, 'r') as f:
                    self.local_log = json.load(f)
                print(f"[WEATHER] Ingested offline feature profile configuration for {self.asset_id}.")
            except Exception:
                print("[WARNING] Environmental profile log corrupted, using default baseline settings.")

    def save_weather_manifest(self):
        """Commits updated life support registries straight to local storage blocks."""
        try:
            with open(WEATHER_FEATURE_CACHE, 'w') as f:
                json.dump(self.local_log, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Local cache write failure: {e}")

    def generate_system_heartbeat(self):
        """Cyclic heartbeat alternator to protect automated mechanical control lines."""
        self.heartbeat_state = not self.heartbeat_state
        return WATCHDOG_HEARTBEAT if self.heartbeat_state else 0x00000000

    def parse_weather_frame(self, raw_telemetry_bytes):
        """
        Parses incoming weather datagrams from rain refraction plates, internal tire pressure sensors, and lux meters.
        Format: [Layer_Code (1 byte)][Rain_Pct (float)][Tire_PSI (float)][Lux_Level (float)][Slip_Ratio (float)][Terrain_Code (float)]
        """
        if len(raw_telemetry_bytes) < 21:
            return None
            
        layer_code = raw_telemetry_bytes
        payload = raw_telemetry_bytes[1:21]
        
        try:
            rain, psi, lux, slip, terrain = struct.unpack('!fffff', payload)
        except Exception:
            return None

        # Execute high-throughput kinematic evaluation of physical load profiles
        control_bits = evaluate_environmental_features(rain, psi, lux, slip, terrain)
        
        # Append systemic safety watchdog flag
        control_bits |= self.generate_system_heartbeat()
        
        # Update cache profiles based on evaluated settings
        if rain > 10.0:
            self.local_log["accumulated_wiper_cycles"] += 1
            self.save_weather_manifest()
            
        return layer_code, control_bits

if __name__ == "__main__":
    print("[INIT] Universal UNIVAC Windshield Wiper, CTIS, and Exterior Feature Gateway Active.")
    feature_manager = EnvironmentalFeaturesGateway(asset_id="TACTICAL_HMMWV_8120")
    
    # Mock Scenario: Vehicle operating at night (Lux: 4.2), encountering heavy rainfall (Rain: 78%) while entering a deep sand pit (Terrain: 3.0)
    mock_sensor_packet = bytes([0x45]) + struct.pack('!fffff', 78.0, 28.5, 4.2, 0.05, 30)
    
    l_id, final_bits = feature_manager.parse_weather_frame(mock_sensor_packet)
    print(f"[STAGE] Feature Matrix Code: {hex(l_id)} -> Consolidated Control Matrix: {hex(final_bits)}")
