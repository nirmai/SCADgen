// param: major_radius=20, minor_radius=5
module param_torus(major_radius=20, minor_radius=5) {
    rotate_extrude() translate([major_radius, 0, 0]) circle(r=minor_radius);
}
param_torus(major_radius=20, minor_radius=5);
