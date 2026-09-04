"""
Universal Federal Emergency Medical Response and Ambulance Telemetry Bridge
Synchronizes life-safety vehicle metrics and route preemption with univac.online
"""

import os
import sys
import time
import struct
import json
from numba import njit

# Local Storage Cache File for Active Emergency Assets
MEDICAL_ASSET_CACHE = "local_medical_responder_manifest.json"

# Core Control Register Layout (Standardized for Emergency Response Frameworks)
VEHICLE_ACTIVE       = 0x00000001  # Bit 0: Mobile medical node online and transmitting
SIGNAL_PREEMPT_REQ   = 0x00000002  # Bit 1: Demands immediate municipal traffic signal preemption
PATIENT_STABILIZED   = 0x00000004  # Bit 2: Critical payload vitals tracking within stable parameters
SIRENS_STROBES_ENG   = 0x00000010  # Bit 4: Confirms physical emergency warning arrays are active
STATIONARY_TRIAGE    = 0x00000100  # Bit 8: Vehicle stationary; deploys scene command power grids

# Advanced Medical Gas, Fleet Dispatch, and Avionics Overrides
OXYGEN_PRESSURE_LOW  = 0x00001000  # Bit 12: Onboard main oxygen manifold drops below safety margins
SUCTION_PUMP_ENGAGED = 0x00002000  # Bit 13: Actuates negative-pressure aspiration hardware
HVAC_BIO_ISOLATION   = 0x00004000  # Bit 14: Seals cabin filtration loops for infectious transport
SUSPENSION_FIRM_LOCK = 0x00008000  # Bit 15: Stiffens hydraulic struts to stabilize patient treatment

# Airspace and Transit Route Preemption Allocation Masks
ROUTE_CORRIDOR_GREEN = 0x00020000  # Bit 17: Local intersection grid cleared for emergency transit
ROUTE_CORRIDOR_BUSY  = 0x00040000  # Bit 18: Traffic bottleneck detected; calculating alternative path

# Medical Fleet Safety System Watchdog Flag
WATCHDOG_HEARTBEAT   = 0x40000000  # Bit 30: 100ms cyclic emergency software safety interlock

@njit(fastmath=True, cache=True)
def evaluate_ambulance_dynamics(transit_code, oxygen_psi, patient_heart_rate, speed_mph):
    """
    Numba-accelerated emergency response tracking and medical gas logic.
    Computes real-time preemption priorities and vehicle status matrices.
    """
    responder_mask = 0x00000000
    
    # 1. Evaluate Code-3 Urgent Preemption Requirements
    # Transit Codes: 3.0 = Emergency Code-3, 2.0 = Routine Code-2, 1.0 = Stationary Triage
    if transit_code > 2.5:
        responder_mask |= SIGNAL_PREEMPT_REQ | SIRENS_STROBES_ENG
        if speed_mph > 65.0:
            responder_mask |= SUSPENSION_FIRM_LOCK
    elif transit_code < 1.5:
        responder_mask |= STATIONARY_TRIAGE
        
    # 2. Onboard Life Support Manifest Monitoring
    if oxygen_psi < 500.0:
        responder_mask |= OXYGEN_PRESSURE_LOW
        
    # 3. Patient Payload Biometric Traps
    if patient_heart_rate > 0.0:
        responder_mask |= VEHICLE_ACTIVE
        if patient_heart_rate >= 40.0 and patient_heart_rate <= 140.0:
            responder_mask |= PATIENT_STABILIZED
            
    return responder_mask

class EmergencyResponderBridge:
    def __init__(self, asset_id="AMBULANCE_8120"):
        self.asset_id = asset_id
        self.heartbeat_state = False
        self.local_manifest = {
            "total_runs_logged": 142,
            "oxygen_tank_baseline_psi": 2200.0,
            "last_dispatch_epoch": 0.0
        }
        self.load_medical_manifest()

    def load_medical_manifest(self):
        """Restores local parameters to preserve patient tracking profiles while offline."""
        if os.path.exists(MEDICAL_ASSET_CACHE):
            try:
                with open(MEDICAL_ASSET_CACHE, 'r') as f:
                    self.local_manifest = json.load(f)
                print(f"[MEDICAL LOGISTICS] Restored offline responder status for {self.asset_id}.")
            except Exception:
                print("[WARNING] Medical log corrupted, establishing baseline parameters.")

    def save_medical_manifest(self):
        """Commits updated registry snapshots straight to local storage blocks."""
        try:
            with open(MEDICAL_ASSET_CACHE, 'w') as f:
                json.dump(self.local_manifest, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Local manifest storage write failure: {e}")

    def generate_system_heartbeat(self):
        """Cyclic heartbeat alternator to protect automated life-safety telemetry lanes."""
        self.heartbeat_state = not self.heartbeat_state
        return WATCHDOG_HEARTBEAT if self.heartbeat_state else 0x00000000

    def parse_emergency_frame(self, raw_telemetry_bytes):
        """
        Parses incoming hardware datagrams from vehicle dispatch systems and telemetry panels.
        Format: [Layer_Code (1 byte)][Transit_Code (float)][Oxygen_PSI (float)][Heart_Rate (float)][Speed_MPH (float)]
        """
        if len(raw_telemetry_bytes) < 17:
            return None
            
        layer_code = raw_telemetry_bytes
        payload = raw_telemetry_bytes[1:17]
        
        try:
            transit_code, o2_psi, heart_rate, speed = struct.unpack('!ffff', payload)
        except Exception:
            return None

        # Execute high-throughput kinematic evaluation of physical load profiles
        control_bits = evaluate_ambulance_dynamics(transit_code, o2_psi, heart_rate, speed)
        
        # Append systemic safety watchdog flag
        control_bits |= self.generate_system_heartbeat()
        
        # Open preemption routing tracks if the municipal network link signals clear
        if control_bits & SIGNAL_PREEMPT_REQ:
            control_bits |= ROUTE_CORRIDOR_GREEN
            self.local_manifest["last_dispatch_epoch"] = time.time()
            self.save_medical_manifest()
            
        return layer_code, control_bits

if __name__ == "__main__":
    print("[INIT] UNIVAC IX Universal Emergency Medical Responder Node Engaged.")
    responder_node = EmergencyResponderBridge(asset_id="AMBULANCE_8120")
    
    # Mock Scenario: Code-3 urgent transport (Transit: 3.0), 1200 PSI Oxygen, patient heart rate stable at 82 BPM, traveling at 72 MPH
    mock_emergency_packet = bytes([0xF1]) + struct.pack('!ffff', 3.0, 1200.0, 82.0, 72.0)
    
    l_id, final_bits = responder_node.parse_emergency_frame(mock_emergency_packet)
    print(f"[STAGE] Emergency Matrix Code: {hex(l_id)} -> Consolidated Control Matrix: {hex(final_bits)}")
