"""
Canvas widget for drawing wire diagrams
"""

from PyQt5.QtWidgets import QWidget, QMenu
from PyQt5.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont
from diagram_elements import Node, Connection
from properties_dialog import NodePropertiesDialog
from config_loader import get_config


class DiagramCanvas(QWidget):
    """Canvas for drawing and managing diagram elements"""

    # Signals
    tool_deactivated = pyqtSignal()  # Emitted when a tool action is completed
    selection_changed = pyqtSignal()  # Emitted when selection changes
    mode_changed = pyqtSignal(str)  # Emitted when operation mode changes

    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setStyleSheet("background-color: white;")

        # Load configuration
        config = get_config()

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
        self.show_grid = config.get_grid_enabled_by_default()
        self.grid_size = config.get_grid_size()
        self.snap_to_grid = config.is_snap_to_grid_enabled_by_default()

        # Pan/zoom settings
        self.pan_offset = QPoint(0, 0)
        self.panning = False
        self.pan_start = QPoint()
        self.zoom_level = 1.0
        self.min_zoom = config.get_zoom_min()
        self.max_zoom = config.get_zoom_max()
        self.zoom_increment = config.get_zoom_increment()

        # Selection settings
        self.selected_nodes = []
        self.selected_connections = []

        # Default colors for new elements
        default_node_color = config.get_node_default_color()
        self.default_node_color = QColor(*default_node_color)
        
        default_connection_color = config.get_connection_default_color()
        self.default_connection_color = QColor(*default_connection_color)

    def set_mode(self, mode):
        """Set the current operation mode"""
        self.mode = mode
        self.selected_node = None
        self.setCursor(Qt.CursorShape.CrossCursor if mode in ["add_node", "add_connection"] else Qt.CursorShape.ArrowCursor)
        self.mode_changed.emit(mode)

    def set_show_grid(self, show):
        """Set whether to show grid"""
        self.show_grid = show
        self.update()

    def set_snap_to_grid(self, snap):
        """Set whether to snap to grid"""
        self.snap_to_grid = snap

    def snap_to_grid_point(self, pos):
        """Snap a position to the nearest grid point"""
        if not self.snap_to_grid:
            return pos
        # Get x and y coordinates as floats
        x = pos.x() if isinstance(pos, QPoint) else pos[0]
        y = pos.y() if isinstance(pos, QPoint) else pos[1]
        # Round to nearest grid point
        snapped_x = round(x / self.grid_size) * self.grid_size
        snapped_y = round(y / self.grid_size) * self.grid_size
        return QPoint(int(snapped_x), int(snapped_y))

    def zoom_in(self):
        """Increase zoom level"""
        new_zoom = min(self.zoom_level * self.zoom_increment, self.max_zoom)
        self.set_zoom(new_zoom)

    def zoom_out(self):
        """Decrease zoom level"""
        new_zoom = max(self.zoom_level / self.zoom_increment, self.min_zoom)
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
            # Snap to grid if enabled
            new_pos = self.snap_to_grid_point(new_pos)
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
        snapped_pos = self.snap_to_grid_point(pos)
        node = Node(f"Node{self.node_counter}", snapped_pos)
        node.color = self.default_node_color
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
        connection.color = self.default_connection_color
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

    def set_selected_nodes_class(self, class_name):
        """Set class for all selected nodes"""
        config = get_config()
        for node in self.selected_nodes:
            node.node_class = class_name
            # Update color based on class
            color_tuple = config.get_node_class_color(class_name)
            node.color = QColor(*color_tuple)
        self.update()

    def set_selected_connections_color(self, color):
        """Set color for all selected connections"""
        for connection in self.selected_connections:
            connection.color = color
        self.update()

    def set_default_node_color(self, color):
        """Set the default color for new nodes"""
        self.default_node_color = color

    def set_default_connection_color(self, color):
        """Set the default color for new connections"""
        self.default_connection_color = color

    def paintEvent(self, event):
        """Paint the canvas and all diagram elements"""
        config = get_config()
        painter = QPainter(self)
        
        if config.is_antialiasing_enabled():
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
        """Draw an infinite grid on the canvas in canvas coordinates"""
        config = get_config()
        grid_color = config.get_grid_color()
        painter.setPen(QPen(QColor(*grid_color), 1))
        
        # Get visible area in canvas coordinates
        # The painter has already been translated and scaled, so we work in canvas space
        top_left_screen = QPoint(0, 0)
        bottom_right_screen = QPoint(self.width(), self.height())
        
        # Convert to canvas coordinates (accounting for pan and zoom)
        top_left_canvas = self.screen_to_canvas(top_left_screen)
        bottom_right_canvas = self.screen_to_canvas(bottom_right_screen)
        
        # Find grid boundaries
        min_x = int(top_left_canvas.x() / self.grid_size) * self.grid_size
        max_x = int(bottom_right_canvas.x() / self.grid_size) * self.grid_size + self.grid_size
        min_y = int(top_left_canvas.y() / self.grid_size) * self.grid_size
        max_y = int(bottom_right_canvas.y() / self.grid_size) * self.grid_size + self.grid_size
        
        # Draw vertical lines in canvas coordinates
        x = min_x
        while x <= max_x:
            painter.drawLine(x, int(min_y), x, int(max_y))
            x += self.grid_size
        
        # Draw horizontal lines in canvas coordinates
        y = min_y
        while y <= max_y:
            painter.drawLine(int(min_x), y, int(max_x), y)
            y += self.grid_size

    def export_diagram(self):
        """Export the diagram as a dictionary for saving"""
        diagram_data = {
            "nodes": [],
            "connections": [],
            "metadata": {
                "grid_enabled": self.show_grid,
                "grid_size": self.grid_size,
                "snap_to_grid": self.snap_to_grid,
                "zoom_level": self.zoom_level,
                "pan_offset": {
                    "x": self.pan_offset.x(),
                    "y": self.pan_offset.y()
                }
            }
        }

        # Export nodes
        for node in self.nodes:
            diagram_data["nodes"].append({
                "name": node.name,
                "x": node.pos.x(),
                "y": node.pos.y(),
                "class": node.node_class,
                "color": {
                    "r": node.color.red(),
                    "g": node.color.green(),
                    "b": node.color.blue()
                }
            })

        # Export connections
        for connection in self.connections:
            # Find the indices of the connected nodes
            node1_idx = self.nodes.index(connection.node1)
            node2_idx = self.nodes.index(connection.node2)
            diagram_data["connections"].append({
                "node1": node1_idx,
                "node2": node2_idx,
                "color": {
                    "r": connection.color.red(),
                    "g": connection.color.green(),
                    "b": connection.color.blue()
                }
            })

        return diagram_data

    def import_diagram(self, data):
        """Import a diagram from a dictionary"""
        try:
            self.clear()

            # Import metadata (grid, zoom, pan settings)
            metadata = data.get("metadata", {})
            self.show_grid = metadata.get("grid_enabled", True)
            self.grid_size = metadata.get("grid_size", 10)
            self.snap_to_grid = metadata.get("snap_to_grid", False)
            self.zoom_level = metadata.get("zoom_level", 1.0)
            
            pan_data = metadata.get("pan_offset", {"x": 0, "y": 0})
            self.pan_offset = QPoint(pan_data.get("x", 0), pan_data.get("y", 0))

            # Import nodes
            node_map = {}
            for node_data in data.get("nodes", []):
                node = Node(
                    node_data["name"],
                    QPoint(int(node_data["x"]), int(node_data["y"]))
                )
                
                # Restore class if available
                if "class" in node_data:
                    node.node_class = node_data["class"]
                
                # Restore color if available in the saved data
                if "color" in node_data:
                    node.color = QColor(
                        node_data["color"]["r"],
                        node_data["color"]["g"],
                        node_data["color"]["b"]
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
                    
                    # Restore color if available in the saved data
                    if "color" in conn_data:
                        connection.color = QColor(
                            conn_data["color"]["r"],
                            conn_data["color"]["g"],
                            conn_data["color"]["b"]
                        )
                    
                    self.connections.append(connection)

            self.update()
            return True
        except Exception as e:
            print(f"Error importing diagram: {e}")
            return False

