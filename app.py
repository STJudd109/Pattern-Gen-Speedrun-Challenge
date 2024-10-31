from flask import Flask, render_template, jsonify
from blueprints.basic_pattern import basic_pattern_bp
from blueprints.circular_pattern import circular_pattern_bp
from blueprints.vine_pattern import vine_pattern_bp
from blueprints.tessellation_pattern import tessellation_pattern_bp
from blueprints.geometric_pattern import geometric_pattern_bp
from blueprints.three_d_pattern import three_d_pattern_bp
from blueprints.physics_pattern import physics_pattern_bp
# ... future imports for other pattern blueprints ...

app = Flask(__name__)

# Register blueprints
app.register_blueprint(basic_pattern_bp, url_prefix='/basic')
app.register_blueprint(circular_pattern_bp, url_prefix='/circular')
app.register_blueprint(vine_pattern_bp, url_prefix='/vine')
app.register_blueprint(tessellation_pattern_bp, url_prefix='/tessellation')
app.register_blueprint(geometric_pattern_bp, url_prefix='/geometric')
app.register_blueprint(three_d_pattern_bp, url_prefix='/three_d')
app.register_blueprint(physics_pattern_bp, url_prefix='/physics')
# ... register other pattern blueprints as needed ...

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=True)
