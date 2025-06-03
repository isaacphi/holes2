#!/usr/bin/env python3
"""
Interactive KiCad Schematic Editor
A high-level wrapper around kiutils for chat-like schematic editing
"""

import re
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import uuid
from kiutils.schematic import Schematic
from kiutils.items.schitems import Wire, Junction, NoConnect, Label
from kiutils.items.common import Position
from kiutils.wires import DrawnWire


class SchematicEditor:
    def __init__(self, schematic_path: str):
        self.path = Path(schematic_path)
        self.sch = Schematic.from_file(str(self.path))
        self.backup_counter = 0
        
        # Build lookup tables for quick access
        self._build_component_map()
        self._build_net_map()
        
    def _build_component_map(self):
        """Build a map of reference designators to symbols"""
        self.components = {}
        for symbol in self.sch.schematicSymbols:
            # Extract reference from properties
            ref = self._get_symbol_reference(symbol)
            if ref:
                self.components[ref] = symbol
                
    def _build_net_map(self):
        """Build a map of net names to net numbers"""
        self.nets = {}
        # This would need to be implemented based on your schematic structure
        
    def _get_symbol_reference(self, symbol):
        """Extract reference designator from symbol"""
        if hasattr(symbol, 'properties'):
            for prop in symbol.properties:
                if prop.key == "Reference":
                    return prop.value.replace('"', '')
        return None
        
    def _get_symbol_pins(self, symbol):
        """Get all pins for a symbol with their positions"""
        pins = []
        # This would need to extract pin information from the symbol library
        # For now, returning empty list - would need to parse lib_symbols
        return pins
        
    def backup(self):
        """Create a backup of current schematic"""
        self.backup_counter += 1
        backup_path = self.path.with_suffix(f'.bak{self.backup_counter}.kicad_sch')
        self.sch.to_file(str(backup_path))
        print(f"Backup saved to: {backup_path}")
        
    def save(self):
        """Save the schematic"""
        self.sch.to_file(str(self.path))
        print(f"Schematic saved to: {self.path}")
        
    def reload(self):
        """Reload schematic from file"""
        self.sch = Schematic.from_file(str(self.path))
        self._build_component_map()
        self._build_net_map()
        print("Schematic reloaded")
        
    def add_wire(self, start: Tuple[float, float], end: Tuple[float, float], net_name: Optional[str] = None):
        """Add a wire between two points"""
        wire = Wire()
        wire.start = Position(X=start[0], Y=start[1])
        wire.end = Position(X=end[0], Y=end[1])
        wire.uuid = str(uuid.uuid4())
        
        # Create a DrawnWire structure
        drawn_wire = DrawnWire()
        drawn_wire.startPoint = wire.start
        drawn_wire.endPoint = wire.end
        drawn_wire.uuid = wire.uuid
        
        self.sch.wires.append(drawn_wire)
        print(f"Added wire from {start} to {end}")
        
    def connect_grounds(self, components: Optional[List[str]] = None):
        """Connect all ground pins together"""
        if components is None:
            # Find all components with GND pins
            components = self._find_components_with_pin("GND")
            
        print(f"Connecting grounds for: {components}")
        # This would need actual implementation based on pin positions
        # For now, just showing the concept
        
    def connect_power(self, voltage: str = "3V3", components: Optional[List[str]] = None):
        """Connect power pins to specified voltage rail"""
        if components is None:
            components = self._find_components_with_pin("VCC", "VDD", "PWR")
            
        print(f"Connecting {voltage} power for: {components}")
        
    def connect_pins(self, pin1: str, pin2: str):
        """Connect two pins specified as 'REF.PIN'"""
        # Parse pin specifications
        ref1, pinname1 = pin1.split('.')
        ref2, pinname2 = pin2.split('.')
        
        print(f"Connecting {pin1} to {pin2}")
        # Would need to look up actual pin positions and add wire
        
    def connect_i2c(self, master: str = "J1", slave: str = "GPIOExtender1"):
        """Connect I2C bus between master and slave"""
        print(f"Connecting I2C from {master} to {slave}")
        # Connect SDA and SCL pins
        self.connect_pins(f"{master}.GPIO2", f"{slave}.SDA")
        self.connect_pins(f"{master}.GPIO3", f"{slave}.SCL")
        
    def list_components(self):
        """List all components in the schematic"""
        for ref, symbol in self.components.items():
            print(f"{ref}: {symbol.libraryIdentifier}")
            
    def list_unconnected(self):
        """List all unconnected pins"""
        # This would analyze the netlist for unconnected pins
        print("Unconnected pins:")
        # Implementation needed
        
    def add_label(self, position: Tuple[float, float], text: str):
        """Add a text label at specified position"""
        label = Label()
        label.text = text
        label.position = Position(X=position[0], Y=position[1])
        label.uuid = str(uuid.uuid4())
        self.sch.labels.append(label)
        print(f"Added label '{text}' at {position}")
        
    def _find_components_with_pin(self, *pin_names):
        """Find all components that have any of the specified pin names"""
        # This would search through component pins
        # For now, returning empty list
        return []
        
    # High-level connection methods
    def wire_stepper_driver(self, driver_ref: str, step_pin: str, dir_pin: str, enable_pin: str):
        """Wire up a stepper driver with common connections"""
        print(f"Wiring stepper driver {driver_ref}")
        # Connect power and ground
        self.connect_pins(f"{driver_ref}.VDD", "+3V3")
        self.connect_pins(f"{driver_ref}.VMOT", "StepperPower1.1")
        self.connect_pins(f"{driver_ref}.GND", "GND")
        
        # Connect control pins
        self.connect_pins(f"{driver_ref}.STEP", step_pin)
        self.connect_pins(f"{driver_ref}.DIR", dir_pin)
        self.connect_pins(f"{driver_ref}.~ENABLE", enable_pin)
        
        # Tie configuration pins
        self.connect_pins(f"{driver_ref}.~RESET", "+3V3")  # Active low, so high = enabled
        self.connect_pins(f"{driver_ref}.~SLEEP", "+3V3")  # Active low, so high = enable