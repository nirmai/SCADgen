// param: base_size=20, height=15
module pyramid(base_size=20, height=15) {
    linear_extrude(height=height, scale=0.01) square(base_size, center=true);
}
pyramid(base_size=20, height=15);
