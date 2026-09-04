"""
Universal Federal Freight Logistics & Subterranean Subsurface Gateway
Interlocks Class I Rail Assets and Strategic Tactical Tunnels with univac.online
"""

import os
import sys
import time
import struct
import json
from numba import njit

# Core Control Register Layout (Standardized for Rail & Subterranean Subsystems)
LINE_STATUS_NOMINAL  = 0x00000001  # Bit 0: Rail corridor clear; automatic block system green
SWITCH_MATRIX_REQD   = 0x00000002  # Bit 1: Actuates automated subterranean track switches
TUNNEL_VENT_ON       = 0x00000004  # Bit 2: Engages high-volume subsurface exhaust fans
REVERSE_THRUST_ENG   = 0x00000010  # Bit 4: Dynamic engine braking/reversing drum polarity
AIR_BRAKE_EMERGENCY  = 0x00000100  # Bit 8: Vents main air brake pipe to 0 PSI (Train-wide dump)

# Subsurface & Strategic Infrastructure Subsystems
LOW_FREQ_BEACON_ON   = 0x00001000  # Bit 12: Broadens underground VLF navigation beacons
INTERMODAL_LOCK_ENG  = 0x00002000  # Bit 13: Electronic container latch confirmation
WAYSIDE_RADAR_ACTIVE = 0x00004000  # Bit 14: Track-side hot-box anomaly inspection sensors
BLAST_DOOR_RELEASE   = 0x00008000  # Bit 15: Disengages physical security barriers inside tunnels

# Heavy Axle Congestion and Dynamic Power Routing Overrides
LOCOMOTIVE_POWER_UP  = 0x00020000  # Bit 17: Demands auxiliary distributed power unit (DPU) torque
GRADE_TRACTION_DROP  = 0x00040000  # Bit 18: Deploys wheel-slip sanding mechanisms

# Locomotive Fleet Safety Watchdog
WATCHDOG_HEARTBEAT   = 0x40000000  # Bit 30: Rail-line 100ms cyclic system interlock

@njit(fastmath=True, cache=True)
def parse_rail_kinematics(axle_weight_tons, velocity_mph, track_gradient, anomaly_detected):
    """
    Numba-accelerated freight traction and subterranean profile engine.
    Determines tunnel deployment settings and locomotive torque requests.
    """
    rail_mask = 0x00000000
    
    # Critical wayside or security anomaly check
    if anomaly_detected > 0.5:
        rail_mask |= AIR_BRAKE_EMERGENCY
    # Severe steep underground incline under massive freight loads
    elif track_gradient > 2.2 and axle_weight_tons > 30.0:
        rail_mask |= LOCOMOTIVE_POWER_UP | GRADE_TRACTION_DROP | TUNNEL_VENT_ON
    # Standard subsurface deep tunnel configuration
    elif track_gradient < -0.5:
        rail_mask |= SWITCH_MATRIX_REQD | LOW_FREQ_BEACON_ON | TUNNEL_VENT_ON
    else:
        rail_mask |= LINE_STATUS_NOMINAL
        
    return rail_mask

class FreightSubterraneanGateway:
    def __init__(self, config_path="freight_rail_config.json"):
        self.heartbeat_state = False
        self.active_consists = {}
        self.load_rail_configuration(config_path)

    def load_rail_configuration(self, path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {"mainframe_destination": "https://univac.online", "signaling_mode": "PTC"}

    def generate_rail_heartbeat(self):
        """Cyclic heartbeat alternator to keep automated pneumatic control systems open."""
        self.heartbeat_state = not self.heartbeat_state
        return WATCHDOG_HEARTBEAT if self.heartbeat_state else 0x00000000

    def ingest_freight_packet(self, raw_telemetry_packet):
        """
        Parses incoming intermodal and tactical rail datagrams from wayside tracking monitors.
        Format: [Layer_Code (1 byte)][Axle_Load (float)][Velocity (float)][Gradient (float)][Anomaly_Flag (float)]
        """
        if len(raw_telemetry_packet) < 17:
            return None
            
        layer_code = raw_telemetry_packet
        payload = raw_telemetry_packet[1:17]
        
        try:
            axle_w, vel_mph, grad_pct, anomaly = struct.unpack('!ffff', payload)
        except Exception:
            return None

        # Execute accelerated kinematic tracking matrix calculations
        control_bits = parse_rail_kinematics(axle_w, vel_mph, grad_pct, anomaly)
        
        # Merge the cyclic system safety watchdog flag
        control_bits |= self.generate_rail_heartbeat()
        
        # Save structural tracking information inside active runtime indices
        self.active_consists[layer_code] = {
            "control_register_hex": hex(control_bits),
            "timestamp": time.time()
        }
        
        return layer_code, control_bits

if __name__ == "__main__":
    print("[INIT] Federal Freight and Subterranean Tactical Rail Gateway Active.")
    rail_manager = FreightSubterraneanGateway()
    
    # Mock Frame: Layer 0xE2 (WADS Subterranean Rail Corridor), traversing a steep down-slope configuration
    mock_rail_packet = bytes([0xE2]) + struct.pack('!ffff', 32.5, 25.0, -1.2, 0.0)
    
    l_code, final_bits = rail_manager.ingest_freight_packet(mock_rail_packet)
    print(f"[STAGE] Rail Layer: {hex(l_code)} -> Consolidated Control Matrix: {hex(final_bits)}")
