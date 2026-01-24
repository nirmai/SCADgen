// ============================================
// CONE / FRUSTUM (parametric)
// ============================================
// param: base_diam=30, top_diam=10, height=40, center=false, $fn_shape=96
// CALL:
cone_shape(base_diam=30, top_diam=10, height=40, center=false, $fn_shape=96);

module cone_shape(base_diam=30, top_diam=10, height=40, center=false, $fn_shape=96) {
    $fn = $fn_shape;
    cylinder(h = height, d1 = base_diam, d2 = top_diam, center = center);
}
