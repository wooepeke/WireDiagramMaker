"""
Properties dialog for editing node and connection properties
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFormLayout, QDialogButtonBox
)
from PyQt5.QtCore import Qt


class NodePropertiesDialog(QDialog):
    """Dialog for editing node properties"""

    def __init__(self, node, parent=None):
        super().__init__(parent)
        self.node = node
        self.setWindowTitle("Node Properties")
        self.setModal(True)
        self.setGeometry(200, 200, 300, 150)

        # Create layout
        layout = QFormLayout()

        # Node name field
        self.name_input = QLineEdit()
        self.name_input.setText(node.name)
        layout.addRow("Node Name:", self.name_input)

        # Position fields (read-only)
        x_label = QLabel(f"{node.pos.x():.0f}")
        y_label = QLabel(f"{node.pos.y():.0f}")
        layout.addRow("X Position:", x_label)
        layout.addRow("Y Position:", y_label)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)

        self.setLayout(layout)

    def get_name(self):
        """Get the edited node name"""
        return self.name_input.text()
