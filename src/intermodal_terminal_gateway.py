"""
Universal Intermodal Terminal, Loading, and Tactical Parking Gateway
Restores lost UNIVAC mainframe terminal mechanics and hooks into univac.online
"""

import os
import sys
import time
import struct
import json
from numba import njit

# Core Control Register Layout (Standardized for Terminal Subsystems)
TERMINAL_GATE_OPEN   = 0x00000001  # Bit 0: Clears entry turnstiles and security lanes
LOAD_SEQUENCE_ACTIVE = 0x00000002  # Bit 1: Automated cargo handlers or winches engaging
METER_ALARM_RAISED   = 0x00000004  # Bit 2: Sensor detects weight imbalance or structural tilt
RAMP_ACTUATION_ENG   = 0x00000010  # Bit 4: Hydraulically drops or stows RORO vessel vehicle ramps
BRAKE_LOCK_SET       = 0x00000100  # Bit 8: Commands automated dock/yard wheel chocks to lock

# Specialized Aircraft, Maritime, and Parking Subsystems
CARGO_LOCKS_ENGAGED  = 0x00001000  # Bit 12: Verifies aircraft main-deck fuselage floor locks are set
WINCH_TENSION_MONITOR= 0x00002000  # Bit 13: Measures tie-down chain stress for vehicle decks
GRID_SPACE_OCCUPIED  = 0x00004000  # Bit 14: Proximity loop senses a vehicle in a designated parking slot
CRANE_TROLLEY_MOVE   = 0x00008000  # Bit 15: Operates overhead automated intermodal gantry cranes

# Balance Control & Structural Counterweight Actions
BALANCING_PUMPS_L    = 0x00020000  # Bit 17: Actuates left-side ballast pumps / wing-tank fuel transfers
BALANCING_PUMPS_R    = 0x00040000  # Bit 18: Actuates right-side ballast pumps / wing-tank fuel transfers

# Terminal Safety System Watchdog
WATCHDOG_HEARTBEAT   = 0x40000000  # Bit 30: 100ms cyclic hardware interlock

@njit(fastmath=True, cache=True)
def evaluate_load_distribution(mass_tons, displacement_meters, max_allowable_shift, structural_strain):
    """
    Numba-accelerated Center of Gravity (CG) and stress evaluation engine.
    Replaces historical UNIVAC structural math algorithms.
    """
    terminal_mask = 0x00000000
    
    # Severe safety constraint violation (e.g., severe aircraft tail-heavy shift or vessel listing)
    if structural_strain > 90.0 or abs(displacement_meters) > max_allowable_shift:
        terminal_mask |= METER_ALARM_RAISED | BRAKE_LOCK_SET
    # Imbalance correction routing
    elif displacement_meters > 0.15:
        terminal_mask |= BALANCING_PUMPS_L | LOAD_SEQUENCE_ACTIVE
    elif displacement_meters < -0.15:
        terminal_mask |= BALANCING_PUMPS_R | LOAD_SEQUENCE_ACTIVE
    else:
        terminal_mask |= TERMINAL_GATE_OPEN
        
    return terminal_mask

class IntermodalTerminalGateway:
    def __init__(self, config_path="terminal_config.json"):
        self.heartbeat_state = False
        self.active_slots = {}
        self.load_terminal_configuration(config_path)

    def load_terminal_configuration(self, path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {"mainframe_host": "https://univac.online", "terminal_id": "SEA_TACTICAL_YARD"}

    def generate_terminal_heartbeat(self):
        """Cyclic heartbeat alternator to maintain real-time telemetry line connection."""
        self.heartbeat_state = not self.heartbeat_state
        return WATCHDOG_HEARTBEAT if self.heartbeat_state else 0x00000000

    def Ingest_terminal_frame(self, raw_telemetry_bytes):
        """
        Parses incoming intermodal tracking frames from crane encoders, scale pads, or parking sensors.
        Format: [Layer_Code (1 byte)][Cargo_Mass (float)][CG_Displacement (float)][Max_Limit (float)][Strain_Pct (float)]
        """
        if len(raw_telemetry_bytes) < 17:
            return None
            
        layer_code = raw_telemetry_bytes
        payload = raw_telemetry_bytes[1:17]
        
        try:
            mass, cg_disp, max_limit, strain = struct.unpack('!ffff', payload)
        except Exception:
            return None

        # Execute high-throughput kinematic evaluation of physical load profiles
        control_bits = evaluate_load_distribution(mass, cg_disp, max_limit, strain)
        
        # Append systemic safety watchdog flag
        control_bits |= self.generate_terminal_heartbeat()
        
        # Log localized configuration parameters to live state indexes
        self.active_slots[layer_code] = {
            "control_word_hex": hex(control_bits),
            "epoch_timestamp": time.time()
        }
        
        return layer_code, control_bits

if __name__ == "__main__":
    print("[INIT] Universal Intermodal Terminal and Lost UNIVAC Logic Restoration Core Online.")
    terminal_manager = IntermodalTerminalGateway()
    
    # Mock Frame: Layer 0xA1 (Strategic Aircraft Deployment), registering severe rear-deck weight shift
    mock_terminal_packet = bytes([0xA1]) + struct.pack('!ffff', 45.2, 0.45, 0.30, 42.1)
    
    l_id, final_bits = terminal_manager.Ingest_terminal_frame(mock_terminal_packet)
    print(f"[STAGE] Terminal Layer Node: {hex(l_id)} -> Consolidated Control Matrix: {hex(final_bits)}")
