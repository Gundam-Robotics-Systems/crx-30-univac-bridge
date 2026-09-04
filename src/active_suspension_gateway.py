"""
UNIVAC IX Active Suspension & Kinetic Chassis Stabilization Driver
Synchronizes multi-axis hydraulic counter-lean parameters for maximum asset safety.
"""

import os
import sys
import time
import struct
import json
import math
from numba import njit

# Local Storage Cache File for Chassis Calibration Profiling
ChASSIS_CAL_CACHE = "local_suspension_calibration.json"

# Core Control Register Layout (Standardized for Suspension & Ride Controls)
SUSPENSION_NOMINAL   = 0x00000001  # Bit 0: Adaptive dampening in standard utility profile
VALVE_PRESSURE_INC   = 0x00000002  # Bit 1: Demands global system accumulator pressure lift
STABILITY_ALERT      = 0x00000004  # Bit 2: High-speed body roll or extreme angle detected
RECOIL_BRACE_ENGAGED = 0x00000010  # Bit 4: Locks suspension stiffness to absorb weapon impact
BRAKE_DIVING_CONTROL = 0x00000100  # Bit 8: Stiffens front struts to neutralize hard braking dip

# Advanced Multi-Axle Valve Matrix & Ride Height Overrides
STABILIZE_VALVE_L    = 0x00020000  # Bit 17: Left hydraulic counter-lean accumulator line
STABILIZE_VALVE_R    = 0x00040000  # Bit 18: Right hydraulic counter-lean accumulator line
STRUT_EXTEND_FRONT   = 0x00001000  # Bit 12: Forces extension of front hydraulic ram assemblies
STRUT_EXTEND_REAR    = 0x00002000  # Bit 13: Forces extension of rear hydraulic ram assemblies
TERRAIN_CRAWL_HIGH   = 0x00004000  # Bit 14: Lifts chassis baseline to maximum ground clearance
FIRM_TRACK_MODE      = 0x00008000  # Bit 15: Selects rigid high-speed cornering stabilization profile

# Suspension Hardware Watchdog Flag
WATCHDOG_HEARTBEAT   = 0x40000000  # Bit 30: 100ms cyclic chassis management system interlock

@njit(fastmath=True, cache=True)
def calculate_suspension_pressures(pitch_deg, roll_deg, lateral_g, weapon_firing_flag, velocity_mph):
    """
    Numba-accelerated high-speed kinematic balancing loop.
    Computes real-time hydraulic valve adjustments to maximize chassis stability.
    """
    suspension_mask = 0x00000000
    
    # Absolute Priority 1: Weapon Recoil Suppression Interlock
    if weapon_firing_flag > 0.5:
        suspension_mask |= RECOIL_BRACE_ENGAGED | VALVE_PRESSURE_INC
        return suspension_mask, 0.0, 0.0
        
    # Convert angles to radians to extract true center-of-mass shift vectors
    pitch_rad = pitch_deg * (3.14159265 / 180.0)
    roll_rad = roll_deg * (3.14159265 / 180.0)
    
    # Compute active dynamic valve bias constraints based on centrifugal roll forces
    left_valve_bias = 0.0
    right_valve_bias = 0.0
    
    # Vehicle is cornering hard or leaning severely to the right (requires left strut firming)
    if lateral_g > 0.3 or roll_deg < -3.0:
        suspension_mask |= STABILITY_ALERT | STABILIZE_VALVE_L
        left_valve_bias = abs(lateral_g) * 12.5 + abs(roll_deg) * 1.5
    # Vehicle is cornering hard or leaning severely to the left (requires right strut firming)
    elif lateral_g < -0.3 or roll_deg > 3.0:
        suspension_mask |= STABILITY_ALERT | STABILIZE_VALVE_R
        right_valve_bias = abs(lateral_g) * 12.5 + abs(roll_deg) * 1.5
        
    # Adjust dynamic ride profiles based on speed threshold variables
    if velocity_mph > 55.0:
        suspension_mask |= FIRM_TRACK_MODE
    elif abs(pitch_deg) > 15.0:
        suspension_mask |= TERRAIN_CRAWL_HIGH | VALVE_PRESSURE_INC
        if pitch_deg > 0.0:
            suspension_mask |= STRUT_EXTEND_FRONT
        else:
            suspension_mask |= STRUT_EXTEND_REAR
    else:
        suspension_mask |= SUSPENSION_NOMINAL
        
    return suspension_mask, left_valve_bias, right_valve_bias

class ActiveSuspensionGateway:
    def __init__(self, asset_id="TACTICAL_HMMWV_8120"):
        self.asset_id = asset_id
        self.heartbeat_state = False
        self.local_profile = {
            "accumulated_cycles": 0,
            "max_lateral_g_sustained": 0.0,
            "calibration_offset_roll": 0.0
        }
        self.load_calibration_manifest()

    def load_calibration_manifest(self):
        """Restores persistent ride metrics to ensure zero-point safety lines while offline."""
        if os.path.exists(ChASSIS_CAL_CACHE):
            try:
                with open(ChASSIS_CAL_CACHE, 'r') as f:
                    self.local_profile = json.load(f)
                print(f"[CHASSIS] Restored offline zero-point stabilization mappings for {self.asset_id}.")
            except Exception:
                print("[WARNING] Calibration profile corrupted, re-establishing safe baseline levels.")

    def save_calibration_manifest(self):
        """Commits updated suspension telemetry matrices directly to storage blocks."""
        try:
            with open(ChASSIS_CAL_CACHE, 'w') as f:
                json.dump(self.local_profile, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Local cache write failure: {e}")

    def generate_system_heartbeat(self):
        """Cyclic heartbeat alternator to maintain continuous hardware safety loops."""
        self.heartbeat_state = not self.heartbeat_state
        return WATCHDOG_HEARTBEAT if self.heartbeat_state else 0x00000000

    def parse_chassis_frame(self, raw_telemetry_bytes):
        """
        Parses high-frequency tracking signals from accelerometers, suspension pots, and CAN speed sensors.
        Format: [Pitch (float)][Roll (float)][Lateral_G (float)][Weapon_Armed (float)][Velocity_MPH (float)]
        """
        if len(raw_telemetry_bytes) < 20:
            return None
            
        try:
            pitch, roll, lat_g, weapon_flag, velocity = struct.unpack('!fffff', raw_telemetry_bytes)
        except Exception:
            return None

        # Execute accelerated kinematic tracking matrix calculations
        control_bits, left_bias, right_bias = calculate_suspension_pressures(pitch, roll, lat_g, weapon_flag, velocity)
        
        # Append systemic safety watchdog flag
        control_bits |= self.generate_system_heartbeat()
        
        # Log localized configuration parameters to live state indexes
        if abs(lat_g) > self.local_profile["max_lateral_g_sustained"]:
            self.local_profile["max_lateral_g_sustained"] = float(abs(lat_g))
            self.save_calibration_manifest()
            
        return control_bits, left_bias, right_bias

if __name__ == "__main__":
    print("[INIT] Universal UNIVAC Active Suspension Gateway Core Active.")
    suspension_manager = ActiveSuspensionGateway(asset_id="TACTICAL_HMMWV_8120")
    
    # Mock Scenario: Vehicle executing high-speed tactical evasion maneuvers at 62 MPH; pushing 0.52 Gs to the left
    mock_sensor_packet = struct.pack('!fffff', 1.2, 5.4, -0.52, 0.0, 62.0)
    
    final_bits, l_valve, r_valve = suspension_manager.parse_chassis_frame(mock_sensor_packet)
    print(f"[STAGE] Active Control Register: {hex(final_bits)} | Strut Adjustments -> Left: {l_valve:.2f} PSI, Right: {r_valve:.2f} PSI")
