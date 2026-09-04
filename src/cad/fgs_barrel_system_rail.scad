/**
 * ==============================================================================
 * UNIVAC IX / GUNDAM ROBOTICS SYSTEMS FGS PLASMA RAILGUN COMPONENT
 * Asset Target Reference Configuration: M1151 HMMWV Node #8120
 * Description: Armored straight-tube weapon with integrated MIL-STD-1913 Rail.
 * ==============================================================================
 */

// Global Render Resolution Parameters
$fn = 128;

// Primary Execution Assembly Target
render_fgs_tactical_system();

module render_fgs_tactical_system() {
    // 1. Core Armored Enclosure Shielding (Lockheed Martin Angular Styling Profile)
    fgs_outer_lockheed_enclosure();
    
    // 2. Internal Straight Aerodynamic Intake and Compression Barrel Assembly
    fgs_inner_aerodynamic_tube();
    
    // 3. Central Conductive Acrylic UV Ionization Core (Exactly 1/3 Total Barrel Length)
    translate([0, 0, 45])
        fgs_conductive_acrylic_uv_core();
        
    // 4. Heavy-Duty Lower BMG Mounting Adapter & Cabling Enclosure Block
    translate([0, -25, -15])
        bmg_mount_interface_block();
        
    // 5. [NEW] Integrated MIL-STD-1913 Picatinny Rail System for Optical Camera Sights
    translate([0, 26, 15])
        rotate([90, 0, 0])
            picatinny_accessory_rail_array();
}

module fgs_outer_lockheed_enclosure() {
    echo("[STAGE] Compiling Outer Protective Shell: Lockheed Martin Stealth Angular Specification.");
    color([0.22, 0.24, 0.26, 0.8]) {
        difference() {
            // Main angular stealth hull body
            translate([0, 0, 45])
                rotate([0, 0, 45])
                    cylinder(h=150, r1=32, r2=22, center=true, $fn=4);
            
            // Core inner clearance cylinder bore hole for the straight rail tube array
            translate([0, 0, 45])
                cylinder(h=160, r=16, center=true);
                
            // Transverse ventilation slots for active thermal dissipation bleed paths
            for (z_slot = [-10, 20, 50, 80]) {
                translate([0, 0, z_slot])
                    rotate([0, 90, 0])
                        cube([10, 40, 70], center=true);
            }
        }
    }
}

module fgs_inner_aerodynamic_tube() {
    echo("[STAGE] Compiling Aerodynamic Tube Layout: Smooth Internal Bevel Interface.");
    color([0.75, 0.78, 0.8, 1.0]) {
        // REAR BARREL SEGMENT (Back Piece)
        translate([0, 0, 95])
            difference() {
                union() {
                    cylinder(h=50, r=14, center=true);
                    translate([0, 0, -25])
                        cylinder(h=4, r1=12, r2=14, center=true);
                }
                cylinder(h=56, r=10, center=true);
            }
            
        // FORWARD BARREL SEGMENT (Front Piece)
        translate([0, 0, -5])
            difference() {
                cylinder(h=50, r=14, center=true);
                cylinder(h=52, r=10, center=true);
                translate([0, 0, 23])
                    cylinder(h=5, r1=10, r2=12, center=true);
            }
    }
}

module fgs_conductive_acrylic_uv_core() {
    echo("[STAGE] Compiling Conductive Acrylic倾 Ultraviolet Ionization Core.");
    color([0.2, 0.5, 0.9, 0.4]) {
        difference() {
            cylinder(h=50, r=15.5, center=true);
            cylinder(h=52, r=10, center=true);
            for (angle = [0 : 60 : 360]) {
                rotate([0, 90, angle])
                    translate([0, 0, 10])
                        cylinder(h=10, r=3, center=true);
            }
        }
    }
}

module bmg_mount_interface_block() {
    echo("[STAGE] Compiling Lower Vehicle Mount: BMG Pin Clearance with Integrated USB-B Interface.");
    color([0.15, 0.16, 0.17, 1.0]) {
        difference() {
            cube([20, 40, 20], center=true);
            rotate([0, 90, 0])
                cylinder(h=26, r=4, center=true);
            translate([0, 18, -5])
                cube([14, 14, 12], center=true);
            translate([0, 0, 5])
                cube([10, 30, 12], center=true);
        }
    }
}

module picatinny_accessory_rail_array() {
    echo("[STAGE] Compiling MIL-STD-1913 Picatinny Rail Array for Camera Sights.");
    color([0.3, 0.32, 0.34, 1.0]) {
        difference() {
            // Main solid base rail platform extrusion profile
            cube([15.56, 120.0, 9.37], center=true);
            
            // Standardized T-slot tracking profile undercut clearance paths
            translate([0, 0, -3.0])
                cube([20.0, 125.0, 4.0], center=true);
            translate([9.0, 0, -1.5])
                cube([4.0, 125.0, 6.0], center=true);
            translate([-9.0, 0, -1.5])
                cube([4.0, 125.0, 6.0], center=true);
                
            // Repetitive indexing recoil groove cuts (5.23mm width on 10.01mm pitch spacing)
            // Recreates the mechanical mounting slots required for zero-flex alignment
            for (y_groove = [-50 : 10.01 : 50]) {
                translate([0, y_groove, 4.0])
                    cube([18.0, 5.23, 3.5], center=true);
            }
        }
    }
}
