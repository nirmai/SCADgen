// param: size=10, height=20
module hexagonal_prism(size=10, height=20) {
    linear_extrude(height=height) circle(r=size, $fn=6);
}
hexagonal_prism(size=10, height=20);
