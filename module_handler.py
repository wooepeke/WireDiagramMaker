"""
Module handler for saving and loading wire diagram modules
"""

import json
import os
from pathlib import Path
from diagram_elements import Module
import uuid


class ModuleHandler:
    """Handles saving and loading of modules"""

    def __init__(self):
        """Initialize the module handler"""
        self.modules_dir = Path("Modules")
        self.modules_dir.mkdir(exist_ok=True)

    def save_module(self, module):
        """Save a module to a JSON file"""
        try:
            file_path = self.modules_dir / f"{module.module_id}.json"
            
            module_dict = module.to_dict()
            
            with open(file_path, "w") as f:
                json.dump(module_dict, f, indent=4)
            
            return True
        except Exception as e:
            print(f"Error saving module: {e}")
            return False

    def load_module(self, module_id):
        """Load a module from a JSON file"""
        try:
            file_path = self.modules_dir / f"{module_id}.json"
            
            if not file_path.exists():
                print(f"Module file not found: {file_path}")
                return None
            
            with open(file_path, "r") as f:
                module_dict = json.load(f)
            
            module = Module.from_dict(module_dict)
            return module
        except Exception as e:
            print(f"Error loading module: {e}")
            return None

    def get_available_modules(self):
        """Get list of available module files with their metadata"""
        modules_list = []
        try:
            for file_path in self.modules_dir.glob("*.json"):
                try:
                    with open(file_path, "r") as f:
                        module_dict = json.load(f)
                    modules_list.append({
                        "id": module_dict.get("id"),
                        "name": module_dict.get("name", file_path.stem),
                        "file_path": str(file_path)
                    })
                except Exception as e:
                    print(f"Error reading module file {file_path}: {e}")
        except Exception as e:
            print(f"Error getting available modules: {e}")
        
        return modules_list

    def delete_module(self, module_id):
        """Delete a module file"""
        try:
            file_path = self.modules_dir / f"{module_id}.json"
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting module: {e}")
            return False

    def generate_module_id(self):
        """Generate a unique module ID"""
        return str(uuid.uuid4())[:8]
