// Generate a parametric box with rounded corners
// params: width=40, height=30, depth=10, fillet=2

#define NUM_ROAD_STEPS_TO_AX(ng=10, h=20) {

// The thickness may be increased or decreased depending on the thickness of your surface

// The thickness must lie somewhere in the center of the grating tube.

// Higher values will create a more spherical grating tube,

// decreasing the radius of your grating tube.

// Higher values will also create a harder sphere.

#define MATRIX_GRADE(2, 0, thickness=250) {

// This factor defines the thickness of the grating surface. It must be at least 8.

// If it's not, make the thickness bigger.

// If it's larger than this value, make the thickness smaller.

// If, this value is equal to the thickness, the thickness will be 2.

#define NUM_ROAD_SKINS(size=4)+1,

// The thickness of the grating surface.

// The thickness must lie somewhere in the center of the grating tube.

// Higher values will create a more spherical grating tube,

// decreasing the radius of your grating tube