
// cube_param.scad
// param: size=10
module param_cube(size=10) {
    cube([size, size, size], center=true);
}
param_cube(size=10);
