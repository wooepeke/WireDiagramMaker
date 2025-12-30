"""
Configuration loader for the Wire Diagram Maker application
"""

import json
import os
from pathlib import Path


class Config:
    """Load and manage application configuration"""
    
    _instance = None
    _config_data = None
    
    def __new__(cls):
        """Singleton pattern - only one config instance"""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load configuration from config.json"""
        config_path = Path(__file__).parent / "config.json"
        
        try:
            with open(config_path, 'r') as f:
                self._config_data = json.load(f)
        except FileNotFoundError:
            print(f"Config file not found at {config_path}, using defaults")
            self._config_data = self._get_defaults()
        except json.JSONDecodeError as e:
            print(f"Error parsing config file: {e}, using defaults")
            self._config_data = self._get_defaults()
    
    def reload_config(self):
        """Reload configuration from disk"""
        self._load_config()
    
    def _get_defaults(self):
        """Return default configuration if file is not found"""
        return {
            "grid": {
                "size": 10,
                "color": [200, 200, 200],
                "enabled_by_default": True
            },
            "node": {
                "size": 30,
                "default_color": [100, 150, 200],
                "selected_color": [255, 0, 0],
                "highlighted_color": [150, 200, 255],
                "border_color": [50, 100, 150],
                "border_width": 2,
                "selected_border_width": 3,
                "border_color_selected": [200, 0, 0],
                "classes": [
                    {"name": "5V", "color": [255, 0, 0]},
                    {"name": "GRD", "color": [0, 0, 0]},
                    {"name": "SDA", "color": [0, 0, 255]},
                    {"name": "SCL", "color": [0, 255, 0]},
                    {"name": "PWM", "color": [255, 255, 0]}
                ]
            },
            "connection": {
                "default_color": [100, 100, 100],
                "width": 2,
                "hitbox_distance": 10
            },
            "zoom": {
                "min": 0.1,
                "max": 5.0,
                "increment": 1.2
            },
            "features": {
                "snap_to_grid_enabled": False,
                "antialiasing_enabled": True
            }
        }
    
    def get(self, key, default=None):
        """Get a configuration value by dot-notation key (e.g., 'grid.size')"""
        keys = key.split('.')
        value = self._config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_grid_size(self):
        """Get grid size"""
        return self.get('grid.size', 10)
    
    def get_grid_color(self):
        """Get grid color as RGB tuple"""
        color = self.get('grid.color', [200, 200, 200])
        return tuple(color)
    
    def get_grid_enabled_by_default(self):
        """Get whether grid is enabled by default"""
        return self.get('grid.enabled_by_default', True)
    
    def get_node_size(self):
        """Get node size"""
        return self.get('node.size', 30)
    
    def get_node_default_color(self):
        """Get default node color as RGB tuple"""
        color = self.get('node.default_color', [100, 150, 200])
        return tuple(color)
    
    def get_node_selected_color(self):
        """Get selected node color as RGB tuple"""
        color = self.get('node.selected_color', [255, 0, 0])
        return tuple(color)
    
    def get_node_highlighted_color(self):
        """Get highlighted node color as RGB tuple"""
        color = self.get('node.highlighted_color', [150, 200, 255])
        return tuple(color)
    
    def get_node_border_color(self):
        """Get node border color as RGB tuple"""
        color = self.get('node.border_color', [50, 100, 150])
        return tuple(color)
    
    def get_node_border_width(self):
        """Get node border width"""
        return self.get('node.border_width', 2)
    
    def get_node_selected_border_width(self):
        """Get selected node border width"""
        return self.get('node.selected_border_width', 3)
    
    def get_node_border_color_selected(self):
        """Get selected node border color as RGB tuple"""
        color = self.get('node.border_color_selected', [200, 0, 0])
        return tuple(color)
    
    def get_node_classes(self):
        """Get list of available node classes"""
        classes = self.get('node.classes', [])
        return classes if classes else [
            {"name": "Generic", "color": [150, 150, 150]}
        ]
    
    def get_node_class_names(self):
        """Get list of node class names"""
        return [cls["name"] for cls in self.get_node_classes()]
    
    def get_node_class_color(self, class_name):
        """Get color for a specific node class"""
        classes = self.get_node_classes()
        for cls in classes:
            if cls["name"] == class_name:
                return tuple(cls["color"])
        return tuple(self.get('node.default_color', [100, 150, 200]))
    
    def get_connection_default_color(self):
        """Get default connection color as RGB tuple"""
        color = self.get('connection.default_color', [100, 100, 100])
        return tuple(color)
    
    def get_connection_width(self):
        """Get connection line width"""
        return self.get('connection.width', 2)
    
    def get_connection_hitbox_distance(self):
        """Get connection hitbox distance"""
        return self.get('connection.hitbox_distance', 10)
    
    def get_zoom_min(self):
        """Get minimum zoom level"""
        return self.get('zoom.min', 0.1)
    
    def get_zoom_max(self):
        """Get maximum zoom level"""
        return self.get('zoom.max', 5.0)
    
    def get_zoom_increment(self):
        """Get zoom increment multiplier"""
        return self.get('zoom.increment', 1.2)
    
    def is_snap_to_grid_enabled_by_default(self):
        """Get whether snap-to-grid is enabled by default"""
        return self.get('features.snap_to_grid_enabled', False)
    
    def is_antialiasing_enabled(self):
        """Get whether antialiasing is enabled"""
        return self.get('features.antialiasing_enabled', True)


# Convenient function to get config instance
def get_config():
    """Get the global config instance"""
    return Config()
