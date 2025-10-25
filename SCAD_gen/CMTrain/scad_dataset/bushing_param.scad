
// bushing_param.scad
// param: inner_d=10, outer_d=20, thickness=8
module param_bushing(inner_d=10, outer_d=20, thickness=8) {
    difference() {
        cylinder(h = thickness, r=outer_d/2, $fn=64);
        cylinder(h = thickness+2, r=inner_d/2, $fn=64);
    }
}
param_bushing(inner_d=10, outer_d=20, thickness=8);
