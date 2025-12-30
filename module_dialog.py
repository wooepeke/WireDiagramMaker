"""
Module creation and editing dialog
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QGroupBox, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from diagram_elements import Module


class ModuleCreationDialog(QDialog):
    """Dialog for creating and editing modules"""
    
    module_created = pyqtSignal(Module)  # Emitted when a module is successfully created

    def __init__(self, canvas, module_handler, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.module_handler = module_handler
        self.selected_nodes = [node for node in canvas.nodes if node.selected]
        
        self.setWindowTitle("Create Module")
        self.setGeometry(200, 200, 500, 400)
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI"""
        main_layout = QVBoxLayout()

        # Title section
        title = QLabel("Create New Module")
        title_font = title.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)

        # Module name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Module Name:")
        name_label.setMinimumWidth(100)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter a name for the module...")
        self.name_input.setText("New Module")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        main_layout.addLayout(name_layout)

        # Selected nodes info
        info_group = QGroupBox("Selected Nodes")
        info_layout = QVBoxLayout()
        
        if self.selected_nodes:
            info_text = QLabel(f"This module will contain {len(self.selected_nodes)} node(s):")
            info_layout.addWidget(info_text)
            
            # List of selected nodes
            self.nodes_list = QListWidget()
            self.nodes_list.setMaximumHeight(150)
            for node in self.selected_nodes:
                item = QListWidgetItem(f"{node.name} ({node.node_class})")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)  # Make non-selectable
                # Color the item based on node class
                item.setForeground(node.color)
                self.nodes_list.addItem(item)
            
            info_layout.addWidget(self.nodes_list)
        else:
            no_nodes_label = QLabel("⚠ No nodes selected!")
            no_nodes_label.setStyleSheet("color: red;")
            info_layout.addWidget(no_nodes_label)
            info_text = QLabel("Please select at least one node before creating a module.")
            info_text.setStyleSheet("color: gray; font-size: 10px;")
            info_layout.addWidget(info_text)

        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)

        # Preview section
        preview_group = QGroupBox("Module Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_label = QLabel()
        self.preview_label.setStyleSheet("color: gray; font-size: 10px;")
        self.update_preview()
        preview_layout.addWidget(self.preview_label)
        
        preview_group.setLayout(preview_layout)
        main_layout.addWidget(preview_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        create_button = QPushButton("Create Module")
        create_button.setMinimumWidth(120)
        create_button.clicked.connect(self.on_create_module)
        if not self.selected_nodes:
            create_button.setEnabled(False)
        button_layout.addWidget(create_button)
        
        main_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        
        # Connect name input to update preview
        self.name_input.textChanged.connect(self.update_preview)

    def update_preview(self):
        """Update the preview of the module"""
        name = self.name_input.text().strip()
        if not name:
            name = "(unnamed)"
        
        node_count = len(self.selected_nodes)
        preview_text = f'Module "{name}" with {node_count} node(s)'
        self.preview_label.setText(preview_text)

    def on_create_module(self):
        """Handle module creation"""
        module_name = self.name_input.text().strip()
        
        # Validate
        if not module_name:
            QMessageBox.warning(self, "Invalid Input", "Please enter a module name.")
            return
        
        if not self.selected_nodes:
            QMessageBox.warning(self, "No Nodes", "Please select at least one node.")
            return
        
        # Create the module
        module_id = self.module_handler.generate_module_id()
        module = Module(module_id, module_name)
        
        for node in self.selected_nodes:
            module.add_node(node)
        
        # Save the module
        if self.module_handler.save_module(module):
            # Mark nodes as part of the module
            for node in self.selected_nodes:
                node.module_id = module_id
                node.locked = True
            
            self.module_created.emit(module)
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to save module.")


class ModuleEditDialog(QDialog):
    """Dialog for editing existing modules (for future use)"""
    
    module_updated = pyqtSignal(Module)

    def __init__(self, module, module_handler, parent=None):
        super().__init__(parent)
        self.module = module
        self.module_handler = module_handler
        
        self.setWindowTitle(f"Edit Module: {module.name}")
        self.setGeometry(200, 200, 500, 400)
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI"""
        main_layout = QVBoxLayout()

        # Title section
        title = QLabel(f"Edit Module: {self.module.name}")
        title_font = title.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)

        # Module name editing
        name_layout = QHBoxLayout()
        name_label = QLabel("Module Name:")
        name_label.setMinimumWidth(100)
        self.name_input = QLineEdit()
        self.name_input.setText(self.module.name)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        main_layout.addLayout(name_layout)

        # Module nodes list
        nodes_group = QGroupBox("Module Nodes")
        nodes_layout = QVBoxLayout()
        
        self.nodes_list = QListWidget()
        for node in self.module.nodes:
            item = QListWidgetItem(f"{node.name} ({node.node_class})")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            item.setForeground(node.color)
            self.nodes_list.addItem(item)
        
        nodes_layout.addWidget(self.nodes_list)
        nodes_group.setLayout(nodes_layout)
        main_layout.addWidget(nodes_group)

        # Module ID info
        id_layout = QHBoxLayout()
        id_label = QLabel("Module ID:")
        id_label.setMinimumWidth(100)
        id_value = QLabel(self.module.module_id)
        id_value.setStyleSheet("font-family: monospace; color: gray;")
        id_layout.addWidget(id_label)
        id_layout.addWidget(id_value)
        id_layout.addStretch()
        main_layout.addLayout(id_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        save_button = QPushButton("Save Changes")
        save_button.setMinimumWidth(120)
        save_button.clicked.connect(self.on_save_changes)
        button_layout.addWidget(save_button)
        
        main_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def on_save_changes(self):
        """Handle saving changes to the module"""
        new_name = self.name_input.text().strip()
        
        if not new_name:
            QMessageBox.warning(self, "Invalid Input", "Please enter a module name.")
            return
        
        # Update the module
        self.module.name = new_name
        
        # Save the module
        if self.module_handler.save_module(self.module):
            self.module_updated.emit(self.module)
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to save module changes.")
