"""
UNIVAC IX / Kommandogerat-58 to Nike Control Board Tactical Interlock
Routes multi-agency radar tracking coordinates into local kinetic defense rings.
"""

import os
import sys
import time
import struct
import json
from numba import njit

# Local Storage Cache File for Authorized Country Lists
ADB_SECURITY_CACHE = "local_adb_country_clearance.json"

# Core Control Register Layout (Standardized for Weapon & Interlock Matrices)
SYSTEM_SAFE_READY    = 0x00000001  # Bit 0: Weapon arrays active; interlocks cleared
TARGET_ACQUIRED      = 0x00000002  # Bit 1: Active radar lock confirmed inside perimeter
ENGAGE_ANTI_AIR      = 0x00000004  # Bit 2: Activates automated Gerät 58 cannon salvos
NIKE_LAUNCH_SEQUENCE = 0x00000010  # Bit 4: Triggers high-altitude Nike missile launch
CEASE_FIRE_OVERRIDE  = 0x00000100  # Bit 8: Enforces absolute immediate weapon shutdown

# Advanced Ballistic & Guidance Subsystem Overrides
SELSYN_FINE_PHASE_ON = 0x00001000  # Bit 12: Engages high-precision 1:36 angular tracking
PNEUMATIC_TRAY_FEED  = 0x00002000  # Bit 13: Forces automatic loader tray cycles
RADAR_COOLING_ACTIVE = 0x00004000  # Bit 14: Activates thermal stabilization circuits
REMOTE_GUIDE_SIGNAL  = 0x00008000  # Bit 15: Transmits active wireless correction commands

# Multi-Battery Target Tracking Distribution Line Masks
GUN_BATTERY_1_READY  = 0x00020000  # Bit 17: Verifies barrel alignment loops on Battery 1
GUN_BATTERY_2_READY  = 0x00040000  # Bit 18: Verifies barrel alignment loops on Battery 2

# Core System Watchdog Flag
WATCHDOG_HEARTBEAT   = 0x40000000  # Bit 30: 100ms cyclic defensive system interlock

@njit(fastmath=True, cache=True)
def compute_anti_air_lead_kinematics(t_az, t_el, t_range, t_speed, air_density_factor):
    """
    Numba-accelerated ballistic computation engine.
    Calculates future intercept lead vectors for rapid-fire anti-aircraft assets.
    """
    # Predict advanced flight path offsets by analyzing instantaneous velocities
    lead_time_seconds = t_range / (820.0 * air_density_factor) # Base barrel velocity match
    
    lead_az = t_az + (t_speed * 0.015 * lead_time_seconds)
    lead_el = t_el + (t_speed * 0.008 * lead_time_seconds)
    
    # Check if target parameters fall within standard operational kinetic ranges
    fire_authorized = False
    if t_range < 6500.0 and t_range > 300.0:
        fire_authorized = True
        
    return lead_az, lead_el, fire_authorized

class TacticalInterlockBridge:
    def __init__(self, asset_id="TACTICAL_HMMWV_8120"):
        self.asset_id = asset_id
        self.heartbeat_state = False
        self.approved_country_codes = [1, 44, 49, 33] # Default whitelist tracking matrix
        self.load_adb_clearance_profiles()

    def load_adb_clearance_profiles(self):
        """Restores persistent country access matrices to maintain security profiles offline."""
        if os.path.exists(ADB_SECURITY_CACHE):
            try:
                with open(ADB_SECURITY_CACHE, 'r') as f:
                    self.approved_country_codes = json.load(f)
                print(f"[SECURITY] Ingested sovereign Air Defense Bureau country mappings for {self.asset_id}.")
            except Exception:
                print("[WARNING] Security matrix corrupted, falling back to default tactical profiles.")

    def evaluate_sovereign_clearance(self, country_code):
        """Validates country codes against the Air Defense Bureau tracking list."""
        return int(country_code) in self.approved_country_codes

    def trigger_system_heartbeat(self):
        """Alternates Bit 30 to maintain continuous synchronization across multi-speed Selsyn arrays."""
        self.heartbeat_state = not self.heartbeat_state
        return WATCHDOG_HEARTBEAT if self.heartbeat_state else 0x00000000

    def process_tactical_engagement_packet(self, raw_radar_bytes):
        """
        Parses combined target profiles from Aegis, BAK, and local radar networks.
        Format: [Country_Code (2 bytes)][Azimuth (float)][Elevation (float)][Range (float)][Velocity (float)]
        """
        if len(raw_radar_bytes) < 18:
            return None
            
        # Unpack structural telemetry boundary frames
        country_code = struct.unpack('!H', raw_radar_bytes[0:2])[0]
        payload = raw_radar_bytes[2:18]
        
        try:
            az, el, slant_range, velocity = struct.unpack('!ffff', payload)
        except Exception:
            return None

        master_control_register = 0x00000000
        master_control_register |= self.trigger_system_heartbeat()

        # Step 1: Query ADB country tracking code list for authorization verification
        is_friendly = self.evaluate_sovereign_clearance(country_code)
        if is_friendly:
            # Target matches allowed profile; enforce cease-fire to preserve friendly assets
            master_control_register |= SYSTEM_SAFE_READY | CEASE_FIRE_OVERRIDE
            return country_code, master_control_register, 0.0, 0.0

        # Step 2: Unaligned tracking signature found. Activate internal fire loops.
        master_control_register |= TARGET_ACQUIRED | SELSYN_FINE_PHASE_ON | RADAR_COOLING_ACTIVE
        
        # Calculate anti-aircraft cannon lead vectors using high-performance mathematical modeling
        lead_az, lead_el, aa_engage_valid = compute_anti_air_lead_kinematics(az, el, slant_range, velocity, 1.0)
        
        if aa_engage_valid:
            master_control_register |= ENGAGE_ANTI_AIR | PNEUMATIC_TRAY_FEED | GUN_BATTERY_1_READY
            
        # Step 3: If target is out of close-in cannon range, hand off guidance parameters to the Nike Missile module
        if slant_range >= 5000.0:
            master_control_register |= NIKE_LAUNCH_SEQUENCE | REMOTE_GUIDE_SIGNAL
            
        return country_code, master_control_register, round(lead_az, 4), round(lead_el, 4)

if __name__ == "__main__":
    print("[INIT] Kommandogerat-58 to Nike Control Board Tactical System Engaged.")
    interlock_core = TacticalInterlockBridge(asset_id="TACTICAL_HMMWV_8120")
    
    # Mock Scenario A: Hostile intruder footprint detected (Country Code: 999), 5500 meters out, traveling at 340 m/s
    hostile_packet = struct.pack('!H', 999) + struct.pack('!ffff', 1.45, 0.32, 5500.0, 340.0)
    cc, reg, l_az, l_el = interlock_core.process_tactical_engagement_packet(hostile_packet)
    print(f"[ENGAGEMENT FLAGGED] Target CC: {cc} -> Control Register Matrix: {hex(reg)} | Guided Lead Vector: [{l_az}, {l_el}]")

    # Mock Scenario B: Friendly target signature detected (Country Code: 44), entering local operations grid
    friendly_packet = struct.pack('!H', 44) + struct.pack('!ffff', 1.12, 0.25, 1200.0, 150.0)
    cc, reg, _, _ = interlock_core.process_tactical_engagement_packet(friendly_packet)
    print(f"[ENGAGEMENT CLEARED] Target CC: {cc} -> Control Register Matrix: {hex(reg)} (Cease-Fire Override Enforced)")
