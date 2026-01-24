// param: size=10, radius=2
module rounded_cube(size=10, radius=2) {
    minkowski() {
        cube([size-2*radius, size-2*radius, size-2*radius], center=true);
        sphere(r=radius);
    }
}
rounded_cube(size=10, radius=2);
