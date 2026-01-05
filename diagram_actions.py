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


class CreateModuleAction(Action):
    """Action for creating a module from selected nodes and images"""

    def __init__(self, canvas, nodes, images, module_id):
        self.canvas = canvas
        self.nodes = nodes
        self.images = images
        self.module_id = module_id
        # Store original state
        self.original_locked = {node: getattr(node, 'locked', False) for node in nodes}
        self.original_module_ids = {node: getattr(node, 'module_id', None) for node in nodes}
        self.image_module_ids = {image: getattr(image, 'module_instance_id', None) for image in images}

    def execute(self):
        """Lock nodes and images as part of the module"""
        for node in self.nodes:
            node.locked = True
            node.module_id = self.module_id
        for image in self.images:
            image.module_instance_id = self.module_id

    def undo(self):
        """Unlock nodes and images, restoring their original state"""
        for node in self.nodes:
            node.locked = self.original_locked[node]
            node.module_id = self.original_module_ids[node]
        for image in self.images:
            image.module_instance_id = self.image_module_ids[image]

    def get_description(self):
        return f"Create module"

    def get_description(self):
        return f"Create module"


class MoveModuleAction(Action):
    """Action for moving an entire module (all nodes and images together)"""

    def __init__(self, canvas, module_id, nodes, images, old_positions, new_positions):
        self.canvas = canvas
        self.module_id = module_id
        self.nodes = nodes
        self.images = images
        self.old_node_positions = old_positions["nodes"]  # Dict: node -> QPoint
        self.new_node_positions = new_positions["nodes"]
        self.old_image_positions = old_positions["images"]  # Dict: image -> QPoint
        self.new_image_positions = new_positions["images"]
        # Handle waypoints for backward compatibility with old files
        self.old_waypoints = old_positions.get("waypoints", {})  # Dict: connection -> list of QPoint
        self.new_waypoints = new_positions.get("waypoints", {})

    def execute(self):
        """Move all nodes and images to their new positions"""
        for node, pos in self.new_node_positions.items():
            node.pos = pos
        for image, pos in self.new_image_positions.items():
            image.pos = pos
        # Restore waypoints to their new positions (if available)
        if hasattr(self, 'new_waypoints') and self.new_waypoints:
            for connection, waypoints in self.new_waypoints.items():
                connection.waypoints = [QPoint(wp) for wp in waypoints]

    def undo(self):
        """Restore all nodes and images to their old positions"""
        print(f"DEBUG UNDO: MoveModuleAction.undo() called")
        for node, pos in self.old_node_positions.items():
            node.pos = pos
        for image, pos in self.old_image_positions.items():
            image.pos = pos
        # Restore waypoints to their old positions (if available)
        if hasattr(self, 'old_waypoints') and self.old_waypoints:
            print(f"DEBUG UNDO: Restoring {len(self.old_waypoints)} connections with waypoints")
            for connection, waypoints in self.old_waypoints.items():
                print(f"DEBUG UNDO: Connection {id(connection)}: restoring {len(waypoints)} waypoints")
                connection.waypoints = [QPoint(wp) for wp in waypoints]
        else:
            print(f"DEBUG UNDO: No waypoints to restore (old_waypoints={getattr(self, 'old_waypoints', 'N/A')})")

    def get_description(self):
        return f"Move module"


class DuplicateModuleAction(Action):
    """Action for duplicating a module with all its nodes, images, and connections"""

    def __init__(self, canvas, nodes, images, connections, new_module_id):
        self.canvas = canvas
        self.nodes = nodes  # List of new nodes to add
        self.images = images  # List of new images to add
        self.connections = connections  # List of new connections to add
        self.new_module_id = new_module_id

    def execute(self):
        """Add all duplicated nodes, images, and connections"""
        for node in self.nodes:
            if node not in self.canvas.nodes:
                self.canvas.nodes.append(node)
        
        for image in self.images:
            if image not in self.canvas.images:
                self.canvas.images.append(image)
        
        for connection in self.connections:
            if connection not in self.canvas.connections:
                self.canvas.connections.append(connection)

    def undo(self):
        """Remove all duplicated nodes, images, and connections"""
        for node in self.nodes:
            if node in self.canvas.nodes:
                self.canvas.nodes.remove(node)
        
        for image in self.images:
            if image in self.canvas.images:
                self.canvas.images.remove(image)
        
        for connection in self.connections:
            if connection in self.canvas.connections:
                self.canvas.connections.remove(connection)

    def get_description(self):
        return f"Duplicate module"


class AddWaypointAction(Action):
    """Action for adding a waypoint to a connection"""

    def __init__(self, canvas, connection, waypoint, index):
        self.canvas = canvas
        self.connection = connection
        self.waypoint = waypoint
        self.index = index

    def execute(self):
        """Add the waypoint to the connection"""
        if self.index <= len(self.connection.waypoints):
            self.connection.waypoints.insert(self.index, self.waypoint)

    def undo(self):
        """Remove the waypoint from the connection"""
        if self.index < len(self.connection.waypoints) and self.connection.waypoints[self.index] == self.waypoint:
            self.connection.waypoints.pop(self.index)

    def get_description(self):
        return f"Add waypoint to connection"


class RemoveWaypointAction(Action):
    """Action for removing a waypoint from a connection"""

    def __init__(self, canvas, connection, waypoint, index):
        self.canvas = canvas
        self.connection = connection
        self.waypoint = waypoint
        self.index = index

    def execute(self):
        """Remove the waypoint from the connection"""
        if self.index < len(self.connection.waypoints) and self.connection.waypoints[self.index] == self.waypoint:
            self.connection.waypoints.pop(self.index)

    def undo(self):
        """Restore the waypoint to the connection"""
        if self.index <= len(self.connection.waypoints):
            self.connection.waypoints.insert(self.index, self.waypoint)

    def get_description(self):
        return f"Remove waypoint from connection"
