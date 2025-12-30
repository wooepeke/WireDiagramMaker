"""
Wire Diagram Maker - A PyQt5 application for creating wire diagrams
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QToolBar, QStatusBar, QMessageBox, QAction, QMenu
)
from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QIcon, QColor, QPainter, QPen, QBrush
from diagram_canvas import DiagramCanvas
from file_handler import DiagramFileHandler
from properties_panel import PropertiesPanel


class WireDiagramMaker(QMainWindow):
    """Main application window for the Wire Diagram Maker"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wire Diagram Maker")
        self.setGeometry(100, 100, 1200, 800)

        # Create the main canvas
        self.canvas = DiagramCanvas()

        # Connect canvas signals
        self.canvas.tool_deactivated.connect(self.on_tool_deactivated)
        self.canvas.selection_changed.connect(self.update_properties_panel)

        # Create file handler
        self.file_handler = DiagramFileHandler(self)
        self.diagram_modified = False

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
        self.properties_panel.connection_color_changed.connect(
            self.on_connection_color_changed
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

    def on_node_color_changed(self, color):
        """Handle node color change from properties panel"""
        self.canvas.set_selected_nodes_color(color)

    def on_connection_color_changed(self, color):
        """Handle connection color change from properties panel"""
        self.canvas.set_selected_connections_color(color)

    def update_properties_panel(self):
        """Update properties panel with current selection"""
        self.properties_panel.set_selected_elements(
            self.canvas.selected_nodes,
            self.canvas.selected_connections
        )

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
        if self.canvas.selected_nodes or self.canvas.selected_connections:
            self.canvas.delete_selected()
            self.statusBar().showMessage("Selected elements deleted")
        else:
            self.statusBar().showMessage("No elements selected")

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
        self.statusBar().showMessage("Undo - coming soon")

    def on_redo(self):
        """Redo the last undone action"""
        self.statusBar().showMessage("Redo - coming soon")

    def on_select_all(self):
        """Select all elements"""
        self.statusBar().showMessage("Select All - coming soon")

    def on_preferences(self):
        """Open preferences dialog"""
        self.statusBar().showMessage("Preferences - coming soon")

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


def main():
    """Entry point for the application"""
    app = QApplication(sys.argv)
    window = WireDiagramMaker()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
