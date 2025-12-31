"""
Undo/Redo actions for the wire diagram maker
"""

from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QColor


class Action:
    """Base class for undoable/redoable actions"""

    def execute(self):
        """Execute the action"""
        raise NotImplementedError

    def undo(self):
        """Undo the action"""
        raise NotImplementedError

    def get_description(self):
        """Get a description of the action for the UI"""
        raise NotImplementedError


class AddNodeAction(Action):
    """Action for adding a node"""

    def __init__(self, canvas, node):
        self.canvas = canvas
        self.node = node

    def execute(self):
        """Add the node to the canvas"""
        if self.node not in self.canvas.nodes:
            self.canvas.nodes.append(self.node)

    def undo(self):
        """Remove the node from the canvas"""
        if self.node in self.canvas.nodes:
            self.canvas.nodes.remove(self.node)
            # Remove any connections involving this node
            self.canvas.connections = [
                conn for conn in self.canvas.connections
                if conn.node1 != self.node and conn.node2 != self.node
            ]

    def get_description(self):
        return f"Add node {self.node.name}"


class DeleteNodeAction(Action):
    """Action for deleting a node"""

    def __init__(self, canvas, node):
        self.canvas = canvas
        self.node = node
        self.connections = []  # Store connections to this node

    def execute(self):
        """Remove the node and its connections"""
        if self.node in self.canvas.nodes:
            # Store all connections to restore on undo
            self.connections = [
                conn for conn in self.canvas.connections
                if conn.node1 == self.node or conn.node2 == self.node
            ]
            # Remove the node
            self.canvas.nodes.remove(self.node)
            # Remove connections
            for conn in self.connections:
                if conn in self.canvas.connections:
                    self.canvas.connections.remove(conn)

    def undo(self):
        """Restore the node and its connections"""
        if self.node not in self.canvas.nodes:
            self.canvas.nodes.append(self.node)
        # Restore connections
        for conn in self.connections:
            if conn not in self.canvas.connections:
                self.canvas.connections.append(conn)

    def get_description(self):
        return f"Delete node {self.node.name}"


class AddConnectionAction(Action):
    """Action for adding a connection"""

    def __init__(self, canvas, connection):
        self.canvas = canvas
        self.connection = connection

    def execute(self):
        """Add the connection to the canvas"""
        if self.connection not in self.canvas.connections:
            self.canvas.connections.append(self.connection)

    def undo(self):
        """Remove the connection from the canvas"""
        if self.connection in self.canvas.connections:
            self.canvas.connections.remove(self.connection)

    def get_description(self):
        return f"Add connection {self.connection.node1.name} -> {self.connection.node2.name}"


class DeleteConnectionAction(Action):
    """Action for deleting a connection"""

    def __init__(self, canvas, connection):
        self.canvas = canvas
        self.connection = connection

    def execute(self):
        """Remove the connection"""
        if self.connection in self.canvas.connections:
            self.canvas.connections.remove(self.connection)

    def undo(self):
        """Restore the connection"""
        if self.connection not in self.canvas.connections:
            self.canvas.connections.append(self.connection)

    def get_description(self):
        return f"Delete connection {self.connection.node1.name} -> {self.connection.node2.name}"


class MoveNodeAction(Action):
    """Action for moving a node"""

    def __init__(self, canvas, node, old_pos, new_pos):
        self.canvas = canvas
        self.node = node
        self.old_pos = QPoint(old_pos)
        self.new_pos = QPoint(new_pos)

    def execute(self):
        """Move the node to the new position"""
        self.node.pos = QPoint(self.new_pos)
        self.node.update_rect()

    def undo(self):
        """Move the node back to the old position"""
        self.node.pos = QPoint(self.old_pos)
        self.node.update_rect()

    def get_description(self):
        return f"Move node {self.node.name}"


class ChangeNodeColorAction(Action):
    """Action for changing a node's color"""

    def __init__(self, canvas, node, old_color, new_color):
        self.canvas = canvas
        self.node = node
        self.old_color = QColor(old_color)
        self.new_color = QColor(new_color)

    def execute(self):
        """Change the node color"""
        self.node.color = QColor(self.new_color)

    def undo(self):
        """Restore the old color"""
        self.node.color = QColor(self.old_color)

    def get_description(self):
        return f"Change color of {self.node.name}"


class ChangeNodeClassAction(Action):
    """Action for changing a node's class"""

    def __init__(self, canvas, node, old_class, new_class, old_color, new_color):
        self.canvas = canvas
        self.node = node
        self.old_class = old_class
        self.new_class = new_class
        self.old_color = QColor(old_color)
        self.new_color = QColor(new_color)

    def execute(self):
        """Change the node class"""
        self.node.node_class = self.new_class
        self.node.color = QColor(self.new_color)

    def undo(self):
        """Restore the old class"""
        self.node.node_class = self.old_class
        self.node.color = QColor(self.old_color)

    def get_description(self):
        return f"Change class of {self.node.name}"


class ChangeConnectionColorAction(Action):
    """Action for changing a connection's color"""

    def __init__(self, canvas, connection, old_color, new_color):
        self.canvas = canvas
        self.connection = connection
        self.old_color = QColor(old_color)
        self.new_color = QColor(new_color)

    def execute(self):
        """Change the connection color"""
        self.connection.color = QColor(self.new_color)

    def undo(self):
        """Restore the old color"""
        self.connection.color = QColor(self.old_color)

    def get_description(self):
        return f"Change connection color"


class AddImageAction(Action):
    """Action for adding an image"""

    def __init__(self, canvas, image):
        self.canvas = canvas
        self.image = image

    def execute(self):
        """Add the image to the canvas"""
        if self.image not in self.canvas.images:
            self.canvas.images.append(self.image)

    def undo(self):
        """Remove the image from the canvas"""
        if self.image in self.canvas.images:
            self.canvas.images.remove(self.image)

    def get_description(self):
        return f"Add image"


class DeleteImageAction(Action):
    """Action for deleting an image"""

    def __init__(self, canvas, image):
        self.canvas = canvas
        self.image = image

    def execute(self):
        """Remove the image"""
        if self.image in self.canvas.images:
            self.canvas.images.remove(self.image)

    def undo(self):
        """Restore the image"""
        if self.image not in self.canvas.images:
            self.canvas.images.append(self.image)

    def get_description(self):
        return f"Delete image"


class MoveImageAction(Action):
    """Action for moving an image"""

    def __init__(self, canvas, image, old_pos, new_pos):
        self.canvas = canvas
        self.image = image
        self.old_pos = QPoint(old_pos)
        self.new_pos = QPoint(new_pos)

    def execute(self):
        """Move the image to the new position"""
        self.image.pos = QPoint(self.new_pos)
        self.image.update_rect()

    def undo(self):
        """Move the image back to the old position"""
        self.image.pos = QPoint(self.old_pos)
        self.image.update_rect()

    def get_description(self):
        return f"Move image"


class ResizeImageAction(Action):
    """Action for resizing an image"""

    def __init__(self, canvas, image, old_width, old_height, new_width, new_height):
        self.canvas = canvas
        self.image = image
        self.old_width = old_width
        self.old_height = old_height
        self.new_width = new_width
        self.new_height = new_height

    def execute(self):
        """Resize the image"""
        self.image.width = self.new_width
        self.image.height = self.new_height
        self.image.update_rect()

    def undo(self):
        """Restore the old size"""
        self.image.width = self.old_width
        self.image.height = self.old_height
        self.image.update_rect()

    def get_description(self):
        return f"Resize image"
