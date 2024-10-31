from flask import Blueprint, render_template

physics_pattern_bp = Blueprint('physics_pattern', __name__)

@physics_pattern_bp.route('/')
def physics_pattern_index():
    return render_template('physics_pattern/index.html') 