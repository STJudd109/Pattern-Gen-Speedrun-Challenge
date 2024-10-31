from flask import Blueprint, render_template, jsonify, request
from pattern_generator import generate_pattern

basic_pattern_bp = Blueprint('basic_pattern', __name__)

@basic_pattern_bp.route('/')
def basic_pattern_index():
    return render_template('basic_pattern/index.html')

@basic_pattern_bp.route('/generate')
def get_pattern():
    shuffle = request.args.get('shuffle', False)
    pattern_data = generate_pattern(shuffle=shuffle)
    return jsonify(pattern_data) 