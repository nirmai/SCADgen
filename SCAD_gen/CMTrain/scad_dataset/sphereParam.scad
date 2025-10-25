// ============================================
// SPHERE (parametric)
// ============================================
// param: diam=30, $fn_shape=96
// CALL:
sphere_shape(diam=30, $fn_shape=96);

module sphere_shape(diam=30, $fn_shape=96) {
    $fn = $fn_shape;
    sphere(d = diam);
}
