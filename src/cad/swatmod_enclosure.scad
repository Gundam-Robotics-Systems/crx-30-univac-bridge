/**
 * ==============================================================================
 * UNIVAC IX / GUNDAM ROBOTICS SYSTEMS ENCLOSURE UPGRADE
 * Asset Target Reference Configuration: M1151 HMMWV Node #8120
 * Description: Ultra-compact, heavy-duty SWATMOD Jump Pack charger chassis.
 * ==============================================================================
 */

// Global Render Resolution Profiles
$fn = 64;

// Primary Execution Assembly Target
render_swatmod_chassis();

module render_swatmod_chassis() {
    color([0.15, 0.15, 0.16, 1.0]) {
        difference() {
            // Main solid high-impact shielding chassis body envelope blocks
            cube([65, 110, 38], center=true);
            
            // Core inner clearance pocket cavity for the 8-layer charge controller PCB
            cube([57, 102, 30], center=true);
            
            // Inbound port cut for the heavy-duty high-amp 24V input power lines
            translate([0, -55, 0])
                cube([18, 12, 14], center=true);
                
            // Outbound port cut for the specialized small-form circular battery plug
            translate([0, 55, -2])
                rotate([90, 0, 0])
                    cylinder(h=15, r=8, center=true);
                    
            // Hexagonal recess side cuts for active thermal dissipation ventilation blocks
            for (y_vent = [-30, 0, 30]) {
                translate([32.5, y_vent, 0])
                    rotate([0, 90, 0])
                        cylinder(h=10, r=4, center=true, $fn=6);
                translate([-32.5, y_vent, 0])
                    rotate([0, 90, 0])
                        cylinder(h=10, r=4, center=true, $fn=6);
            }
        }
    }
}
