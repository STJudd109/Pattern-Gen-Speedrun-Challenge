import random

def normalize_angle(angle):
    """Normalize angle to be between 0 and 360 degrees."""
    return angle % 360

def random_float(min_val, max_val):
    """Generate a random float between min_val and max_val."""
    return min_val + (max_val - min_val) * random.random()