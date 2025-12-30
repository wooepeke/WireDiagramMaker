"""
Basic diagram elements - nodes and connections
"""

from PyQt5.QtCore import QPoint, QRect, QSize
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont
from config_loader import get_config


class Node:
    """Represents a node in the wire diagram"""

    def __init__(self, name, pos):
        """Initialize a node"""
        config = get_config()
        self.NODE_SIZE = config.get_node_size()
        self.NODE_RADIUS = self.NODE_SIZE // 2
        
        self.name = name
        self.pos = pos
        self.highlighted = False
        self.selected = False
        # Get default class (first one in the list)
        class_names = config.get_node_class_names()
        self.node_class = class_names[0] if class_names else "Generic"
        # Color is determined by class
        color_tuple = config.get_node_class_color(self.node_class)
        self.color = QColor(*color_tuple)
        self.update_rect()

    def update_rect(self):
        """Update the bounding rectangle of the node"""
        size = self.NODE_SIZE
        self.rect = QRect(
            int(self.pos.x() - size // 2),
            int(self.pos.y() - size // 2),
            size,
            size
        )

    def set_highlighted(self, highlighted):
        """Set highlight state"""
        self.highlighted = highlighted

    def set_selected(self, selected):
        """Set selection state"""
        self.selected = selected

    def draw(self, painter):
        """Draw the node"""
        config = get_config()
        self.update_rect()

        # Determine color based on state
        if self.selected:
            selected_color = config.get_node_selected_color()
            color = QColor(*selected_color)
        elif self.highlighted:
            highlighted_color = config.get_node_highlighted_color()
            color = QColor(*highlighted_color)
        else:
            color = self.color  # Use node's color

        painter.setBrush(QBrush(color))
        
        # Draw border
        if self.selected:
            border_color = config.get_node_border_color_selected()
            border_width = config.get_node_selected_border_width()
            painter.setPen(QPen(QColor(*border_color), border_width))
        else:
            border_color = config.get_node_border_color()
            border_width = config.get_node_border_width()
            painter.setPen(QPen(QColor(*border_color), border_width))
        
        painter.drawEllipse(self.pos, self.NODE_RADIUS, self.NODE_RADIUS)

    def get_center(self):
        """Get the center point of the node"""
        return self.pos


class Connection:
    """Represents a wire connection between two nodes"""

    def __init__(self, node1, node2):
        """Initialize a connection"""
        config = get_config()
        self.HITBOX_DISTANCE = config.get_connection_hitbox_distance()
        
        self.node1 = node1
        self.node2 = node2
        self.selected = False
        color_tuple = config.get_connection_default_color()
        self.color = QColor(*color_tuple)

    def set_selected(self, selected):
        """Set selection state"""
        self.selected = selected

    def is_point_on_line(self, point):
        """Check if a point is close to the connection line"""
        x0, y0 = point.x(), point.y()
        x1, y1 = self.node1.get_center().x(), self.node1.get_center().y()
        x2, y2 = self.node2.get_center().x(), self.node2.get_center().y()

        # Calculate distance from point to line segment
        # Using formula: distance = |ax + by + c| / sqrt(a^2 + b^2)
        
        # Line equation: (y2-y1)x - (x2-x1)y + x2*y1 - y2*x1 = 0
        num = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        den = ((y2 - y1) ** 2 + (x2 - x1) ** 2) ** 0.5
        
        if den == 0:
            return False
        
        distance = num / den
        
        # Also check if point is within the bounding box of the line
        min_x = min(x1, x2)
        max_x = max(x1, x2)
        min_y = min(y1, y2)
        max_y = max(y1, y2)
        
        in_bounds = min_x - self.HITBOX_DISTANCE <= x0 <= max_x + self.HITBOX_DISTANCE and \
                    min_y - self.HITBOX_DISTANCE <= y0 <= max_y + self.HITBOX_DISTANCE
        
        return distance <= self.HITBOX_DISTANCE and in_bounds

    def draw(self, painter):
        """Draw the connection"""
        # Draw line with different color if selected
        if self.selected:
            painter.setPen(QPen(QColor(255, 0, 0), 4))  # Red for selected
        else:
            painter.setPen(QPen(self.color, 2))  # Use connection's color
        
        painter.drawLine(self.node1.get_center(), self.node2.get_center())

        # Draw connection points as small circles
        if self.selected:
            painter.setBrush(QBrush(QColor(255, 0, 0)))
            painter.setPen(QPen(QColor(200, 0, 0), 1))
        else:
            painter.setBrush(QBrush(self.color))
            painter.setPen(QPen(self.color, 1))
        
        painter.drawEllipse(self.node1.get_center(), 4, 4)
        painter.drawEllipse(self.node2.get_center(), 4, 4)
