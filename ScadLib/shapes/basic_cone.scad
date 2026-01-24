// param: radius=10, height=20
module param_cone(radius=10, height=20) {
    cylinder(r1=radius, r2=0, h=height, center=true);
}
param_cone(radius=10, height=20);
