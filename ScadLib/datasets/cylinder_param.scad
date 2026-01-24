// ============================================
// ROBUST CYLINDER / TUBE (with cutter mode)
// ============================================
// Notes:
// - Use as_cutter=true when subtracting (difference()) to avoid coplanar z-faces.
// - For tubes (inner_diam>0), inner subtraction also overshoots.
// - Increase overshoot to 0.5 if your preview still flickers; F6 render is exact.
//
// param: diam=20, height=40, center=false, inner_diam=0, as_cutter=false, overshoot=0.3, $fn_shape=96
// CALL:
cyl_shape(diam=20, height=40, center=false, inner_diam=0, as_cutter=false, overshoot=0.3, $fn_shape=96);

module cyl_shape(diam=20, height=40, center=false,
                 inner_diam=0, as_cutter=false,
                 overshoot=0.3, $fn_shape=96)
{
    $fn = $fn_shape;

    // Determine final height and z-shift when overshooting
    extra_h = as_cutter ? (height + 2*overshoot) : height;
    z_shift = 0;
    if (as_cutter) {
        // Overshoot both ends to avoid coplanar faces with the host solid
        z_shift = center ? 0 : -overshoot;
    }

    // Solid cylinder (no inner bore)
    if (inner_diam <= 0) {
        translate([0,0,z_shift])
            cylinder(h = extra_h, d = diam, center = center);
    }
    // Tube: subtract an over-length inner cylinder
    else {
        difference() {
            translate([0,0,z_shift])
                cylinder(h = extra_h, d = diam, center = center);

            // Inner subtraction: always over-length to avoid coplanarity inside
            inner_extra_h = height + 2*overshoot;
            inner_shift   = center ? 0 : -overshoot;
            translate([0,0,inner_shift])
                cylinder(h = inner_extra_h, d = inner_diam, center = center);
        }
    }
}
