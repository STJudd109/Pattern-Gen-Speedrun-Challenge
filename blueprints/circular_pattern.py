from flask import Blueprint, render_template, jsonify, request
import math
import random
import colorsys

circular_pattern_bp = Blueprint('circular_pattern', __name__)

def generate_color_palette(base_hue, palette_type="complementary"):
    colors = []
    
    if palette_type == "complementary":
        colors = [
            hsv_to_hex(base_hue, 0.7, 0.9),
            hsv_to_hex((base_hue + 0.5) % 1.0, 0.7, 0.9),
            hsv_to_hex(base_hue, 0.5, 0.9),
            hsv_to_hex((base_hue + 0.5) % 1.0, 0.5, 0.9),
        ]
    elif palette_type == "analogous":
        for i in range(4):
            hue = (base_hue + (i * 0.1)) % 1.0
            colors.append(hsv_to_hex(hue, 0.7, 0.9))
    elif palette_type == "triadic":
        for i in range(3):
            hue = (base_hue + (i * 0.33)) % 1.0
            colors.append(hsv_to_hex(hue, 0.7, 0.9))
            colors.append(hsv_to_hex(hue, 0.5, 0.9))
    
    return colors

def hsv_to_hex(h, s, v):
    rgb = colorsys.hsv_to_rgb(h, s, v)
    return '#{:02x}{:02x}{:02x}'.format(
        int(rgb[0] * 255),
        int(rgb[1] * 255),
        int(rgb[2] * 255)
    )

def generate_circular_pattern(
    num_circles=8,
    num_points=12,
    connection_density=0.7,
    symmetry=1,
    color_palette=None,
    base_hue=0.5,
    palette_type="complementary"
):
    if color_palette is None:
        color_palette = generate_color_palette(base_hue, palette_type)
    
    pattern = {
        'circles': [],
        'connections': [],
        'rotationSpeed': random.uniform(0.1, 0.5)
    }
    
    # Generate points for each circle with symmetry
    for circle_idx in range(num_circles):
        radius = 50 + (circle_idx * 30)
        circle_points = []
        
        # Generate base points for one segment
        points_per_segment = num_points // symmetry
        for point_idx in range(points_per_segment):
            angle = (2 * math.pi * point_idx) / num_points
            
            # Repeat points for symmetry
            for sym in range(symmetry):
                sym_angle = angle + (2 * math.pi * sym / symmetry)
                x = radius * math.cos(sym_angle)
                y = radius * math.sin(sym_angle)
                
                circle_points.append({
                    'x': x,
                    'y': y,
                    'color': random.choice(color_palette)
                })
        
        pattern['circles'].append({
            'radius': radius,
            'points': circle_points,
            'color': random.choice(color_palette)
        })
        
        # Generate connections between points
        if circle_idx > 0:
            for i in range(len(circle_points)):
                if random.random() < connection_density:
                    # Maintain symmetry in connections
                    for sym in range(symmetry):
                        from_idx = (i + (sym * points_per_segment)) % len(circle_points)
                        to_idx = ((i + random.randint(0, 2)) + (sym * points_per_segment)) % len(circle_points)
                        
                        pattern['connections'].append({
                            'from': {
                                'circle': circle_idx - 1,
                                'point': from_idx
                            },
                            'to': {
                                'circle': circle_idx,
                                'point': to_idx
                            },
                            'color': random.choice(color_palette)
                        })
    
    return pattern

@circular_pattern_bp.route('/')
def circular_pattern_index():
    return render_template('circular_pattern/index.html')

@circular_pattern_bp.route('/generate')
def get_pattern():
    num_circles = int(request.args.get('circles', 8))
    num_points = int(request.args.get('points', 12))
    connection_density = float(request.args.get('density', 0.7))
    symmetry = int(request.args.get('symmetry', 1))
    base_hue = float(request.args.get('hue', 0.5))
    palette_type = request.args.get('palette', 'complementary')
    
    pattern_data = generate_circular_pattern(
        num_circles=num_circles,
        num_points=num_points,
        connection_density=connection_density,
        symmetry=symmetry,
        base_hue=base_hue,
        palette_type=palette_type
    )
    return jsonify(pattern_data) 