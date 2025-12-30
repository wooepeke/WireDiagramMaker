"""
Canvas widget for drawing wire diagrams
"""

from PyQt5.QtWidgets import QWidget, QMenu
from PyQt5.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont
from diagram_elements import Node, Connection
from properties_dialog import NodePropertiesDialog


class DiagramCanvas(QWidget):
    """Canvas for drawing and managing diagram elements"""

    # Signals
    tool_deactivated = pyqtSignal()  # Emitted when a tool action is completed
    selection_changed = pyqtSignal()  # Emitted when selection changes

    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setStyleSheet("background-color: white;")

        # Lists to store diagram elements
        self.nodes = []
        self.connections = []

        # Current operation mode
        self.mode = None

        # For adding connections
        self.selected_node = None

        # For dragging nodes
        self.dragging_node = None
        self.drag_offset = QPoint()

        # Node counter for naming
        self.node_counter = 0

        # Grid settings
        self.show_grid = True
        self.grid_size = 20

        # Pan/zoom settings
        self.pan_offset = QPoint(0, 0)
        self.panning = False
        self.pan_start = QPoint()
        self.zoom_level = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0

        # Selection settings
        self.selected_nodes = []
        self.selected_connections = []

    def set_mode(self, mode):
        """Set the current operation mode"""
        self.mode = mode
        self.selected_node = None
        self.setCursor(Qt.CursorShape.CrossCursor if mode in ["add_node", "add_connection"] else Qt.CursorShape.ArrowCursor)

    def set_show_grid(self, show):
        """Set whether to show grid"""
        self.show_grid = show
        self.update()

    def zoom_in(self):
        """Increase zoom level"""
        new_zoom = min(self.zoom_level * 1.2, self.max_zoom)
        self.set_zoom(new_zoom)

    def zoom_out(self):
        """Decrease zoom level"""
        new_zoom = max(self.zoom_level / 1.2, self.min_zoom)
        self.set_zoom(new_zoom)

    def reset_zoom(self):
        """Reset zoom to 1.0"""
        self.set_zoom(1.0)

    def set_zoom(self, zoom_level):
        """Set the zoom level"""
        self.zoom_level = max(self.min_zoom, min(zoom_level, self.max_zoom))
        self.update()

    def screen_to_canvas(self, screen_pos):
        """Convert screen coordinates to canvas coordinates"""
        return (screen_pos - self.pan_offset) / self.zoom_level


    def mousePressEvent(self, event):
        """Handle mouse press events"""
        pos = event.pos()

        # Handle panning with middle mouse button or right mouse button
        if event.button() == Qt.MouseButton.MiddleButton:
            self.panning = True
            self.pan_start = pos
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            return

        # Handle right mouse button for context menu
        if event.button() == Qt.MouseButton.RightButton:
            adjusted_pos = self.screen_to_canvas(pos)
            clicked_node = self.get_node_at(adjusted_pos)
            if clicked_node:
                self.show_node_context_menu(clicked_node, event.globalPos())
                return
            
            clicked_connection = self.get_connection_at(adjusted_pos)
            if clicked_connection:
                self.show_connection_context_menu(clicked_connection, event.globalPos())
                return

        if self.mode == "add_node":
            # Adjust position for pan offset and zoom
            adjusted_pos = self.screen_to_canvas(pos)
            self.add_node(adjusted_pos)

        elif self.mode == "add_connection":
            # Adjust position for pan offset and zoom
            adjusted_pos = self.screen_to_canvas(pos)
            clicked_node = self.get_node_at(adjusted_pos)
            if clicked_node:
                if self.selected_node is None:
                    self.selected_node = clicked_node
                    clicked_node.set_highlighted(True)
                elif clicked_node != self.selected_node:
                    self.add_connection(self.selected_node, clicked_node)
                    self.selected_node.set_highlighted(False)
                    self.selected_node = None
                    self.update()

        else:
            # Check if a node is clicked
            adjusted_pos = self.screen_to_canvas(pos)
            clicked_node = self.get_node_at(adjusted_pos)
            
            if clicked_node:
                # Toggle selection with Ctrl, otherwise select single node
                ctrl_pressed = event.modifiers() & Qt.KeyboardModifier.ControlModifier
                if ctrl_pressed:
                    if clicked_node in self.selected_nodes:
                        self.deselect_node(clicked_node)
                    else:
                        self.select_node(clicked_node, multi=True)
                else:
                    self.clear_selection()
                    self.select_node(clicked_node)
                
                # Start dragging
                self.dragging_node = clicked_node
                self.drag_offset = adjusted_pos - clicked_node.pos
            else:
                # Check if a connection is clicked
                clicked_connection = self.get_connection_at(adjusted_pos)
                if clicked_connection:
                    ctrl_pressed = event.modifiers() & Qt.KeyboardModifier.ControlModifier
                    if ctrl_pressed:
                        if clicked_connection in self.selected_connections:
                            self.deselect_connection(clicked_connection)
                        else:
                            self.select_connection(clicked_connection, multi=True)
                    else:
                        self.clear_selection()
                        self.select_connection(clicked_connection)
                else:
                    # Clear selection if clicking on empty space
                    self.clear_selection()

    def mouseMoveEvent(self, event):
        """Handle mouse move events"""
        if self.panning:
            # Calculate the pan offset
            delta = event.pos() - self.pan_start
            self.pan_offset += delta
            self.pan_start = event.pos()
            self.update()
        elif self.dragging_node:
            new_pos = self.screen_to_canvas(event.pos()) - self.drag_offset
            self.dragging_node.pos = new_pos
            self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if self.panning:
            self.panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        self.dragging_node = None

    def add_node(self, pos):
        """Add a new node at the given position"""
        self.node_counter += 1
        node = Node(f"Node{self.node_counter}", pos)
        self.nodes.append(node)
        self.update()

    def add_connection(self, node1, node2):
        """Add a connection between two nodes"""
        # Avoid duplicate connections
        for conn in self.connections:
            if (conn.node1 == node1 and conn.node2 == node2) or \
               (conn.node1 == node2 and conn.node2 == node1):
                return

        connection = Connection(node1, node2)
        self.connections.append(connection)
        self.update()

    def get_node_at(self, pos):
        """Get the node at the given position, if any"""
        for node in self.nodes:
            if node.rect.contains(pos):
                return node
        return None

    def get_connection_at(self, pos):
        """Get the connection at the given position, if any"""
        for connection in self.connections:
            if connection.is_point_on_line(pos):
                return connection
        return None

    def clear(self):
        """Clear all diagram elements"""
        self.nodes.clear()
        self.connections.clear()
        self.node_counter = 0
        self.selected_node = None
        self.dragging_node = None
        self.clear_selection()
        self.update()

    def select_node(self, node, multi=False):
        """Select a node"""
        if not multi:
            self.clear_selection()
        if node not in self.selected_nodes:
            self.selected_nodes.append(node)
            node.set_selected(True)
        self.selection_changed.emit()
        self.update()

    def deselect_node(self, node):
        """Deselect a node"""
        if node in self.selected_nodes:
            self.selected_nodes.remove(node)
            node.set_selected(False)
        self.selection_changed.emit()
        self.update()

    def select_connection(self, connection, multi=False):
        """Select a connection"""
        if not multi:
            self.clear_selection()
        if connection not in self.selected_connections:
            self.selected_connections.append(connection)
            connection.set_selected(True)
        self.selection_changed.emit()
        self.update()

    def deselect_connection(self, connection):
        """Deselect a connection"""
        if connection in self.selected_connections:
            self.selected_connections.remove(connection)
            connection.set_selected(False)
        self.selection_changed.emit()
        self.update()

    def clear_selection(self):
        """Clear all selections"""
        for node in self.selected_nodes:
            node.set_selected(False)
        for connection in self.selected_connections:
            connection.set_selected(False)
        self.selected_nodes.clear()
        self.selected_connections.clear()
        self.selection_changed.emit()
        self.update()

    def delete_selected(self):
        """Delete all selected nodes and their connections"""
        # Remove connections involving selected nodes
        self.connections = [
            conn for conn in self.connections
            if conn.node1 not in self.selected_nodes and conn.node2 not in self.selected_nodes
        ]
        
        # Remove selected connections
        for conn in self.selected_connections:
            if conn in self.connections:
                self.connections.remove(conn)
        
        # Remove selected nodes
        for node in self.selected_nodes:
            if node in self.nodes:
                self.nodes.remove(node)
        
        self.clear_selection()

    def show_context_menu(self, node, global_pos):
        """Show a context menu for a node"""
        menu = QMenu(self)
        
        edit_action = menu.addAction("Edit Properties")
        edit_action.triggered.connect(lambda: self.edit_node(node))
        
        menu.addSeparator()
        
        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(lambda: self.delete_node(node))
        
        menu.exec_(global_pos)

    def show_node_context_menu(self, node, global_pos):
        """Show a context menu for a node"""
        menu = QMenu(self)
        
        edit_action = menu.addAction("Edit Properties")
        edit_action.triggered.connect(lambda: self.edit_node(node))
        
        menu.addSeparator()
        
        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(lambda: self.delete_node(node))
        
        menu.exec_(global_pos)

    def show_connection_context_menu(self, connection, global_pos):
        """Show a context menu for a connection"""
        menu = QMenu(self)
        
        delete_action = menu.addAction("Delete Connection")
        delete_action.triggered.connect(lambda: self.delete_connection(connection))
        
        menu.exec_(global_pos)

    def edit_node(self, node):
        """Edit node properties"""
        dialog = NodePropertiesDialog(node, self)
        if dialog.exec_():
            new_name = dialog.get_name()
            if new_name.strip():
                node.name = new_name
                self.update()

    def delete_node(self, node):
        """Delete a node and its connections"""
        # Remove connections
        self.connections = [
            conn for conn in self.connections
            if conn.node1 != node and conn.node2 != node
        ]
        
        # Remove node
        if node in self.nodes:
            self.nodes.remove(node)
        
        # Remove from selection
        self.deselect_node(node)
        self.update()

    def delete_connection(self, connection):
        """Delete a connection"""
        if connection in self.connections:
            self.connections.remove(connection)
        
        # Remove from selection
        self.deselect_connection(connection)
        self.update()

    def set_selected_nodes_color(self, color):
        """Set color for all selected nodes"""
        for node in self.selected_nodes:
            node.color = color
        self.update()

    def set_selected_connections_color(self, color):
        """Set color for all selected connections"""
        for connection in self.selected_connections:
            connection.color = color
        self.update()

    def paintEvent(self, event):
        """Paint the canvas and all diagram elements"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Apply pan transformation
        painter.translate(self.pan_offset)

        # Apply zoom transformation
        painter.scale(self.zoom_level, self.zoom_level)

        # Draw grid if enabled
        if self.show_grid:
            self.draw_grid(painter)

        # Draw connections first (so they appear behind nodes)
        for connection in self.connections:
            connection.draw(painter)

        # Draw nodes
        for node in self.nodes:
            node.draw(painter)

        painter.end()

    def draw_grid(self, painter):
        """Draw a grid on the canvas"""
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        width = self.width()
        height = self.height()

        # Draw vertical lines
        for x in range(0, width, self.grid_size):
            painter.drawLine(x, 0, x, height)

        # Draw horizontal lines
        for y in range(0, height, self.grid_size):
            painter.drawLine(0, y, width, y)

    def export_diagram(self):
        """Export the diagram as a dictionary for saving"""
        diagram_data = {
            "nodes": [],
            "connections": []
        }

        # Export nodes
        for node in self.nodes:
            diagram_data["nodes"].append({
                "name": node.name,
                "x": node.pos.x(),
                "y": node.pos.y()
            })

        # Export connections
        for connection in self.connections:
            # Find the indices of the connected nodes
            node1_idx = self.nodes.index(connection.node1)
            node2_idx = self.nodes.index(connection.node2)
            diagram_data["connections"].append({
                "node1": node1_idx,
                "node2": node2_idx
            })

        return diagram_data

    def import_diagram(self, data):
        """Import a diagram from a dictionary"""
        try:
            self.clear()

            # Import nodes
            node_map = {}
            for node_data in data.get("nodes", []):
                node = Node(
                    node_data["name"],
                    QPoint(int(node_data["x"]), int(node_data["y"]))
                )
                self.nodes.append(node)
                node_map[len(self.nodes) - 1] = node
                # Update node counter
                if node_data["name"].startswith("Node"):
                    try:
                        num = int(node_data["name"][4:])
                        self.node_counter = max(self.node_counter, num)
                    except ValueError:
                        pass

            # Import connections
            for conn_data in data.get("connections", []):
                node1_idx = conn_data["node1"]
                node2_idx = conn_data["node2"]
                if node1_idx in node_map and node2_idx in node_map:
                    connection = Connection(node_map[node1_idx], node_map[node2_idx])
                    self.connections.append(connection)

            self.update()
            return True
        except Exception as e:
            print(f"Error importing diagram: {e}")
            return False

