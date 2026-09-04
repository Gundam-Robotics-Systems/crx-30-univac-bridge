/**
 * ==============================================================================
 * UNIVAC IX / GUNDAM ROBOTICS SYSTEMS HIGH-MOBILITY CHASSIS ENHANCEMENT
 * Asset Target Reference Configuration: M1151 HMMWV Node #8120
 * Description: Deep-socket rotary wheel armor disk with sidewall flex clearance.
 * ==============================================================================
 */

// Global Render Resolution Profiles
$fn = 128;

// Primary Execution Assembly Target
render_rotary_wheel_armor();

module render_rotary_wheel_armor() {
    color([0.28, 0.30, 0.26, 1.0]) {
        difference() {
            union() {
                // Step 1: Base Deflective Shielding Disk (Faceted Cone Base)
                cylinder(h=8, r1=215, r2=245, center=true);
                
                // Step 2: Outer 15-Degree Flanged Deflection Ring Rim
                translate([0, 0, 5])
                    cylinder(h=4, r1=245, r2=255, center=true);
                    
                // Step 3: Central Deep-Socket Structural Mounting Sleeve
                translate([0, 0, -20])
                    cylinder(h=40, r=65, center=true);
            }
            
            // Step 4: Inner Core Clearance Bore (Creates the 10mm Steel Shield Wall Thickness)
            translate([0, 0, -2])
                cylinder(h=10, r1=205, r2=235, center=true);
                
            // Step 5: Recessed Deep-Socket Hexagonal Spindle Nut Receptacle
            // Fits a standard deep impact socket for secure torque fastening
            translate([0, 0, -25])
                rotate([0, 0, 30])
                    cylinder(h=35, r=42, center=true, $fn=6);
                    
            // Step 6: Axle Center Pin Pass-Through Bore Hole
            translate([0, 0, -42])
                cylinder(h=20, r=25, center=true);
                
            // Step 7: Circular Array of 8 Ventilation & Mud-Ejection Ports
            // Positioned to allow cooling airflow across brake components
            for (angle = [0 : 45 : 360]) {
                rotate([0, 0, angle])
                    translate([135, 0, 0])
                        cylinder(h=30, r=18, center=true);
            }
        }
    }
}
