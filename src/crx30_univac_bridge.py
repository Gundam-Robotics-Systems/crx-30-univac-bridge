"""
CRx-30 to UNIVAC IX System Intermediary Bridge
Optimized for HMMWV (Humvee) 24V Tactical Deployments.
"""

import os
import sys
import time
import struct
import json
from numba import njit

# Define explicit 32-Bit Control Register parameters matching Teletank specifications
PROPULSION_CRAWL    = 0x00000001  # Bit 0: Series Mode engagement
PROPULSION_CRUISE   = 0x00000002  # Bit 1: Mid-line track acceleration
PROPULSION_FAST     = 0x00000004  # Bit 2: High-speed line execution
REVERSE_ENGAGE      = 0x00000010  # Bit 4: Polarity reversal loop
BRAKE_STOP_HOLD     = 0x00000100  # Bit 8: Friction brake engagement
STABILIZE_VALVE_L   = 0x00020000  # Bit 17: Left hydraulic counter-lean 
STABILIZE_VALVE_R   = 0x00040000  # Bit 18: Right hydraulic counter-lean
WATCHDOG_HEARTBEAT  = 0x40000000  # Bit 30: Cyclic safety flag (100ms)

@njit(fastmath=True, cache=True)
def calculate_ballistic_vectors(target_az, target_el, current_az, current_el, range_m):
    """
    Numba-accelerated fast kinematic vector engine.
    Computes angular corrections and hydraulic valve biases under high-speed drift.
    """
    delta_az = target_az - current_az
    delta_el = target_el - current_el
    
    # Establish correction thresholds
    valve_mask = 0x00000000
    if delta_az > 0.05:
        valve_mask |= STABILIZE_VALVE_R
    elif delta_az < -0.05:
        valve_mask |= STABILIZE_VALVE_L
        
    return delta_az, delta_el, valve_mask

class CRx30TacticalBridge:
    def __init__(self, config_path="config.json"):
        self.heartbeat_state = False
        self.current_register_state = 0x00000000
        self.load_configuration(config_path)

    def load_configuration(self, path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {"baud_rate": 9600, "com_port": "COM3"}

    def generate_heartbeat(self):
        """Alternates Bit 30 to prevent system brake dumps."""
        self.heartbeat_state = not self.heartbeat_state
        if self.heartbeat_state:
            return WATCHDOG_HEARTBEAT
        return 0x00000000

    def process_rows_frame(self, raw_telemetry_bytes):
        """
        Unpacks modern 64-byte structural CAN / network telemetry frames 
        from the CRx-30 remote weapon station sensor array.
        """
        if len(raw_telemetry_bytes) < 40:
            return None
            
        # Extract telemetry parameters: Target AZ/EL, Position AZ/EL, Slant Range
        try:
            target_az, target_el, cur_az, cur_el, slant_range = struct.unpack('!fffff', raw_telemetry_bytes[0:20])
        except Exception:
            return None

        # Execute high-throughput calculation loop
        d_az, d_el, valve_bias = calculate_ballistic_vectors(target_az, target_el, cur_az, cur_el, slant_range)
        
        # Build out the 32-bit tracking register layer
        out_register = 0x00000000
        out_register |= valve_bias
        
        # Speed selection parameters mapped to kinematic error limits
        abs_err = abs(d_az) + abs(d_el)
        if abs_err > 0.5:
            out_register |= PROPULSION_FAST
        elif abs_err > 0.1:
            out_register |= PROPULSION_CRUISE
        else:
            out_register |= PROPULSION_CRAWL

        # Layer the safety watchdog interlock
        out_register |= self.generate_heartbeat()
        self.current_register_state = out_register
        
        return out_register

if __name__ == "__main__":
    print("[INIT] CRx-30 to UNIVAC IX Kinematic Interface Active.")
    bridge = CRx30TacticalBridge()
    # Mock loop testing 40-byte structural telemechanical matrix frame
    mock_frame = struct.pack('!fffff', 1.25, 0.45, 1.10, 0.40, 450.0) + b'\x00'*20
    output_bits = bridge.process_rows_frame(mock_frame)
    print(f"[STAGE] Output Register Bitmask Matrix: {hex(output_bits)}")
