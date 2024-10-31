from flask import Blueprint, render_template, jsonify, request
import math
import random
import colorsys

geometric_pattern_bp = Blueprint('geometric_pattern', __name__)

def generate_color_palette(base_hue, palette_type="monochromatic"):
    colors = []
    
    if palette_type == "monochromatic":
        for i in range(4):
            colors.append(hsv_to_hex(base_hue, 0.3 + (i * 0.2), 0.9))
    elif palette_type == "complementary":
        colors = [
            hsv_to_hex(base_hue, 0.7, 0.9),
            hsv_to_hex((base_hue + 0.5) % 1.0, 0.7, 0.9),
            hsv_to_hex(base_hue, 0.5, 0.9),
            hsv_to_hex((base_hue + 0.5) % 1.0, 0.5, 0.9),
        ]
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

def generate_geometric_pattern(
    symmetry=6,
    layers=3,
    complexity=0.7,
    rotation=0,
    base_hue=0.5,
    palette_type="monochromatic"
):
    pattern = {
        'shapes': [],
        'colors': generate_color_palette(base_hue, palette_type),
        'rotationSpeed': random.uniform(0.1, 0.3)
    }
    
    # Generate base shapes for each layer
    for layer in range(layers):
        radius = 100 + (layer * 50)
        points = []
        num_points = symmetry * (layer + 2)
        
        # Generate base points
        for i in range(num_points):
            angle = (2 * math.pi * i) / num_points + math.radians(rotation)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            points.append((x, y))
        
        # Generate shapes based on complexity
        if random.random() < complexity:
            # Create polygons
            for i in range(0, len(points), symmetry):
                shape_points = []
                for j in range(symmetry):
                    idx = (i + j) % len(points)
                    shape_points.append(points[idx])
                
                pattern['shapes'].append({
                    'type': 'polygon',
                    'points': shape_points,
                    'color': random.choice(pattern['colors']),
                    'layer': layer
                })
        
        # Add connecting lines
        for i in range(len(points)):
            if random.random() < complexity:
                start = points[i]
                end = points[(i + symmetry) % len(points)]
                pattern['shapes'].append({
                    'type': 'line',
                    'start': start,
                    'end': end,
                    'color': random.choice(pattern['colors']),
                    'layer': layer
                })
    
    return pattern

@geometric_pattern_bp.route('/')
def geometric_pattern_index():
    return render_template('geometric_pattern/index.html')

@geometric_pattern_bp.route('/generate')
def get_pattern():
    symmetry = int(request.args.get('symmetry', 6))
    layers = int(request.args.get('layers', 3))
    complexity = float(request.args.get('complexity', 0.7))
    rotation = float(request.args.get('rotation', 0))
    base_hue = float(request.args.get('hue', 0.5))
    palette_type = request.args.get('palette', 'monochromatic')
    
    pattern_data = generate_geometric_pattern(
        symmetry=symmetry,
        layers=layers,
        complexity=complexity,
        rotation=rotation,
        base_hue=base_hue,
        palette_type=palette_type
    )
    return jsonify(pattern_data) 