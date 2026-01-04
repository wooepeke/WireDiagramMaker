"""
Wire Diagram Maker - A PyQt5 application for creating wire diagrams
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QToolBar, QStatusBar, QMessageBox, QAction, QMenu,
    QInputDialog, QListWidget, QListWidgetItem, QDialog, QLabel, QFileDialog
)
from PyQt5.QtCore import Qt, QPoint, QSize, QRect
from PyQt5.QtGui import QIcon, QColor, QPainter, QPen, QBrush
from diagram_canvas import DiagramCanvas
from file_handler import DiagramFileHandler
from module_handler import ModuleHandler
from module_dialog import ModuleCreationDialog
from preferences_dialog import PreferencesDialog
from diagram_elements import Module, Node
from properties_panel import PropertiesPanel


class WireDiagramMaker(QMainWindow):
    """Main application window for the Wire Diagram Maker"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wire Diagram Maker")
        
        # Get screen geometry and set window to screen size
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)

        # Create the main canvas
        self.canvas = DiagramCanvas()

        # Connect canvas signals
        self.canvas.tool_deactivated.connect(self.on_tool_deactivated)
        self.canvas.selection_changed.connect(self.update_properties_panel)
        self.canvas.mode_changed.connect(self.on_canvas_mode_changed)
        self.canvas.diagram_modified.connect(self.on_diagram_modified)

        # Create file handler
        self.file_handler = DiagramFileHandler(self)
        self.diagram_modified = False

        # Create module handler
        self.module_handler = ModuleHandler()

        # Store tool buttons for styling
        self.tool_buttons = {}
        self.active_tool = None

        # Create menu bar first
        self.create_menu_bar()

        # Create toolbars
        self.create_toolbars()

        # Create central widget with canvas and properties panel
        central_widget = QWidget()
        central_layout = QHBoxLayout()
        
        # Add canvas
        central_layout.addWidget(self.canvas, stretch=1)
        
        # Add properties panel
        self.properties_panel = PropertiesPanel()
        self.properties_panel.node_color_changed.connect(
            self.on_node_color_changed
        )
        self.properties_panel.node_class_changed.connect(
            self.on_node_class_changed
        )
        self.properties_panel.connection_color_changed.connect(
            self.on_connection_color_changed
        )
        self.properties_panel.image_rotated.connect(
            self.on_image_rotated
        )
        self.properties_panel.module_rotated_cw.connect(
            self.on_module_rotated_cw
        )
        self.properties_panel.module_rotated_ccw.connect(
            self.on_module_rotated_ccw
        )
        central_layout.addWidget(self.properties_panel, stretch=0)

        # Set the central widget
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        # Create status bar
        self.statusBar().showMessage("Ready")

        # Show the window
        self.show()

        # Update window title with current file
        self.update_title()

    def create_menu_bar(self):
        """Create and configure the menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.on_new_diagram)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.on_open)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.on_save)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.on_save_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.on_undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.on_redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        select_all_action = QAction("Select All", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.on_select_all)
        edit_menu.addAction(select_all_action)

        delete_action = QAction("Delete", self)
        delete_action.setShortcut("Delete")
        delete_action.triggered.connect(self.on_delete)
        edit_menu.addAction(delete_action)

        edit_menu.addSeparator()

        clear_action = QAction("Clear All", self)
        clear_action.triggered.connect(self.on_clear)
        edit_menu.addAction(clear_action)

        edit_menu.addSeparator()

        add_image_action = QAction("Add Image", self)
        add_image_action.triggered.connect(self.on_add_image)
        edit_menu.addAction(add_image_action)

        edit_menu.addSeparator()

        create_module_action = QAction("Create Module", self)
        create_module_action.triggered.connect(self.on_create_module)
        edit_menu.addAction(create_module_action)

        load_module_action = QAction("Load Module", self)
        load_module_action.triggered.connect(self.on_load_module)
        edit_menu.addAction(load_module_action)

        # View menu
        view_menu = menubar.addMenu("View")

        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.on_zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.on_zoom_out)
        view_menu.addAction(zoom_out_action)

        reset_zoom_action = QAction("Reset Zoom", self)
        reset_zoom_action.setShortcut("Ctrl+0")
        reset_zoom_action.triggered.connect(self.on_reset_zoom)
        view_menu.addAction(reset_zoom_action)

        view_menu.addSeparator()

        self.grid_action = QAction("Show Grid", self)
        self.grid_action.setCheckable(True)
        self.grid_action.setChecked(True)
        self.grid_action.triggered.connect(self.on_toggle_grid)
        view_menu.addAction(self.grid_action)

        self.snap_to_grid_action = QAction("Snap to Grid", self)
        self.snap_to_grid_action.setCheckable(True)
        self.snap_to_grid_action.setChecked(False)
        self.snap_to_grid_action.triggered.connect(self.on_toggle_snap_to_grid)
        view_menu.addAction(self.snap_to_grid_action)

        # Settings menu
        settings_menu = menubar.addMenu("Settings")

        preferences_action = QAction("Preferences", self)
        preferences_action.triggered.connect(self.on_preferences)
        settings_menu.addAction(preferences_action)

        settings_menu.addSeparator()

        about_action = QAction("About", self)
        about_action.triggered.connect(self.on_about)
        settings_menu.addAction(about_action)

    def create_toolbars(self):
        """Create and configure the toolbars"""
        # Main tools toolbar
        tools_toolbar = self.addToolBar("Tools")
        tools_toolbar.setMovable(False)
        tools_toolbar.setObjectName("ToolsToolbar")

        # Selection tool (cursor)
        select_btn = QPushButton("◀ Select")
        select_btn.clicked.connect(self.on_select_mode)
        select_btn.setCheckable(True)
        self.tool_buttons["select"] = select_btn
        tools_toolbar.addWidget(select_btn)

        tools_toolbar.addSeparator()

        # Add node button
        add_node_btn = QPushButton("● Add Node")
        add_node_btn.clicked.connect(self.on_add_node_toggled)
        add_node_btn.setCheckable(True)
        self.tool_buttons["add_node"] = add_node_btn
        tools_toolbar.addWidget(add_node_btn)

        # Add connection button
        add_conn_btn = QPushButton("┐ Add Connection")
        add_conn_btn.clicked.connect(self.on_add_connection_toggled)
        add_conn_btn.setCheckable(True)
        self.tool_buttons["add_connection"] = add_conn_btn
        tools_toolbar.addWidget(add_conn_btn)

        tools_toolbar.addSeparator()

        # Delete tool
        delete_btn = QPushButton("🗑 Delete")
        delete_btn.clicked.connect(self.on_delete)
        tools_toolbar.addWidget(delete_btn)

        tools_toolbar.addSeparator()

        # Zoom controls toolbar
        zoom_toolbar = self.addToolBar("Zoom")
        zoom_toolbar.setMovable(False)
        zoom_toolbar.setObjectName("ZoomToolbar")

        zoom_in_btn = QPushButton("Zoom In")
        zoom_in_btn.clicked.connect(self.on_zoom_in)
        zoom_toolbar.addWidget(zoom_in_btn)

        zoom_out_btn = QPushButton("Zoom Out")
        zoom_out_btn.clicked.connect(self.on_zoom_out)
        zoom_toolbar.addWidget(zoom_out_btn)

        reset_zoom_btn = QPushButton("Reset Zoom")
        reset_zoom_btn.clicked.connect(self.on_reset_zoom)
        zoom_toolbar.addWidget(reset_zoom_btn)

    def set_active_tool(self, tool_name):
        """Set the active tool and update button styling"""
        # Deactivate previously active tool
        if self.active_tool and self.active_tool in self.tool_buttons:
            self.tool_buttons[self.active_tool].setChecked(False)
            self.tool_buttons[self.active_tool].setStyleSheet("")
        
        # Set new active tool
        if tool_name:
            self.active_tool = tool_name
            self.tool_buttons[tool_name].setChecked(True)
            self.tool_buttons[tool_name].setStyleSheet(
                "background-color: #4CAF50; color: white; font-weight: bold;"
            )
        else:
            self.active_tool = None

    def on_tool_deactivated(self):
        """Handle tool deactivation signal from canvas"""
        self.set_active_tool(None)

    def on_diagram_modified(self):
        """Handle diagram modification signal from canvas"""
        self.diagram_modified = True
        self.update_title()

    def on_node_color_changed(self, color):
        """Handle node color change from properties panel"""
        self.canvas.set_selected_nodes_color(color)
        self.canvas.set_default_node_color(color)

    def on_node_class_changed(self, class_name):
        """Handle node class change from properties panel"""
        self.canvas.set_selected_nodes_class(class_name)
        self.canvas.set_default_node_class(class_name)

    def on_connection_color_changed(self, color):
        """Handle connection color change from properties panel"""
        self.canvas.set_selected_connections_color(color)
        self.canvas.set_default_connection_color(color)

    def on_image_rotated(self):
        """Handle image rotation from properties panel"""
        self.canvas.update()
        self.canvas.diagram_modified.emit()

    def on_module_rotated_cw(self):
        """Handle module rotation clockwise from properties panel"""
        module_id = self.properties_panel.selected_module_id
        if module_id:
            self.canvas.rotate_module(module_id, 1)  # 1 for clockwise
            self.canvas.update()
            self.canvas.diagram_modified.emit()

    def on_module_rotated_ccw(self):
        """Handle module rotation counter-clockwise from properties panel"""
        module_id = self.properties_panel.selected_module_id
        if module_id:
            self.canvas.rotate_module(module_id, -1)  # -1 for counter-clockwise
            self.canvas.update()
            self.canvas.diagram_modified.emit()

    def update_properties_panel(self):
        """Update properties panel with current selection"""
        self.properties_panel.set_selected_elements(
            self.canvas.selected_nodes,
            self.canvas.selected_connections,
            self.canvas.get_selected_images()
        )

    def on_canvas_mode_changed(self, mode):
        """Handle canvas mode changes"""
        self.properties_panel.on_mode_changed(mode)

    def on_select_mode(self):
        """Toggle selection mode"""
        if self.active_tool == "select":
            # Deactivate selection mode
            self.canvas.set_mode(None)
            self.set_active_tool(None)
            self.statusBar().showMessage("Selection mode deactivated")
        else:
            # Activate selection mode
            self.canvas.set_mode("select")
            self.set_active_tool("select")
            self.statusBar().showMessage("Selection mode activated")

    def on_add_node(self):
        """Handle add node action"""
        self.canvas.set_mode("add_node")
        self.statusBar().showMessage("Click on the canvas to add a node")

    def on_add_node_toggled(self):
        """Toggle add node mode"""
        if self.active_tool == "add_node":
            # Deactivate add node mode
            self.canvas.set_mode(None)
            self.set_active_tool(None)
            self.statusBar().showMessage("Add node mode deactivated")
        else:
            # Activate add node mode
            self.canvas.set_mode("add_node")
            self.set_active_tool("add_node")
            self.statusBar().showMessage("Click on the canvas to add a node")

    def on_add_connection(self):
        """Handle add connection action"""
        self.canvas.set_mode("add_connection")
        self.statusBar().showMessage("Click two nodes to create a connection")

    def on_add_connection_toggled(self):
        """Toggle add connection mode"""
        if self.active_tool == "add_connection":
            # Deactivate add connection mode
            self.canvas.set_mode(None)
            self.set_active_tool(None)
            self.statusBar().showMessage("Add connection mode deactivated")
        else:
            # Activate add connection mode
            self.canvas.set_mode("add_connection")
            self.set_active_tool("add_connection")
            self.statusBar().showMessage("Click two nodes to create a connection")

    def on_delete(self):
        """Delete selected elements"""
        if self.canvas.selected_nodes or self.canvas.selected_connections or self.canvas.images:
            self.canvas.delete_selected()
            self.statusBar().showMessage("Selected elements deleted")
        else:
            self.statusBar().showMessage("No elements selected")

    def on_add_image(self):
        """Open file dialog to add an image"""
        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image File",
            "./Images",
            "PNG Files (*.png);;All Image Files (*.svg *.png);;SVG Files (*.svg);;All Files (*)"
        )
        
        if file_path:
            # Set canvas to image placement mode with default dimensions (100x100)
            self.canvas.set_image_placement_mode(file_path, 100, 100)
            self.statusBar().showMessage("Click on canvas to place image")

    def on_clear(self):
        """Clear all diagram elements"""
        reply = QMessageBox.question(
            self,
            "Clear Diagram",
            "Are you sure you want to clear the entire diagram?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.canvas.clear()
            self.statusBar().showMessage("Diagram cleared")

    def on_zoom_in(self):
        """Zoom in"""
        self.canvas.zoom_in()
        self.statusBar().showMessage(f"Zoom: {self.canvas.zoom_level * 100:.0f}%")

    def on_zoom_out(self):
        """Zoom out"""
        self.canvas.zoom_out()
        self.statusBar().showMessage(f"Zoom: {self.canvas.zoom_level * 100:.0f}%")

    def on_reset_zoom(self):
        """Reset zoom to default"""
        self.canvas.reset_zoom()
        self.statusBar().showMessage("Zoom: 100%")

    def on_toggle_grid(self, checked):
        """Toggle grid visibility"""
        self.canvas.set_show_grid(checked)
        self.statusBar().showMessage(f"Grid {'enabled' if checked else 'disabled'}")

    def on_toggle_snap_to_grid(self, checked):
        """Toggle snap to grid"""
        self.canvas.set_snap_to_grid(checked)
        self.statusBar().showMessage(f"Snap to grid {'enabled' if checked else 'disabled'}")

    def on_new_diagram(self):
        """Create a new diagram"""
        if self.diagram_modified:
            reply = QMessageBox.question(
                self,
                "New Diagram",
                "Do you want to save the current diagram before creating a new one?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.on_save()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        self.canvas.clear()
        self.file_handler.current_file = None
        self.diagram_modified = False
        self.update_title()
        self.statusBar().showMessage("New diagram created")

    def on_open(self):
        """Open a diagram file"""
        file_path = self.file_handler.open_file()
        if file_path:
            success, result = self.file_handler.load_diagram(file_path)
            if success:
                if self.canvas.import_diagram(result):
                    self.statusBar().showMessage(f"Opened {self.file_handler.get_current_filename()}")
                    self.diagram_modified = False
                    self.update_title()
                else:
                    QMessageBox.critical(self, "Error", "Failed to import diagram")
            else:
                QMessageBox.critical(self, "Error", result)

    def on_save(self):
        """Save the diagram"""
        if self.file_handler.current_file:
            self.save_to_file(self.file_handler.current_file)
        else:
            self.on_save_as()

    def on_save_as(self):
        """Save the diagram as a new file"""
        file_path = self.file_handler.save_file_dialog()
        if file_path:
            self.save_to_file(file_path)

    def save_to_file(self, file_path):
        """Save diagram to a specific file"""
        diagram_data = self.canvas.export_diagram()
        success, message = self.file_handler.save_diagram(file_path, diagram_data)
        if success:
            self.statusBar().showMessage(message)
            self.diagram_modified = False
            self.update_title()
        else:
            QMessageBox.critical(self, "Error", message)

    def update_title(self):
        """Update window title with current filename"""
        filename = self.file_handler.get_current_filename()
        modified = " *" if self.diagram_modified else ""
        self.setWindowTitle(f"Wire Diagram Maker - {filename}{modified}")

    def on_undo(self):
        """Undo the last action"""
        if self.canvas.can_undo():
            self.canvas.undo()
            self.statusBar().showMessage(f"Undone: {self.canvas.get_undo_description()}")
        else:
            self.statusBar().showMessage("Nothing to undo")

    def on_redo(self):
        """Redo the last undone action"""
        if self.canvas.can_redo():
            self.canvas.redo()
            self.statusBar().showMessage(f"Redone: {self.canvas.get_redo_description()}")
        else:
            self.statusBar().showMessage("Nothing to redo")

    def on_select_all(self):
        """Select all elements"""
        self.statusBar().showMessage("Select All - coming soon")

    def on_preferences(self):
        """Open preferences dialog"""
        preferences_dialog = PreferencesDialog(self)
        preferences_dialog.preferences_saved.connect(self.on_preferences_saved)
        preferences_dialog.exec_()
    
    def on_preferences_saved(self):
        """Handle preferences saved signal - refresh UI"""
        # Refresh all nodes from updated config
        for node in self.canvas.nodes:
            node.refresh_from_config()
        
        # Refresh canvas
        self.canvas.update()
        self.statusBar().showMessage("Preferences saved and reloaded successfully")

    def on_about(self):
        """Show about dialog"""
        QMessageBox.information(
            self,
            "About Wire Diagram Maker",
            "Wire Diagram Maker v1.0\n\n"
            "A PyQt5 application for creating wire diagrams.\n\n"
            "Features:\n"
            "- Add nodes to the canvas\n"
            "- Connect nodes with wires\n"
            "- Drag nodes to reposition\n"
            "- Save and load diagrams\n"
            "- Zoom and pan controls",
        )

    def on_create_module(self):
        """Create a module from selected nodes"""
        # Get selected nodes
        selected_nodes = [node for node in self.canvas.nodes if node.selected]
        
        if not selected_nodes:
            QMessageBox.warning(self, "No Selection", "Please select at least one node to create a module.")
            return
        
        # Open the module creation dialog
        dialog = ModuleCreationDialog(self.canvas, self.module_handler, self)
        dialog.module_created.connect(self.on_module_created)
        dialog.exec_()

    def on_module_created(self, module):
        """Handle successful module creation"""
        self.statusBar().showMessage(f"Module '{module.name}' created successfully!")
        self.canvas.clear_selection()
        self.canvas.update()

    def on_load_module(self):
        """Load a module onto the canvas"""
        # Get available modules
        available_modules = self.module_handler.get_available_modules()
        
        if not available_modules:
            QMessageBox.information(self, "No Modules", "No modules available. Create one first!")
            return
        
        # Create a dialog to select module
        dialog = QDialog(self)
        dialog.setWindowTitle("Load Module")
        dialog.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Select a module to load:"))
        
        module_list = QListWidget()
        for module_info in available_modules:
            item = QListWidgetItem(module_info["name"])
            item.setData(Qt.UserRole, module_info["id"])
            module_list.addItem(item)
        
        layout.addWidget(module_list)
        
        # Add buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("Load")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        def load_selected():
            selected_items = module_list.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "No Selection", "Please select a module.")
                return
            
            module_id = selected_items[0].data(Qt.UserRole)
            module = self.module_handler.load_module(module_id)
            
            if module:
                # Count how many instances of this module already exist
                # Look for nodes with module_id pattern: "original_id_inst_1", "original_id_inst_2", etc.
                existing_instances = len([n for n in self.canvas.nodes if hasattr(n, 'module_id') and n.module_id.startswith(f"{module_id}_inst_")])
                
                # Create a UNIQUE instance ID for this loaded instance
                instance_number = existing_instances + 1
                unique_instance_id = f"{module_id}_inst_{instance_number}"
                
                # Calculate offset for this instance
                node_offset = 50
                offset_x = existing_instances * node_offset
                offset_y = existing_instances * node_offset
                
                # Add module nodes to canvas - create completely independent copies
                for node in module.nodes:
                    # Create a completely new, independent node object
                    new_node = Node(
                        f"{node.name}_inst{instance_number}",  # Make node names unique per instance
                        QPoint(
                            int(node.pos.x() + offset_x),
                            int(node.pos.y() + offset_y)
                        )
                    )
                    # Copy all properties
                    new_node.node_class = node.node_class
                    new_node.color = QColor(node.color.red(), node.color.green(), node.color.blue())
                    new_node.module_id = unique_instance_id  # Each instance gets a unique ID!
                    new_node.locked = True
                    self.canvas.nodes.append(new_node)
                
                # Add module images to canvas - create completely independent copies
                for image in module.images:
                    from diagram_elements import Image
                    # Create a completely new, independent image object
                    new_image = Image(
                        image.image_path,
                        QPoint(
                            int(image.pos.x() + offset_x),
                            int(image.pos.y() + offset_y)
                        ),
                        image.width,
                        image.height
                    )
                    # Tag the image with the module instance ID so it moves with the module
                    new_image.module_instance_id = unique_instance_id
                    self.canvas.images.append(new_image)
                
                self.canvas.update()
                self.statusBar().showMessage(f"Module '{module.name}' (instance {instance_number}) loaded successfully!")
                dialog.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to load module.")
        
        ok_button.clicked.connect(load_selected)
        cancel_button.clicked.connect(dialog.reject)
        
        dialog.exec_()

    def closeEvent(self, event):
        """Handle close event - ask to save if there are unsaved changes"""
        if self.diagram_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before closing?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.on_save()
                event.accept()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
            else:
                # No - discard changes and close
                event.accept()
        else:
            # No unsaved changes, close normally
            event.accept()


def main():
    """Entry point for the application"""
    app = QApplication(sys.argv)
    window = WireDiagramMaker()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
