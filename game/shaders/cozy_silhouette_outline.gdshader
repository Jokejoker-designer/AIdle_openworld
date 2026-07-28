// Cozy Cyber-Pixel silhouette outline (ART-G01 foundation).
// Inverted-hull style for MeshInstance3D; cream-friendly dark edge, not neon.
// Apply as next_pass or second material on production meshes after Human visual check.
shader_type spatial;
render_mode unshaded, cull_front, depth_draw_always;

uniform vec4 outline_color : source_color = vec4(0.15, 0.12, 0.10, 1.0);
uniform float outline_growth : hint_range(0.0, 0.08) = 0.018;

void vertex() {
	vec3 n = normalize(NORMAL);
	VERTEX += n * outline_growth;
}

void fragment() {
	ALBEDO = outline_color.rgb;
	ALPHA = outline_color.a;
}
