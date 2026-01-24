// ============================================
// HEX NUT (robust internal thread subtraction)
// ============================================
// Notes:
// - Subtract ONE over-length threaded "bolt" tool (with clearance).
// - No separate bore subtraction => no coplanar faces.
// - ε overshoot avoids z-coplanarity; use F6 (Render) for final.
//
// param: thread_diam=8, pitch=1.25, flat=13, thickness=6.5, clearance=0.25, add_threads=true, $fn_nut=96, $fn_thread=96
// CALL:
hex_nut(thread_diam=8, pitch=1.25, flat=13, thickness=6.5, clearance=0.25, add_threads=true, $fn_nut=96, $fn_thread=96);

module hex_nut(thread_diam=8, pitch=1.25, flat=13, thickness=6.5,
               clearance=0.25, add_threads=true, $fn_nut=96, $fn_thread=96)
{
    // Across-flats -> circumscribed cylinder diameter for $fn=6
    hex_d_circ = flat / cos(30);
    $fn = $fn_nut;

    difference() {
        // Hex prism body
        cylinder(h = thickness, d = hex_d_circ, $fn = 6);

        // Internal “tap” tool (over-length, with clearance)
        if (add_threads) {
            internal_thread_void(major_diam = thread_diam + clearance,
                                 pitch = pitch,
                                 length = thickness,
                                 $fn_thread = $fn_thread);
        } else {
            // Simple smooth bore (no threads)
            // Slightly over-length to avoid coplanar faces
            translate([0,0,-0.2]) cylinder(h = thickness + 0.4, d = thread_diam + clearance);
        }
    }
}

// Carves internal thread by subtracting an external-thread solid
module internal_thread_void(major_diam=8.25, pitch=1.25, length=6.5, $fn_thread=96)
{
    // Overshoot to avoid coplanar faces at both ends
    eps = 0.3;                         // increase to 0.5 if your preview still flickers
    turns = length / pitch;

    // Very simple thread geometry model
    minor_diam_raw = major_diam - 1.2 * pitch;   // crude depth estimate
    minor_diam = (minor_diam_raw < 0.1) ? 0.1 : minor_diam_raw;
    thread_depth = (major_diam - minor_diam) / 2;
    minor_r = minor_diam / 2;

    $fn = $fn_thread;

    // “Bolt-like” solid: core + helical ridge; slightly longer than the nut
    translate([0,0,-eps])
    union() {
        cylinder(h = length + 2*eps, d = minor_diam);
        // Helical ridge (triangular profile), over-length and twisted
        linear_extrude(height = length + 2*eps, twist = 360 * turns, convexity = 10)
            translate([minor_r, 0])
                polygon(points = [
                    [0, -pitch/2],
                    [thread_depth, 0],
                    [0,  pitch/2]
                ]);
    }
}
