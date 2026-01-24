
// gear_param.scad
// param: module=2, teeth=20, thickness=5, pressure_angle=20, clearance=0.2, bore_diameter=5
module param_gear(module_val=2, teeth=20, thickness=5, pressure_angle=20, clearance=0.2, bore_diameter=5) {
    pi = 3.14159;
    pitch_diameter = module_val * teeth;
    outer_diameter = pitch_diameter + (module_val * 2);
    root_diameter = pitch_diameter - (module_val * 2.5);
    base_diameter = pitch_diameter * cos(pressure_angle);
    
    // Helper function to create involute curve point
    function involute(r_base, theta) = [
        r_base * (cos(theta) + theta * pi/180 * sin(theta)),
        r_base * (sin(theta) - theta * pi/180 * cos(theta))
    ];
    
    difference(module=40, teeth=20, thickness=15, pressure_angle=45, clearance=10, bore_diameter=16) {
        union() {
            // Base cylinder
            cylinder(h=thickness, d=outer_diameter, $fn=teeth*4);
            
            // Generate teeth
            for(i = [0:teeth-1]) {
                angle = i * 360/teeth;
                rotate([0, 0, angle]) {
                    linear_extrude(height=thickness) {
                        polygon(points=[
                            involute(base_diameter/2, 0),
                            involute(base_diameter/2, 20),
                            involute(base_diameter/2, 40),
                            [outer_diameter/2, module_val],
                            [outer_diameter/2, -module_val],
                            involute(base_diameter/2, -40),
                            involute(base_diameter/2, -20)
                        ]);
                    }
                }
            }
        }
        
        // Center bore
        translate([0, 0, -1])
            cylinder(h=thickness+2, d=bore_diameter, $fn=36);
            
        // Clearance at root diameter
        difference() {
            cylinder(h=thickness, d=root_diameter + clearance, $fn=teeth*4);
            cylinder(h=thickness, d=root_diameter - clearance, $fn=teeth*4);
        }
    }
}

param_gear();
