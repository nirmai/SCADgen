// ============================================================
// SPUR GEAR — CLEAN TEMPLATE (arc-based tooth, printable)
// ============================================================
// Naming conventions:
// - snake_case for variables and parameters
// - avoid OpenSCAD reserved words (e.g., DO NOT name a parameter "module")
// - degrees for trig (OpenSCAD sin/cos use degrees)
// - all lengths assumed millimeters
//
// UI metadata for your generator:
// param: teeth=24, modul=2, thickness=8, bore_diam=5, $fn_gear=128
// CALL:(teeth=10, modul=2, thickness=13, bore_diam=18, $fn_gear=14);
gear(teeth=24, modul=2, thickness=8, bore_diam=5, $fn_gear=128);

// --------------------------- Public API ---------------------------
/**
 * gear()
 * @param teeth       : integer >= 6 (fewer can look degenerate with simple teeth)
 * @param modul       : ISO gear module (mm per tooth). NOT named "module" to avoid keyword clash.
 * @param thickness   : extrusion height (mm)
 * @param bore_diam   : center hole (mm)
 * @param $fn_gear    : circle resolution for smoother arcs (overrides $fn locally)
 *
 * Notes:
 * - This is a simple, printable tooth outline using arcs (not true involute). Good for demos.
 * - For realistic loads/meshing, switch to an involute version later.
 */
module gear(teeth=24, modul=2, thickness=8, bore_diam=5, $fn_gear=128)
{
    // ------------ Lightweight argument checks (avoid hard failures) ------------
    valid_teeth     = (teeth >= 6);
    valid_modul     = (modul > 0);
    valid_thickness = (thickness > 0);
    valid_bore      = (bore_diam >= 0);

    // You can flip these to "assert(...)" if you prefer hard stops:
    if (!valid_teeth)     echo("[WARN] teeth should be >= 6 for a clean outline.");
    if (!valid_modul)     echo("[WARN] modul must be > 0.");
    if (!valid_thickness) echo("[WARN] thickness must be > 0.");
    if (!valid_bore)      echo("[WARN] bore_diam must be >= 0.");

    // ------------ Derived geometry (ISO-ish defaults) ------------
    m = modul;
    z = teeth;

    pitch_radius     = 0.5 * m * z;       // r_p
    addendum_radius  = pitch_radius + m;  // r_a
    dedendum_factor  = 1.25;              // common approximation
    root_radius_raw  = pitch_radius - dedendum_factor * m;
    root_radius      = (root_radius_raw < 0.1) ? 0.1 : root_radius_raw; // avoid negatives

    // Tooth angular half-width at pitch circle (degrees).
    // This arc-based tooth centers a wedge around the tooth centerline.
    half_tooth_deg   = 180 / z;

    // local resolution for smooth circles
    gear_fn = $fn_gear;

    // ------------ Build 3D ------------
    // Use local $fn inside scope (OpenSCAD respects lexical $fn)
    // 'difference' to subtract the bore
    // linear_extrude is centered at z=0..thickness
    $fn = gear_fn;
    linear_extrude(height = thickness)
        difference() {
            gear_2d(z, pitch_radius, addendum_radius, root_radius, half_tooth_deg);
            if (bore_diam > 0)
                circle(d = bore_diam);
        }
}

// --------------------------- Internal: 2D outline ---------------------------
/**
 * gear_2d()
 * Builds a 2D gear via repeated single-tooth wedges around the origin.
 */
module gear_2d(teeth_count, pitch_radius, addendum_radius, root_radius, half_tooth_deg)
{
    tooth_step_deg = 360 / teeth_count;
    union() {
        for (i = [0 : teeth_count - 1])
            rotate(i * tooth_step_deg)
                single_tooth(addendum_radius, root_radius, half_tooth_deg);
    }
}

/**
 * single_tooth()
 * Simple wedge-like tooth made of four arc points.
 * NOTE: This is an approximation (not a true involute).
 */
module single_tooth(addendum_radius, root_radius, half_angle_deg)
{
    // Four key points: root−, tip−, tip+, root+
    pts = [
        [ root_radius * cos(-half_angle_deg),     root_radius * sin(-half_angle_deg)     ],
        [ addendum_radius * cos(-half_angle_deg/2), addendum_radius * sin(-half_angle_deg/2) ],
        [ addendum_radius * cos( half_angle_deg/2), addendum_radius * sin( half_angle_deg/2) ],
        [ root_radius * cos( half_angle_deg),     root_radius * sin( half_angle_deg)     ]
    ];
    polygon(points = pts);
}

