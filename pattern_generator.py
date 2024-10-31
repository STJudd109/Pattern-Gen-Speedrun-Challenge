import numpy as np
import random

def generate_pattern(size=20, amplitude=1.0, frequency=0.1, shuffle=False):
    """
    Generate a 3D sine wave pattern.
    Returns data in a format suitable for Three.js
    """
    if shuffle:
        # Randomize parameters when shuffle is requested
        amplitude = random.uniform(0.5, 2.0)
        frequency = random.uniform(0.05, 0.2)
        size = random.randint(15, 30)
    
    vertices = []
    x = np.linspace(-size/2, size/2, size)
    y = np.linspace(-size/2, size/2, size)
    
    for i in x:
        for j in y:
            # Create a sine wave pattern
            z = amplitude * np.sin(frequency * i) * np.cos(frequency * j)
            vertices.extend([float(i), float(j), float(z)])
    
    return {
        'vertices': vertices,
        'size': size
    }
