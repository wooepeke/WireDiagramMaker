"""
Properties panel for editing element properties
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QColorDialog, QStackedWidget, QComboBox
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal
from config_loader import get_config


class PropertiesPanel(QWidget):
    """Panel for editing properties of selected elements"""

    # Signals
    node_color_changed = pyqtSignal(QColor)
    node_class_changed = pyqtSignal(str)  # Emitted when node class changes
    connection_color_changed = pyqtSignal(QColor)
    image_rotated = pyqtSignal()  # Emitted when image is rotated

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_nodes = []
        self.selected_connections = []
        self.selected_image = None  # Track selected image for rotation
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Stacked widget to switch between different panels
        self.stacked_widget = QStackedWidget()

        # Panel 0: Empty panel
        empty_panel = self._create_empty_panel()
        self.stacked_widget.addWidget(empty_panel)

        # Panel 1: Node editor panel (for both selecting and adding nodes)
        node_panel = self._create_node_panel()
        self.stacked_widget.addWidget(node_panel)

        # Panel 2: Connection editor panel (for both selecting and adding connections)
        conn_panel = self._create_connection_panel()
        self.stacked_widget.addWidget(conn_panel)

        # Panel 3: Module info panel
        module_panel = self._create_module_panel()
        self.stacked_widget.addWidget(module_panel)

        # Panel 4: Image editor panel
        image_panel = self._create_image_panel()
        self.stacked_widget.addWidget(image_panel)

        main_layout.addWidget(self.stacked_widget)
        main_layout.addStretch()
        self.setLayout(main_layout)

    def _create_empty_panel(self):
        """Create the empty/default panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        info_label = QLabel("Select nodes or connections to edit properties")
        info_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(info_label)
        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def _create_node_panel(self):
        """Create the node editor panel (works for both selecting and adding nodes)"""
        panel = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Nodes")
        title_font = title.font()
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Status/Instructions label
        self.node_mode_label = QLabel()
        self.node_mode_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(self.node_mode_label)

        # Node Class
        class_layout = QHBoxLayout()
        class_label = QLabel("Class:")
        self.node_class_combo = QComboBox()
        config = get_config()
        class_names = config.get_node_class_names()
        self.node_class_combo.addItems(class_names)
        self.node_class_combo.currentTextChanged.connect(self.on_node_class_changed)
        class_layout.addWidget(class_label)
        class_layout.addWidget(self.node_class_combo)
        class_layout.addStretch()
        layout.addLayout(class_layout)

        # Node Color
        color_layout = QHBoxLayout()
        color_label = QLabel("Color:")
        self.node_color_btn = QPushButton("Select Color")
        self.node_color_btn.clicked.connect(self.on_node_color_select)
        self.node_color_preview = QPushButton()
        self.node_color_preview.setMaximumWidth(50)
        self.node_color_preview.setEnabled(False)
        self.node_color = QColor(100, 150, 200)
        self.update_node_color_preview()
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.node_color_btn)
        color_layout.addWidget(self.node_color_preview)
        color_layout.addStretch()
        layout.addLayout(color_layout)

        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def _create_connection_panel(self):
        """Create the connection editor panel (works for both selecting and adding connections)"""
        panel = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Connections")
        title_font = title.font()
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Status/Instructions label
        self.conn_mode_label = QLabel()
        self.conn_mode_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(self.conn_mode_label)

        # Connection Color
        color_layout = QHBoxLayout()
        color_label = QLabel("Color:")
        self.conn_color_btn = QPushButton("Select Color")
        self.conn_color_btn.clicked.connect(self.on_connection_color_select)
        self.conn_color_preview = QPushButton()
        self.conn_color_preview.setMaximumWidth(50)
        self.conn_color_preview.setEnabled(False)
        self.conn_color = QColor(100, 100, 100)
        self.update_connection_color_preview()
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.conn_color_btn)
        color_layout.addWidget(self.conn_color_preview)
        color_layout.addStretch()
        layout.addLayout(color_layout)
        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def _create_module_panel(self):
        """Create the module info panel"""
        panel = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Module Info")
        title_font = title.font()
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Module name display
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        self.module_name_display = QLabel()
        self.module_name_display.setStyleSheet("font-weight: bold;")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.module_name_display)
        name_layout.addStretch()
        layout.addLayout(name_layout)

        # Module ID display
        id_layout = QHBoxLayout()
        id_label = QLabel("ID:")
        self.module_id_display = QLabel()
        self.module_id_display.setStyleSheet("font-family: monospace; font-size: 10px;")
        id_layout.addWidget(id_label)
        id_layout.addWidget(self.module_id_display)
        id_layout.addStretch()
        layout.addLayout(id_layout)

        # Node count display
        count_layout = QHBoxLayout()
        count_label = QLabel("Nodes:")
        self.module_node_count = QLabel()
        count_layout.addWidget(count_label)
        count_layout.addWidget(self.module_node_count)
        count_layout.addStretch()
        layout.addLayout(count_layout)

        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def _create_image_panel(self):
        """Create the image editor panel"""
        panel = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Image")
        title_font = title.font()
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Rotation controls
        rotation_label = QLabel("Rotation:")
        layout.addWidget(rotation_label)

        rotation_layout = QHBoxLayout()
        self.rotate_ccw_btn = QPushButton("↺ -90°")
        self.rotate_cw_btn = QPushButton("+90° ↻")
        self.rotate_ccw_btn.clicked.connect(self.on_rotate_ccw)
        self.rotate_cw_btn.clicked.connect(self.on_rotate_cw)
        rotation_layout.addWidget(self.rotate_ccw_btn)
        rotation_layout.addWidget(self.rotate_cw_btn)
        rotation_layout.addStretch()
        layout.addLayout(rotation_layout)

        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def on_node_color_select(self):
        """Handle node color selection"""
        color = QColorDialog.getColor(self.node_color, self, "Select Node Color")
        if color.isValid():
            self.node_color = color
            self.update_node_color_preview()
            self.node_color_changed.emit(color)

    def on_node_class_changed(self, class_name):
        """Handle node class change"""
        self.node_class_changed.emit(class_name)

    def on_connection_color_select(self):
        """Handle connection color selection"""
        color = QColorDialog.getColor(self.conn_color, self, "Select Connection Color")
        if color.isValid():
            self.conn_color = color
            self.update_connection_color_preview()
            self.connection_color_changed.emit(color)

    def update_node_color_preview(self):
        """Update the node color preview button"""
        self.node_color_preview.setStyleSheet(
            f"background-color: rgb({self.node_color.red()}, "
            f"{self.node_color.green()}, {self.node_color.blue()});"
        )
        # Also update add_node preview if it exists
        if hasattr(self, 'add_node_color_preview'):
            self.add_node_color_preview.setStyleSheet(
                f"background-color: rgb({self.node_color.red()}, "
                f"{self.node_color.green()}, {self.node_color.blue()});"
            )

    def update_connection_color_preview(self):
        """Update the connection color preview button"""
        self.conn_color_preview.setStyleSheet(
            f"background-color: rgb({self.conn_color.red()}, "
            f"{self.conn_color.green()}, {self.conn_color.blue()});"
        )
        # Also update add_connection preview if it exists
        if hasattr(self, 'add_conn_color_preview'):
            self.add_conn_color_preview.setStyleSheet(
                f"background-color: rgb({self.conn_color.red()}, "
                f"{self.conn_color.green()}, {self.conn_color.blue()});"
            )

    def on_mode_changed(self, mode):
        """Handle canvas mode changes"""
        if mode == "add_node":
            self.stacked_widget.setCurrentIndex(1)
            self.node_mode_label.setText("Click on the canvas to add nodes")
        elif mode == "add_connection":
            self.stacked_widget.setCurrentIndex(2)
            self.conn_mode_label.setText("Click on two nodes to connect them")
        elif mode == "select":
            # If nothing is selected, show empty panel
            if not self.selected_nodes and not self.selected_connections:
                self.stacked_widget.setCurrentIndex(0)

    def set_selected_elements(self, nodes, connections, images=None):
        """Update the panel with selected elements"""
        if images is None:
            images = []
        
        self.selected_nodes = nodes
        self.selected_connections = connections
        self.selected_image = images[0] if images else None

        # If an image is selected, show the image panel
        if self.selected_image:
            self.stacked_widget.setCurrentIndex(4)
            return

        # Check if all selected nodes belong to the same module
        module_id = None
        is_module = False
        if nodes and all(getattr(node, 'locked', False) and hasattr(node, 'module_id') and node.module_id for node in nodes):
            # Check if all nodes have the same module_id
            module_ids = set(node.module_id for node in nodes if hasattr(node, 'module_id'))
            if len(module_ids) == 1:
                module_id = module_ids.pop()
                is_module = True

        # Determine which panel to show
        if is_module and module_id:
            # Module is selected - show module panel
            self.stacked_widget.setCurrentIndex(3)
            self.update_module_display(nodes, module_id)
        elif nodes and not connections:
            # Only nodes selected (not a module)
            self.stacked_widget.setCurrentIndex(1)
            self.node_mode_label.setText(f"Selected: {len(nodes)} node(s)")
            
            # Update class combo box to show the class of the first selected node
            if nodes:
                self.node_class_combo.blockSignals(True)
                self.node_class_combo.setCurrentText(nodes[0].node_class)
                self.node_class_combo.blockSignals(False)
        elif connections and not nodes:
            # Only connections selected
            self.stacked_widget.setCurrentIndex(2)
            self.conn_mode_label.setText(f"Selected: {len(connections)} connection(s)")
        elif nodes and connections:
            # Both selected - show empty panel
            self.stacked_widget.setCurrentIndex(0)
        else:
            # Nothing selected - show empty panel
            self.stacked_widget.setCurrentIndex(0)

    def update_module_display(self, nodes, module_id):
        """Update the module panel with module information"""
        # Extract module name from the first node's data (we'll use a simple approach)
        # In a real implementation, you might want to load the module from file to get the name
        self.module_id_display.setText(module_id)
        self.module_node_count.setText(str(len(nodes)))
        
        # Try to find the module name from the module_handler
        # For now, we'll display the module ID as the name if we can't find it
        module_name = f"Module {module_id[:4]}"
        
        # Check if we can get the actual module name
        try:
            from module_handler import ModuleHandler
            handler = ModuleHandler()
            modules = handler.get_available_modules()
            for mod_info in modules:
                if mod_info["id"] == module_id:
                    module_name = mod_info["name"]
                    break
        except:
            pass
        
        self.module_name_display.setText(module_name)

    def on_rotate_cw(self):
        """Rotate selected image clockwise by 90 degrees"""
        if self.selected_image:
            self.selected_image.rotation = (self.selected_image.rotation + 90) % 360
            self.image_rotated.emit()

    def on_rotate_ccw(self):
        """Rotate selected image counter-clockwise by 90 degrees"""
        if self.selected_image:
            self.selected_image.rotation = (self.selected_image.rotation - 90) % 360
            self.image_rotated.emit()
