/**
 * ==============================================================================
 * UNIVAC IX / GUNDAM ROBOTICS SYSTEMS TACTICAL ARMOR UPGRADE PACK
 * Asset Target Reference Configuration: M1151 HMMWV Node #8120
 * Description: Multi-faceted kinetic deflection shell with integrated V-Hull.
 * ==============================================================================
 */

// Global Render Resolution Configuration parameters
$fn = 64;

// Central Module Execution Target
render_modernized_armor_suite();

module render_modernized_armor_suite() {
    color([0.35, 0.38, 0.32, 1.0]) {
        // Step 1: Initialize Front Deflective Engine Glacis Shield
        translate([0, 90, 10]) 
            front_glacis_plate();
            
        // Step 2: Initialize Left Faceted Hull Shielding Profile
        translate([-42, 0, 5]) 
            lateral_shield_panel(is_left=true);
            
        // Step 3: Initialize Right Faceted Hull Shielding Profile
        translate([42, 0, 5]) 
            lateral_shield_panel(is_left=false);
            
        // Step 4: Initialize Lower Sub-Chassis Blast Deflection V-Hull
        translate([0, 0, -18]) 
            underbelly_v_hull();
    }
}

module front_glacis_plate() {
    echo("[STAGE] Compiling Front Glacis Plate: 55-Degree Kinetic Deflection Angle.");
    
    difference() {
        // Base plate extrusion layout
        rotate([55, 0, 0]) // Deflective slope parameter interlock
            cube([76, 3, 35], center=true);
            
        // Clean optical port clearance paths for the forward camera vision traps
        translate([-22, 0, 5]) 
            rotate([55, 0, 0]) 
                cube([10, 10, 10], center=true);
        translate([22, 0, 5]) 
            rotate([55, 0, 0]) 
                cube([10, 10, 10], center=true);
    }
}

module lateral_shield_panel(is_left=true) {
    echo("[STAGE] Compiling Lateral Shield Array. Side Selection Indicator Left=", is_left);
    
    rotation_angle = is_left ? -12 : 12;
    
    translate([0, 0, 0])
    difference() {
        // Core structural multi-faceted side armor segment
        rotate([0, rotation_angle, 0])
            cube([4, 120, 42], center=true);
            
        // Machine-cut cylindrical countersunk channels for the pyrotechnic release latches
        // Mapped to avoid structural compression bounds handled by armor_release_core.py
        for (y_offset = [-45, 0, 45]) {
            translate([0, y_offset, 10])
                rotate([0, 90, 0])
                    cylinder(h=15, r=2.5, center=true);
            translate([0, y_offset, -10])
                rotate([0, 90, 0])
                    cylinder(h=15, r=2.5, center=true);
        }
    }
}

module underbelly_v_hull() {
    echo("[STAGE] Compiling Lower Sub-Chassis Blast Deflection Channel (V-Hull Engine).");
    
    // Extrude a symmetric triangular prism along the length of the vehicle platform 
    // to direct land-displaced mine blast vectors outward away from driver cage floorboards
    rotate([90, 0, 90])
    linear_extrude(height=140, center=true)
    polygon(points=[
        [-38, 0],   // Left frame anchor line point
        [0, -16],   // Apex point of the V-Chassis displacement channel,    // Right frame anchor line point,    // Upper interior floorboard bracket line
        [-34, 4]    // Upper interior floorboard bracket line
    ]);
}
