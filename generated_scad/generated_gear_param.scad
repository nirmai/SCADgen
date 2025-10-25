
// gear_param.scad
// param: module=2, teeth=12, thickness=5
module param_gear(module_val=2, teeth=12, thickness=5) {
    difference(module=25, teeth=10, thickness=14) {
        cylinder(h = thickness, r = (module_val*teeth)/2, $fn=teeth*4);
        cylinder(h = thickness+1, r = (module_val*teeth)/4);
    }
}
param_gear(module_val=2, teeth=12, thickness=5);
