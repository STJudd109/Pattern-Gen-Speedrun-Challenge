from flask import Blueprint, render_template, jsonify, request
import math
import random

tessellation_pattern_bp = Blueprint('tessellation_pattern', __name__)

@tessellation_pattern_bp.route('/')
def tessellation_pattern_index():
    return render_template('tessellation_pattern/index.html')

@tessellation_pattern_bp.route('/generate')
def generate_pattern():
    # Get parameters from request
    pattern_type = request.args.get('pattern', 'triangular')
    cell_size = float(request.args.get('cellSize', 50))
    rotation = float(request.args.get('rotation', 0))
    offset = float(request.args.get('offset', 0))
    color_scheme = request.args.get('colorScheme', 'monochromatic')
    
    # Generate base pattern unit
    pattern_data = {
        'type': pattern_type,
        'cellSize': cell_size,
        'rotation': rotation,
        'offset': offset,
        'colorScheme': color_scheme,
        'baseUnit': generate_base_unit(pattern_type, cell_size),
        'colors': generate_color_scheme(color_scheme)
    }
    
    return jsonify(pattern_data)

def generate_base_unit(pattern_type, cell_size):
    # Generate coordinates for basic tessellation units
    if pattern_type == 'triangular':
        return {
            'points': [
                [0, 0],
                [cell_size, 0],
                [cell_size/2, cell_size * math.sin(math.pi/3)]
            ]
        }
    elif pattern_type == 'square':
        return {
            'points': [
                [0, 0],
                [cell_size, 0],
                [cell_size, cell_size],
                [0, cell_size]
            ]
        }
    elif pattern_type == 'hexagonal':
        points = []
        for i in range(6):
            angle = i * math.pi/3
            x = cell_size * math.cos(angle)
            y = cell_size * math.sin(angle)
            points.append([x, y])
        return {'points': points}
    
    return {'points': [[0, 0], [cell_size, 0], [cell_size, cell_size], [0, cell_size]]}

def generate_color_scheme(scheme_type):
    base_hue = random.random()
    if scheme_type == 'monochromatic':
        return [
            hsv_to_hex(base_hue, 0.8, 0.9),
            hsv_to_hex(base_hue, 0.6, 0.8),
            hsv_to_hex(base_hue, 0.4, 0.7)
        ]
    elif scheme_type == 'complementary':
        return [
            hsv_to_hex(base_hue, 0.8, 0.9),
            hsv_to_hex((base_hue + 0.5) % 1.0, 0.8, 0.9),
            hsv_to_hex(base_hue, 0.6, 0.7)
        ]
    else:
        return ['#000000', '#666666', '#CCCCCC']

def hsv_to_hex(h, s, v):
    # Convert HSV to hex color string
    i = int(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    
    i = i % 6
    values = [
        (v, t, p),
        (q, v, p),
        (p, v, t),
        (p, q, v),
        (t, p, v),
        (v, p, q)
    ]
    
    rgb = values[i]
    return '#{:02x}{:02x}{:02x}'.format(
        int(rgb[0] * 255),
        int(rgb[1] * 255),
        int(rgb[2] * 255)
    ) 