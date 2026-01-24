// ============================================
// HEX BOLT (simple thread option)
// ============================================
// Notes:
// - head_flat is across-flats (S). Cylinder with $fn=6 uses circumscribed circle,
//   so we set d = S / cos(30) to match across-flats.
// - Threads are a lightweight helical approximation for prints/demos.
//
// param: shaft_diam=8, shaft_len=30, head_flat=13, head_height=6, thread_pitch=1.25, thread_len=20, add_threads=true, $fn_bolt=96, $fn_thread=64
// CALL:
hex_bolt(shaft_diam=8, shaft_len=30, head_flat=13, head_height=6, thread_pitch=1.25, thread_len=20, add_threads=true, $fn_bolt=96, $fn_thread=64);

module hex_bolt(shaft_diam=8, shaft_len=30, head_flat=13, head_height=6,
                thread_pitch=1.25, thread_len=20, add_threads=true,
                $fn_bolt=96, $fn_thread=64)
{
    // Build with head at z=[0, +head_height], shaft extends to negative z
    $fn = $fn_bolt;
    head_d_circ = head_flat / cos(30);  // across-corners diameter to get across-flats=head_flat

    // Head
    translate([0,0,0])
        cylinder(h = head_height, d = head_d_circ, $fn = 6);

    // Shaft (unthreaded core)
    translate([0,0,-shaft_len])
        cylinder(h = shaft_len, d = shaft_diam);

    // Optional simple threads on the lower portion of the shaft
    if (add_threads && thread_len > 0) {
        translate([0,0,-thread_len])
            simple_outer_thread(major_diam = shaft_diam,
                                pitch = thread_pitch,
                                length = thread_len,
                                $fn_thread = $fn_thread);
    }
}

// ---- Simple external thread: helical ridge + core ----
module simple_outer_thread(major_diam=8, pitch=1.25, length=10, $fn_thread=64) {
    turns = length / pitch;
    minor_diam_raw = major_diam - 1.2 * pitch;     // crude depth
    minor_diam = (minor_diam_raw < 0.1) ? 0.1 : minor_diam_raw;
    thread_depth = (major_diam - minor_diam) / 2;
    minor_r = minor_diam / 2;

    // Core
    $fn = $fn_thread;
    cylinder(h = length, d = minor_diam);

    // Helical ridge (triangular)
    linear_extrude(height = length, twist = 360 * turns, center = false)
        translate([minor_r, 0])
            polygon(points = [
                [0, -pitch/2],          // at minor radius
                [thread_depth, 0],      // outward to major
                [0,  pitch/2]
            ]);
}
