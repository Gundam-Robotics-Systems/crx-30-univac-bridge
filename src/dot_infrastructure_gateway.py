"""
Universal DOT Infrastructure and ITS Network Gateway
Interlocks Federal, State, and Municipal transit metrics with univac.online
"""

import os
import sys
import time
import struct
import json
from numba import njit

# Core Control Register Layout (Standardized for DOT & ITS Subsystems)
GRID_STATUS_NOMINAL  = 0x00000001  # Bit 0: Intersection operating under local automation
SIGNAL_PREEMPT_REQD  = 0x00000002  # Bit 1: Emergency vehicle approaching; route override active
INCIDENT_DETECTED    = 0x00000004  # Bit 2: Sensor loop flags an active roadway anomaly
REVERSE_LANE_FLIP    = 0x00000010  # Bit 4: Actuates dynamic reversible lane control gates
GATE_CLOSURE_LOCK    = 0x00000100  # Bit 8: Deploys physical ramp meters or highway barriers

# ITS and Smart City Infrastructure Subsystems
VMS_ALERT_DISPLAYED  = 0x00001000  # Bit 12: Variable Message Signs flashing active tactical warnings
TRANSIT_PRIORITY_ON  = 0x00002000  # Bit 13: Grants signal priority for mass transit tracking
RADAR_SPEED_MONITOR  = 0x00004000  # Bit 14: Engages automated radar vehicle volume tracking
WEATHER_STATION_ALIVE= 0x00008000  # Bit 15: Road Weather Information System (RWIS) streaming live

# Regional Congestion and Active Traffic Management (ATM) Overrides
SPEED_LIMIT_DROP_10  = 0x00020000  # Bit 17: Drops variable speed limit by 10 MPH
SPEED_LIMIT_DROP_20  = 0x00040000  # Bit 18: Drops variable speed limit by 20 MPH

# Infrastructure Safety Watchdog
WATCHDOG_HEARTBEAT   = 0x40000000  # Bit 30: Infrastructure 100ms cyclic system interlock

@njit(fastmath=True, cache=True)
def analyze_traffic_telemetry(vehicle_count, average_speed, preemption_requested, occupancy_pct):
    """
    Numba-accelerated NTCIP traffic flow parsing engine.
    Determines grid signal adjustments and corridor warning states in real time.
    """
    its_mask = 0x00000000
    
    # Check for active emergency preemption flag from first responders or law enforcement
    if preemption_requested > 0.5:
        its_mask |= SIGNAL_PREEMPT_REQD | VMS_ALERT_DISPLAYED
    # Check for severe bottleneck or standstill indicating an incident
    elif vehicle_count > 45 and average_speed < 15.0:
        its_mask |= INCIDENT_DETECTED | VMS_ALERT_DISPLAYED | SPEED_LIMIT_DROP_20
    # Moderate congestion check
    elif occupancy_pct > 30.0:
        its_mask |= SPEED_LIMIT_DROP_10 | TRANSIT_PRIORITY_ON
    else:
        its_mask |= GRID_STATUS_NOMINAL
        
    return its_mask

class DOTInfrastructureGateway:
    def __init__(self, config_path="dot_network_config.json"):
        self.heartbeat_state = False
        self.active_intersections = {}
        self.load_network_configuration(config_path)

    def load_network_configuration(self, path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {"mainframe_url": "https://univac.online", "ntcip_version": "v2"}

    def generate_infrastructure_heartbeat(self):
        """Cyclic heartbeat alternator to keep field controller lines synchronized."""
        self.heartbeat_state = not self.heartbeat_state
        return WATCHDOG_HEARTBEAT if self.heartbeat_state else 0x00000000

    def ingest_ntcip_frame(self, raw_ntcip_packet):
        """
        Parses incoming ITS telemetry datagrams from local inductive loops or radar sensors.
        Format: [Network_Layer_Code (1 byte)][Vehicle_Count (float)][Avg_Speed (float)][Preempt_Flag (float)][Occupancy (float)]
        """
        if len(raw_ntcip_packet) < 17:
            return None
            
        layer_code = raw_ntcip_packet[0]
        payload = raw_ntcip_packet[1:17]
        
        try:
            veh_count, avg_spd, preempt_flag, occupancy = struct.unpack('!ffff', payload)
        except Exception:
            return None

        # Execute high-throughput kinematic evaluation of the corridor
        control_bits = analyze_traffic_telemetry(veh_count, avg_spd, preempt_flag, occupancy)
        
        # Append the cyclic network heartbeat
        control_bits |= self.generate_infrastructure_heartbeat()
        
        # Store active state for tracking updates
        self.active_intersections[layer_code] = {
            "control_matrix_hex": hex(control_bits),
            "timestamp_epoch": time.time()
        }
        
        return layer_code, control_bits

if __name__ == "__main__":
    print("[INIT] Multi-Tier DOT Infrastructure Network Interface Online.")
    dot_manager = DOTInfrastructureGateway()
    
    # Mock Frame: Layer 0xD3 (Municipal DOT Controller), registering incoming emergency preemption request
    mock_ntcip_packet = bytes([0xD3]) + struct.pack('!ffff', 12.0, 42.5, 1.0, 15.4)
    
    l_id, final_bits = dot_manager.ingest_ntcip_frame(mock_ntcip_packet)
    print(f"[STAGE] DOT Network Layer: {hex(l_id)} -> Consolidated Control Matrix: {hex(final_bits)}")
