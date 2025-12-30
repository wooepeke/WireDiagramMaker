"""
Properties panel for editing element properties
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QSpinBox, QColorDialog
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal


class PropertiesPanel(QWidget):
    """Panel for editing properties of selected elements"""

    # Signals
    node_color_changed = pyqtSignal(QColor)
    connection_color_changed = pyqtSignal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_nodes = []
        self.selected_connections = []
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Node Properties Group
        node_group = QGroupBox("Node Properties")
        node_layout = QVBoxLayout()

        # Node Color
        color_layout = QHBoxLayout()
        color_label = QLabel("Node Color:")
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
        node_layout.addLayout(color_layout)

        node_group.setLayout(node_layout)
        layout.addWidget(node_group)

        # Connection Properties Group
        conn_group = QGroupBox("Connection Properties")
        conn_layout = QVBoxLayout()

        # Connection Color
        conn_color_layout = QHBoxLayout()
        conn_color_label = QLabel("Line Color:")
        self.conn_color_btn = QPushButton("Select Color")
        self.conn_color_btn.clicked.connect(self.on_connection_color_select)
        self.conn_color_preview = QPushButton()
        self.conn_color_preview.setMaximumWidth(50)
        self.conn_color_preview.setEnabled(False)
        self.conn_color = QColor(100, 100, 100)
        self.update_connection_color_preview()
        conn_color_layout.addWidget(conn_color_label)
        conn_color_layout.addWidget(self.conn_color_btn)
        conn_color_layout.addWidget(self.conn_color_preview)
        conn_color_layout.addStretch()
        conn_layout.addLayout(conn_color_layout)

        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)

        # Info Label
        self.info_label = QLabel("Select nodes or connections to edit properties")
        self.info_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(self.info_label)

        # Stretch at the bottom
        layout.addStretch()

        self.setLayout(layout)

    def on_node_color_select(self):
        """Handle node color selection"""
        color = QColorDialog.getColor(self.node_color, self, "Select Node Color")
        if color.isValid():
            self.node_color = color
            self.update_node_color_preview()
            self.node_color_changed.emit(color)

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

    def update_connection_color_preview(self):
        """Update the connection color preview button"""
        self.conn_color_preview.setStyleSheet(
            f"background-color: rgb({self.conn_color.red()}, "
            f"{self.conn_color.green()}, {self.conn_color.blue()});"
        )

    def set_selected_elements(self, nodes, connections):
        """Update the panel with selected elements"""
        self.selected_nodes = nodes
        self.selected_connections = connections

        # Update info label
        if nodes and connections:
            self.info_label.setText(
                f"Selected: {len(nodes)} node(s), {len(connections)} connection(s)"
            )
        elif nodes:
            self.info_label.setText(f"Selected: {len(nodes)} node(s)")
        elif connections:
            self.info_label.setText(f"Selected: {len(connections)} connection(s)")
        else:
            self.info_label.setText("Select nodes or connections to edit properties")

    def get_node_color(self):
        """Get the current node color"""
        return self.node_color

    def get_connection_color(self):
        """Get the current connection color"""
        return self.conn_color
