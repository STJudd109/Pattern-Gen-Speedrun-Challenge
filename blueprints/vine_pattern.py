from flask import Blueprint, render_template, jsonify, request
import uuid
from blueprints.patterns.vine_pattern import VinePattern
from datetime import datetime
from typing import Dict, Any, List, Tuple
import json

vine_pattern_bp = Blueprint('vine_pattern', __name__)
active_vines = {}  # Store active vine patterns

@vine_pattern_bp.route('/')
def vine_pattern_index():
    return render_template('vine_pattern/index.html')

@vine_pattern_bp.route('/init')
def init_vine():
    start_x = float(request.args.get('start_x', 0))
    start_y = float(request.args.get('start_y', 0))
    
    config = {
        'growth_pattern': request.args.get('growth_pattern', 'climbing'),
        'growth_speed': float(request.args.get('growth_speed', 1.0)),
        'branch_probability': float(request.args.get('branch_probability', 0.3)),
        'leaf_probability': float(request.args.get('leaf_probability', 0.4)),
        'flower_probability': float(request.args.get('flower_probability', 0.2)),
        'max_length': int(request.args.get('max_length', 10)),
        'season': request.args.get('season', 'summer'),
        'start_pos': (start_x, start_y)
    }
    
    pattern = VinePattern(config)
    pattern_id = str(uuid.uuid4())
    active_vines[pattern_id] = pattern
    
    initial_state = pattern.init_growth((start_x, start_y))
    return jsonify({'id': pattern_id, 'pattern': _transform_pattern_data(initial_state)})

@vine_pattern_bp.route('/grow/<pattern_id>')
def grow_vine(pattern_id):
    if pattern_id not in active_vines:
        return jsonify({'error': 'Pattern not found'}), 404
        
    pattern = active_vines[pattern_id]
    current_state = pattern.grow_step()
    
    if current_state['completed']:
        del active_vines[pattern_id]
        
    return jsonify({
        'completed': current_state['completed'],
        'pattern': _transform_pattern_data(current_state)
    })

def _get_season_from_request() -> str:
    """Get season from request or current date"""
    season = request.args.get('season', None)
    if not season:
        month = datetime.now().month
        if month in [3, 4, 5]:
            season = 'spring'
        elif month in [6, 7, 8]:
            season = 'summer'
        elif month in [9, 10, 11]:
            season = 'autumn'
        else:
            season = 'winter'
    return season

def _transform_pattern_data(pattern_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform pattern data into format expected by frontend"""
    
    def _rgb_to_hex(rgb: tuple) -> str:
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
    
    transformed = {
        'segments': [],
        'leaves': [],
        'flowers': []
    }
    
    # Transform segments
    for segment in pattern_data['segments']:
        transformed['segments'].append({
            'start': segment['start'],
            'end': segment['end'],
            'thickness': segment['thickness'],
            'color': _rgb_to_hex(segment['color'])
        })
    
    # Transform leaves
    for leaf in pattern_data['leaves']:
        transformed['leaves'].append({
            'pos': leaf['pos'],
            'angle': leaf['angle'],
            'size': leaf['size'],
            'type': leaf['type'].value if hasattr(leaf['type'], 'value') else leaf['type'],
            'color': _rgb_to_hex(leaf['color']),
            'shape': leaf.get('shape', [])
        })
    
    # Transform flowers
    for flower in pattern_data['flowers']:
        transformed['flowers'].append({
            'pos': flower['pos'],
            'size': flower['size'],
            'type': flower['type'].value if hasattr(flower['type'], 'value') else flower['type'],
            'color': _rgb_to_hex(pattern_data['colors'].flower_color),
            'rotation': flower.get('rotation', 0)
        })
    
    return transformed

def _parse_obstacles(obstacles_str: str) -> List[Tuple[Tuple[float, float], float]]:
    """Parse obstacles from request string format"""
    try:
        obstacles_data = json.loads(obstacles_str)
        return [((float(o['x']), float(o['y'])), float(o['radius'])) for o in obstacles_data]
    except (json.JSONDecodeError, KeyError, ValueError):
        return []