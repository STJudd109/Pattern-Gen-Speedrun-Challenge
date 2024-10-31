from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import random
import math
from blueprints.core.pattern import Pattern
from blueprints.utils.vector import Vector2

class Season(Enum):
    SPRING = auto()
    SUMMER = auto()
    AUTUMN = auto()
    WINTER = auto()
    
    @classmethod
    def get_current(cls):
        month = datetime.now().month
        if month in [3, 4, 5]:
            return cls.SPRING
        elif month in [6, 7, 8]:
            return cls.SUMMER
        elif month in [9, 10, 11]:
            return cls.AUTUMN
        else:
            return cls.WINTER

class GrowthPattern(Enum):
    CLIMBING = "climbing"
    HANGING = "hanging"
    SPREADING = "spreading"
    SPIRAL = "spiral"

class LeafType(Enum):
    SIMPLE = "simple"
    COMPOUND = "compound"
    HEART = "heart"
    MAPLE = "maple"

class FlowerType(Enum):
    BUD = "bud"
    BLOOM = "bloom"
    CLUSTER = "cluster"

@dataclass
class ColorScheme:
    vine_color: Tuple[int, int, int]
    leaf_color: Tuple[int, int, int]
    flower_color: Tuple[int, int, int]
    
    @classmethod
    def create_random_natural(cls):
        vine_green = (random.randint(40, 80), random.randint(90, 130), random.randint(40, 80))
        leaf_green = (random.randint(50, 100), random.randint(120, 180), random.randint(50, 100))
        flower_colors = [
            (random.randint(200, 255), random.randint(100, 150), random.randint(150, 200)),  # Pink
            (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255)),  # White
            (random.randint(180, 220), random.randint(180, 220), random.randint(0, 50)),     # Yellow
        ]
        return cls(vine_green, leaf_green, random.choice(flower_colors))

class VinePattern(Pattern):
    """Blueprint for generating organic vine growth patterns."""
    
    pattern_type = "vine"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.config = {
            'max_length': 10,
            'growth_speed': 1.0,
            'growth_pattern': GrowthPattern.CLIMBING,
            'start_pos': Vector2(0, 0),
        }
        if config:
            self.config.update(config)
        
        self.segments = []
        self.leaves = []
        self.flowers = []
        self.colors = ColorScheme.create_random_natural()
        self.growth_points = []  # Stack of points to grow from
        self.completed = False

    def init_growth(self, start_pos: Tuple[float, float]):
        """Initialize the growth point with appropriate starting angle"""
        growth_pattern = self.config['growth_pattern']
        
        # Set initial angle based on growth pattern
        if isinstance(growth_pattern, str):
            growth_pattern = GrowthPattern(growth_pattern)
        
        match growth_pattern:
            case GrowthPattern.CLIMBING:
                initial_angle = 270  # Start growing upward
            case GrowthPattern.HANGING:
                initial_angle = 90   # Start growing downward
            case GrowthPattern.SPREADING:
                initial_angle = 0    # Start growing to the right
            case GrowthPattern.SPIRAL:
                initial_angle = 0    # Start horizontally for spiral
            case _:
                initial_angle = 270  # Default to upward growth
        
        self.growth_points = [(start_pos, initial_angle, 0)]  # (pos, angle, depth)
        return self.get_current_state()

    def grow_step(self):
        """Perform one growth step"""
        if not self.growth_points or self.completed:
            self.completed = True
            return self.get_current_state()

        pos, angle, depth = self.growth_points.pop(0)
        
        if depth >= self.config['max_length']:
            return self.get_current_state()

        # Generate new segment
        length = random.uniform(10, 20)
        next_angle = self._adjust_growth_angle(angle, depth)
        
        end_x = pos[0] + length * math.cos(math.radians(next_angle))
        end_y = pos[1] + length * math.sin(math.radians(next_angle))
        end_pos = (end_x, end_y)

        # Add segment
        self.segments.append({
            'start': pos,
            'end': end_pos,
            'thickness': max(1, (self.config['max_length'] - depth) / 2),
            'color': self.colors.vine_color
        })

        # Randomly add leaf
        if random.random() < 0.3:
            self._add_leaf(end_pos, next_angle)

        # Randomly add flower
        if random.random() < 0.2:
            self._add_flower(end_pos)

        # Add branching points
        if random.random() < 0.3 and depth < self.config['max_length'] - 1:
            branch_angle = next_angle + random.uniform(-45, 45)
            self.growth_points.append((end_pos, branch_angle, depth + 1))

        # Continue main growth
        self.growth_points.append((end_pos, next_angle, depth + 1))
        
        return self.get_current_state()

    def get_current_state(self):
        """Get the current state of the pattern"""
        return {
            'completed': self.completed,
            'segments': self.segments,
            'leaves': self.leaves,
            'flowers': self.flowers,
            'colors': self.colors
        }

    def check_collision(self, pos: Tuple[float, float]) -> bool:
        """Check if a position collides with any obstacle"""
        for obstacle_pos, radius in self.config['obstacles']:
            dx = pos[0] - obstacle_pos[0]
            dy = pos[1] - obstacle_pos[1]
            distance = math.sqrt(dx*dx + dy*dy)
            if distance < radius + self.config['obstacle_margin']:
                return True
        return False

    def _generate_segment(self, start_pos: Tuple[float, float], angle: float, depth: int, length: Optional[float] = None) -> None:
        """Generate a single vine segment with branches, leaves, and flowers."""
        if depth >= self.config['max_length'] or self.check_collision(start_pos):
            return
            
        if length is None:
            length = random.uniform(10, 20)
            
        # Calculate end position with obstacle avoidance
        end_x = start_pos[0] + length * math.cos(math.radians(angle))
        end_y = start_pos[1] + length * math.sin(math.radians(angle))
        end_pos = (end_x, end_y)
        
        # If endpoint collides with obstacle, try adjusting angle
        if self.check_collision(end_pos):
            for _ in range(8):  # Try 8 different angles
                test_angle = angle + random.uniform(-45, 45)
                test_x = start_pos[0] + length * math.cos(math.radians(test_angle))
                test_y = start_pos[1] + length * math.sin(math.radians(test_angle))
                if not self.check_collision((test_x, test_y)):
                    end_pos = (test_x, test_y)
                    angle = test_angle  # Update angle if valid position found
                    break
            else:  # If no valid angle found, terminate branch
                return

        # Add main vine segment
        self.segments.append({
            'start': start_pos,
            'end': end_pos,
            'thickness': max(1, (self.config['max_length'] - depth) / 2),
            'color': self.colors.vine_color
        })

        # Add leaf with random type
        if random.random() < self.config['leaf_probability']:
            leaf_type = random.choice(list(LeafType))
            leaf_angle = angle + random.choice([-90, 90])
            leaf_size = random.uniform(5, 15)
            self.leaves.append({
                'pos': end_pos,
                'angle': leaf_angle,
                'size': leaf_size,
                'type': leaf_type,
                'shape': self._generate_leaf_shape(leaf_type, leaf_size),
                'color': self.colors.leaf_color
            })

        # Add flower
        if random.random() < self.config['flower_probability']:
            flower_type = random.choice(list(FlowerType))
            self._generate_flower(end_pos, flower_type)

        # Branch generation with varying patterns
        if random.random() < self.config['branch_probability'] and depth < self.config['max_length'] - 1:
            num_branches = random.randint(1, 2)
            for _ in range(num_branches):
                branch_angle = angle + random.uniform(-45, 45)
                self._generate_segment(end_pos, branch_angle, depth + 1, length * 0.8)
        
        # Continue main vine with adjusted angle based on growth pattern
        next_angle = self._adjust_growth_angle(angle, depth)
        next_length = length * random.uniform(0.8, 1.0)
        self._generate_segment(end_pos, next_angle, depth + 1, next_length)

    def _generate_leaf_shape(self, leaf_type: LeafType, size: float) -> List[Tuple[float, float]]:
        """Generate points for different leaf shapes."""
        points = []
        match leaf_type:
            case LeafType.SIMPLE:
                points = [
                    (0, 0),
                    (size, -size/2),
                    (size*2, 0),
                    (size, size/2)
                ]
            case LeafType.HEART:
                num_points = 12
                for i in range(num_points):
                    angle = (i * 2 * math.pi / num_points)
                    r = size * (1 + math.sin(angle))
                    x = r * math.cos(angle)
                    y = r * math.sin(angle)
                    points.append((x, y))
            case LeafType.MAPLE:
                # Generate maple leaf points
                angles = [0, 72, 144, 216, 288]
                for angle in angles:
                    rad = math.radians(angle)
                    points.extend([
                        (size * math.cos(rad), size * math.sin(rad)),
                        (size * 0.5 * math.cos(rad + math.radians(36)),
                         size * 0.5 * math.sin(rad + math.radians(36)))
                    ])
            case LeafType.COMPOUND:
                # Generate compound leaf with multiple leaflets
                num_leaflets = 5
                for i in range(num_leaflets):
                    offset = (i - num_leaflets//2) * size/3
                    points.extend([
                        (offset, 0),
                        (offset + size/2, -size/4),
                        (offset + size, 0),
                        (offset + size/2, size/4)
                    ])
        return points

    def _generate_flower(self, pos: Tuple[float, float], flower_type: FlowerType) -> None:
        """Generate a flower at the specified position."""
        size = random.uniform(3, 8)
        self.flowers.append({
            'pos': pos,
            'size': size,
            'type': flower_type,
            'color': self.colors.flower_color,
            'rotation': random.uniform(0, 360)
        })

    def _adjust_growth_angle(self, current_angle: float, depth: int) -> float:
        """Adjust the growth angle based on the growth pattern."""
        base_variation = random.uniform(-15, 15)
        growth_pattern = self.config['growth_pattern']
        
        if isinstance(growth_pattern, str):
            growth_pattern = GrowthPattern(growth_pattern)
        
        match growth_pattern:
            case GrowthPattern.CLIMBING:
                # Tend upward (270 degrees is up in SVG)
                target_angle = 270
                return current_angle + (target_angle - current_angle) * 0.1 + base_variation * 0.5
                
            case GrowthPattern.HANGING:
                # Tend downward (90 degrees is down in SVG)
                target_angle = 90
                return current_angle + (target_angle - current_angle) * 0.1 + base_variation * 0.5
                
            case GrowthPattern.SPREADING:
                # Alternate between left and right growth
                spread_angle = (depth % 2) * 180 - 90  # Alternates between -90 and 90
                return current_angle + (spread_angle - current_angle) * 0.1 + base_variation
                
            case GrowthPattern.SPIRAL:
                # Create continuous rotation
                return current_angle + 15 + base_variation * 0.3
                
            case _:
                return current_angle + base_variation

    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """Return the configuration schema for this pattern."""
        return {
            "type": "object",
            "properties": {
                "max_length": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 30,
                    "default": 10
                },
                "branch_probability": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "default": 0.3
                },
                "leaf_probability": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "default": 0.4
                },
                "flower_probability": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "default": 0.2
                },
                "growth_pattern": {
                    "type": "string",
                    "enum": ["climbing", "hanging", "spreading", "spiral"],
                    "default": "climbing"
                },
                "season": {
                    "type": "string",
                    "enum": ["spring", "summer", "autumn", "winter"],
                    "default": "summer"
                }
            },
            "required": ["max_length"]
        } 

    def _add_leaf(self, pos: Tuple[float, float], angle: float) -> None:
        """Add a leaf at the specified position"""
        leaf_type = random.choice(list(LeafType))
        leaf_angle = angle + random.choice([-90, 90])
        leaf_size = random.uniform(5, 15)
        
        self.leaves.append({
            'pos': pos,
            'angle': leaf_angle,
            'size': leaf_size,
            'type': leaf_type,
            'shape': self._generate_leaf_shape(leaf_type, leaf_size),
            'color': self.colors.leaf_color
        })

    def _add_flower(self, pos: Tuple[float, float]) -> None:
        """Add a flower at the specified position"""
        flower_type = random.choice(list(FlowerType))
        flower_size = random.uniform(3, 8)
        
        self.flowers.append({
            'pos': pos,
            'size': flower_size,
            'type': flower_type,
            'color': self.colors.flower_color,
            'rotation': random.uniform(0, 360)
        })