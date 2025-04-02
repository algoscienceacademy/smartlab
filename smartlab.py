import sys
import math
import numpy as np
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QToolBar, QLabel, QListWidget,
                             QGraphicsScene, QGraphicsView, QMenuBar, QMenu,
                             QGraphicsItem, QGraphicsLineItem, QGraphicsRectItem,
                             QStatusBar, QGraphicsTextItem, QFrame, QGraphicsEllipseItem,
                             QGraphicsDropShadowEffect, QDialog, QFormLayout,
                             QLineEdit, QDoubleSpinBox, QComboBox, QPushButton,
                             QCheckBox, QGraphicsPathItem, QGraphicsProxyWidget,
                             QTabWidget, QSlider, QTextEdit)  # Added QSlider and QTextEdit here
from PySide6.QtCore import Qt, QPointF, QRectF, QMimeData, Signal, QPoint, QSize
from PySide6.QtGui import (QPainter, QPen, QColor, QAction, QDrag, QPainterPath, 
                          QFont, QPixmap, QBrush, QLinearGradient)
# Add matplotlib for visualization
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import time
import threading
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
import colorsys

# Professional component symbols and colors
class Component:
    def __init__(self, name, symbol, pins=2):
        self.name = name
        self.symbol = symbol
        self.pins = pins
        self.properties = self._get_default_properties()
        
    def _get_default_properties(self):
        """Set default properties based on component type"""
        if self.name == "Resistor":
            return {"Resistance (Ω)": "1000", "Power (W)": "0.25", "Tolerance (%)": "5"}
        elif self.name == "Capacitor":
            return {"Capacitance (F)": "0.000001", "Voltage Rating (V)": "25", "Type": "Ceramic"}
        elif self.name == "Inductor":
            return {"Inductance (H)": "0.001", "Current Rating (A)": "1.0"}
        elif self.name == "Battery":
            return {"Voltage (V)": "9.0", "Type": "DC"}
        elif self.name == "LED":
            return {"Forward Voltage (V)": "2.0", "Current (mA)": "20", "Color": "Red"}
        elif self.name == "Transistor":
            return {"Type": "NPN", "Gain (hFE)": "100", "Vce max (V)": "40"}
        elif self.name == "Diode":
            return {"Forward Voltage (V)": "0.7", "Current (mA)": "100"}
        elif self.name == "Switch":
            return {"Type": "SPST", "Current Rating (A)": "1.0"}
        elif self.name == "Potentiometer":
            return {"Resistance (Ω)": "10000", "Power (W)": "0.5"}
        elif self.name == "IC":
            return {"Type": "Op-Amp", "Supply Voltage (V)": "±15"}
        else:
            return {}

# Fix for the missing attributes in ComponentItem class
class ComponentItem(QGraphicsItem):
    def __init__(self, component, parent=None):
        super().__init__(parent)
        self.component = component
        # Create a deep copy of the component for individual properties
        if isinstance(component, Component):
            # Create a new Component instance with the same attributes
            self.component = Component(
                component.name,
                component.symbol,
                component.pins
            )
            # Deep copy the properties dictionary to ensure independence
            self.component.properties = component.properties.copy()
        
        # Fix: Add the missing attributes
        self.hovered = False  # Add missing hovered attribute
        self.pen_width = 2    # Add missing pen_width attribute
        self.bg_color = QColor(240, 240, 240)  # Add background color
        self.rotation_angle = 0  # Initialize rotation angle
        
        # Initialize pin points - this was missing
        self.pin_points = []
        self._generate_pin_points()  # Generate the pin points on initialization
        
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)  # Enable hover events

    def _generate_pin_points(self):
        # Generate pin connection points based on component type
        self.pin_points = []
        if self.component.pins == 2:  # Standard 2-pin components
            self.pin_points = [QPointF(-25, 0), QPointF(25, 0)]
        elif self.component.pins == 3:  # Transistors, etc.
            self.pin_points = [QPointF(-25, 0), QPointF(25, -15), QPointF(25, 15)]
        elif self.component.pins == 4:  # ICs, etc.
            self.pin_points = [QPointF(-25, -15), QPointF(-25, 15), 
                              QPointF(25, -15), QPointF(25, 15)]

    def boundingRect(self):
        return QRectF(-30, -25, 60, 50)

    def paint(self, painter, option, widget):
        # Draw component with professional appearance
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background fill
        if self.isSelected():
            background = QLinearGradient(0, -25, 0, 25)
            background.setColorAt(0, QColor(200, 230, 250))
            background.setColorAt(1, QColor(150, 200, 240))
            painter.setBrush(QBrush(background))
            pen = QPen(QColor(50, 100, 220), self.pen_width)
        elif self.hovered:
            painter.setBrush(QBrush(QColor(245, 245, 220)))
            pen = QPen(QColor(100, 100, 100), self.pen_width)
        else:
            painter.setBrush(QBrush(self.bg_color))
            pen = QPen(QColor(0, 0, 0), self.pen_width)
        
        painter.setPen(pen)
        painter.drawRoundedRect(-25, -20, 50, 40, 5, 5)
        
        # Draw component symbol
        font = QFont()
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRectF(-20, -15, 40, 30), Qt.AlignCenter, self.component.symbol)
        
        # Draw pin connection points
        painter.setPen(QPen(QColor(200, 0, 0), 1.5))
        for pin in self.pin_points:
            painter.drawEllipse(pin, 3, 3)

    def hoverEnterEvent(self, event):
        self.hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.hovered = False
        self.update()
        super().hoverLeaveEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            # Snap to grid (grid size 10x10)
            grid_size = 10
            x = round(value.x() / grid_size) * grid_size
            y = round(value.y() / grid_size) * grid_size
            return QPointF(x, y)
        return super().itemChange(change, value)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.showPropertyEditor()
        else:
            super().mousePressEvent(event)
    
    def showPropertyEditor(self):
        """Show the property editor dialog for this component"""
        dialog = PropertyEditorDialog(self.component)
        if dialog.exec():
            self.update()  # Redraw the component if properties changed

    def setMovable(self, movable):
        """Enable or disable movement of the component"""
        if movable:
            self.setFlag(QGraphicsItem.ItemIsMovable, True)
        else:
            self.setFlag(QGraphicsItem.ItemIsMovable, False)

class PropertyEditorDialog(QDialog):
    def __init__(self, component, parent=None):
        super().__init__(parent)
        self.component = component
        self.setWindowTitle(f"Edit {component.name} Properties")
        self.setMinimumWidth(300)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Form layout for properties
        form_layout = QFormLayout()
        
        # Create editors for each property
        self.editors = {}
        for key, value in component.properties.items():
            if "Resistance" in key or "Voltage" in key or "Current" in key or "Power" in key:
                editor = QDoubleSpinBox()
                editor.setRange(0, 1000000)
                editor.setValue(float(value))
                editor.setDecimals(6)  # Allow for small values like capacitance
                editor.setSuffix(f" {key.split('(')[1].split(')')[0]}")
            elif "Type" in key or "Color" in key:
                editor = QComboBox()
                if "Type" in key and "Transistor" in component.name:
                    editor.addItems(["NPN", "PNP", "MOSFET-N", "MOSFET-P"])
                elif "Type" in key and "Capacitor" in component.name:
                    editor.addItems(["Ceramic", "Electrolytic", "Tantalum", "Film"])
                elif "Type" in key and "Switch" in component.name:
                    editor.addItems(["SPST", "SPDT", "DPST", "DPDT"])
                elif "Color" in key:
                    editor.addItems(["Red", "Green", "Blue", "Yellow", "White", "RGB"])
                elif "Type" in key and "IC" in component.name:
                    editor.addItems(["Op-Amp", "Microcontroller", "Logic Gate", "Timer"])
                elif "Type" in key:
                    editor.addItems(["DC", "AC"])
                
                current_index = editor.findText(value)
                if current_index >= 0:
                    editor.setCurrentIndex(current_index)
            else:
                editor = QLineEdit(value)
            
            form_layout.addRow(key, editor)
            self.editors[key] = editor
        
        layout.addLayout(form_layout)
        
        # Add buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        # Connect accept signal
        self.accepted.connect(self.update_properties)
    
    def update_properties(self):
        """Update component properties from editors"""
        for key, editor in self.editors.items():
            if isinstance(editor, QDoubleSpinBox):
                self.component.properties[key] = str(editor.value())
            elif isinstance(editor, QComboBox):
                self.component.properties[key] = editor.currentText()
            else:
                self.component.properties[key] = editor.text()

class SmartWire(QGraphicsPathItem):
    def __init__(self, x1, y1, x2, y2, parent=None):
        super().__init__(parent)
        self.start_pos = QPointF(x1, y1)
        self.end_pos = QPointF(x2, y2)
        self.start_component = None  # Add these to track connected components
        self.end_component = None
        self.start_pin_index = -1
        self.end_pin_index = -1
        
        # Make wire more visible
        self.setPen(QPen(QColor(0, 0, 0), 4.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.setZValue(-1)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)
        
        self.recalculate_path()

    def hoverEnterEvent(self, event):
        # Highlight wire on hover
        self.setPen(QPen(QColor(0, 100, 255), 4.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        # Reset wire appearance
        self.setPen(QPen(QColor(0, 0, 0), 4.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        super().hoverLeaveEvent(event)

    def recalculate_path(self):
        """Calculate the smart path for the wire with Manhattan routing"""
        # Create a path with horizontal and vertical segments
        path = QPainterPath()
        path.moveTo(self.start_pos)
        
        # Decide if we should go horizontal first or vertical first
        dx = self.end_pos.x() - self.start_pos.x()
        dy = self.end_pos.y() - self.start_pos.y()
        
        if abs(dx) > abs(dy):
            # Go horizontal first
            midpoint_x = self.start_pos.x() + dx/2
            path.lineTo(midpoint_x, self.start_pos.y())
            path.lineTo(midpoint_x, self.end_pos.y())
        else:
            # Go vertical first
            midpoint_y = self.start_pos.y() + dy/2
            path.lineTo(self.start_pos.x(), midpoint_y)
            path.lineTo(self.end_pos.x(), midpoint_y)
        
        path.lineTo(self.end_pos)
        self.setPath(path)
    
    def update_end_point(self, x, y):
        """Update the end point of the wire and recalculate the path"""
        self.end_pos = QPointF(x, y)
        self.recalculate_path()
    
    def update_start_point(self, x, y):
        """Update the start point of the wire and recalculate the path"""
        self.start_pos = QPointF(x, y)
        self.recalculate_path()
    
    def paint(self, painter, option, widget):
        if self.isSelected():
            pen = QPen(QColor(50, 100, 220), 2.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
        else:
            painter.setPen(self.pen())
        painter.drawPath(self.path())
    
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            # Handle right-click menu through parent view
            pass
        else:
            super().mousePressEvent(event)

class CircuitSimulator:
    """Basic circuit simulator class that handles the simulation calculations"""
    def __init__(self):
        self.components = {}
        self.connections = []
        self.voltage_sources = []
        self.ground_nodes = []
        
    def add_component(self, component_id, component_type, value, connections=None):
        """Add a component to the simulation"""
        self.components[component_id] = {
            'type': component_type,
            'value': value,
            'connections': connections or []
        }
        
        # Track voltage sources for simulation
        if component_type == "Battery":
            self.voltage_sources.append(component_id)
    
    def add_connection(self, from_component, from_pin, to_component, to_pin):
        """Add a connection between components"""
        self.connections.append({
            'from': (from_component, from_pin),
            'to': (to_component, to_pin)
        })
    
    def simulate(self, duration=1.0, step=0.001):
        """Run a basic circuit simulation and return time and voltage/current data"""
        # For basic circuits, we'll use simplified simulation logic
        # A real implementation would use proper circuit analysis
        time_points = np.arange(0, duration, step)
        voltage_data = {}
        current_data = {}
        
        # Check for common circuit patterns
        if len(self.voltage_sources) == 0:
            # No voltage source, no simulation possible
            return time_points, {}, {}
        
        # Generate simulation data
        for component_id, component in self.components.items():
            # Generate voltage waveforms
            if component['type'] == "Resistor":
                resistance = float(component['value'])
                # Voltage across resistor - account for simple voltage dividers
                connected_sources = self._find_connected_sources(component_id)
                voltage = 0
                for src in connected_sources:
                    voltage += float(self.components[src]['value'])
                voltage_data[component_id] = voltage * np.ones_like(time_points)
                
                # Current through resistor (V=IR)
                current_data[component_id] = (voltage / resistance) * np.ones_like(time_points)
                
            elif component['type'] == "Capacitor":
                capacitance = float(component['value'])
                connected_sources = self._find_connected_sources(component_id)
                source_voltage = 0
                for src in connected_sources:
                    source_voltage += float(self.components[src]['value'])
                
                # Capacitor charging curve: V(t) = V_source * (1 - e^(-t/RC))
                # Find connected resistor(s)
                total_resistance = 1000  # Default
                for conn in self.connections:
                    if conn['from'][0] == component_id or conn['to'][0] == component_id:
                        other = conn['to'][0] if conn['from'][0] == component_id else conn['from'][0]
                        if self.components.get(other, {}).get('type') == "Resistor":
                            total_resistance = float(self.components[other]['value'])
                
                rc = total_resistance * capacitance
                voltage_data[component_id] = source_voltage * (1 - np.exp(-time_points/rc))
                current_data[component_id] = (source_voltage/total_resistance) * np.exp(-time_points/rc)
                
            elif component['type'] == "Inductor":
                inductance = float(component['value'])
                connected_sources = self._find_connected_sources(component_id)
                source_voltage = 0
                for src in connected_sources:
                    source_voltage += float(self.components[src]['value'])
                
                # Find connected resistor(s)
                total_resistance = 1000  # Default
                for conn in self.connections:
                    if conn['from'][0] == component_id or conn['to'][0] == component_id:
                        other = conn['to'][0] if conn['from'][0] == component_id else conn['from'][0]
                        if self.components.get(other, {}).get('type') == "Resistor":
                            total_resistance = float(self.components[other]['value'])
                
                # Inductor current: I(t) = (V/R) * (1 - e^(-Rt/L))
                voltage_data[component_id] = source_voltage * np.exp(-total_resistance*time_points/inductance)
                current_data[component_id] = (source_voltage/total_resistance) * (1 - np.exp(-total_resistance*time_points/inductance))
                
            elif component['type'] == "Battery":
                voltage = float(component['value'])
                voltage_data[component_id] = voltage * np.ones_like(time_points)
                
                # Current depends on the circuit
                # Find connected resistors
                total_resistance = float('inf')  # Default
                for conn in self.connections:
                    if conn['from'][0] == component_id or conn['to'][0] == component_id:
                        other = conn['to'][0] if conn['from'][0] == component_id else conn['from'][0]
                        if self.components.get(other, {}).get('type') == "Resistor":
                            r = float(self.components[other]['value'])
                            total_resistance = min(total_resistance, r)
                
                if total_resistance < float('inf'):
                    current_data[component_id] = (voltage / total_resistance) * np.ones_like(time_points)
                else:
                    current_data[component_id] = np.zeros_like(time_points)
                
            elif component['type'] == "LED":
                forward_voltage = float(component['value'])
                connected_sources = self._find_connected_sources(component_id)
                source_voltage = 0
                for src in connected_sources:
                    source_voltage += float(self.components[src]['value'])
                
                # LED has voltage drop when conducting
                if source_voltage > forward_voltage:
                    voltage_data[component_id] = forward_voltage * np.ones_like(time_points)
                    
                    # Find current limiting resistor
                    total_resistance = 1000  # Default
                    for conn in self.connections:
                        if conn['from'][0] == component_id or conn['to'][0] == component_id:
                            other = conn['to'][0] if conn['from'][0] == component_id else conn['from'][0]
                            if self.components.get(other, {}).get('type') == "Resistor":
                                total_resistance = float(self.components[other]['value'])
                    
                    current_data[component_id] = ((source_voltage - forward_voltage) / total_resistance) * np.ones_like(time_points)
                else:
                    voltage_data[component_id] = source_voltage * np.ones_like(time_points)
                    current_data[component_id] = np.zeros_like(time_points)
            else:
                # Default behavior for other components
                voltage_data[component_id] = np.zeros_like(time_points)
                current_data[component_id] = np.zeros_like(time_points)
        
        return time_points, voltage_data, current_data
    
    def _find_connected_sources(self, component_id):
        """Find all voltage sources connected to this component"""
        connected_sources = []
        for conn in self.connections:
            if conn['from'][0] == component_id:
                if conn['to'][0] in self.voltage_sources:
                    connected_sources.append(conn['to'][0])
            elif conn['to'][0] == component_id:
                if conn['from'][0] in self.voltage_sources:
                    connected_sources.append(conn['from'][0])
        return connected_sources

class MatplotlibCanvas(FigureCanvasQTAgg):
    """Canvas for displaying matplotlib plots in Qt"""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)

class CircuitCanvas(QGraphicsView):
    def __init__(self, main_window=None):
        super().__init__()
        # Store reference to main window
        self.main_window = main_window
        
        # Create scene
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # View settings
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        
        # Wire drawing state
        self.drawing_wire = False
        self.temp_line = None
        self.wire_start = None
        self.wire_mode = False
        
        # Grid settings
        self.grid_size = 10
        self.grid_visible = True
        
        # Setup scene
        self.scene.setSceneRect(-2000, -2000, 4000, 4000)
        self.setupGrid()
        
        # Styling
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Sunken)
        self.setStyleSheet("background-color: #FFFFFF;")
        
        # Add temporary wire as SmartWire
        self.temp_wire = None
        self.highlight_pin = None
        self.target_highlight = None

        # Add context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        self.components_movable = True
        self.wire_start_pin_index = None  # Add this new line to track which pin is being connected
        self.connections = []  # Add this to track all wire connections
        self.simulator = EnhancedCircuitSimulator()
        self.simulation_results = None
        self.target_pin_index = -1  # Initialize missing attribute
        self.simulation_probes = []  # Add this to track simulation probes
        self.animation_frame = 0  # Add this for animation
        self.animation_timer = None  # Add this for animation
        self.current_flows = {}  # Add this for animation

    def showStatusMessage(self, message):
        """Helper method to safely access status bar"""
        if self.main_window and hasattr(self.main_window, 'statusBar'):
            self.main_window.statusBar.showMessage(message)

    def setupGrid(self):
        # Create grid
        self.grid_lines = []
        for x in range(-2000, 2001, self.grid_size):
            line = self.scene.addLine(x, -2000, x, 2000, 
                                    QPen(QColor(230, 230, 230), 0.5))
            line.setZValue(-10)
            self.grid_lines.append(line)
        
        for y in range(-2000, 2001, self.grid_size):
            line = self.scene.addLine(-2000, y, 2000, y, 
                                    QPen(QColor(230, 230, 230), 0.5))
            line.setZValue(-10)
            self.grid_lines.append(line)
        
        # Add major grid lines
        for x in range(-2000, 2001, self.grid_size * 5):
            line = self.scene.addLine(x, -2000, x, 2000, 
                                    QPen(QColor(200, 200, 220), 0.8))
            line.setZValue(-9)
            self.grid_lines.append(line)
        
        for y in range(-2000, 2001, self.grid_size * 5):
            line = self.scene.addLine(-2000, y, 2000, y, 
                                    QPen(QColor(200, 200, 220), 0.8))
            line.setZValue(-9)
            self.grid_lines.append(line)

    def toggleGrid(self):
        self.grid_visible = not self.grid_visible
        for line in self.grid_lines:
            line.setVisible(self.grid_visible)

    def setComponentsMovable(self, movable):
        """Set all components movable or not movable"""
        self.components_movable = movable
        for item in self.scene.items():
            if isinstance(item, ComponentItem):
                item.setMovable(movable)

    def mousePressEvent(self, event):
        if self.wire_mode and event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.position().toPoint())
            item = self.scene.itemAt(scene_pos, self.transform())
            
            if isinstance(item, ComponentItem):
                self.setComponentsMovable(False)
                self.wire_start = item
                min_dist = float('inf')
                closest_pin = None
                pin_index = -1
                
                for idx, pin in enumerate(item.pin_points):
                    angle_rad = item.rotation() * math.pi / 180
                    rotated_pin = QPointF()
                    rotated_pin.setX(pin.x() * math.cos(angle_rad) - pin.y() * math.sin(angle_rad))
                    rotated_pin.setY(pin.x() * math.sin(angle_rad) + pin.y() * math.cos(angle_rad))
                    pin_pos = item.pos() + rotated_pin
                    
                    dist = ((pin_pos.x() - scene_pos.x())**2 + 
                           (pin_pos.y() - scene_pos.y())**2)**0.5
                    
                    if dist < min_dist and dist < 25:
                        min_dist = dist
                        closest_pin = pin_pos
                        pin_index = idx
                
                if closest_pin:
                    self.wire_start_pos = closest_pin
                    self.wire_start_pin_index = pin_index  # Store the pin index
                    self.drawing_wire = True
                    
                    self.temp_wire = SmartWire(
                        closest_pin.x(), closest_pin.y(),
                        closest_pin.x(), closest_pin.y()
                    )
                    self.scene.addItem(self.temp_wire)
                    
                    # Add visual feedback
                    self.highlight_pin = QGraphicsEllipseItem(
                        closest_pin.x() - 6, closest_pin.y() - 6, 12, 12)
                    self.highlight_pin.setBrush(QBrush(QColor(255, 140, 0, 200)))
                    self.highlight_pin.setPen(QPen(Qt.transparent))
                    self.highlight_pin.setZValue(10)
                    self.scene.addItem(self.highlight_pin)
                else:
                    self.wire_start = None
                    self.wire_start_pin_index = None
                    self.showStatusMessage("Click closer to a component pin")
            
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drawing_wire and self.temp_wire:
            scene_pos = self.mapToScene(event.position().toPoint())
            
            # Find potential target pins while moving
            found_target = False
            target_pin = None
            target_component = None
            
            # Grid snap
            x = round(scene_pos.x() / self.grid_size) * self.grid_size
            y = round(scene_pos.y() / self.grid_size) * self.grid_size
            scene_pos = QPointF(x, y)
            
            # Search all components for potential pin targets
            for item in self.scene.items():
                if isinstance(item, ComponentItem) and item != self.wire_start:
                    for pin in item.pin_points:
                        # Get the rotation-adjusted pin position
                        angle_rad = item.rotation() * math.pi / 180
                        rotated_pin = QPointF()
                        rotated_pin.setX(pin.x() * math.cos(angle_rad) - pin.y() * math.sin(angle_rad))
                        rotated_pin.setY(pin.x() * math.sin(angle_rad) + pin.y() * math.cos(angle_rad))
                        
                        pin_pos = item.pos() + rotated_pin
                        dist = ((pin_pos.x() - scene_pos.x())**2 + 
                                (pin_pos.y() - scene_pos.y())**2)**0.5
                        
                        if dist < 25:  # Increased snap range
                            scene_pos = pin_pos
                            found_target = True
                            target_pin = pin_pos
                            target_component = item
                            break
                    if found_target:
                        break
            
            # Update or create target highlight
            if hasattr(self, 'target_highlight') and self.target_highlight:
                self.scene.removeItem(self.target_highlight)
                self.target_highlight = None
                
            if found_target and target_pin and target_component != self.wire_start:
                self.target_highlight = QGraphicsEllipseItem(
                    target_pin.x() - 6, target_pin.y() - 6, 12, 12)
                self.target_highlight.setBrush(QBrush(QColor(0, 200, 0, 200)))
                self.target_highlight.setPen(QPen(Qt.transparent))
                self.target_highlight.setZValue(10)
                self.scene.addItem(self.target_highlight)
                self.showStatusMessage(f"Connect to {target_component.component.name}")
            
            # Update smart wire
            self.temp_wire.update_end_point(scene_pos.x(), scene_pos.y())
            
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.drawing_wire and self.temp_wire:
            scene_pos = self.mapToScene(event.position().toPoint())
            
            # Clean up highlights
            self._cleanup_highlights()
            
            valid_connection = False
            end_pos = scene_pos
            target_component = None
            self.target_pin_index = -1  # Initialize as class member so it's available to _create_wire_connection
            
            # Find target component and pin
            for item in self.scene.items():
                if isinstance(item, ComponentItem) and item != self.wire_start:
                    for idx, pin in enumerate(item.pin_points):
                        angle_rad = item.rotation() * math.pi / 180
                        rotated_pin = QPointF()
                        rotated_pin.setX(pin.x() * math.cos(angle_rad) - pin.y() * math.sin(angle_rad))
                        rotated_pin.setY(pin.x() * math.sin(angle_rad) + pin.y() * math.cos(angle_rad))
                        pin_pos = item.pos() + rotated_pin
                        
                        dist = ((pin_pos.x() - scene_pos.x())**2 + 
                               (pin_pos.y() - scene_pos.y())**2)**0.5
                        
                        if dist < 35:  # Increased detection radius
                            end_pos = pin_pos
                            valid_connection = True
                            target_component = item
                            self.target_pin_index = idx  # Store as class member, not local variable
                            break
                    if valid_connection:
                        break
            
            if target_component == self.wire_start:
                valid_connection = False
            
            if valid_connection:
                connection_exists = self._check_existing_connection(
                    self.wire_start, self.wire_start_pin_index,
                    target_component, self.target_pin_index
                )
                
                if not connection_exists:
                    self._create_wire_connection(end_pos, target_component)
                else:
                    self.showStatusMessage("Connection already exists")
            else:
                self.showStatusMessage("Invalid connection point")
            
            # Cleanup
            self._cleanup_wire_state()
            
        super().mouseReleaseEvent(event)
    
    def _cleanup_highlights(self):
        """Clean up highlight indicators"""
        if hasattr(self, 'highlight_pin') and self.highlight_pin:
            self.scene.removeItem(self.highlight_pin)
            self.highlight_pin = None
        if hasattr(self, 'target_highlight') and self.target_highlight:
            self.scene.removeItem(self.target_highlight)
            self.target_highlight = None
    
    def _check_existing_connection(self, start_comp, start_idx, end_comp, end_idx):
        """Check if a connection already exists between specific pins"""
        for wire in self.connections:
            if ((wire.start_component == start_comp and wire.end_component == end_comp and
                 wire.start_pin_index == start_idx and wire.end_pin_index == end_idx) or
                (wire.start_component == end_comp and wire.end_component == start_comp and
                 wire.start_pin_index == end_idx and wire.end_pin_index == start_idx)):
                return True
        return False
    
    def _create_wire_connection(self, end_pos, target_component):
        """Create a new wire connection"""
        try:
            # Print debugging info
            print(f"Creating wire from {self.wire_start_pos} to {end_pos}")
            print(f"Pin indices: {self.wire_start_pin_index} to {self.target_pin_index}")
            
            # Create permanent wire with thick line
            wire = SmartWire(
                self.wire_start_pos.x(), self.wire_start_pos.y(),
                end_pos.x(), end_pos.y()
            )
            
            # Store connection information
            wire.start_component = self.wire_start
            wire.end_component = target_component
            wire.start_pin_index = self.wire_start_pin_index
            wire.end_pin_index = self.target_pin_index  # Now correctly defined
            
            # Make wire very clearly visible
            wire.setPen(QPen(QColor(0, 0, 0), 4.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            
            # Add wire to scene and tracking list
            self.scene.addItem(wire)
            self.connections.append(wire)
            
            # Force visual update
            wire.update()
            self.scene.update()
            self.viewport().update()
            
            self.showStatusMessage(f"Connected {self.wire_start.component.name} to {target_component.component.name}")
            
            # Switch back to select mode
            self.wire_mode = False
            self.setDragMode(QGraphicsView.RubberBandDrag)
            if self.main_window:
                self.main_window.current_tool = "select"
                self.main_window.updateToolbarState()
                
        except Exception as e:
            print(f"Wire creation error: {str(e)}")
            self.showStatusMessage(f"Error creating wire: {str(e)}")
    
    def _cleanup_wire_state(self):
        """Clean up the wire drawing state"""
        if self.temp_wire:
            self.scene.removeItem(self.temp_wire)
            self.temp_wire = None
        
        self.wire_start = None
        self.wire_start_pin_index = None
        self.drawing_wire = False
        self.setComponentsMovable(True)
        self.viewport().update()

    def dragEnterEvent(self, event):
        if isinstance(event.mimeData(), ComponentMimeData):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if isinstance(event.mimeData(), ComponentMimeData):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if isinstance(event.mimeData(), ComponentMimeData):
            scene_pos = self.mapToScene(event.position().toPoint())
            
            # Snap to grid
            x = round(scene_pos.x() / self.grid_size) * self.grid_size
            y = round(scene_pos.y() / self.grid_size) * self.grid_size
            
            component_item = ComponentItem(event.mimeData().component)
            component_item.setPos(x, y)
            self.scene.addItem(component_item)
            event.accept()
        else:
            event.ignore()

    def wheelEvent(self, event):
        # Custom zoom handling
        zoom_factor = 1.15
        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
        else:
            self.scale(1.0 / zoom_factor, 1.0 / zoom_factor)
    
    # Update to use SmartWire in simulation preview
    def showSimulationPreview(self, show=True):
        """Enhanced simulation preview with better visual feedback"""
        items = self.scene.items()
        
        try:
            for item in items:
                if isinstance(item, ComponentItem):
                    if show:
                        # Highlight active components in simulation
                        glow_effect = QGraphicsDropShadowEffect()
                        glow_effect.setColor(QColor(0, 200, 0))
                        glow_effect.setOffset(0, 0)
                        glow_effect.setBlurRadius(15)
                        item.setGraphicsEffect(glow_effect)
                    else:
                        item.setGraphicsEffect(None)
                elif isinstance(item, SmartWire) and show:
                    # Show current flow in wires during simulation, but keep them thick and visible
                    item.setPen(QPen(QColor(50, 180, 50), 4.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                elif isinstance(item, SmartWire) and not show:
                    # Make sure wires stay visible even when not simulating
                    item.setPen(QPen(QColor(0, 0, 0), 4.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

            # Force scene update to refresh display
            self.scene.update()
            self.viewport().update()
            
        except Exception as e:
            print(f"Error in simulation preview: {str(e)}")
    
    # Update validation to use SmartWire class
    def validateCircuit(self):
        items = self.scene.items()
        components = [item for item in items if isinstance(item, ComponentItem)]
        wires = [item for item in items if isinstance(item, SmartWire)]
        
        errors = []
        
        # Check for unconnected components
        for component in components:
            connected_pins = 0
            for wire in wires:
                start_pos = wire.start_pos
                end_pos = wire.end_pos
                
                # Check if wire connects to any pin of this component
                for pin in component.pin_points:
                    # Get rotation-adjusted pin position
                    angle_rad = component.rotation() * math.pi / 180
                    rotated_pin = QPointF()
                    rotated_pin.setX(pin.x() * math.cos(angle_rad) - pin.y() * math.sin(angle_rad))
                    rotated_pin.setY(pin.x() * math.sin(angle_rad) + pin.y() * math.cos(angle_rad))
                    pin_pos = component.pos() + rotated_pin
                    
                    if ((abs(pin_pos.x() - start_pos.x()) < 5 and 
                         abs(pin_pos.y() - start_pos.y()) < 5) or
                        (abs(pin_pos.x() - end_pos.x()) < 5 and 
                         abs(pin_pos.y() - end_pos.y()) < 5)):
                        connected_pins += 1
            
            if connected_pins < component.component.pins:
                errors.append(f"{component.component.name} has {component.component.pins - connected_pins} unconnected pins")
        
        # Check for floating wires
        for wire in wires:
            connected_ends = 0
            start_pos = wire.start_pos
            end_pos = wire.end_pos
            
            for component in components:
                for pin in component.pin_points:
                    # Get rotation-adjusted pin position
                    angle_rad = component.rotation() * math.pi / 180
                    rotated_pin = QPointF()
                    rotated_pin.setX(pin.x() * math.cos(angle_rad) - pin.y() * math.sin(angle_rad))
                    rotated_pin.setY(pin.x() * math.sin(angle_rad) + pin.y() * math.cos(angle_rad))
                    pin_pos = component.pos() + rotated_pin
                    
                    if ((abs(pin_pos.x() - start_pos.x()) < 5 and 
                         abs(pin_pos.y() - start_pos.y()) < 5) or
                        (abs(pin_pos.x() - end_pos.x()) < 5 and 
                         abs(pin_pos.y() - end_pos.y()) < 5)):
                        connected_ends += 1
            
            if connected_ends < 2:
                errors.append("Floating wire detected")
        
        return errors

    def showContextMenu(self, position):
        scene_pos = self.mapToScene(position)
        item = self.scene.itemAt(scene_pos, self.transform())
        
        # Create menu
        menu = QMenu()
        
        if item:
            # Clicked on an item - show item-specific options
            if isinstance(item, ComponentItem):
                # Component menu
                edit_action = menu.addAction("Edit Properties")
                edit_action.triggered.connect(lambda: item.showPropertyEditor())
                rotate_action = menu.addAction("Rotate")
                rotate_action.triggered.connect(lambda: self.rotateItem(item))
                menu.addSeparator()
                delete_action = menu.addAction("Delete")
                delete_action.triggered.connect(lambda: self.deleteItem(item))
            elif isinstance(item, SmartWire):
                # Wire menu
                delete_action = menu.addAction("Delete")
                delete_action.triggered.connect(lambda: self.deleteItem(item))
        else:
            # Clicked on empty canvas - show component add menu
            add_menu = menu.addMenu("Add Component")
            # Get components from main window
            if self.main_window and hasattr(self.main_window, 'component_library'):
                for i, component in enumerate(self.main_window.component_library.components):
                    action = add_menu.addAction(component.name)
                    action.triggered.connect(lambda checked, comp=component, pos=scene_pos: 
                                            self.addComponentAt(comp, pos))
        
        menu.exec(self.viewport().mapToGlobal(position))
    
    def addComponentAt(self, component, position):
        # Snap to grid
        x = round(position.x() / self.grid_size) * self.grid_size
        y = round(position.y() / self.grid_size) * self.grid_size
        
        # Create new component
        component_item = ComponentItem(component)
        component_item.setPos(x, y)
        self.scene.addItem(component_item)
        self.showStatusMessage(f"Added {component.name} to circuit")
    
    def rotateItem(self, item):
        if isinstance(item, ComponentItem):
            item.rotation_angle += 90
            item.setRotation(item.rotation_angle)
            self.showStatusMessage(f"Rotated {item.component.name}")
    
    def deleteItem(self, item):
        """Enhanced delete item method with proper checks to avoid segmentation faults"""
        try:
            if isinstance(item, ComponentItem):
                # Remove all connected wires first
                wires_to_remove = []
                
                # Make a copy of the connections list to avoid modification during iteration
                for wire in list(self.connections):
                    if wire.start_component == item or wire.end_component == item:
                        if wire in self.scene.items():  # Check if wire is still in the scene
                            wires_to_remove.append(wire)
                
                for wire in wires_to_remove:
                    if wire in self.scene.items():  # Double-check before removal
                        self.scene.removeItem(wire)
                        if wire in self.connections:
                            self.connections.remove(wire)
                
                if item in self.scene.items():  # Check if item is still in the scene
                    self.scene.removeItem(item)
                    msg = f"Deleted {item.component.name} and its connections"
                else:
                    msg = f"Component already removed"
            
            elif isinstance(item, SmartWire):
                if item in self.scene.items():  # Check if item is still in the scene
                    self.scene.removeItem(item)
                    if item in self.connections:
                        self.connections.remove(item)
                    msg = "Deleted wire connection"
                else:
                    msg = "Wire already removed"
            else:
                msg = "Unknown item type"
            
            # Force visual update
            self.scene.update()
            self.viewport().update()
            self.showStatusMessage(msg)
            
        except Exception as e:
            print(f"Error during item deletion: {str(e)}")
            self.showStatusMessage(f"Error deleting item: {str(e)}")

    def prepareSimulation(self):
        """Prepare the simulation by analyzing the circuit"""
        # Reset the simulator
        self.simulator = EnhancedCircuitSimulator()
        
        # Collect all components and connections
        components = {}
        for item in self.scene.items():
            if isinstance(item, ComponentItem):
                comp_id = str(id(item))
                value = "0"
                
                # Get appropriate value based on component type
                if item.component.name == "Resistor":
                    value = item.component.properties.get("Resistance (Ω)", "1000")
                elif item.component.name == "Capacitor":
                    value = item.component.properties.get("Capacitance (F)", "0.000001")
                elif item.component.name == "Inductor":
                    value = item.component.properties.get("Inductance (H)", "0.001")
                elif item.component.name == "Battery":
                    value = item.component.properties.get("Voltage (V)", "9.0")
                elif item.component.name == "LED":
                    value = item.component.properties.get("Forward Voltage (V)", "2.0")
                
                # Add to simulator
                self.simulator.add_component(comp_id, item.component.name, value)
                components[item] = comp_id
        
        # Process connections
        for wire in self.connections:
            if wire.start_component and wire.end_component:
                from_id = components.get(wire.start_component)
                to_id = components.get(wire.end_component)
                if from_id and to_id:
                    self.simulator.add_connection(
                        from_id, wire.start_pin_index,
                        to_id, wire.end_pin_index
                    )
        
        return len(components) > 0
    
    def runSimulation(self):
        """Run the circuit simulation and store results"""
        if self.prepareSimulation():
            # Run simulation for 0.1 seconds with 0.001 second step
            time_points, voltage_data, current_data = self.simulator.simulate(0.1, 0.001)
            self.simulation_results = {
                'time': time_points,
                'voltage': voltage_data,
                'current': current_data
            }
            return True
        return False
    
    def showSimulationResults(self):
        """Display simulation results in a dialog"""
        if not self.simulation_results:
            return
        
        # Create dialog for results
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Circuit Simulation Results")
        dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Create tabs for different plots
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Voltage waveform
        voltage_canvas = MatplotlibCanvas(dialog, width=5, height=4, dpi=100)
        voltage_tab = QWidget()
        voltage_layout = QVBoxLayout(voltage_tab)
        voltage_layout.addWidget(voltage_canvas)
        tabs.addTab(voltage_tab, "Voltage")
        
        # Current waveform
        current_canvas = MatplotlibCanvas(dialog, width=5, height=4, dpi=100)
        current_tab = QWidget()
        current_layout = QVBoxLayout(current_tab)
        current_layout.addWidget(current_canvas)
        tabs.addTab(current_tab, "Current")
        
        # Plot voltage data
        voltage_canvas.axes.clear()
        for component_id, voltage in self.simulation_results['voltage'].items():
            component_type = self.simulator.components[component_id]['type']
            voltage_canvas.axes.plot(
                self.simulation_results['time'], 
                voltage, 
                label=f"{component_type}"
            )
        voltage_canvas.axes.set_xlabel('Time (s)')
        voltage_canvas.axes.set_ylabel('Voltage (V)')
        voltage_canvas.axes.set_title('Voltage vs. Time')
        voltage_canvas.axes.grid(True)
        voltage_canvas.axes.legend()
        voltage_canvas.draw()
        
        # Plot current data
        current_canvas.axes.clear()
        for component_id, current in self.simulation_results['current'].items():
            component_type = self.simulator.components[component_id]['type']
            current_canvas.axes.plot(
                self.simulation_results['time'], 
                current, 
                label=f"{component_type}"
            )
        current_canvas.axes.set_xlabel('Time (s)')
        current_canvas.axes.set_ylabel('Current (A)')
        current_canvas.axes.set_title('Current vs. Time')
        current_canvas.axes.grid(True)
        current_canvas.axes.legend()
        current_canvas.draw()
        
        # Add close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        
        # Show dialog
        dialog.exec()

    def addProbe(self, position, type="voltage"):
        """Add a measurement probe to the circuit"""
        # Create a dialog to let the user choose the probe type
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Add Measurement Probe")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        
        # Add instruction label
        instructions = QLabel(
            "Add a probe to measure voltage or current.\n"
            "Drag the probe near a component pin to connect it."
        )
        instructions.setStyleSheet("color: #000; font-weight: bold;")
        layout.addWidget(instructions)
        
        # Add radio buttons for probe type
        layout.addWidget(QLabel("Select measurement type:"))
        
        voltage_button = QCheckBox("Voltage (V)")
        voltage_button.setChecked(type == "voltage")
        current_button = QCheckBox("Current (I)")
        current_button.setChecked(type == "current")
        
        # Ensure only one can be selected
        def voltage_toggled(checked):
            if checked:
                current_button.setChecked(False)
        
        def current_toggled(checked):
            if checked:
                voltage_button.setChecked(False)
                
        voltage_button.toggled.connect(voltage_toggled)
        current_button.toggled.connect(current_toggled)
        
        layout.addWidget(voltage_button)
        layout.addWidget(current_button)
        
        # Add usage notes
        notes = QLabel(
            "Usage Tips:\n"
            "- Drag the probe close to a component pin to connect\n"
            "- Right-click to toggle between voltage/current\n"
            "- Probe will display measurements during simulation"
        )
        notes.setStyleSheet("color: #555; font-style: italic;")
        layout.addWidget(notes)
        
        # Add buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("Add Probe")
        ok_button.setStyleSheet("background-color: #4E9F3D; color: white; font-weight: bold;")
        ok_button.clicked.connect(dialog.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        # Show dialog and get result
        if dialog.exec():
            if voltage_button.isChecked():
                probe_type = "voltage"
            elif current_button.isChecked():
                probe_type = "current"
            else:
                probe_type = "voltage"  # Default to voltage
                
            # Create and add probe with improved visibility and functionality
            probe = Probe()
            probe.setPos(position)
            probe.measurement_type = probe_type
            self.scene.addItem(probe)
            self.simulation_probes.append(probe)
            
            # Try to find nearby component immediately
            probe.findNearbyComponent()
            
            self.showStatusMessage(f"Added {probe_type} probe. Drag it close to a component pin to connect.")
            return probe
        
        return None

    def startSimulationAnimation(self):
        """Start animated simulation with visual effects"""
        if self.animation_timer is not None:
            return
            
        # Initialize current flow effects on wires
        self.current_flows = {}
        for wire in self.connections:
            self.current_flows[wire] = 0
            
        # Start animation timer for wire animations
        self.animation_timer = self.startTimer(50)  # 20fps
        self.animation_frame = 0
        
        # Start simulator
        self.simulator.add_update_callback(self.updateSimulationData)
        self.simulator.start_simulation(duration=1.0, step=0.001)
    
    def stopSimulationAnimation(self):
        """Stop the simulation animation"""
        if self.animation_timer is not None:
            self.killTimer(self.animation_timer)
            self.animation_timer = None
            
        # Stop the simulator if it's running
        if hasattr(self.simulator, 'stop_simulation'):
            self.simulator.stop_simulation()
        
        # Reset wire appearances
        for wire in self.connections:
            wire.setPen(QPen(QColor(0, 0, 0), 4.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    
    def resetSimulation(self):
        """Reset simulation state"""
        self.stopSimulationAnimation()
        if hasattr(self.simulator, 'reset_simulation'):
            self.simulator.reset_simulation()
        self.showSimulationPreview(False)
    
    def timerEvent(self, event):
        """Handle animation timer events"""
        if hasattr(self, 'animation_timer') and event.timerId() == self.animation_timer:
            self.updateWireAnimations()
            self.animation_frame += 1
    
    def updateWireAnimations(self):
        """Update wire animations to show current flow"""
        if not self.connections:
            return
            
        # Get current simulation time if available
        sim_time = getattr(self.simulator, 'current_time', 0)
        
        for wire, flow in self.current_flows.items():
            # Generate animated flow pattern
            if not hasattr(wire, 'start_component') or not hasattr(wire, 'end_component'):
                continue
                
            # Start with a default flow value
            flow_value = 0
            
            # Try to get actual current from simulation if available
            start_comp_id = str(id(wire.start_component))
            if hasattr(self.simulator, 'current_data') and start_comp_id in self.simulator.current_data:
                # Get current at current time point
                time_idx = int(sim_time / self.simulator.time_step)
                if time_idx < len(self.simulator.current_data[start_comp_id]):
                    flow_value = self.simulator.current_data[start_comp_id][time_idx]
            
            # Animation pattern offset based on frame
            offset = self.animation_frame % 20
            
            if abs(flow_value) > 0.001:  # Only animate if there's meaningful current
                # Create animated dash pattern
                pen = QPen(QColor(50, 180, 50), 4.0)
                pen.setDashPattern([3, 6])
                pen.setDashOffset(offset)
                
                # Adjust color intensity based on current magnitude
                intensity = min(abs(flow_value) * 5, 1.0)  # Scale the intensity
                hue = 0.3  # Green
                if flow_value < 0:
                    hue = 0.6  # Blue for reverse current
                    
                r, g, b = [int(255 * x) for x in colorsys.hsv_to_rgb(hue, 0.8, 0.7 + 0.3 * intensity)]
                pen.setColor(QColor(r, g, b))
                
                wire.setPen(pen)
            else:
                # No significant current, use default style
                wire.setPen(QPen(QColor(150, 150, 150), 4.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    
    def updateSimulationData(self, **kwargs):
        """Callback for simulator data updates with improved probe measurements"""
        if 'reset' in kwargs and kwargs['reset']:
            # Reset simulation data
            for probe in self.simulation_probes:
                probe.value = 0
                probe.update()
            return
            
        # Update probe values
        if 'time' in kwargs and self.simulation_probes:
            time_val = kwargs['time']
            voltage_data = kwargs.get('voltage_data', {})
            current_data = kwargs.get('current_data', {})
            
            # Update time display if available
            if self.main_window and hasattr(self.main_window, 'simulation_control_panel'):
                self.main_window.simulation_control_panel.updateTime(time_val)
            
            # Update probe values based on connections
            for probe in self.simulation_probes:
                # Check if probe is connected to a component
                if probe.connected_component:
                    # Get the component ID for simulation data
                    comp_id = str(id(probe.connected_component))
                    
                    if probe.measurement_type == "voltage" and comp_id in voltage_data:
                        # Get latest value
                        data = voltage_data[comp_id]
                        if len(data) > 0:
                            probe.value = data[-1]
                            probe.update()
                    elif probe.measurement_type == "current" and comp_id in current_data:
                        # Get latest value
                        data = current_data[comp_id]
                        if len(data) > 0:
                            probe.value = data[-1]
                            probe.update()
                else:
                    # Not directly connected - use nearest component approach as fallback
                    nearest_component = None
                    min_dist = float('inf')
                    
                    scene_pos = probe.pos()
                    for item in self.scene.items():
                        if isinstance(item, ComponentItem):
                            comp_pos = item.pos()
                            dist = ((comp_pos.x() - scene_pos.x())**2 + 
                                    (comp_pos.y() - scene_pos.y())**2)**0.5
                            if dist < min_dist:
                                min_dist = dist
                                nearest_component = item
                    
                    # If probe is close to a component, show its values
                    if nearest_component and min_dist < 50:
                        comp_id = str(id(nearest_component))
                        
                        if probe.measurement_type == "voltage" and comp_id in voltage_data:
                            data = voltage_data[comp_id]
                            if len(data) > 0:
                                probe.value = data[-1]
                                probe.update()
                        elif probe.measurement_type == "current" and comp_id in current_data:
                            data = current_data[comp_id]
                            if len(data) > 0:
                                probe.value = data[-1]
                                probe.update()
    
    def runEnhancedSimulation(self):
        """Run enhanced simulation with real-time visualization"""
        if self.prepareSimulation():
            # Set up for real-time simulation
            self.showStatusMessage("Starting enhanced simulation...")
            
            # Show visual preview effects
            self.showSimulationPreview(True)
            
            # Start animation
            self.startSimulationAnimation()
            
            return True
        return False
    
    def showEnhancedSimulationResults(self):
        """Show enhanced simulation results with interactive plots"""
        # Ensure we have simulation data
        if not hasattr(self.simulator, 'components') or not self.simulator.components:
            self.showStatusMessage("No simulation data available")
            return
            
        # Create dialog with more advanced features
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Circuit Simulation Analysis")
        dialog.setMinimumSize(900, 700)
        
        # Layout setup
        layout = QVBoxLayout(dialog)
        
        # Add simulation control panel
        control_panel = SimulationControlPanel()
        layout.addWidget(control_panel)
        
        # Connect control panel signals
        control_panel.simulationStarted.connect(self.startSimulationAnimation)
        control_panel.simulationStopped.connect(self.stopSimulationAnimation)
        control_panel.simulationReset.connect(self.resetSimulation)
        control_panel.simulationSpeedChanged.connect(
            lambda speed: self.simulator.set_speed(speed) if hasattr(self.simulator, 'set_speed') else None
        )
        
        # Create tabs for different analysis views
        tabs = QTabWidget()
        layout.addWidget(tabs, stretch=1)
        
        # Add waveform plots
        voltage_tab = QWidget()
        voltage_layout = QVBoxLayout(voltage_tab)
        voltage_canvas = AnimatedMatplotlibCanvas(dialog, width=5, height=4, dpi=100)
        voltage_canvas.setup_plot("Voltage vs. Time", "Time (s)", "Voltage (V)")
        voltage_layout.addWidget(voltage_canvas.toolbar)
        voltage_layout.addWidget(voltage_canvas)
        tabs.addTab(voltage_tab, "Voltage Waveforms")
        
        current_tab = QWidget()
        current_layout = QVBoxLayout(current_tab)
        current_canvas = AnimatedMatplotlibCanvas(dialog, width=5, height=4, dpi=100)
        current_canvas.setup_plot("Current vs. Time", "Time (s)", "Current (A)")
        current_layout.addWidget(current_canvas.toolbar)
        current_layout.addWidget(current_canvas)
        tabs.addTab(current_tab, "Current Waveforms")
        
        # Add power analysis tab
        power_tab = QWidget()
        power_layout = QVBoxLayout(power_tab)
        power_canvas = AnimatedMatplotlibCanvas(dialog, width=5, height=4, dpi=100)
        power_canvas.setup_plot("Power Consumption", "Time (s)", "Power (W)")
        power_layout.addWidget(power_canvas.toolbar)
        power_layout.addWidget(power_canvas)
        tabs.addTab(power_tab, "Power Analysis")
        
        # Add circuit statistics tab
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)
        stats_text = QTextEdit()
        stats_text.setReadOnly(True)
        stats_layout.addWidget(stats_text)
        tabs.addTab(stats_tab, "Circuit Statistics")
        
        # Fill stats with component information
        stats_html = "<h2>Circuit Components</h2><table border='1' cellspacing='0' cellpadding='5'>"
        stats_html += "<tr><th>Component</th><th>Type</th><th>Value</th><th>Connections</th></tr>"
        
        # Add component stats
        for component_id, component in self.simulator.components.items():
            comp_type = component['type']
            value = component['value']
            connections = len([c for c in self.simulator.connections 
                            if c['from'][0] == component_id or c['to'][0] == component_id])
            
            stats_html += f"<tr><td>{component_id[-6:]}</td><td>{comp_type}</td><td>{value}</td><td>{connections}</td></tr>"
        
        stats_html += "</table>"
        
        # Add simulation summary
        voltage_sources = len(self.simulator.voltage_sources)
        ground_nodes = len(self.simulator.ground_nodes)
        components = len(self.simulator.components)
        connections = len(self.simulator.connections)
        
        stats_html += f"""
        <h2>Simulation Summary</h2>
        <ul>
            <li>Total components: {components}</li>
            <li>Voltage sources: {voltage_sources}</li>
            <li>Ground nodes: {ground_nodes}</li>
            <li>Connections: {connections}</li>
            <li>Simulation time: {getattr(self.simulator, 'max_time', 1.0):.3f}s</li>
            <li>Time step: {getattr(self.simulator, 'time_step', 0.001):.6f}s</li>
        </ul>
        """
        
        stats_text.setHtml(stats_html)
        
        # Add animation update functions
        def update_voltage_plot(frame):
            time = getattr(self.simulator, 'current_time', 0)
            voltage_canvas.axes.clear()
            voltage_canvas.setup_plot("Voltage vs. Time", "Time (s)", "Voltage (V)")
            
            # Get simulation results up to current time
            if hasattr(self.simulator, 'time_points'):
                time_idx = min(int(time / self.simulator.time_step) + 1, 
                              len(self.simulator.time_points))
                
                plot_times = self.simulator.time_points[:time_idx]
                
                if hasattr(self.simulator, 'voltage_data'):
                    # Plot each component's voltage
                    for component_id, voltage in self.simulator.voltage_data.items():
                        comp_type = self.simulator.components[component_id]['type']
                        if time_idx > 0:
                            voltage_canvas.axes.plot(
                                plot_times, 
                                voltage[:time_idx], 
                                label=f"{comp_type} {component_id[-4:]}"
                            )
            
            voltage_canvas.axes.legend(loc='upper right')
            handles, labels = voltage_canvas.axes.get_legend_handles_labels()
            if not handles:  # Only add text if no data
                voltage_canvas.axes.text(
                    0.5, 0.5, 
                    "No data available",
                    ha='center', va='center',
                    transform=voltage_canvas.axes.transAxes,
                    fontsize=12, color='gray'
                )
            
            return voltage_canvas.axes
        
        def update_current_plot(frame):
            time = getattr(self.simulator, 'current_time', 0)
            current_canvas.axes.clear()
            current_canvas.setup_plot("Current vs. Time", "Time (s)", "Current (A)")
            
            # Get simulation results up to current time
            if hasattr(self.simulator, 'time_points'):
                time_idx = min(int(time / self.simulator.time_step) + 1, 
                              len(self.simulator.time_points))
                
                plot_times = self.simulator.time_points[:time_idx]
                
                if hasattr(self.simulator, 'current_data'):
                    # Plot each component's current
                    for component_id, current in self.simulator.current_data.items():
                        comp_type = self.simulator.components[component_id]['type']
                        if time_idx > 0:
                            current_canvas.axes.plot(
                                plot_times, 
                                current[:time_idx], 
                                label=f"{comp_type} {component_id[-4:]}"
                            )
            
            current_canvas.axes.legend(loc='upper right')
            return current_canvas.axes
        
        def update_power_plot(frame):
            time = getattr(self.simulator, 'current_time', 0)
            power_canvas.axes.clear()
            power_canvas.setup_plot("Power Consumption", "Time (s)", "Power (W)")
            
            # Get simulation results up to current time
            if hasattr(self.simulator, 'time_points'):
                time_idx = min(int(time / self.simulator.time_step) + 1, 
                              len(self.simulator.time_points))
                
                plot_times = self.simulator.time_points[:time_idx]
                
                if hasattr(self.simulator, 'voltage_data') and hasattr(self.simulator, 'current_data'):
                    # Calculate power for each component
                    for component_id in self.simulator.components:
                        if (component_id in self.simulator.voltage_data and 
                            component_id in self.simulator.current_data):
                            
                            voltage = self.simulator.voltage_data[component_id][:time_idx]
                            current = self.simulator.current_data[component_id][:time_idx]
                            
                            if len(voltage) > 0 and len(current) > 0:
                                # Calculate power (P = V * I)
                                power = [v * i for v, i in zip(voltage, current)]
                                
                                comp_type = self.simulator.components[component_id]['type']
                                power_canvas.axes.plot(
                                    plot_times, 
                                    power, 
                                    label=f"{comp_type} {component_id[-4:]}"
                                )
            
            power_canvas.axes.legend(loc='upper right')
            return power_canvas.axes
        
        # Start animations
        voltage_anim = voltage_canvas.start_animation(update_voltage_plot, interval=100)
        current_anim = current_canvas.start_animation(update_current_plot, interval=100)
        power_anim = power_canvas.start_animation(update_power_plot, interval=100)
        
        # Add new tab for probe measurements
        probes_tab = QWidget()
        
        # Add close button - fix: define before use
        close_button = QPushButton("Close")
        close_button.clicked.connect(lambda: self._cleanup_simulation_dialog(dialog))
        layout.addWidget(close_button)
        
        # Set simulation results to window
        if self.main_window:
            self.main_window.simulation_control_panel = control_panel
        
        # Show dialog
        dialog.exec()
    
    def _cleanup_simulation_dialog(self, dialog):
        """Clean up resources when closing simulation dialog"""
        # Stop any running simulations
        self.stopSimulationAnimation()
        
        # Find and stop all animations
        for child in dialog.findChildren(AnimatedMatplotlibCanvas):
            if hasattr(child, 'clear_animations'):
                child.clear_animations()
            
        dialog.reject()

class ComponentLibrary(QListWidget):
    def __init__(self):
        super().__init__()
        self.components = [
            Component("Resistor", "R", 2),
            Component("Capacitor", "C", 2),
            Component("Inductor", "L", 2),
            Component("Battery", "V", 2),
            Component("LED", "LED", 2),
            Component("Transistor", "T", 3),
            Component("Diode", "D", 2),
            Component("Switch", "SW", 2),
            Component("Potentiometer", "POT", 3),
            Component("IC", "IC", 4)
        ]
        
        for component in self.components:
            self.addItem(f"{component.name}")
        
        self.setDragEnabled(True)
        self.setStyleSheet("""
            QListWidget {
                background-color: #F5F5F5;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 4px;
                border-bottom: 1px solid #EEEEEE;
            }
            QListWidget::item:selected {
                background-color: #D0E3FA;
                color: #000000;
            }
            QListWidget::item:hover {
                background-color: #E5E5E5;
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.position().toPoint())
            if item:
                index = self.row(item)
                component = self.components[index]
                
                drag = QDrag(self)
                mime_data = ComponentMimeData()
                mime_data.component = component
                drag.setMimeData(mime_data)
                
                # Create a pixmap for drag visual feedback
                pixmap = QPixmap(60, 40)
                pixmap.fill(Qt.transparent)
                painter = QPainter(pixmap)
                painter.setPen(QPen(Qt.black, 2))
                painter.setBrush(QBrush(QColor(240, 240, 240)))
                painter.drawRoundedRect(5, 5, 50, 30, 5, 5)
                painter.drawText(pixmap.rect(), Qt.AlignCenter, component.symbol)
                painter.end()
                
                drag.setPixmap(pixmap)
                drag.setHotSpot(QPoint(30, 20))
                
                drag.exec()
        super().mousePressEvent(event)

class SmartLab(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartLab - Professional Circuit Designer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Create left panel with component library - update styling with new colors
        left_panel = QWidget()
        left_panel.setMaximumWidth(220)
        left_panel.setStyleSheet("""
            background-color: #1E5128;  /* Dark green instead of dark blue */
            border-radius: 6px;
            margin: 2px;
        """)
        left_layout = QVBoxLayout(left_panel)
        
        # Component library header with updated colors
        library_label = QLabel("Components")
        library_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 16px; 
            color: #FFFFFF;
            padding: 8px;
            background-color: #4E9F3D;  /* Medium green */
            border-radius: 4px;
        """)
        left_layout.addWidget(library_label)
        
        # Component library with updated styling
        self.component_library = ComponentLibrary()
        self.component_library.setStyleSheet("""
            QListWidget {
                background-color: #F6F6F6;
                border: 1px solid #4E9F3D;
                border-radius: 4px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px;
                border-bottom: 1px solid #E0E0E0;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
            QListWidget::item:selected {
                background-color: #D8E9A8;  /* Light green */
                color: #1E5128;
            }
            QListWidget::item:hover {
                background-color: #F0F7E6;
            }
        """)
        left_layout.addWidget(self.component_library)
        
        # Add simulation results area
        self.sim_results_label = QLabel("Simulation Results")
        self.sim_results_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 16px; 
            color: #FFFFFF;
            padding: 8px;
            background-color: #4E9F3D;  /* Medium green */
            border-radius: 4px;
            margin-top: 10px;
        """)
        left_layout.addWidget(self.sim_results_label)
        
        self.sim_results = QLabel("No simulation data")
        self.sim_results.setStyleSheet("""
            background-color: #F6F6F6;
            color: #333333;
            padding: 8px;
            border-radius: 4px;
            min-height: 100px;
        """)
        self.sim_results.setWordWrap(True)
        self.sim_results.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        left_layout.addWidget(self.sim_results)
        
        # Error panel
        self.error_label = QLabel("Circuit Validation")
        self.error_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 16px; 
            color: #FFFFFF;
            padding: 8px;
            background-color: #4E9F3D;  /* Medium green */
            border-radius: 4px;
            margin-top: 10px;
        """)
        left_layout.addWidget(self.error_label)
        
        self.error_panel = QLabel("No errors detected")
        self.error_panel.setStyleSheet("""
            background-color: #F6F6F6;
            color: #00AA00;
            padding: 8px;
            border-radius: 4px;
            min-height: 80px;
        """)
        self.error_panel.setWordWrap(True)
        self.error_panel.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        left_layout.addWidget(self.error_panel)
        
        # Create circuit canvas with reference to main window
        self.canvas = CircuitCanvas(self)
        self.canvas.setAcceptDrops(True)
        
        # Add widgets to main layout
        layout.addWidget(left_panel)
        layout.addWidget(self.canvas, stretch=4)
        
        # Setup menu and toolbar
        self.create_menu_bar()
        self.create_toolbar()
        self.create_status_bar()
        
        # Application state
        self.current_tool = "select"
        self.canvas.wire_mode = False
        
        # Apply main window stylesheet with updated colors
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F0F0F5;
            }
            QToolBar {
                background-color: #1E5128;  /* Dark green */
                spacing: 3px;
                padding: 3px;
                border: none;
            }
            QToolButton {
                color: #FFFFFF;
                background-color: #4E9F3D;  /* Medium green */
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 5px;
                margin: 2px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #D8E9A8;  /* Light green */
                border: 1px solid #F0F0F0;
                color: #1E5128;
            }
            QToolButton:pressed {
                background-color: #91C788;
            }
            QStatusBar {
                background-color: #1E5128;  /* Dark green */
                color: #FFFFFF;
            }
            QLabel {
                color: #333333;
            }
            QMenuBar {
                background-color: #1E5128;  /* Dark green */
                color: #FFFFFF;
            }
            QMenuBar::item {
                background-color: transparent;
                color: #FFFFFF;
                padding: 6px 10px;
            }
            QMenuBar::item:selected {
                background-color: #4E9F3D;  /* Medium green */
            }
            QMenu {
                background-color: #1E5128;  /* Dark green */
                color: #FFFFFF;
                border: 1px solid #4E9F3D;
            }
            QMenu::item {
                padding: 6px 20px;
            }
            QMenu::item:selected {
                background-color: #4E9F3D;  /* Medium green */
            }
        """)
        
        # Add a toolbar for simulation-specific tools
        self.create_simulation_toolbar()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        new_action = file_menu.addAction("New")
        new_action.setShortcut("Ctrl+N")
        open_action = file_menu.addAction("Open")
        open_action.setShortcut("Ctrl+O")
        save_action = file_menu.addAction("Save")
        save_action.setShortcut("Ctrl+S")
        file_menu.addSeparator()
        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        undo_action = edit_menu.addAction("Undo")
        undo_action.setShortcut("Ctrl+Z")
        redo_action = edit_menu.addAction("Redo")
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addSeparator()
        select_all_action = edit_menu.addAction("Select All")
        select_all_action.setShortcut("Ctrl+A")
        
        # View menu
        view_menu = menubar.addMenu("View")
        zoom_in_action = view_menu.addAction("Zoom In")
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        zoom_out_action = view_menu.addAction("Zoom Out")
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        reset_view_action = view_menu.addAction("Reset View")
        reset_view_action.setShortcut("Ctrl+0")
        reset_view_action.triggered.connect(self.reset_view)
        view_menu.addSeparator()
        toggle_grid_action = view_menu.addAction("Toggle Grid")
        toggle_grid_action.setShortcut("Ctrl+G")
        toggle_grid_action.triggered.connect(self.canvas.toggleGrid)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        simulate_action = tools_menu.addAction("Simulate Circuit")
        simulate_action.setShortcut("F5")
        pcb_action = tools_menu.addAction("Generate PCB")
        pcb_action.setShortcut("F6")
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        help_action = help_menu.addAction("SmartLab Help")
        help_action.setShortcut("F1")
        about_action = help_menu.addAction("About SmartLab")
    
    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Create actions
        self.select_action = toolbar.addAction("Select")
        self.wire_action = toolbar.addAction("Wire")
        self.delete_action = toolbar.addAction("Delete")
        toolbar.addSeparator()
        self.rotate_action = toolbar.addAction("Rotate")
        self.mirror_action = toolbar.addAction("Mirror")
        toolbar.addSeparator()
        self.zoom_in_action = toolbar.addAction("Zoom In")
        self.zoom_out_action = toolbar.addAction("Zoom Out")
        toolbar.addSeparator()
        self.validate_action = toolbar.addAction("Validate")
        self.simulate_action = toolbar.addAction("Simulate")
        
        # Store toolbar for later updates
        self.toolbar = toolbar
        
        toolbar.actionTriggered.connect(self.handle_tool_action)
    
    def updateToolbarState(self):
        """Update toolbar button states based on current tool"""
        # Reset all button styles
        for action in self.toolbar.actions():
            if hasattr(action, 'setChecked'):
                action.setChecked(False)
        
        # Highlight the current tool
        if self.current_tool == "select":
            if hasattr(self.select_action, 'setChecked'):
                self.select_action.setChecked(True)
        elif self.current_tool == "wire":
            if hasattr(self.wire_action, 'setChecked'):
                self.wire_action.setChecked(True)
    
    def create_status_bar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
    
    def handle_tool_action(self, action):
        tool = action.text().lower()
        
        # Special debug - let user know that the wire tool is being selected
        if tool == "wire":
            self.statusBar.showMessage("Wire tool selected - Click on a pin of a component to start connecting")
            
        self.current_tool = tool
        
        # Update toolbar to reflect current tool
        self.updateToolbarState()
        
        # Reset all tools first
        self.canvas.wire_mode = False
        self.canvas.setDragMode(QGraphicsView.RubberBandDrag)
        self.canvas.showSimulationPreview(False)
        
        # Set status message
        self.statusBar.showMessage(f"Tool: {action.text()}")
        
        # Handle specific tools
        if tool == "select":
            self.canvas.setComponentsMovable(True)
            
        elif tool == "wire":
            self.canvas.wire_mode = True
            self.canvas.setDragMode(QGraphicsView.NoDrag)
            # Keep components selectable but not movable during wire mode
            self.canvas.setComponentsMovable(False)
            self.statusBar.showMessage("Wire Tool: Click on component pins to connect. Each connection requires selecting the tool again.")
        
        elif tool == "rotate":
            selected_items = self.canvas.scene.selectedItems()
            for item in selected_items:
                if isinstance(item, ComponentItem):
                    item.rotation_angle += 90
                    item.setRotation(item.rotation_angle)
                    # Regenerate pins after rotation if needed
            self.statusBar.showMessage(f"Rotated {len(selected_items)} component(s)")
        elif tool == "delete":
            selected_items = self.canvas.scene.selectedItems()
            if selected_items:
                for item in selected_items:
                    # Use the enhanced delete method
                    self.canvas.deleteItem(item)
                self.statusBar.showMessage(f"Deleted {len(selected_items)} item(s)")
            else:
                self.statusBar.showMessage("Select items to delete")
        elif tool == "mirror":
            selected_items = self.canvas.scene.selectedItems()
            for item in selected_items:
                if isinstance(item, ComponentItem):
                    item.setScale(-1 if item.scale() == 1 else 1, 1)
            self.statusBar.showMessage(f"Mirrored {len(selected_items)} component(s)")
        elif tool == "zoom in":
            self.zoom_in()
        elif tool == "zoom out":
            self.zoom_out()
        elif tool == "validate":
            errors = self.canvas.validateCircuit()
            if errors:
                error_text = "\n".join(errors)
                self.error_panel.setText(error_text)
                self.error_panel.setStyleSheet("""
                    background-color: #FFF0F0;
                    color: #CC0000;
                    padding: 8px;
                    border-radius: 4px;
                    min-height: 80px;
                """)
                self.statusBar.showMessage(f"Circuit validation found {len(errors)} issues")
            else:
                self.error_panel.setText("No errors detected")
                self.error_panel.setStyleSheet("""
                    background-color: #F0FFF0;
                    color: #00AA00;
                    padding: 8px;
                    border-radius: 4px;
                    min-height: 80px;
                """)
                self.statusBar.showMessage("Circuit validation passed")
        elif tool == "simulate":
            # Run simulation with proper error handling
            try:
                # Validate circuit first
                errors = self.canvas.validateCircuit()
                if errors:
                    error_text = "Cannot simulate circuit with errors:\n" + "\n".join(errors)
                    self.sim_results.setText(error_text)
                    self.sim_results.setStyleSheet("""
                        background-color: #FFF0F0;
                        color: #CC0000;
                        padding: 8px;
                        border-radius: 4px;
                        min-height: 100px;
                    """)
                    self.statusBar.showMessage("Simulation failed - circuit has errors")
                else:
                    # Show simulation animation
                    self.statusBar.showMessage("Circuit simulation in progress...")
                    QApplication.processEvents()
                    
                    # Run simulation
                    self.canvas.showSimulationPreview(True)
                    QApplication.processEvents()
                    
                    success = self.canvas.runSimulation()
                    if success:
                        # Show results dialog
                        self.canvas.showSimulationResults()
                        
                        # Generate summary text for simulation panel
                        comp_count = len(self.canvas.simulator.components)
                        self.sim_results.setText(
                            f"Simulation Results Summary:\n"
                            f"- Components analyzed: {comp_count}\n"
                            f"- Simulation time: 0.1s\n"
                            f"- Status: Complete\n\n"
                            f"Click Simulate again to view detailed waveforms."
                        )
                        self.sim_results.setStyleSheet("""
                            background-color: #F0FFF0;
                            color: #00AA00;
                            padding: 8px;
                            border-radius: 4px;
                            min-height: 100px;
                        """)
                        self.statusBar.showMessage("Simulation completed successfully")
                    else:
                        self.sim_results.setText(
                            "Simulation could not be completed.\n"
                            "Please check your circuit design."
                        )
                        self.sim_results.setStyleSheet("""
                            background-color: #FFF0F0;
                            color: #CC0000;
                            padding: 8px;
                            border-radius: 4px;
                            min-height: 100px;
                        """)
                        self.statusBar.showMessage("Simulation failed")
            except Exception as e:
                print(f"Simulation error: {str(e)}")
                self.sim_results.setText(f"Simulation error: {str(e)}")
                self.sim_results.setStyleSheet("""
                    background-color: #FFF0F0;
                    color: #CC0000;
                    padding: 8px;
                    border-radius: 4px;
                    min-height: 100px;
                """)
                self.statusBar.showMessage("Simulation failed - unexpected error")
            finally:
                # Ensure we always return to normal display
                self.canvas.showSimulationPreview(False)
                QApplication.processEvents()
    
    def zoom_in(self):
        self.canvas.scale(1.2, 1.2)
    
    def zoom_out(self):
        self.canvas.scale(1/1.2, 1/1.2)
    
    def reset_view(self):
        self.canvas.resetTransform()
        self.canvas.fitInView(self.canvas.scene.sceneRect(), Qt.KeepAspectRatio)

    def create_simulation_toolbar(self):
        """Create a toolbar for simulation tools"""
        sim_toolbar = QToolBar("Simulation Toolbar")
        sim_toolbar.setMovable(False)
        sim_toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(Qt.BottomToolBarArea, sim_toolbar)
        
        # Add simulation tools
        self.add_probe_action = sim_toolbar.addAction("Add Probe")
        self.advanced_sim_action = sim_toolbar.addAction("Advanced Simulation")
        sim_toolbar.addSeparator()
        self.oscilloscope_action = sim_toolbar.addAction("Oscilloscope")
        self.spectrum_action = sim_toolbar.addAction("Spectrum Analyzer")
        
        # Connect actions
        self.add_probe_action.triggered.connect(self.add_measurement_probe)
        self.advanced_sim_action.triggered.connect(self.run_advanced_simulation)
        self.oscilloscope_action.triggered.connect(self.show_oscilloscope)
        self.spectrum_action.triggered.connect(self.show_spectrum_analyzer)
        
        # Store toolbar for later access
        self.sim_toolbar = sim_toolbar
    
    def add_measurement_probe(self):
        """Add a measurement probe to the current view position"""
        # Get center of current view
        view_center = self.canvas.mapToScene(
            self.canvas.viewport().rect().center()
        )
        
        # Add probe at view center
        self.canvas.addProbe(view_center)
        
    def run_advanced_simulation(self):
        """Run the advanced simulation with animation"""
        # Validate circuit first
        errors = self.canvas.validateCircuit()
        if errors:
            error_text = "Cannot simulate circuit with errors:\n" + "\n".join(errors)
            self.sim_results.setText(error_text)
            self.sim_results.setStyleSheet("""
                background-color: #FFF0F0;
                color: #CC0000;
                padding: 8px;
                border-radius: 4px;
                min-height: 100px;
            """)
            self.statusBar.showMessage("Simulation failed - circuit has errors")
            return
            
        try:
            # Run enhanced simulation
            self.statusBar.showMessage("Running advanced simulation...")
            QApplication.processEvents()
            
            success = self.canvas.runEnhancedSimulation()
            if success:
                # Show advanced results dialog
                self.canvas.showEnhancedSimulationResults()
                
                # Update summary text
                self.sim_results.setText(
                    "Advanced Simulation Results:\n"
                    "- Interactive waveform analysis available\n"
                    "- Real-time animation enabled\n"
                    "- Circuit behavior analyzed\n\n"
                    "Use simulation controls to playback and analyze."
                )
                self.sim_results.setStyleSheet("""
                    background-color: #F0FFF0;
                    color: #00AA00;
                    padding: 8px;
                    border-radius: 4px;
                    min-height: 100px;
                """)
                
                self.statusBar.showMessage("Advanced simulation completed")
            else:
                self.sim_results.setText(
                    "Simulation could not be completed.\n"
                    "Please check your circuit design."
                )
                self.sim_results.setStyleSheet("""
                    background-color: #FFF0F0;
                    color: #CC0000;
                    padding: 8px;
                    border-radius: 4px;
                    min-height: 100px;
                """)
                
                self.statusBar.showMessage("Simulation failed")
                
        except Exception as e:
            print(f"Advanced simulation error: {str(e)}")
            self.sim_results.setText(f"Simulation error: {str(e)}")
            self.sim_results.setStyleSheet("""
                background-color: #FFF0F0;
                color: #CC0000;
                padding: 8px;
                border-radius: 4px;
                min-height: 100px;
            """)
            
            self.statusBar.showMessage("Simulation failed - unexpected error")
        finally:
            # Restore normal display
            self.canvas.stopSimulationAnimation()
            self.canvas.showSimulationPreview(False)
    
    def show_oscilloscope(self):
        """Show oscilloscope view of current circuit signals"""
        # First ensure we have some simulation data
        if not hasattr(self.canvas.simulator, 'components') or not self.canvas.simulator.components:
            # Run a quick simulation to get data
            self.canvas.prepareSimulation()
            time_points, voltage_data, current_data = self.canvas.simulator.simulate(0.1, 0.001)
        else:
            # Use existing data if available
            time_points = getattr(self.canvas.simulator, 'time_points', None)
            voltage_data = getattr(self.canvas.simulator, 'voltage_data', {})
            current_data = getattr(self.canvas.simulator, 'current_data', {})
            
            # Fix: Check length of time_points array instead of direct boolean evaluation
            if time_points is None or len(time_points) == 0 or len(voltage_data) == 0:
                time_points, voltage_data, current_data = self.canvas.simulator.simulate(0.1, 0.001)
        
        # Create oscilloscope dialog with real-time updates
        dialog = QDialog(self)
        dialog.setWindowTitle("SmartLab Oscilloscope")
        dialog.setMinimumSize(800, 600)
        
        # Add plot canvas for oscilloscope display
        layout = QVBoxLayout(dialog)
        
        # Add title with professional styling
        title_label = QLabel("Digital Oscilloscope")
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #1E5128;
            padding: 8px;
            background-color: #F6F6F6;
            border-bottom: 1px solid #CCCCCC;
        """)
        layout.addWidget(title_label)
        
        # Create more professional control panel
        control_panel = QWidget()
        control_panel.setStyleSheet("""
            background-color: #F0F0F0;
            border-radius: 4px;
            padding: 5px;
        """)
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(10, 5, 10, 5)
        
        # Signal selection with better labeling
        signal_group = QWidget()
        signal_layout = QVBoxLayout(signal_group)
        signal_layout.setContentsMargins(0, 0, 0, 0)
        signal_label = QLabel("Signal Source:")
        signal_combo = QComboBox()
        signal_combo.setMinimumWidth(150)
        
        # Populate with available components
        for comp_id, comp in self.canvas.simulator.components.items():
            signal_combo.addItem(f"{comp['type']} - {comp_id[-6:]}", comp_id)
        
        signal_layout.addWidget(signal_label)
        signal_layout.addWidget(signal_combo)
        
        # Channel selection with better UI
        channel_group = QWidget()
        channel_layout = QVBoxLayout(channel_group)
        channel_layout.setContentsMargins(0, 0, 0, 0)
        channel_label = QLabel("Channel:")
        channel_combo = QComboBox()
        channel_combo.addItems(["Voltage", "Current"])
        channel_combo.setStyleSheet("background-color: white;")
        channel_layout.addWidget(channel_label)
        channel_layout.addWidget(channel_combo)
        
        # Add professional time scale controls
        timescale_group = QWidget()
        timescale_layout = QVBoxLayout(timescale_group)
        timescale_layout.setContentsMargins(0, 0, 0, 0)
        timescale_label = QLabel("Time Scale:")
        timescale_slider = QSlider(Qt.Horizontal)
        timescale_slider.setRange(1, 100)
        timescale_slider.setValue(50)
        timescale_slider.setTickPosition(QSlider.TicksBelow)
        timescale_slider.setTickInterval(10)
        timescale_layout.addWidget(timescale_label)
        timescale_layout.addWidget(timescale_slider)
        
        # Add professional trigger controls
        trigger_group = QWidget()
        trigger_layout = QVBoxLayout(trigger_group)
        trigger_layout.setContentsMargins(0, 0, 0, 0)
        trigger_label = QLabel("Trigger:")
        trigger_button = QPushButton("Edge Trigger")
        trigger_button.setCheckable(True)
        trigger_button.setStyleSheet("""
            QPushButton {
                background-color: #4E9F3D;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QPushButton:checked {
                background-color: #D62828;
            }
        """)
        trigger_layout.addWidget(trigger_label)
        trigger_layout.addWidget(trigger_button)
        
        # Add run/stop button for professional look
        run_button = QPushButton("Run/Stop")
        run_button.setCheckable(True)
        run_button.setChecked(True)
        run_button.setStyleSheet("""
            QPushButton {
                background-color: #4E9F3D;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 4px 12px;
                min-width: 80px;
            }
            QPushButton:checked {
                background-color: #D62828;
            }
        """)
        
        # Add measurement display
        measurement_label = QLabel("0.00 V")
        measurement_label.setStyleSheet("""
            font-family: 'Courier New';
            font-size: 14px;
            font-weight: bold;
            color: #D62828;
            padding: 4px;
            border: 1px solid #CCCCCC;
            background-color: white;
            min-width: 100px;
            qproperty-alignment: AlignCenter;
        """)
        
        # Add all controls to layout
        control_layout.addWidget(signal_group)
        control_layout.addWidget(channel_group)
        control_layout.addWidget(timescale_group)
        control_layout.addWidget(trigger_group)
        control_layout.addStretch(1)
        control_layout.addWidget(measurement_label)
        control_layout.addWidget(run_button)
        
        layout.addWidget(control_panel)
        
        # Create plot canvas with professional styling
        canvas = AnimatedMatplotlibCanvas(dialog, width=6, height=4, dpi=100)
        canvas.fig.patch.set_facecolor('#F6F6F6')
        canvas.axes.set_facecolor('#FFFFFF')
        canvas.setup_plot("Oscilloscope", "Time (s)", "Amplitude")
        
        # Add canvas toolbar with professional styling
        toolbar_layout = QHBoxLayout()
        toolbar_layout.addWidget(canvas.toolbar)
        toolbar_layout.addStretch(1)
        layout.addLayout(toolbar_layout)
        
        # Add the canvas as the main element
        layout.addWidget(canvas, stretch=1)
        
        # Setup animation function to update plot with improved visuals
        def update_oscilloscope(frame):
            # Only update if running
            if not run_button.isChecked():
                return canvas.axes
                
            canvas.axes.clear()
            canvas.axes.set_facecolor('#FFFFFF')
            canvas.axes.grid(True, linestyle='--', alpha=0.7, color='#CCCCCC')
            
            # Get selected signal
            if signal_combo.count() > 0:
                comp_id = signal_combo.currentData()
                signal_type = channel_combo.currentText().lower()
                
                # Get data based on signal type
                if signal_type == "voltage" and comp_id in voltage_data:
                    signal_data = voltage_data[comp_id]
                    label = f"Voltage - {self.canvas.simulator.components[comp_id]['type']}"
                    color = '#1E5128'  # Green color theme
                    unit = "V"
                elif signal_type == "current" and comp_id in current_data:
                    signal_data = current_data[comp_id]
                    label = f"Current - {self.canvas.simulator.components[comp_id]['type']}"
                    color = '#D62828'  # Red color theme
                    unit = "A"
                else:
                    # No data, show empty plot with grid
                    canvas.axes.text(0.5, 0.5, "No data available for selected channel", 
                                    ha='center', va='center', 
                                    transform=canvas.axes.transAxes,
                                    fontsize=12, color='gray')
                    canvas.axes.set_xlabel("Time (s)")
                    canvas.axes.set_ylabel("Amplitude")
                    return canvas.axes
                
                # Apply time scaling for professional visualization
                scale_factor = timescale_slider.value() / 50.0  # 1.0 at middle
                time_slice = min(len(time_points), max(10, int(len(time_points) / scale_factor)))
                
                # Plot the data with better styling
                canvas.axes.plot(
                    time_points[:time_slice], 
                    signal_data[:time_slice], 
                    color=color, 
                    label=label,
                    linewidth=1.5
                )
                
                # Add trigger line if triggered with professional look
                if trigger_button.isChecked():
                    # Find trigger point (where signal crosses mean)
                    mean_value = np.mean(signal_data[:time_slice])
                    trigger_points = []
                    for i in range(1, time_slice):
                        if (signal_data[i-1] < mean_value and signal_data[i] >= mean_value):
                            trigger_points.append(i)
                    
                    if trigger_points:
                        # Use first trigger point and show with better styling
                        trigger_idx = trigger_points[0]
                        canvas.axes.axvline(
                            x=time_points[trigger_idx], 
                            color='#D62828', 
                            linestyle='--', 
                            alpha=0.8,
                            linewidth=1.5
                        )
                        # Add trigger marker text
                        canvas.axes.text(
                            time_points[trigger_idx], 
                            canvas.axes.get_ylim()[1] * 0.95,
                            "T",
                            color='#D62828',
                            fontweight='bold',
                            ha='center'
                        )
                
                # Improve axis labels and title for professional look
                if signal_type == "voltage":
                    canvas.axes.set_ylabel(f"Voltage ({unit})", fontweight='bold', color='#333333')
                else:
                    canvas.axes.set_ylabel(f"Current ({unit})", fontweight='bold', color='#333333')
                
                canvas.axes.set_xlabel("Time (s)", fontweight='bold', color='#333333')
                
                # Add measurement markers for professional oscilloscope feel
                # Find peak value
                if len(signal_data[:time_slice]) > 0:
                    peak_value = np.max(np.abs(signal_data[:time_slice]))
                    peak_idx = np.argmax(np.abs(signal_data[:time_slice]))
                    
                    # Mark peak
                    canvas.axes.plot(
                        time_points[peak_idx], 
                        signal_data[peak_idx], 
                        'o', 
                        color='#D62828', 
                        markersize=6
                    )
                    
                    # Update measurement label
                    if signal_type == "voltage":
                        measurement_label.setText(f"{peak_value:.3f} V")
                    else:
                        measurement_label.setText(f"{peak_value*1000:.1f} mA")
                    
                    # Add measurement text on graph
                    canvas.axes.text(
                        time_points[peak_idx], 
                        signal_data[peak_idx],
                        f"  {signal_data[peak_idx]:.3f} {unit}",
                        va='center',
                        color='#D62828'
                    )
                
                # Add professional markers for Y-axis scale
                max_val = np.max(signal_data[:time_slice])
                min_val = np.min(signal_data[:time_slice])
                
                # Add grid and legend with better styling
                canvas.axes.legend(loc='upper right', framealpha=0.7)
                
                # Fix axes limits for stable display
                if len(time_points) > 0:
                    canvas.axes.set_xlim(time_points[0], time_points[time_slice-1])
                    canvas.axes.set_ylim(min_val * 1.1 if min_val < 0 else min_val * 0.9, max_val * 1.1)
            
            return canvas.axes
        
        # Connect control changes to update the plot
        def update_view():
            # Force animation update
            if hasattr(canvas, 'animations') and canvas.animations:
                canvas.animations[0].event_source.start()
        
        signal_combo.currentIndexChanged.connect(update_view)
        channel_combo.currentIndexChanged.connect(update_view)
        timescale_slider.valueChanged.connect(update_view)
        trigger_button.toggled.connect(update_view)
        run_button.toggled.connect(update_view)
        
        # Add professional close button
        close_button = QPushButton("Close")
        close_button.setStyleSheet("""
            background-color: #1E5128;
            color: white;
            font-weight: bold;
            border-radius: 4px;
            padding: 6px;
            min-width: 80px;
        """)
        close_button.clicked.connect(dialog.close)
        
        # Add button to layout
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        # Start the animation
        anim = canvas.start_animation(update_oscilloscope, interval=100)
        
        # Show dialog
        dialog.exec()

    def show_spectrum_analyzer(self):
        """Show spectrum analyzer for frequency domain analysis"""
        # First ensure we have some simulation data
        if not hasattr(self.canvas.simulator, 'components') or not self.canvas.simulator.components:
            # Run a quick simulation to get data
            self.canvas.prepareSimulation()
            time_points, voltage_data, current_data = self.canvas.simulator.simulate(0.2, 0.0005)  # Higher resolution for FFT
        else:
            # Use existing data if available
            time_points = getattr(self.canvas.simulator, 'time_points', None)
            voltage_data = getattr(self.canvas.simulator, 'voltage_data', {})
            current_data = getattr(self.canvas.simulator, 'current_data', {})
            
            # Fix: Check length of time_points array instead of direct boolean evaluation
            if time_points is None or len(time_points) == 0 or len(voltage_data) == 0:
                time_points, voltage_data, current_data = self.canvas.simulator.simulate(0.2, 0.0005)
        
        # Create spectrum analyzer dialog with professional look
        dialog = QDialog(self)
        dialog.setWindowTitle("SmartLab Spectrum Analyzer")
        dialog.setMinimumSize(800, 600)
        
        # Add plot canvas for spectrum display
        layout = QVBoxLayout(dialog)
        
        # Add title with professional styling
        title_label = QLabel("Frequency Spectrum Analyzer")
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #1E5128;
            padding: 8px;
            background-color: #F6F6F6;
            border-bottom: 1px solid #CCCCCC;
        """)
        layout.addWidget(title_label)
        
        # Create professional control panel
        control_panel = QWidget()
        control_panel.setStyleSheet("""
            background-color: #F0F0F0;
            border-radius: 4px;
            padding: 5px;
        """)
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(10, 5, 10, 5)
        
        # Signal selection with better UI
        signal_group = QWidget()
        signal_layout = QVBoxLayout(signal_group)
        signal_layout.setContentsMargins(0, 0, 0, 0)
        signal_label = QLabel("Signal Source:")
        signal_combo = QComboBox()
        signal_combo.setMinimumWidth(150)
        
        # Populate with available components
        for comp_id, comp in self.canvas.simulator.components.items():
            signal_combo.addItem(f"{comp['type']} - {comp_id[-6:]}", comp_id)
        
        signal_layout.addWidget(signal_label)
        signal_layout.addWidget(signal_combo)
        
        # Signal type selection
        type_group = QWidget()
        type_layout = QVBoxLayout(type_group)
        type_layout.setContentsMargins(0, 0, 0, 0)
        type_label = QLabel("Signal Type:")
        type_combo = QComboBox()
        type_combo.addItems(["Voltage", "Current"])
        type_layout.addWidget(type_label)
        type_layout.addWidget(type_combo)
        
        # Window selection for professional FFT
        window_group = QWidget()
        window_layout = QVBoxLayout(window_group)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_label = QLabel("Window Function:")
        window_combo = QComboBox()
        window_combo.addItems(["Rectangular", "Hamming", "Hann", "Blackman", "Flat Top"])
        window_layout.addWidget(window_label)
        window_layout.addWidget(window_combo)
        
        # Add frequency range control
        freq_group = QWidget()
        freq_layout = QVBoxLayout(freq_group)
        freq_layout.setContentsMargins(0, 0, 0, 0)
        freq_label = QLabel("Frequency Range:")
        freq_slider = QSlider(Qt.Horizontal)
        freq_slider.setRange(1, 100)
        freq_slider.setValue(50)
        freq_slider.setTickPosition(QSlider.TicksBelow)
        freq_layout.addWidget(freq_label)
        freq_layout.addWidget(freq_slider)
        
        # Add measurement display for dominant frequency
        freq_value_label = QLabel("0.00 Hz")
        freq_value_label.setStyleSheet("""
            font-family: 'Courier New';
            font-size: 14px;
            font-weight: bold;
            color: #D62828;
            padding: 4px;
            border: 1px solid #CCCCCC;
            background-color: white;
            min-width: 120px;
            qproperty-alignment: AlignCenter;
        """)
        
        # Add all controls to layout
        control_layout.addWidget(signal_group)
        control_layout.addWidget(type_group)
        control_layout.addWidget(window_group)
        control_layout.addWidget(freq_group)
        control_layout.addStretch(1)
        control_layout.addWidget(freq_value_label)
        
        layout.addWidget(control_panel)
        
        # Create professional canvas
        canvas = AnimatedMatplotlibCanvas(dialog, width=6, height=4, dpi=100)
        canvas.fig.patch.set_facecolor('#F6F6F6')
        canvas.axes.set_facecolor('#FFFFFF')
        canvas.setup_plot("Frequency Spectrum", "Frequency (Hz)", "Magnitude (dB)")
        
        # Add toolbar with professional styling
        toolbar_layout = QHBoxLayout()
        toolbar_layout.addWidget(canvas.toolbar)
        toolbar_layout.addStretch(1)
        layout.addLayout(toolbar_layout)
        
        # Add the canvas as the main element
        layout.addWidget(canvas, stretch=1)
        
        # Setup professional FFT calculation and plotting function
        def calculate_fft(signal, sample_rate, window_type):
            n = len(signal)
            
            # Apply window function with professional options
            if window_type == "Hamming":
                window = np.hamming(n)
            elif window_type == "Hann":
                window = np.hanning(n)
            elif window_type == "Blackman":
                window = np.blackman(n)
            elif window_type == "Flat Top":
                # Better for amplitude accuracy
                window = np.array([0.21557895, 0.41663158, 0.277263158, 0.083578947, 0.006947368])
                window = np.resize(window, n)  # Extend to full signal length
            else:  # Rectangular
                window = np.ones(n)
                
            # Apply window and calculate FFT with zero padding for better frequency resolution
            windowed_signal = signal * window
            fft_result = np.fft.rfft(windowed_signal, n=n*2)  # 2x zero padding
            
            # Calculate magnitude in dB with improved scaling
            magnitude = 20 * np.log10(np.abs(fft_result) + 1e-10)  # Add small value to avoid log(0)
            
            # Calculate frequency bins with proper scaling
            freq_bins = np.fft.rfftfreq(n*2, d=1/sample_rate)
            
            return freq_bins, magnitude
        
        # Animation update function with professional spectrum display
        def update_spectrum(frame):
            canvas.axes.clear()
            canvas.axes.set_facecolor('#FFFFFF')
            canvas.axes.grid(True, linestyle='--', alpha=0.7, color='#CCCCCC')
            
            # Get selected signal
            if signal_combo.count() > 0:
                comp_id = signal_combo.currentData()
                signal_type = type_combo.currentText().lower()
                window_type = window_combo.currentText()
                
                # Get data based on signal type
                if signal_type == "voltage" and comp_id in voltage_data:
                    signal_data = voltage_data[comp_id]
                    label = f"Voltage Spectrum - {self.canvas.simulator.components[comp_id]['type']}"
                    color = '#1E5128'  # Green color theme
                elif signal_type == "current" and comp_id in current_data:
                    signal_data = current_data[comp_id]
                    label = f"Current Spectrum - {self.canvas.simulator.components[comp_id]['type']}"
                    color = '#D62828'  # Red color theme
                else:
                    # No data, show empty plot with professional grid
                    canvas.axes.text(0.5, 0.5, "No data available for selected channel", 
                                    ha='center', va='center',
                                    transform=canvas.axes.transAxes,
                                    fontsize=12, color='gray')
                    canvas.axes.set_xlabel("Frequency (Hz)")
                    canvas.axes.set_ylabel("Magnitude (dB)")
                    return canvas.axes
                
                # Calculate sample rate from time points
                if len(time_points) > 1:
                    sample_rate = 1 / (time_points[1] - time_points[0])
                else:
                    sample_rate = 1000  # Default if we can't determine
                    
                # Calculate FFT
                freq, magnitude = calculate_fft(signal_data, sample_rate, window_type)
                
                # Apply frequency range adjustment based on slider
                max_freq = min(sample_rate/2, 1000)  # Nyquist limit or 1kHz max
                freq_scale = freq_slider.value() / 100.0  # 0-1 scale
                plot_max_freq = max_freq * freq_scale
                if plot_max_freq < 1:
                    plot_max_freq = max_freq  # Ensure we show something
                
                # Find plot data range based on selected frequency range
                freq_mask = freq <= plot_max_freq
                plot_freq = freq[freq_mask]
                plot_magnitude = magnitude[freq_mask]
                
                # Plot frequency spectrum with professional styling
                canvas.axes.plot(
                    plot_freq, 
                    plot_magnitude, 
                    color=color, 
                    label=label,
                    linewidth=1.5
                )
                canvas.axes.set_xlabel("Frequency (Hz)", fontweight='bold', color='#333333')
                canvas.axes.set_ylabel("Magnitude (dB)", fontweight='bold', color='#333333')
                
                # Limit x-axis to meaningful frequencies with professional scaling
                canvas.axes.set_xlim(0, plot_max_freq)
                
                # Add grid and legend with professional styling
                canvas.axes.legend(loc='upper right', framealpha=0.7)
                
                # Add professional annotation with dominant frequencies
                if len(plot_freq) > 1:
                    # Find peaks in the spectrum using a more professional algorithm
                    if len(plot_magnitude) > 10:  # Need enough points for peak detection
                        # Use higher percentile for cleaner peak detection
                        threshold = np.percentile(plot_magnitude, 95)
                        peak_indices = np.where(plot_magnitude > threshold)[0]
                        
                        # Filter peaks to avoid duplicates (at least 5 indices apart)
                        filtered_peaks = []
                        for idx in peak_indices:
                            if not filtered_peaks or all(abs(idx - p) > 5 for p in filtered_peaks):
                                filtered_peaks.append(idx)
                        
                        if filtered_peaks:
                            # Sort by magnitude
                            filtered_peaks.sort(key=lambda i: plot_magnitude[i], reverse=True)
                            
                            # Take top 3 peaks max for clarity
                            display_peaks = filtered_peaks[:min(3, len(filtered_peaks))]
                            
                            # Show peak markers and annotations
                            for i, peak_idx in enumerate(display_peaks):
                                peak_freq = plot_freq[peak_idx]
                                peak_mag = plot_magnitude[peak_idx]
                                
                                # Plot peak marker
                                canvas.axes.plot(
                                    peak_freq, 
                                    peak_mag, 
                                    'o', 
                                    color='#D62828' if i == 0 else '#4E9F3D', 
                                    markersize=6
                                )
                                
                                # Add measurement text
                                canvas.axes.axvline(
                                    x=peak_freq, 
                                    color='#D62828' if i == 0 else '#4E9F3D', 
                                    linestyle='--', 
                                    alpha=0.6,
                                    linewidth=1
                                )
                                
                                # Add frequency label
                                canvas.axes.text(
                                    peak_freq, 
                                    peak_mag + 2,
                                    f"{peak_freq:.1f} Hz",
                                    ha='center',
                                    va='bottom',
                                    rotation=90,
                                    color='#D62828' if i == 0 else '#4E9F3D',
                                    fontsize=8
                                )
                            
                            # Update frequency label for dominant (first) peak
                            if len(display_peaks) > 0:
                                dominant_freq = plot_freq[display_peaks[0]]
                                freq_value_label.setText(f"{dominant_freq:.2f} Hz")
                            else:
                                freq_value_label.setText("N/A")
                            
            return canvas.axes
        
        # Connect control changes to update the plot
        def update_view():
            # Force animation update
            if hasattr(canvas, 'animations') and canvas.animations:
                canvas.animations[0].event_source.start()
        
        signal_combo.currentIndexChanged.connect(update_view)
        type_combo.currentIndexChanged.connect(update_view)
        window_combo.currentIndexChanged.connect(update_view)
        freq_slider.valueChanged.connect(update_view)
        
        # Add professional close button
        close_button = QPushButton("Close")
        close_button.setStyleSheet("""
            background-color: #1E5128;
            color: white;
            font-weight: bold;
            border-radius: 4px;
            padding: 6px;
            min-width: 80px;
        """)
        close_button.clicked.connect(dialog.close)
        
        # Add button to layout
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        # Start the animation
        anim = canvas.start_animation(update_spectrum, interval=100)
        
        # Show dialog
        dialog.exec()

class ComponentMimeData(QMimeData):
    def __init__(self):
        super().__init__()
        self.component = None
        self.setData("application/x-component", b"component")

class Probe(QGraphicsItem):
    """Measurement probe for circuit simulation"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)  # Add this to ensure proper movement
        self.setAcceptHoverEvents(True)
        self.hover = False
        self.measurement_type = "voltage"  # or "current"
        self.value = 0.0
        self.probe_color = QColor(220, 50, 50)
        self.setZValue(5)  # Above wires, below component highlights
        
        # Add connection properties
        self.connected_component = None
        self.connected_wire = None
        self.connection_point = None
        self.connection_line = None  # Line showing connection
        
    def boundingRect(self):
        return QRectF(-15, -15, 30, 30)  # Slightly larger bounding box
    
    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw probe body
        if self.isSelected():
            painter.setBrush(QBrush(QColor(255, 200, 200)))
            painter.setPen(QPen(QColor(220, 0, 0), 2))
        elif self.hover:
            painter.setBrush(QBrush(QColor(255, 230, 230)))
            painter.setPen(QPen(self.probe_color, 1.5))
        else:
            painter.setBrush(QBrush(QColor(240, 240, 240)))
            painter.setPen(QPen(self.probe_color, 1.5))
        
        # Draw background for indicator
        if self.connected_component:
            # Draw a connection indicator behind the probe
            painter.setBrush(QBrush(QColor(180, 255, 180, 100)))
            painter.setPen(QPen(QColor(0, 150, 0, 150), 1, Qt.DashLine))
            painter.drawEllipse(QRectF(-12, -12, 24, 24))
            
        # Draw different shapes for voltage vs current probes with improved visibility
        if self.measurement_type == "voltage":
            painter.drawEllipse(QRectF(-8, -8, 16, 16))
            painter.setPen(QPen(QColor(0, 0, 0), 1.5))
            painter.drawText(QRectF(-5, -5, 10, 10), Qt.AlignCenter, "V")
        else:
            painter.drawRect(QRectF(-8, -8, 16, 16))
            painter.setPen(QPen(QColor(0, 0, 0), 1.5))
            painter.drawText(QRectF(-5, -5, 10, 10), Qt.AlignCenter, "I")
            
        # Add small hint text
        hint_font = painter.font()
        hint_font.setPointSize(6)
        painter.setFont(hint_font)
        painter.setPen(QPen(QColor(80, 80, 80)))
        painter.drawText(QRectF(-15, -20, 30, 10), Qt.AlignCenter, "Right-click to switch")
            
        # Show measurement value with enhanced visibility
        if hasattr(self, 'value') and self.value is not None:
            font = painter.font()
            font.setPointSize(8)
            font.setBold(True)
            painter.setFont(font)
            
            if self.measurement_type == "voltage":
                text = f"{self.value:.2f}V"
                painter.setPen(QPen(QColor(180, 0, 0), 1.5))
            else:
                text = f"{self.value*1000:.1f}mA"
                painter.setPen(QPen(QColor(0, 0, 180), 1.5))
            
            # Draw with better background
            bg_rect = QRectF(-25, 8, 50, 14)
            painter.setBrush(QBrush(QColor(255, 255, 220, 220)))
            painter.drawRoundedRect(bg_rect, 3, 3)
            painter.drawText(bg_rect, Qt.AlignCenter, text)
            
            # Add component name if connected
            if self.connected_component:
                comp_name = self.connected_component.component.name
                font.setPointSize(6)
                painter.setFont(font)
                painter.setPen(QPen(QColor(0, 100, 0)))
                painter.drawText(QRectF(-25, 22, 50, 10), Qt.AlignCenter, f"on {comp_name}")
    
    def hoverEnterEvent(self, event):
        self.hover = True
        self.update()
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        self.hover = False
        self.update()
        super().hoverLeaveEvent(event)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.toggleMeasurementType()
        super().mousePressEvent(event)
        
    def toggleMeasurementType(self):
        """Toggle between voltage and current measurement"""
        self.measurement_type = "current" if self.measurement_type == "voltage" else "voltage"
        self.update()
    
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            # When moving, update the connection line if we have one
            if self.connection_line and self.scene():
                # Moving probe: get the new position and update connection line
                scene = self.scene()
                if self.connection_line in scene.items():
                    scene.removeItem(self.connection_line)
                self.connection_line = None
                
        elif change == QGraphicsItem.ItemPositionHasChanged:
            # After moving, check for nearby components to connect to
            if self.scene():
                self.findNearbyComponent()
                
        return super().itemChange(change, value)
        
    def findNearbyComponent(self):
        """Find nearby component to connect to"""
        if not self.scene():
            return
            
        scene = self.scene()
        nearest_component = None
        min_dist = float('inf')
        connection_point = None
        
        # Check components first
        for item in scene.items():
            if isinstance(item, ComponentItem):
                # Check each pin on the component
                for pin_idx, pin in enumerate(item.pin_points):
                    # Get rotation-adjusted pin position
                    angle_rad = item.rotation() * math.pi / 180
                    rotated_pin = QPointF(
                        pin.x() * math.cos(angle_rad) - pin.y() * math.sin(angle_rad),
                        pin.x() * math.sin(angle_rad) + pin.y() * math.cos(angle_rad)
                    )
                    pin_pos = item.pos() + rotated_pin
                    
                    # Calculate distance to this pin
                    dist = ((pin_pos.x() - self.pos().x())**2 + 
                            (pin_pos.y() - self.pos().y())**2)**0.5
                    
                    if dist < min_dist and dist < 30:  # Snap distance
                        min_dist = dist
                        nearest_component = item
                        connection_point = pin_pos
                        
        # If we found a component to connect to
        if nearest_component and connection_point:
            self.connected_component = nearest_component
            self.connection_point = connection_point
            
            # Create connection line
            self.connection_line = QGraphicsLineItem(
                self.pos().x(), self.pos().y(), 
                connection_point.x(), connection_point.y()
            )
            self.connection_line.setPen(QPen(QColor(200, 0, 0, 180), 2, Qt.DashLine))
            self.connection_line.setZValue(4)  # Below probe but above most items
            scene.addItem(self.connection_line)
            self.update()
        else:
            # No nearby component, remove connection
            self.connected_component = None
            self.connection_point = None
            if self.connection_line:
                scene.removeItem(self.connection_line)
                self.connection_line = None
            self.update()

class SimulationControlPanel(QWidget):
    """Panel with controls for simulation playback"""
    simulationStarted = Signal()
    simulationStopped = Signal()
    simulationReset = Signal()
    simulationSpeedChanged = Signal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumHeight(50)
        self.setupUi()
        
    def setupUi(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        
        # Play/Pause button
        self.playButton = QPushButton("▶ Start")
        self.playButton.setCheckable(True)
        self.playButton.setMaximumWidth(80)
        self.playButton.clicked.connect(self.togglePlayback)
        
        # Reset button
        self.resetButton = QPushButton("⟳ Reset")
        self.resetButton.setMaximumWidth(80)
        self.resetButton.clicked.connect(self.resetSimulation)
        
        # Speed control slider
        self.speedLabel = QLabel("Speed:")
        self.speedSlider = QSlider(Qt.Horizontal)
        self.speedSlider.setRange(1, 20)
        self.speedSlider.setValue(10)
        self.speedSlider.setTickPosition(QSlider.TicksBelow)
        self.speedSlider.setTickInterval(5)
        self.speedSlider.valueChanged.connect(self.speedChanged)
        
        # Time display
        self.timeLabel = QLabel("Time: 0.000s")
        
        # Add widgets to layout
        layout.addWidget(self.playButton)
        layout.addWidget(self.resetButton)
        layout.addWidget(self.speedLabel)
        layout.addWidget(self.speedSlider)
        layout.addWidget(self.timeLabel)
        
        # Set styling
        self.setStyleSheet("""
            QPushButton {
                background-color: #4E9F3D;
                color: white;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:checked {
                background-color: #D62828;
            }
            QPushButton:hover {
                background-color: #D8E9A8;
                color: #1E5128;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #CCCCCC;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: #4E9F3D;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 4px;
            }
        """)
        
    def togglePlayback(self, checked):
        if checked:
            self.playButton.setText("■ Stop")
            self.simulationStarted.emit()
        else:
            self.playButton.setText("▶ Start")
            self.simulationStopped.emit()
            
    def resetSimulation(self):
        self.playButton.setChecked(False)
        self.playButton.setText("▶ Start")
        self.timeLabel.setText("Time: 0.000s")
        self.simulationReset.emit()
        
    def speedChanged(self, value):
        # Convert to a reasonable speed multiplier (0.1x to 2.0x)
        speed = value / 10.0
        self.simulationSpeedChanged.emit(speed)
        
    def updateTime(self, time_value):
        self.timeLabel.setText(f"Time: {time_value:.3f}s")
        
class EnhancedCircuitSimulator(CircuitSimulator):
    """Enhanced simulation with real-time capabilities"""
    
    def __init__(self):
        super().__init__()
        self.probes = []
        self.is_running = False
        self.simulation_thread = None
        self.simulation_speed = 1.0
        self.current_time = 0.0
        self.max_time = 1.0
        self.time_step = 0.001
        self.callbacks = []
        
    def add_probe(self, probe_id, location, measurement_type="voltage"):
        """Add a measurement probe to the circuit"""
        self.probes.append({
            'id': probe_id,
            'location': location,
            'type': measurement_type,
            'values': []
        })
        
    def add_update_callback(self, callback):
        """Add a callback to be called on each simulation update"""
        self.callbacks.append(callback)
        
    def start_simulation(self, duration=1.0, step=0.001):
        """Start a real-time simulation"""
        if self.is_running:
            return
        
        self.current_time = 0.0
        self.max_time = duration
        self.time_step = step
        self.is_running = True
        
        # Start simulation in a separate thread
        self.simulation_thread = threading.Thread(target=self._simulation_loop)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
        
    def stop_simulation(self):
        """Stop the simulation"""
        self.is_running = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=0.5)
            self.simulation_thread = None
            
    def reset_simulation(self):
        """Reset the simulation to initial state"""
        self.stop_simulation()
        self.current_time = 0.0
        
        # Reset probe data
        for probe in self.probes:
            probe['values'] = []
            
        # Notify callbacks of reset
        for callback in self.callbacks:
            callback(reset=True)
        
    def set_speed(self, speed):
        """Set the simulation speed multiplier"""
        self.simulation_speed = speed
        
    def simulate(self, duration=1.0, step=0.001):
        """Run simulation and store the results for later use"""
        # Run the parent class simulation
        self.time_points, self.voltage_data, self.current_data = super().simulate(duration, step)
        
        # Store as instance variables for easier access
        self.duration = duration
        self.step = step
        
        return self.time_points, self.voltage_data, self.current_data
    
    def _simulation_loop(self):
        """Main simulation loop running in a separate thread"""
        try:
            # Pre-compute simulation data
            if not hasattr(self, 'time_points') or self.time_points is None:
                self.time_points, self.voltage_data, self.current_data = self.simulate(self.max_time, self.time_step)
            
            # Real-time simulation loop
            while self.is_running and self.current_time < self.max_time:
                # Find the closest time point index
                time_idx = int(self.current_time / self.time_step)
                if time_idx >= len(self.time_points):
                    break
                
                # Update probe values
                for probe in self.probes:
                    component_id = probe['location']
                    if probe['type'] == 'voltage' and component_id in self.voltage_data:
                        value = self.voltage_data[component_id][time_idx]
                        probe['values'].append((self.current_time, value))
                    elif probe['type'] == 'current' and component_id in self.current_data:
                        value = self.current_data[component_id][time_idx]
                        probe['values'].append((self.current_time, value))
                        
                # Notify callbacks of update
                for callback in self.callbacks:
                    callback(
                        time=self.current_time,
                        time_points=self.time_points[:time_idx+1],
                        voltage_data={k: v[:time_idx+1] for k, v in self.voltage_data.items()},
                        current_data={k: v[:time_idx+1] for k, v in self.current_data.items()}
                    )
                    
                # Increment time based on speed
                self.current_time += self.time_step * self.simulation_speed
                
                # Sleep to control update rate
                time.sleep(0.02)  # ~50 fps max update rate
                
            # One final update at the end
            if self.is_running:
                for callback in self.callbacks:
                    callback(
                        time=self.max_time,
                        time_points=self.time_points,
                        voltage_data=self.voltage_data,
                        current_data=self.current_data,
                        finished=True
                    )
            self.is_running = False
            
        except Exception as e:
            print(f"Simulation error: {str(e)}")
            self.is_running = False

# Fix the animation warning by adding save_count parameter in AnimatedMatplotlibCanvas class
class AnimatedMatplotlibCanvas(MatplotlibCanvas):
    """Enhanced matplotlib canvas with animation support"""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        super().__init__(parent, width, height, dpi)
        self.animations = []
        self.toolbar = NavigationToolbar2QT(self, parent)
        
    def setup_plot(self, title, xlabel, ylabel):
        """Setup the plot with appropriate labels and styling"""
        self.axes.set_title(title)
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
        self.axes.grid(True, linestyle='--', alpha=0.7)
        self.fig.tight_layout()
        
    def start_animation(self, update_func, interval=50):
        """Start a matplotlib animation"""
        # Add save_count parameter to fix the warning
        anim = FuncAnimation(self.fig, update_func, interval=interval, blit=False, 
                             save_count=100)  # Limit frames cached to 100
        self.animations.append(anim)
        return anim
        
    def clear_animations(self):
        """Clear all animations"""
        for anim in self.animations:
            anim.event_source.stop()
        self.animations.clear()
        
    def reset_plot(self):
        """Clear the plot and reset to initial state"""
        self.clear_animations()
        self.axes.clear()
        self.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    window = SmartLab()
    window.show()
    
    sys.exit(app.exec())
