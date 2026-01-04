"""
Basic diagram elements - nodes and connections
"""

from PyQt5.QtCore import QPoint, QRect, QRectF, QSize, Qt
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPixmap
from PyQt5.QtSvg import QSvgRenderer
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
        self.module_id = None  # Track which module this node belongs to
        self.locked = False  # Locked nodes cannot be dragged (part of a module)
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

    def refresh_from_config(self):
        """Refresh node properties from current config"""
        config = get_config()
        self.NODE_SIZE = config.get_node_size()
        self.NODE_RADIUS = self.NODE_SIZE // 2
        self.update_rect()

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

        # Always use the node's actual color for the fill
        painter.setBrush(QBrush(self.color))
        
        # Don't draw border for locked (module) nodes
        if self.locked:
            # Set pen style to NoPen for locked nodes
            pen = QPen()
            pen.setStyle(Qt.PenStyle.NoPen)
            painter.setPen(pen)
        # Draw border based on state
        elif self.selected:
            border_color = config.get_node_border_color_selected()
            border_width = config.get_node_selected_border_width()
            painter.setPen(QPen(QColor(*border_color), border_width))
        elif self.highlighted:
            # Highlighted (hovering over while making connection) - use a brighter outline
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
        # Draw line - use thicker width when selected instead of changing color
        if self.selected:
            painter.setPen(QPen(self.color, 4))  # Thicker line for selected
        else:
            painter.setPen(QPen(self.color, 2))  # Normal width
        
        painter.drawLine(self.node1.get_center(), self.node2.get_center())

        # Draw connection points as small circles
        if self.selected:
            # Selected connection - thicker outline
            painter.setBrush(QBrush(self.color))
            painter.setPen(QPen(self.color, 2))
        else:
            painter.setBrush(QBrush(self.color))
            painter.setPen(QPen(self.color, 1))
        
        painter.drawEllipse(self.node1.get_center(), 4, 4)
        painter.drawEllipse(self.node2.get_center(), 4, 4)


class Module:
    """Represents a reusable module containing a group of nodes and images"""

    def __init__(self, module_id, name):
        """Initialize a module"""
        self.module_id = module_id
        self.name = name
        self.nodes = []  # List of Node objects in this module
        self.images = []  # List of Image objects in this module

    def add_node(self, node):
        """Add a node to this module"""
        if node not in self.nodes:
            self.nodes.append(node)

    def remove_node(self, node):
        """Remove a node from this module"""
        if node in self.nodes:
            self.nodes.remove(node)

    def add_image(self, image):
        """Add an image to this module"""
        if image not in self.images:
            self.images.append(image)

    def remove_image(self, image):
        """Remove an image from this module"""
        if image in self.images:
            self.images.remove(image)

    def to_dict(self):
        """Convert module to dictionary for JSON serialization"""
        nodes_data = []
        for node in self.nodes:
            nodes_data.append({
                "name": node.name,
                "pos": {"x": node.pos.x(), "y": node.pos.y()},
                "class": node.node_class,
                "color": [node.color.red(), node.color.green(), node.color.blue()]
            })
        
        images_data = []
        for image in self.images:
            images_data.append({
                "path": image.image_path,
                "pos": {"x": image.pos.x(), "y": image.pos.y()},
                "width": image.width,
                "height": image.height
            })
        
        return {
            "id": self.module_id,
            "name": self.name,
            "nodes": nodes_data,
            "images": images_data
        }

    @staticmethod
    def from_dict(module_dict):
        """Create a Module from a dictionary"""
        module = Module(module_dict["id"], module_dict["name"])
        
        for node_data in module_dict.get("nodes", []):
            node = Node(node_data["name"], QPoint(int(node_data["pos"]["x"]), int(node_data["pos"]["y"])))
            node.node_class = node_data.get("class", "Generic")
            color_data = node_data.get("color", [255, 0, 0])
            node.color = QColor(*color_data)
            module.add_node(node)
        
        for image_data in module_dict.get("images", []):
            image = Image(
                image_data["path"],
                QPoint(int(image_data["pos"]["x"]), int(image_data["pos"]["y"])),
                image_data.get("width", 100),
                image_data.get("height", 100)
            )
            module.add_image(image)
        
        return module


class Image:
    """Represents an image on the canvas"""

    def __init__(self, image_path, pos, width=100, height=100):
        """Initialize an image"""
        self.image_path = image_path
        self.pos = pos
        self.width = width
        self.height = height
        self.selected = False
        self.pixmap = None
        self.svg_renderer = None
        self.module_instance_id = None  # Track which module instance this image belongs to
        self.rotation = 0  # Rotation angle in degrees (0-360)
        
        # Load the image
        self.load_image()
        self.update_rect()

    def load_image(self):
        """Load the image from file"""
        try:
            if self.image_path.lower().endswith('.svg'):
                # Handle SVG images
                self.svg_renderer = QSvgRenderer(self.image_path)
            else:
                # Handle PNG and other formats
                self.pixmap = QPixmap(self.image_path)
                if self.pixmap.isNull():
                    print(f"Failed to load image: {self.image_path}")
        except Exception as e:
            print(f"Error loading image {self.image_path}: {e}")

    def update_rect(self):
        """Update the bounding rectangle of the image based on rotation"""
        import math
        
        # Calculate the actual axis-aligned bounding box of the rotated image
        center_x = self.pos.x() + self.width / 2
        center_y = self.pos.y() + self.height / 2
        
        # Get the four corners in unrotated space
        half_w = self.width / 2
        half_h = self.height / 2
        corners = [
            (-half_w, -half_h),
            (half_w, -half_h),
            (half_w, half_h),
            (-half_w, half_h),
        ]
        
        # Rotate corners and find bounding box
        angle_rad = math.radians(self.rotation)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        rotated_corners = []
        for dx, dy in corners:
            rotated_x = dx * cos_a - dy * sin_a
            rotated_y = dx * sin_a + dy * cos_a
            rotated_corners.append((rotated_x, rotated_y))
        
        # Find min/max x and y
        xs = [x for x, y in rotated_corners]
        ys = [y for x, y in rotated_corners]
        
        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)
        
        # Convert to screen coordinates
        self.rect = QRect(
            int(center_x + min_x),
            int(center_y + min_y),
            int(max_x - min_x),
            int(max_y - min_y)
        )

    def set_selected(self, selected):
        """Set selection state"""
        self.selected = selected

    def get_resize_handle_at(self, pos, handle_size=12):
        """Check if position is on a resize handle. Returns 'tl', 'br', or None"""
        # Update rect first to ensure it's current
        self.update_rect()
        
        # Check corners of the axis-aligned bounding box
        tl = self.rect.topLeft()
        br = self.rect.bottomRight()
        
        # Check if point is on top-left corner
        if (abs(pos.x() - tl.x()) <= handle_size and 
            abs(pos.y() - tl.y()) <= handle_size):
            return 'tl'
        
        # Check if point is on bottom-right corner
        if (abs(pos.x() - br.x()) <= handle_size and 
            abs(pos.y() - br.y()) <= handle_size):
            return 'br'
        
        return None

    def is_point_inside(self, pos):
        """Check if a point is inside the rotated image bounding box"""
        import math
        
        # Get image center
        center_x = self.pos.x() + self.width / 2
        center_y = self.pos.y() + self.height / 2
        
        # Translate point to center-based coordinates
        dx = pos.x() - center_x
        dy = pos.y() - center_y
        
        # Rotate point back (negative rotation) to unrotated space
        angle_rad = math.radians(-self.rotation)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        rotated_dx = dx * cos_a - dy * sin_a
        rotated_dy = dx * sin_a + dy * cos_a
        
        # Check if point is within unrotated rectangle bounds
        return (abs(rotated_dx) <= self.width / 2 and 
                abs(rotated_dy) <= self.height / 2)

    def draw(self, painter):
        """Draw the image"""
        self.update_rect()
        
        # Save painter state to restore after rotation
        painter.save()
        
        # Calculate center point
        center_x = self.pos.x() + self.width / 2
        center_y = self.pos.y() + self.height / 2
        
        # Apply rotation if needed
        if self.rotation != 0:
            painter.translate(center_x, center_y)
            painter.rotate(self.rotation)
            painter.translate(-center_x, -center_y)
        
        # Draw the image
        if self.svg_renderer and self.svg_renderer.isValid():
            rect_f = QRectF(int(self.pos.x()), int(self.pos.y()), int(self.width), int(self.height))
            self.svg_renderer.render(painter, rect_f)
        elif self.pixmap:
            # Scale pixmap to fit within the specified width and height while maintaining aspect ratio
            scaled_pixmap = self.pixmap.scaledToWidth(int(self.width), Qt.SmoothTransformation)
            # If scaled height exceeds desired height, scale by height instead
            if scaled_pixmap.height() > int(self.height):
                scaled_pixmap = self.pixmap.scaledToHeight(int(self.height), Qt.SmoothTransformation)
            painter.drawPixmap(self.pos, scaled_pixmap)
        
        # Restore painter state
        painter.restore()
        
        # Draw selection border and handles using axis-aligned rect (not rotated)
        if self.selected:
            painter.setPen(QPen(QColor(200, 0, 0), 3))
            painter.setBrush(QBrush(Qt.NoBrush))
            painter.drawRect(self.rect)
            
            # Draw resize handles at corners
            handle_size = 8
            painter.fillRect(self.rect.topLeft().x() - handle_size//2, 
                           self.rect.topLeft().y() - handle_size//2, 
                           handle_size, handle_size, QColor(200, 0, 0))
            painter.fillRect(self.rect.bottomRight().x() - handle_size//2, 
                           self.rect.bottomRight().y() - handle_size//2, 
                           handle_size, handle_size, QColor(200, 0, 0))

    def to_dict(self):
        """Convert image to dictionary for JSON serialization"""
        return {
            "type": "image",
            "path": self.image_path,
            "pos": {"x": self.pos.x(), "y": self.pos.y()},
            "width": self.width,
            "height": self.height,
            "rotation": self.rotation
        }

    @staticmethod
    def from_dict(image_dict):
        """Create an Image from a dictionary"""
        image = Image(
            image_dict["path"],
            QPoint(int(image_dict["pos"]["x"]), int(image_dict["pos"]["y"])),
            image_dict.get("width", 100),
            image_dict.get("height", 100)
        )
        image.rotation = image_dict.get("rotation", 0)
        return image
