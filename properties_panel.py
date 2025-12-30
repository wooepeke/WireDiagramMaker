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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_nodes = []
        self.selected_connections = []
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

    def set_selected_elements(self, nodes, connections):
        """Update the panel with selected elements"""
        self.selected_nodes = nodes
        self.selected_connections = connections

        # Determine which panel to show
        if nodes and not connections:
            # Only nodes selected
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
