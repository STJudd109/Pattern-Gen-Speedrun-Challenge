from typing import Dict, Any, Optional

class Pattern:
    """Base class for all pattern generators."""
    
    pattern_type = "base"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = {}
        if config:
            self.config.update(config)
    
    def generate(self) -> Dict[str, Any]:
        """Generate the pattern. Must be implemented by subclasses."""
        raise NotImplementedError
    
    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """Return the configuration schema. Must be implemented by subclasses."""
        raise NotImplementedError 