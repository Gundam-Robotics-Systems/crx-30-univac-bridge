"""
UNIVAC IX / Centauri TriAD System Safety Enforcer and Emergency Lockout Core
Monitors physical feedback lines across CRx-7, CRx-10, CRx-30, and CRx-40 turrets.
"""

import os
import sys
import time
import struct
import json
from numba import njit

# Local Storage Cache File for Active Turret Hardware Overrides
TURRET_SAFETY_CACHE = "local_triad_hardware_safety.json"

# Core Control Register Layout (Standardized for Multi-ROWS Safety Rings)
CRX7_CIRCUIT_OK     = 0x00000001  # Bit 0: Light machine gun telemetry loop closed
CRX10_CIRCUIT_OK    = 0x00000002  # Bit 1: Heavy machine gun telemetry loop closed
CRX30_CIRCUIT_OK    = 0x00000004  # Bit 2: Autocannon telemetry loop closed
CRX40_CIRCUIT_OK    = 0x00000008  # Bit 3: Grenade launcher telemetry loop closed
BATTERY_ARMED       = 0x00000010  # Bit 4: All active systems clear of safety pins

# Advanced Mechanical and Systemic Safety Interlock Flags
RECOIL_PRESSURE_MAX = 0x00001000  # Bit 12: Hydraulic buffers indicate critical compression limits
AZIMUTH_LIMIT_REACHED=0x00002000  # Bit 13: Turret structure hits physical rotation bumper
COMSEC_KEY_LOADED   = 0x00004000  # Bit 14: Confirms internal encryption variables are loaded
EMERGENCY_SAFE_LOCK = 0x00000100  # Bit 8: Immediately cuts power relays to stop firing

# Dynamic Structural Allocation Verification Masks
VEHICLE_HULL_CLEAR  = 0x00020000  # Bit 17: Firing arc completely clear of vehicle body segments
SERVO_THERMAL_OK    = 0x00040000  # Bit 18: Drive motor temperatures within safe parameters

# Unified Weapon Matrix Safety System Watchdog Flag
WATCHDOG_HEARTBEAT  = 0x40000000  # Bit 30: 100ms cyclic system interlock safety heartbeat

@njit(fastmath=True, cache=True)
def evaluate_hardware_safety_matrix(feedback_bits, servo_temp_c, buffer_stroke_mm, azimuth_angle):
    """
    Numba-accelerated structural safety verification loop.
    Enforces absolute interlocks to protect vehicle hull geometries during intense firing cycles.
    """
    safety_mask = 0x00000000
    
    # 1. Critical Structural Envelope & Deflection Boundary Verification
    # Enforce safe firing boundary checks (e.g., prevent barrel alignment with local chassis antennas)
    if azimuth_angle > 175.0 and azimuth_angle < 185.0:
        safety_mask |= EMERGENCY_SAFE_LOCK
        return safety_mask
        
    # 2. Check for Servo Thermal or Hydraulic Buffer Failures
    if servo_temp_c > 95.0 or buffer_stroke_mm > 48.0:
        safety_mask |= EMERGENCY_SAFE_LOCK | RECOIL_PRESSURE_MAX
        return safety_mask
    else:
        safety_mask |= SERVO_THERMAL_OK | VEHICLE_HULL_CLEAR
        
    # 3. Map Available Hardware Nodes from Feed Signals
    # Feedback Bit Definitions: 1.0 = CRx-7, 2.0 = CRx-10, 3.0 = CRx-30, 4.0 = CRx-40
    if feedback_bits == 3.0:
        safety_mask |= CRX30_CIRCUIT_OK | BATTERY_ARMED
    elif feedback_bits == 4.0:
        safety_mask |= CRX40_CIRCUIT_OK | BATTERY_ARMED
    elif feedback_bits == 2.0:
        safety_mask |= CRX10_CIRCUIT_OK | BATTERY_ARMED
    elif feedback_bits == 1.0:
        safety_mask |= CRX7_CIRCUIT_OK | BATTERY_ARMED
        
    return safety_mask

class TriADSafetyEnforcer:
    def __init__(self, node_id="SAFETY_ENFORCER_8120"):
        self.node_id = node_id
        self.heartbeat_state = False
        self.safety_log = {
            "accumulated_hardware_faults": 0,
            "peak_servo_temp_recorded": 42.0,
            "last_lockout_epoch": 0.0
        }
        self.load_safety_cache()

    def load_safety_cache(self):
        """Restores persistent hardware constants to maintain safe loops offline."""
        if os.path.exists(TURRET_SAFETY_CACHE):
            try:
                with open(TURRET_SAFETY_CACHE, 'r') as f:
                    self.safety_log = json.load(f)
                print(f"[SAFETY ENFORCER] Restored offline structural safety logs for {self.node_id}.")
            except Exception:
                print("[WARNING] Safety log database corrupted, re-establishing baseline constants.")

    def save_safety_cache(self):
        """Commits updated register profiles straight to physical storage blocks."""
        try:
            with open(TURRET_SAFETY_CACHE, 'w') as f:
                json.dump(self.safety_log, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Local cache write failure: {e}")

    def generate_safety_heartbeat(self):
        """Cyclic heartbeat alternator to protect active hardware safety lines."""
        self.heartbeat_state = not self.heartbeat_state
        return WATCHDOG_HEARTBEAT if self.heartbeat_state else 0x00000000

    def parse_hardware_feedback(self, raw_telemetry_bytes):
        """
        Parses incoming feedback signals from internal turret encoders, thermocouples, and pressure pads.
        Format: [Feedback_ID (float)][Servo_Temp_C (float)][Buffer_Stroke_MM (float)][Azimuth_Angle (float)]
        """
        if len(raw_telemetry_bytes) < 16:
            return None
            
        try:
            f_id, temp, stroke, angle = struct.unpack('!ffff', raw_telemetry_bytes)
        except Exception:
            return None

        # Execute high-throughput evaluation of physical load profiles
        control_bits = evaluate_hardware_safety_matrix(f_id, temp, stroke, angle)
        
        # Append systemic safety watchdog flag
        control_bits |= self.generate_safety_heartbeat()
        
        # Ingest logging parameters to update internal database records if an active fault occurs
        if control_bits & EMERGENCY_SAFE_LOCK:
            self.safety_log["accumulated_hardware_faults"] += 1
            self.safety_log["last_lockout_epoch"] = time.time()
            if temp > self.safety_log["peak_servo_temp_recorded"]:
                self.safety_log["peak_servo_temp_recorded"] = float(temp)
            self.save_safety_cache()
            
        return control_bits

if __name__ == "__main__":
    print("[INIT] UNIVAC IX / Centauri TriAD Structural Safety Enforcer Active.")
    enforcer = TriADSafetyEnforcer(node_id="HARDWARE_LOCKOUT_8120")
    
    # Mock Scenario: CRx-30 platform (ID: 3.0) registers severe heat spike in drive servos (Temp: 98.5°C) during rapid tracking
    mock_feedback_packet = struct.pack('!ffff', 3.0, 98.5, 12.0, 45.2)
    
    final_bits = enforcer.parse_hardware_feedback(mock_feedback_packet)
    print(f"[HARDWARE MONITOR LOCKOUT] Output Safety Register: {hex(final_bits)}")
