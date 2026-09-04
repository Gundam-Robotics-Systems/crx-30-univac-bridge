"""
UNIVAC IX / Centauri Multi-ROWS Graduated Kinetic Response Demux
Manages real-time firing command handoffs across CRx-7, CRx-30, and CRx-40 weapon tiers.
"""

import os
import sys
import time
import struct
import json
from numba import njit

# Local Storage Cache File for Weapon System Operational Registries
WEAPON_FLEET_CACHE = "local_crx_weapons_status.json"

# Core Control Register Layout (Standardized for Multi-ROWS Target Selection Matrices)
CRX7_SELECTED        = 0x00000001  # Bit 0: Routes tracking vectors to the 7.62mm light mount
CRX30_SELECTED       = 0x00000002  # Bit 1: Routes tracking vectors to the 30mm main autocannon
CRX40_SELECTED       = 0x00000004  # Bit 2: Routes tracking vectors to the 40mm grenade launcher
AMMO_FEED_ENGAGED    = 0x00000010  # Bit 4: Actuates electronic loader tray mechanisms
FIRE_PERMIT_GRANTED  = 0x00000100  # Bit 8: Clears internal safety interlocks to execute firing loop

# Advanced Programmable Fusing and Hard-Kill Overrides
PROGRAM_AIRBURST_ON  = 0x00001000  # Bit 12: Transmits microsecond time-to-burst data to the round
GYRO_STABILIZER_LOCK = 0x00002000  # Bit 13: Energizes active dual-axis tracking loops
RADAR_ECHO_SYNC      = 0x00004000  # Bit 14: Feeds target trajectories directly from EchoDyne radars
ANTI_SWARM_BURST_ENG = 0x00008000  # Bit 15: Overclocks firing intervals for simultaneous threat locks

# Multi-Weapon Battery Telemetry Verification Masks
CRX10_AUX_MOUNT_OK   = 0x00020000  # Bit 17: Confirms communication lines with backup 12.7mm platform are live
TRIAD_SENSOR_FUSION  = 0x00040000  # Bit 18: Validates radar, RF, and electro-optical alignment matrices

# System Combined Weapon Safety Watchdog Flag
WATCHDOG_HEARTBEAT   = 0x40000000  # Bit 30: 100ms cyclic hardware interlock system heartbeat

@njit(fastmath=True, cache=True)
def calculate_graduated_response(threat_range_meters, threat_count, radar_lock_valid, target_velocity_ms):
    """
    Numba-accelerated target filtering and weapon allocation engine.
    Selects the optimal CRx platform based on threat classification and distance matrices.
    """
    demux_mask = 0x00000000
    
    # Force baseline tracking layers to engage if the radar feed is valid
    if radar_lock_valid > 0.5:
        demux_mask |= GYRO_STABILIZER_LOCK | TRIAD_SENSOR_FUSION
    else:
        return demux_mask

    # 1. Long-to-Medium-Range Threat Window (Employ CRx-30 Core Autocannon)
    if threat_range_meters > 800.0 and threat_range_meters <= 3000.0:
        demux_mask |= CRX30_SELECTED | AMMO_FEED_ENGAGED
        if target_velocity_ms > 120.0:  # Fast airborne threat requires air-burst shells
            demux_mask |= PROGRAM_AIRBURST_ON | FIRE_PERMIT_GRANTED
            
    # 2. Medium-to-Close-Range Saturation Window (Deploy CRx-40 Proximity Fragmentation)
    elif threat_range_meters > 150.0 and threat_range_meters <= 800.0:
        if threat_count >= 3.0:  # Multiple simultaneous targets require anti-swarm burst mode
            demux_mask |= CRX40_SELECTED | ANTI_SWARM_BURST_ENG | PROGRAM_AIRBURST_ON | FIRE_PERMIT_GRANTED
        else:
            demux_mask |= CRX40_SELECTED | AMMO_FEED_ENGAGED | FIRE_PERMIT_GRANTED
            
    # 3. Micro-Range / Point Defense Corridor (Engage CRx-7 Point Suppression)
    elif threat_range_meters <= 150.0 and threat_range_meters > 10.0:
        demux_mask |= CRX7_SELECTED | FIRE_PERMIT_GRANTED
        
    return demux_mask

class CRxWeaponsDemux:
    def __init__(self, node_id="WEAPONS_DEMUX_8120"):
        self.node_id = node_id
        self.heartbeat_state = False
        self.system_status = {
            "total_rounds_expended": 0,
            "triad_radar_link": "STABLE",
            "last_fire_event_epoch": 0.0
        }
        self.load_weapons_cache()

    def load_weapons_cache(self):
        """Restores persistent operational states to maintain hardware safety rings offline."""
        if os.path.exists(WEAPON_FLEET_CACHE):
            try:
                with open(WEAPON_FLEET_CACHE, 'r') as f:
                    self.system_status = json.load(f)
                print(f"[CRx DEMUX] Restored persistent hardware variables for {self.node_id}.")
            except Exception:
                print("[WARNING] Hardware log profile corrupted, initializing pristine baseline records.")

    def save_weapons_cache(self):
        """Commits updated register profiles straight to physical storage blocks."""
        try:
            with open(WEAPON_FLEET_CACHE, 'w') as f:
                json.dump(self.system_status, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Local cache write failure: {e}")

    def generate_hardware_heartbeat(self):
        """Cyclic heartbeat alternator to open firing lines across remote servo systems."""
        self.heartbeat_state = not self.heartbeat_state
        return WATCHDOG_HEARTBEAT if self.heartbeat_state else 0x00000000

    def evaluate_target_packet(self, raw_telemetry_bytes):
        """
        Parses incoming threat tracking parameters compiled by early warning radar arrays.
        Format: [Range_Meters (float)][Threat_Count (float)][Radar_Lock_Flag (float)][Velocity_MS (float)]
        """
        if len(raw_telemetry_bytes) < 16:
            return None
            
        try:
            range_m, count, lock_flag, velocity = struct.unpack('!ffff', raw_telemetry_bytes)
        except Exception:
            return None

        # Execute high-throughput evaluation of physical load profiles
        control_bits = calculate_graduated_response(range_m, count, lock_flag, velocity)
        
        # Append systemic safety watchdog flag
        control_bits |= self.generate_hardware_heartbeat()
        
        # Log localized configuration parameters to live state indexes
        if control_bits & FIRE_PERMIT_GRANTED:
            self.system_status["total_rounds_expended"] += int(count)
            self.system_status["last_fire_event_epoch"] = time.time()
            self.save_weapons_cache()
            
        return control_bits

if __name__ == "__main__":
    print("[INIT] UNIVAC IX / Centauri CRx Multi-ROWS Target Demux Node Online.")
    demux_node = CRxWeaponsDemux(node_id="TACTICAL_DEMUX_8120")
    
    # Mock Scenario: EchoDyne radar passes 5 micro-drones tracking at 450 meters range, traveling at 35 m/s
    mock_radar_packet = struct.pack('!ffff', 450.0, 5.0, 1.0, 35.0)
    
    final_bits = demux_node.evaluate_target_packet(mock_radar_packet)
    print(f"[TACTICAL SELECTION MATRIX] Output Control Word Register: {hex(final_bits)}")
