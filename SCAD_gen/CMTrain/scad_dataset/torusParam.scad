// ============================================
// TORUS (parametric)
// ============================================
// param: major_r=25, minor_r=6, $fn_shape=120
// CALL:
torus_shape(major_r=25, minor_r=6, $fn_shape=120);

module torus_shape(major_r=25, minor_r=6, $fn_shape=120) {
    $fn = $fn_shape;
    rotate_extrude(angle = 360)
        translate([major_r, 0, 0])
            circle(r = minor_r);
}
