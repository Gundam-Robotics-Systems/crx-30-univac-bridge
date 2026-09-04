/**
 * ==============================================================================
 * UNIVAC IX / GUNDAM ROBOTICS SYSTEMS FGS PLASMA RAILGUN COMPONENT
 * Asset Target Reference Configuration: M1151 HMMWV Node #8120
 * Description: Armored straight-tube plasma weapon mounting to standard BMG pins.
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
    translate([0, 0, 40])
        fgs_conductive_acrylic_uv_core();
        
    // 4. Heavy-Duty Lower BMG Mounting Adapter & Cabling Enclosure Block
    translate([0, -25, -15])
        bmg_mount_interface_block();
}

module fgs_outer_lockheed_enclosure() {
    echo("[STAGE] Compiling Outer Protective Shell: Lockheed Martin Stealth Angular Specification.");
    // Main structural housing protecting internal optoelectronic and electrical lines
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
                    rotate([90, 0, 45])
                        cube([45, 8, 60], center=true);
            }
        }
    }
}

module fgs_inner_aerodynamic_tube() {
    echo("[STAGE] Compiling Aerodynamic Tube Layout: Smooth Internal Bevel Interface Matching Sketch.");
    // Inbound air flow moves down from Back (Z=120) to Front (Z=-30)
    color([0.75, 0.78, 0.8, 1.0]) {
        
        // REAR BARREL SEGMENT (Back Piece - Extends down to insert into front section)
        translate([0, 0, 95])
            difference() {
                union() {
                    cylinder(h=50, r=14, center=true);
                    // External mating bevel lip chamfer sloping out to fit inside the next section
                    translate([0, 0, -25])
                        cylinder(h=4, r1=12, r2=14, center=true);
                }
                // Seamless inner bore conduit channel
                cylinder(h=56, r=10, center=true);
            }
            
        // FORWARD BARREL SEGMENT (Front Piece - Features an internal bevel seat to maintain smooth air flow)
        translate([0, 0, -5])
            difference() {
                cylinder(h=50, r=14, center=true);
                
                // Main inner conduit channel
                cylinder(h=52, r=10, center=true);
                
                // Internal mating bevel profile cut directly into the pipe mouth interface
                // Prevents boundary-layer fluid drag separation and parasitic drag turbulence
                translate([0, 0, 23])
                    cylinder(h=5, r1=10, r2=12, center=true);
            }
    }
}

module fgs_conductive_acrylic_uv_core() {
    echo("[STAGE] Compiling Conductive Acrylic Ultraviolet Ionization Core (1/3 Total Length).");
    // Mid-barrel high-amplitude photon injection section
    color([0.2, 0.5, 0.9, 0.4]) {
        difference() {
            // Solid state transparent conductive polymer matrix sleeve
            cylinder(h=50, r=15.5, center=true);
            
            // Internal path bore matching the fluid compression tube channel lines
            cylinder(h=52, r=10, center=true);
            
            // Radially arrays mounting channels for the high-amplitude UV laser bolts
            for (angle = [0 : 60 : 360]) {
                rotate([0, 90, angle])
                    translate([0, 0, 11])
                        cylinder(h=10, r=3, center=true);
            }
        }
    }
}

module bmg_mount_interface_block() {
    echo("[STAGE] Compiling Lower Vehicle Mount Mount: BMG Pin Clearance with Integrated USB-B Interface.");
    color([0.15, 0.16, 0.17, 1.0]) {
        difference() {
            // Main solid heavy machine gun cradle block assembly
            cube([24, 40, 30], center=true);
            
            // Standard dual-axis mounting pin alignment hole
            rotate([0, 90, 0])
                cylinder(h=26, r=4, center=true);
                
            // Rear-facing protected square receptacle cut for the high-draw USB-B signal link
            translate([0, 18, -5])
                cube([12, 6, 12], center=true);
                
            // Internal path route for heavy routing cable lines to reach the upper enclosure
            translate([0, 0, 5])
                cube([8, 20, 25], center=true);
        }
    }
}
