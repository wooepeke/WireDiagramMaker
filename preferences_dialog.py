"""
Preferences/Settings dialog for configuring application settings
"""

import json
from pathlib import Path
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QCheckBox,
    QPushButton, QTabWidget, QWidget, QGroupBox, QColorDialog, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtGui import QColor, QPixmap, QIcon
from PyQt5.QtCore import Qt, pyqtSignal
from config_loader import get_config


class PreferencesDialog(QDialog):
    """Dialog for editing application preferences"""
    
    # Signal emitted when preferences are saved
    preferences_saved = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setGeometry(100, 100, 600, 500)
        self.config = get_config()
        self.config_path = Path(__file__).parent / "config.json"
        
        # Load current config
        with open(self.config_path, 'r') as f:
            self.config_data = json.load(f)
        
        # Create UI
        self.create_ui()

    def create_ui(self):
        """Create the preferences dialog UI"""
        layout = QVBoxLayout()
        
        # Create tabs
        tabs = QTabWidget()
        
        # Grid tab
        tabs.addTab(self.create_grid_tab(), "Grid")
        
        # Node tab
        tabs.addTab(self.create_node_tab(), "Node")
        
        # Connection tab
        tabs.addTab(self.create_connection_tab(), "Connection")
        
        # Zoom tab
        tabs.addTab(self.create_zoom_tab(), "Zoom")
        
        # Features tab
        tabs.addTab(self.create_features_tab(), "Features")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_button)
        
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_preferences)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def create_grid_tab(self):
        """Create grid settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Grid size
        grid_size_layout = QHBoxLayout()
        grid_size_layout.addWidget(QLabel("Grid Size:"))
        self.grid_size_spinbox = QSpinBox()
        self.grid_size_spinbox.setMinimum(5)
        self.grid_size_spinbox.setMaximum(50)
        self.grid_size_spinbox.setValue(self.config_data['grid']['size'])
        grid_size_layout.addWidget(self.grid_size_spinbox)
        grid_size_layout.addStretch()
        layout.addLayout(grid_size_layout)
        
        # Grid enabled by default
        self.grid_enabled_checkbox = QCheckBox("Show Grid by Default")
        self.grid_enabled_checkbox.setChecked(self.config_data['grid']['enabled_by_default'])
        layout.addWidget(self.grid_enabled_checkbox)
        
        # Grid color
        grid_color_layout = QHBoxLayout()
        grid_color_layout.addWidget(QLabel("Grid Color:"))
        self.grid_color_button = QPushButton("Choose Color")
        self.grid_color = self.config_data['grid']['color']
        self.update_grid_color_button()
        self.grid_color_button.clicked.connect(self.choose_grid_color)
        grid_color_layout.addWidget(self.grid_color_button)
        grid_color_layout.addStretch()
        layout.addLayout(grid_color_layout)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_node_tab(self):
        """Create node settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Node size
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Node Size:"))
        self.node_size_spinbox = QSpinBox()
        self.node_size_spinbox.setMinimum(10)
        self.node_size_spinbox.setMaximum(100)
        self.node_size_spinbox.setValue(self.config_data['node']['size'])
        size_layout.addWidget(self.node_size_spinbox)
        size_layout.addStretch()
        layout.addLayout(size_layout)
        
        # Border width
        border_width_layout = QHBoxLayout()
        border_width_layout.addWidget(QLabel("Border Width:"))
        self.border_width_spinbox = QSpinBox()
        self.border_width_spinbox.setMinimum(1)
        self.border_width_spinbox.setMaximum(5)
        self.border_width_spinbox.setValue(self.config_data['node']['border_width'])
        border_width_layout.addWidget(self.border_width_spinbox)
        border_width_layout.addStretch()
        layout.addLayout(border_width_layout)
        
        # Selected border width
        selected_border_layout = QHBoxLayout()
        selected_border_layout.addWidget(QLabel("Selected Border Width:"))
        self.selected_border_width_spinbox = QSpinBox()
        self.selected_border_width_spinbox.setMinimum(1)
        self.selected_border_width_spinbox.setMaximum(5)
        self.selected_border_width_spinbox.setValue(self.config_data['node']['selected_border_width'])
        selected_border_layout.addWidget(self.selected_border_width_spinbox)
        selected_border_layout.addStretch()
        layout.addLayout(selected_border_layout)
        
        # Node classes section
        classes_group = QGroupBox("Node Classes")
        classes_layout = QVBoxLayout()
        
        self.classes_table = QTableWidget()
        self.classes_table.setColumnCount(2)
        self.classes_table.setHorizontalHeaderLabels(["Name", "Color"])
        self.classes_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.classes_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
        self.populate_classes_table()
        classes_layout.addWidget(self.classes_table)
        classes_group.setLayout(classes_layout)
        layout.addWidget(classes_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def populate_classes_table(self):
        """Populate the classes table with current node classes"""
        classes = self.config_data['node']['classes']
        self.classes_table.setRowCount(len(classes))
        
        for row, cls in enumerate(classes):
            # Name column
            name_item = QTableWidgetItem(cls['name'])
            self.classes_table.setItem(row, 0, name_item)
            
            # Color column with button
            color_button = QPushButton()
            color = cls['color']
            self.set_button_color(color_button, color)
            color_data = (color, row)  # Store color and row index
            color_button.clicked.connect(lambda checked, cb=color_button, r=row: self.choose_class_color(cb, r))
            self.classes_table.setCellWidget(row, 1, color_button)

    def choose_class_color(self, button, row):
        """Open color picker for a node class"""
        color = self.config_data['node']['classes'][row]['color']
        color_dialog = QColorDialog(QColor(*color), self)
        if color_dialog.exec_() == QColorDialog.Accepted:
            new_color = color_dialog.selectedColor()
            rgb = [new_color.red(), new_color.green(), new_color.blue()]
            self.config_data['node']['classes'][row]['color'] = rgb
            self.set_button_color(button, rgb)

    def create_connection_tab(self):
        """Create connection settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Connection width
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Connection Width:"))
        self.connection_width_spinbox = QSpinBox()
        self.connection_width_spinbox.setMinimum(1)
        self.connection_width_spinbox.setMaximum(10)
        self.connection_width_spinbox.setValue(self.config_data['connection']['width'])
        width_layout.addWidget(self.connection_width_spinbox)
        width_layout.addStretch()
        layout.addLayout(width_layout)
        
        # Hitbox distance
        hitbox_layout = QHBoxLayout()
        hitbox_layout.addWidget(QLabel("Hitbox Distance:"))
        self.hitbox_spinbox = QSpinBox()
        self.hitbox_spinbox.setMinimum(1)
        self.hitbox_spinbox.setMaximum(50)
        self.hitbox_spinbox.setValue(self.config_data['connection']['hitbox_distance'])
        hitbox_layout.addWidget(self.hitbox_spinbox)
        hitbox_layout.addStretch()
        layout.addLayout(hitbox_layout)
        
        # Default color
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Default Color:"))
        self.connection_color_button = QPushButton("Choose Color")
        self.connection_color = self.config_data['connection']['default_color']
        self.update_connection_color_button()
        self.connection_color_button.clicked.connect(self.choose_connection_color)
        color_layout.addWidget(self.connection_color_button)
        color_layout.addStretch()
        layout.addLayout(color_layout)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_zoom_tab(self):
        """Create zoom settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Min zoom
        min_zoom_layout = QHBoxLayout()
        min_zoom_layout.addWidget(QLabel("Minimum Zoom:"))
        self.min_zoom_spinbox = QSpinBox()
        self.min_zoom_spinbox.setMinimum(1)
        self.min_zoom_spinbox.setMaximum(100)
        self.min_zoom_spinbox.setSingleStep(1)
        self.min_zoom_spinbox.setValue(int(self.config_data['zoom']['min'] * 100))
        self.min_zoom_spinbox.setSuffix("%")
        min_zoom_layout.addWidget(self.min_zoom_spinbox)
        min_zoom_layout.addStretch()
        layout.addLayout(min_zoom_layout)
        
        # Max zoom
        max_zoom_layout = QHBoxLayout()
        max_zoom_layout.addWidget(QLabel("Maximum Zoom:"))
        self.max_zoom_spinbox = QSpinBox()
        self.max_zoom_spinbox.setMinimum(100)
        self.max_zoom_spinbox.setMaximum(1000)
        self.max_zoom_spinbox.setSingleStep(10)
        self.max_zoom_spinbox.setValue(int(self.config_data['zoom']['max'] * 100))
        self.max_zoom_spinbox.setSuffix("%")
        max_zoom_layout.addWidget(self.max_zoom_spinbox)
        max_zoom_layout.addStretch()
        layout.addLayout(max_zoom_layout)
        
        # Zoom increment
        increment_layout = QHBoxLayout()
        increment_layout.addWidget(QLabel("Zoom Increment:"))
        self.zoom_increment_spinbox = QSpinBox()
        self.zoom_increment_spinbox.setMinimum(100)
        self.zoom_increment_spinbox.setMaximum(300)
        self.zoom_increment_spinbox.setSingleStep(10)
        self.zoom_increment_spinbox.setValue(int(self.config_data['zoom']['increment'] * 100))
        self.zoom_increment_spinbox.setSuffix("%")
        increment_layout.addWidget(self.zoom_increment_spinbox)
        increment_layout.addStretch()
        layout.addLayout(increment_layout)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_features_tab(self):
        """Create features settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Snap to grid
        self.snap_to_grid_checkbox = QCheckBox("Enable Snap to Grid by Default")
        self.snap_to_grid_checkbox.setChecked(self.config_data['features']['snap_to_grid_enabled'])
        layout.addWidget(self.snap_to_grid_checkbox)
        
        # Antialiasing
        self.antialiasing_checkbox = QCheckBox("Enable Antialiasing")
        self.antialiasing_checkbox.setChecked(self.config_data['features']['antialiasing_enabled'])
        layout.addWidget(self.antialiasing_checkbox)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def choose_grid_color(self):
        """Open color picker for grid color"""
        color_dialog = QColorDialog(QColor(*self.grid_color), self)
        if color_dialog.exec_() == QColorDialog.Accepted:
            new_color = color_dialog.selectedColor()
            self.grid_color = [new_color.red(), new_color.green(), new_color.blue()]
            self.update_grid_color_button()

    def update_grid_color_button(self):
        """Update grid color button appearance"""
        self.set_button_color(self.grid_color_button, self.grid_color)

    def choose_connection_color(self):
        """Open color picker for connection color"""
        color_dialog = QColorDialog(QColor(*self.connection_color), self)
        if color_dialog.exec_() == QColorDialog.Accepted:
            new_color = color_dialog.selectedColor()
            self.connection_color = [new_color.red(), new_color.green(), new_color.blue()]
            self.update_connection_color_button()

    def update_connection_color_button(self):
        """Update connection color button appearance"""
        self.set_button_color(self.connection_color_button, self.connection_color)

    def set_button_color(self, button, rgb):
        """Set button background to show a color"""
        color = QColor(*rgb)
        pixmap = QPixmap(40, 20)
        pixmap.fill(color)
        button.setIcon(QIcon(pixmap))
        button.setIconSize(pixmap.size())

    def save_preferences(self):
        """Save preferences to config.json"""
        # Grid settings
        self.config_data['grid']['size'] = self.grid_size_spinbox.value()
        self.config_data['grid']['enabled_by_default'] = self.grid_enabled_checkbox.isChecked()
        self.config_data['grid']['color'] = self.grid_color
        
        # Node settings
        self.config_data['node']['size'] = self.node_size_spinbox.value()
        self.config_data['node']['border_width'] = self.border_width_spinbox.value()
        self.config_data['node']['selected_border_width'] = self.selected_border_width_spinbox.value()
        
        # Connection settings
        self.config_data['connection']['default_color'] = self.connection_color
        self.config_data['connection']['width'] = self.connection_width_spinbox.value()
        self.config_data['connection']['hitbox_distance'] = self.hitbox_spinbox.value()
        
        # Zoom settings
        self.config_data['zoom']['min'] = self.min_zoom_spinbox.value() / 100.0
        self.config_data['zoom']['max'] = self.max_zoom_spinbox.value() / 100.0
        self.config_data['zoom']['increment'] = self.zoom_increment_spinbox.value() / 100.0
        
        # Features settings
        self.config_data['features']['snap_to_grid_enabled'] = self.snap_to_grid_checkbox.isChecked()
        self.config_data['features']['antialiasing_enabled'] = self.antialiasing_checkbox.isChecked()
        
        # Write to file
        with open(self.config_path, 'w') as f:
            json.dump(self.config_data, f, indent=2)
        
        # Reload config in memory
        self.config.reload_config()
        
        # Emit signal to notify main application of changes
        self.preferences_saved.emit()
        
        self.accept()

    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Load default config
            default_config = self.config._get_defaults()
            self.config_data = default_config
            
            # Refresh UI
            self.grid_size_spinbox.setValue(default_config['grid']['size'])
            self.grid_enabled_checkbox.setChecked(default_config['grid']['enabled_by_default'])
            self.grid_color = default_config['grid']['color']
            self.update_grid_color_button()
            
            self.node_size_spinbox.setValue(default_config['node']['size'])
            self.border_width_spinbox.setValue(default_config['node']['border_width'])
            self.selected_border_width_spinbox.setValue(default_config['node']['selected_border_width'])
            
            self.connection_width_spinbox.setValue(default_config['connection']['width'])
            self.hitbox_spinbox.setValue(default_config['connection']['hitbox_distance'])
            self.connection_color = default_config['connection']['default_color']
            self.update_connection_color_button()
            
            self.min_zoom_spinbox.setValue(int(default_config['zoom']['min'] * 100))
            self.max_zoom_spinbox.setValue(int(default_config['zoom']['max'] * 100))
            self.zoom_increment_spinbox.setValue(int(default_config['zoom']['increment'] * 100))
            
            self.snap_to_grid_checkbox.setChecked(default_config['features']['snap_to_grid_enabled'])
            self.antialiasing_checkbox.setChecked(default_config['features']['antialiasing_enabled'])
            
            # Repopulate classes table
            self.populate_classes_table()
