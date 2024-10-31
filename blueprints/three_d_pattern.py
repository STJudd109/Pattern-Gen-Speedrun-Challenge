from flask import Blueprint, render_template, jsonify, request
import random
import math

three_d_pattern_bp = Blueprint('three_d_pattern', __name__)

@three_d_pattern_bp.route('/')
def three_d_pattern_index():
    return render_template('three_d_pattern/index.html')

@three_d_pattern_bp.route('/generate')
def generate_pattern():
    pattern_type = request.args.get('type', 'cube')
    complexity = int(request.args.get('complexity', 5))
    rotation_speed = float(request.args.get('rotation_speed', 0.01))
    color_scheme = request.args.get('color_scheme', 'rainbow')
    
    pattern_data = {
        'type': pattern_type,
        'complexity': complexity,
        'rotation_speed': rotation_speed,
        'color_scheme': color_scheme,
        'elements': generate_3d_elements(pattern_type, complexity)
    }
    
    return jsonify(pattern_data)

def generate_3d_elements(pattern_type, complexity):
    elements = []
    
    if pattern_type == 'cube':
        for i in range(complexity):
            elements.append({
                'type': 'cube',
                'position': [
                    random.uniform(-5, 5),
                    random.uniform(-5, 5),
                    random.uniform(-5, 5)
                ],
                'rotation': [
                    random.uniform(0, math.pi * 2),
                    random.uniform(0, math.pi * 2),
                    random.uniform(0, math.pi * 2)
                ],
                'scale': random.uniform(0.5, 2.0)
            })
    elif pattern_type == 'sphere':
        # Generate sphere pattern
        for i in range(complexity):
            elements.append({
                'type': 'sphere',
                'position': [
                    random.uniform(-5, 5),
                    random.uniform(-5, 5),
                    random.uniform(-5, 5)
                ],
                'radius': random.uniform(0.3, 1.0)
            })
            
    return elements
