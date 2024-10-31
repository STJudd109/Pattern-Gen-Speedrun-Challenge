# Pattern Generator Collection

A versatile web application that offers multiple pattern generation tools, each with unique features and customization options.

This was built as a learning exercise to explore the capabilities of rapid project development using Python and Flask, while also leveraging the capabilities of modern web technologies.

I gave myself a list of requirements for the project:
- The project must be built using Python and Flask
- The project must be a web application
- The project must be a collection of pattern generators
- The project must be built in 2 hours
- The project must utilize Cursor AI for co-development

Lessons learned:
- Cursor AI is a powerful tool for co-development, but it is not a replacement for actual coding skills. Lots of debugging and re-directing the AI to do what I want.
- Don't box your ideas in, you can explore and expand your ideas much more with a blank canvas, especially with AI to help you establish the basics.
- Allowing your brain to wander and explore ideas is key to creativity.
- It's important to have a plan, but it's also important to be willing to deviate from the plan and explore unexpected ideas.

## Features

### 1. Basic Pattern Generator
- Interactive point-based pattern creation
- Customizable connection distances and colors
- Real-time visualization
- User-controlled point placement

### 2. Geometric Pattern Generator
- Symmetrical pattern generation
- Multiple layer support
- Color palette options:
  - Monochromatic
  - Complementary
  - Triadic
- Animation controls
- SVG export functionality

### 3. Circular Pattern Generator
- Radial pattern generation
- Adjustable parameters:
  - Number of circles
  - Point density
  - Symmetry options
- Animated rotation
- SVG download support

### 4. 3D Pattern Generator
- Three.js-based 3D visualization
- Multiple pattern types
- Customizable complexity and rotation
- Interactive camera controls

### 5. Physics Pattern Generator
- Real-time physics simulation using Cannon.js
- Multiple object types:
  - Spheres
  - Cubes
  - Cylinders
- Gravity and collision detection
- Interactive object placement

### 6. Tessellation Pattern Generator
- Regular geometric tessellations
- Multiple tiling patterns
- Color scheme customization
- SVG export capability

## Technology Stack

- Frontend:
  - HTML5
  - CSS3
  - JavaScript
  - Three.js (3D rendering)
  - Cannon.js (Physics engine)
  - D3.js (SVG manipulation)

- Backend:
  - Flask (Python web framework)
  - NumPy (Numerical computations)
  - Gunicorn (WSGI HTTP Server)
  - Nginx (Reverse Proxy)

## Getting Started

### Using Docker (Recommended)

1. Clone the repository
2. Generate SSL certificates (for development):
```bash
chmod +x scripts/generate-certs.sh
./scripts/generate-certs.sh
```
3. Build and run with Docker Compose:
```bash
docker-compose up --build
```
4. Access the application:
   - HTTPS: https://localhost
   - HTTP will automatically redirect to HTTPS

### Manual Setup (Development Only)

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the application:
```bash
python app.py
```
4. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Select a pattern generator from the main menu
2. Adjust the available parameters using the control panel
3. Generate new patterns using the "Generate" button
4. Export or save your creations using the provided download options

## Security Notes

- The Docker setup includes:
  - HTTPS with TLS 1.2/1.3
  - Security headers
  - Non-root user execution
  - Health checks
  - Container isolation

- For production deployment:
  - Replace self-signed certificates with proper ones from a trusted CA
  - Configure proper logging and monitoring
  - Consider adding a WAF (Web Application Firewall)
  - Implement rate limiting

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Three.js for 3D rendering capabilities
- Cannon.js for physics simulation
- D3.js for SVG manipulation