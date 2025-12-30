"""
File handler for saving and loading wire diagram files in JSON format
"""

import json
import os
from pathlib import Path
from PyQt5.QtWidgets import QFileDialog, QMessageBox


class DiagramFileHandler:
    """Handles saving and loading diagram files"""

    DEFAULT_DIR = "Files"

    def __init__(self, parent=None):
        """Initialize the file handler"""
        self.parent = parent
        self.current_file = None
        self.ensure_files_directory()

    def ensure_files_directory(self):
        """Ensure the Files directory exists"""
        if not os.path.exists(self.DEFAULT_DIR):
            os.makedirs(self.DEFAULT_DIR)

    def open_file(self):
        """Open a file dialog to select a diagram file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent,
            "Open Diagram",
            self.DEFAULT_DIR,
            "JSON Files (*.json);;All Files (*)",
        )
        return file_path if file_path else None

    def save_file_dialog(self):
        """Open a file dialog to save a diagram file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent,
            "Save Diagram",
            self.DEFAULT_DIR,
            "JSON Files (*.json)",
        )
        return file_path if file_path else None

    def save_diagram(self, file_path, diagram_data):
        """Save diagram data to a JSON file"""
        try:
            # Ensure the file has .json extension
            if not file_path.endswith('.json'):
                file_path += '.json'

            with open(file_path, 'w') as f:
                json.dump(diagram_data, f, indent=2)

            self.current_file = file_path
            return True, f"Diagram saved to {os.path.basename(file_path)}"
        except Exception as e:
            return False, f"Error saving file: {str(e)}"

    def load_diagram(self, file_path):
        """Load diagram data from a JSON file"""
        try:
            if not os.path.exists(file_path):
                return False, "File not found"

            with open(file_path, 'r') as f:
                data = json.load(f)

            self.current_file = file_path
            return True, data
        except json.JSONDecodeError:
            return False, "Invalid JSON file format"
        except Exception as e:
            return False, f"Error loading file: {str(e)}"

    def get_current_filename(self):
        """Get the name of the current file"""
        if self.current_file:
            return os.path.basename(self.current_file)
        return "Untitled"
