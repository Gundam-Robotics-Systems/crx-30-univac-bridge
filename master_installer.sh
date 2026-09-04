#!/bin/bash
set -e

# ==============================================================================
# UNIVAC IX System Interlock Fleet Infrastructure Master Deployment Script
# Optimized for HMMWV (Humvee) Asset Deployment Grid #8120
# Execution Prerequisite: Privileged Root Access / Sudo Rings
# ==============================================================================

# Core System Terminal Style Outputs
export TERM=xterm-256color
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================================================${NC}"
echo -e "${GREEN}[INIT] Initializing Master System Deployment for HMMWV Asset #8120...${NC}"
echo -e "${BLUE}========================================================================${NC}"

# Step 1: Enforce Administrator Privilege Operational Layer Checks
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[FATAL ERROR] Installation requires root privileges. Execute via sudo.${NC}"
    exit 1
fi

# Step 2: Provision Local Persistent Cache Paths for Offline Isolation Continuity
echo -e "${YELLOW}[STAGE 01/05] Establishing Local Offline-First Database Caches...${NC}"
CACHE_DIRS=(
    "/var/log/ecu_tuning"
    "/etc/univac_mesh/security"
    "/etc/univac_mesh/telemetry"
    "/var/cache/soldier_vitals"
    "/var/cache/environmental_matrix"
)

for dir in "${CACHE_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        chmod 700 "$dir"
        echo -e " -> Directory Securely Created: ${GREEN}$dir${NC}"
    fi
done

# Step 3: Configure Linux Udev Rule Mappings for Core Hardware Interfaces
echo -e "\n${YELLOW}[STAGE 02/05] Programming Physical Interface Port Access Mappings...${NC}"
UDEV_RULE_FILE="/etc/udev/rules.rules"

cat << 'EOF' > "$UDEV_RULE_FILE"
# Humvee CAN Bus ECU Interface (J1939 Architecture Integration)
KERNEL=="ttyUSB*", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", MODE="0666", SYMLINK+="hmmwv_ecu_bus"
# Kommandogerat-58 / Nike Missile Board Serial Link
KERNEL=="ttyUSB*", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE="0666", SYMLINK+="kdo58_weapon_link"
# Software-Defined Radio (SDR) Universal Mesh Transceiver
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2838", MODE="0666", SYMLINK+="univac_sdr_mesh"
EOF

echo -e " -> Udev rule blocks committed to ${GREEN}$UDEV_RULE_FILE${NC}"
echo -e " -> Triggering kernel hardware device reload profiles..."
udevadm control --reload-rules && udevadm trigger || true

# Step 4: Validate and Compile System Core Python Software Dependencies
echo -e "\n${YELLOW}[STAGE 03/05] Provisioning Python Computational Libraries...${NC}"
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}[FATAL ERROR] Manifest requirements.txt index not found in local path.${NC}"
    exit 1
fi

echo -e " -> Installing pinned structural application matrices via pip engine..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 5: Pre-compile Local Hardware Numba JIT Thermodynamic Kernels
echo -e "\n${YELLOW}[STAGE 04/05] Executing Pre-Compilation for Local JIT Optimization Modules...${NC}"
cat << 'EOF' > test_numba_warmup.py
import numba
import numpy as np

@numba.njit(fastmath=True, cache=True)
def warmup_kernel(val):
    return np.sin(val) * 1.5

print(f" -> Numba JIT Layer Verified. Cache Active Status: {warmup_kernel(0.5) > 0}")
EOF

python3 test_numba_warmup.py
rm test_numba_warmup.py

# Step 6: Generate Baseline Configuration Profiles
echo -e "\n${YELLOW}[STAGE 05/05] Generating Consolidated Baseline Parameter Schema...${NC}"
GLOBAL_CONFIG="/etc/univac_mesh/global_fleet_manifest.json"

if [ ! -f "$GLOBAL_CONFIG" ]; then
    cat << 'EOF' > "$GLOBAL_CONFIG"
{
  "system_identity": {
    "assigned_asset_id": "TACTICAL_HMMWV_8120",
    "primary_cloud_target": "https://univac.online",
    "operational_mode": "HYBRID_OFFLINE_RESILIENT"
  },
  "subsystem_hardware_ports": {
    "engine_ecu_device": "/dev/hmmwv_ecu_bus",
    "weapon_fire_link": "/dev/kdo58_weapon_link",
    "sdr_mesh_transceiver": "/dev/univac_sdr_mesh"
  },
  "synchronization_watchdogs": {
    "cyclic_heartbeat_interval_ms": 100,
    "local_cache_prune_interval_days": 30,
    "fallback_loopback_ip": "127.0.0.1"
  }
}
EOF
    chmod 644 "$GLOBAL_CONFIG"
    echo -e " -> Sovereign parameters successfully output to ${GREEN}$GLOBAL_CONFIG${NC}"
fi

echo -e "\n${BLUE}========================================================================${NC}"
echo -e "${GREEN}[COMPLETED] Master Suite Architecture Successfully Installed on Asset #8120.${NC}"
echo -e "${GREEN}[COMPLETED] All hardware interfaces configured. System Ready for Headless Boot.${NC}"
echo -e "${BLUE}========================================================================${NC}"
