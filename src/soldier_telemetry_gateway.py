"""
Universal Soldier Biometric Telemetry & FLIR IFF Gateway Driver
Links boot tracking components and thermal badges directly with univac.online
"""

import os
import sys
import time
import struct
import json
from numba import njit

# Local Storage Cache File for Personnel Manifests
SOLDIER_TRACK_CACHE = "local_soldier_telemetry_manifest.json"

# Core Control Register Layout (Standardized for Personnel Tracking & Safety)
PERSONNEL_ACTIVE     = 0x00000001  # Bit 0: Soldier transceiver online and broadcasting
IFF_FRIENDLY_CONFIRMED=0x00000002  # Bit 1: FLIR thermal badge verified by visual tracking loop
VITAL_SIGNS_NOMINAL  = 0x00000004  # Bit 2: Heart rate, core temperature, and SpO2 in safe thresholds
TROOP_STATIONARY     = 0x00000010  # Bit 4: Stride counter register detects asset is immobile
MEDICAL_ALERT_RAISED = 0x00000100  # Bit 8: Critical vital anomaly detected; flags immediate evacuation

# Advanced Combat ID and Wearable Array Overrides
BOOT_GPS_LOCK_ALIVE  = 0x00001000  # Bit 12: Boot tracking chip confirms stable satellite telemetry
FLIR_IFF_EMITTING    = 0x00002000  # Bit 13: Uniform sensors detect active infrared flash signatures
LOW_BATTERY_WARNING  = 0x00004000  # Bit 14: Wearable power cell capacity dropped below 15%
BLEED_DETECTION_ALARM= 0x00008000  # Bit 15: Smart fabric impedance mesh registers fluid boundary breach

# Combat System Threat Avoidance Interlocks
CEASE_FIRE_ZONE_SET  = 0x00020000  # Bit 17: Injects coordinates into weapons mesh to prevent friendly fire
TACTICAL_BEACON_ON   = 0x00040000  # Bit 18: Activates high-frequency rescue transponder lines

# Personnel Monitoring System Watchdog Flag
WATCHDOG_HEARTBEAT   = 0x40000000  # Bit 30: 100ms cyclic soldier safety tracking interlock

@njit(fastmath=True, cache=True)
def evaluate_soldier_vitals(heart_rate, core_temp_c, spo2_pct, stride_rate_spm, flir_signal_active):
    """
    Numba-accelerated physiological mapping engine.
    Calculates operational fitness index thresholds and tactical IFF tracking profiles.
    """
    soldier_mask = 0x00000000
    
    # Absolute Priority 1: Critical Medical Stress Evaluation
    if heart_rate > 190 or heart_rate < 40 or core_temp_c > 40.5 or spo2_pct < 85.0:
        soldier_mask |= MEDICAL_ALERT_RAISED | TACTICAL_BEACON_ON | CEASE_FIRE_ZONE_SET
        return soldier_mask
        
    # Standard operational parameters configuration
    soldier_mask |= PERSONNEL_ACTIVE
    
    if heart_rate > 140 or stride_rate_spm > 120.0:
        # Asset is executing a high-stress sprint or physical advance
        soldier_mask |= BOOT_GPS_LOCK_ALIVE
    elif stride_rate_spm < 5.0:
        # Asset is stationary or entrenched
        soldier_mask |= TROOP_STATIONARY | BOOT_GPS_LOCK_ALIVE
    else:
        soldier_mask |= VITAL_SIGNS_NOMINAL | BOOT_GPS_LOCK_ALIVE
        
    # Process FLIR Identification Friend or Foe (IFF) reflection validations
    if flir_signal_active > 0.5:
        soldier_mask |= IFF_FRIENDLY_CONFIRMED | FLIR_IFF_EMITTING | CEASE_FIRE_ZONE_SET
        
    return soldier_mask

class SoldierTelemetryGateway:
    def __init__(self, vehicle_id="TACTICAL_HMMWV_8120"):
        self.vehicle_id = vehicle_id
        self.heartbeat_state = False
        self.active_personnel = {}
        self.load_soldier_manifest()

    def load_soldier_manifest(self):
        """Restores local troop logs to preserve deployment statuses during internet drops."""
        if os.path.exists(SOLDIER_TRACK_CACHE):
            try:
                with open(SOLDIER_TRACK_CACHE, 'r') as f:
                    self.active_personnel = json.load(f)
                print(f"[TROOP TRACE] Ingested offline personnel metrics for squad tied to {self.vehicle_id}.")
            except Exception:
                print("[WARNING] Soldier manifest data corrupted, establishing default squad registers.")

    def save_soldier_manifest(self):
        """Commits updated biographical and vital telemetry arrays directly to local storage blocks."""
        try:
            with open(SOLDIER_TRACK_CACHE, 'w') as f:
                json.dump(self.active_personnel, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Local manifest storage write failure: {e}")

    def generate_system_heartbeat(self):
        """Cyclic heartbeat alternator to protect personnel wireless data transfer frames."""
        self.heartbeat_state = not self.heartbeat_state
        return WATCHDOG_HEARTBEAT if self.heartbeat_state else 0x00000000

    def parse_wearable_packet(self, raw_telemetry_bytes):
        """
        Parses incoming tactical data packets from uniform sensors and embedded boot transceivers.
        Format: [Soldier_Callsign (2 bytes)][Heart_Rate (float)][Core_Temp_C (float)][SpO2_Pct (float)][Stride_SPM (float)][FLIR_Flag (float)]
        """
        if len(raw_telemetry_bytes) < 22:
            return None
            
        callsign = struct.unpack('!H', raw_telemetry_bytes[0:2])[0]
        payload = raw_telemetry_bytes[2:22]
        
        try:
            hr, temp, spo2, stride, flir = struct.unpack('!fffff', payload)
        except Exception:
            return None

        # Execute high-throughput personnel biometric processing loop
        control_bits = evaluate_soldier_vitals(hr, temp, spo2, stride, flir)
        
        # Append systemic safety watchdog flag
        control_bits |= self.generate_system_heartbeat()
        
        # Store live telemetry matrix state parameters inside the offline manifest
        self.active_personnel[str(callsign)] = {
            "control_matrix_hex": hex(control_bits),
            "vital_snapshots": {
                "heart_rate_bpm": int(hr),
                "core_temperature_c": round(temp, 1),
                "oxygen_saturation_pct": int(spo2)
            },
            "last_packet_epoch": time.time()
        }
        self.save_soldier_manifest()
        
        return callsign, control_bits

if __name__ == "__main__":
    print("[INIT] Universal Personal Telemetry & FLIR IFF Gateway Controller Active.")
    troop_manager = SoldierTelemetryGateway(vehicle_id="TACTICAL_HMMWV_8120")
    
    # Mock Scenario A: Soldier 501 executing high-intensity movement; FLIR badge visible on thermal optic feed
    mock_squad_packet_1 = struct.pack('!H', 501) + struct.pack('!fffff', 152.0, 38.2, 98.0, 134.0, 1.0)
    c_sign1, bits1 = troop_manager.parse_wearable_packet(mock_squad_packet_1)
    print(f"[PERSONNEL SYNC] Callsign: #{c_sign1} -> Control Word: {hex(bits1)}")

    # Mock Scenario B: Soldier 502 registers severe vitals drop (SpO2 down to 82%), triggering automated medical alerts
    mock_squad_packet_2 = struct.pack('!H', 502) + struct.pack('!fffff', 38.0, 35.1, 82.0, 0.0, 0.0)
    c_sign2, bits2 = troop_manager.parse_wearable_packet(mock_squad_packet_2)
    print(f"[CRITICAL FAILURE] Callsign: #{c_sign2} -> Control Word: {hex(bits2)} (Medical Emergency Initialized)")
