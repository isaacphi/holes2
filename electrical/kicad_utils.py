#!/usr/bin/env python3
"""
KiCad Schematic Utilities
General-purpose functions for manipulating KiCad schematics
"""

import uuid
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Union
from kiutils.schematic import Schematic
from kiutils.items.schitems import SchematicSymbol, Wire, Junction, Label, GlobalLabel
from kiutils.items.common import Position
from kiutils.wires import DrawnWire
import kiutils.items.syitems as syitems


class SchematicEditor:
    def __init__(self, path: str):
        self.path = Path(path)
        self.sch = Schematic.from_file(str(self.path))
        
    def save(self, backup: bool = True):
        """Save schematic with optional backup"""
        if backup:
            backup_path = self.path.with_suffix('.bak.kicad_sch')
            self.sch.to_file(str(backup_path))
        self.sch.to_file(str(self.path))
        return self
        
    def add_symbol(self, library_ref: str, reference: str, x: float, y: float, 
                   orientation: int = 0, unit: int = 1) -> SchematicSymbol:
        """Add a symbol to the schematic
        
        Args:
            library_ref: Library reference like "Device:R" or "MCU_Module:RaspberryPi_Zero"
            reference: Reference designator like "R1" or "U1"
            x, y: Position in mm
            orientation: Rotation in degrees (0, 90, 180, 270)
            unit: Unit number for multi-unit symbols
        """
        symbol = SchematicSymbol()
        symbol.libraryIdentifier = library_ref
        symbol.position = Position(X=x, Y=y, angle=orientation)
        symbol.unit = unit
        symbol.uuid = str(uuid.uuid4())
        
        # Add reference property
        ref_prop = syitems.Property()
        ref_prop.key = "Reference"
        ref_prop.value = reference
        ref_prop.position = Position(X=x, Y=y-2.54)  # Above symbol
        ref_prop.effects = syitems.Effects()
        symbol.properties = [ref_prop]
        
        self.sch.schematicSymbols.append(symbol)
        return symbol
        
    def add_wire(self, points: List[Tuple[float, float]]) -> DrawnWire:
        """Add a wire connecting multiple points
        
        Args:
            points: List of (x, y) coordinates in mm
        """
        if len(points) < 2:
            raise ValueError("Wire needs at least 2 points")
            
        wire = DrawnWire()
        wire.points = [Position(X=x, Y=y) for x, y in points]
        wire.uuid = str(uuid.uuid4())
        
        self.sch.wires.append(wire)
        return wire
        
    def add_junction(self, x: float, y: float) -> Junction:
        """Add a junction at specified position"""
        junction = Junction()
        junction.position = Position(X=x, Y=y)
        junction.uuid = str(uuid.uuid4())
        junction.diameter = 0  # Use default
        
        self.sch.junctions.append(junction)
        return junction
        
    def add_label(self, text: str, x: float, y: float, 
                  orientation: int = 0, global_label: bool = False) -> Union[Label, GlobalLabel]:
        """Add a net label
        
        Args:
            text: Label text (net name)
            x, y: Position in mm
            orientation: Text orientation
            global_label: If True, creates a global label
        """
        if global_label:
            label = GlobalLabel()
            label.shape = "input"  # Can be: input, output, bidirectional, tri_state, passive
        else:
            label = Label()
            
        label.text = text
        label.position = Position(X=x, Y=y, angle=orientation)
        label.uuid = str(uuid.uuid4())
        
        if global_label:
            self.sch.globalLabels.append(label)
        else:
            self.sch.labels.append(label)
        return label
        
    def find_symbol(self, reference: str) -> Optional[SchematicSymbol]:
        """Find a symbol by reference designator"""
        for symbol in self.sch.schematicSymbols:
            if hasattr(symbol, 'properties'):
                for prop in symbol.properties:
                    if prop.key == "Reference" and prop.value == reference:
                        return symbol
        return None
        
    def get_symbol_position(self, reference: str) -> Optional[Tuple[float, float]]:
        """Get the position of a symbol"""
        symbol = self.find_symbol(reference)
        if symbol and hasattr(symbol, 'position'):
            return (symbol.position.X, symbol.position.Y)
        return None
        
    def move_symbol(self, reference: str, x: float, y: float):
        """Move a symbol to a new position"""
        symbol = self.find_symbol(reference)
        if symbol:
            symbol.position.X = x
            symbol.position.Y = y
        return self
        
    def connect_points(self, start: Tuple[float, float], end: Tuple[float, float], 
                      label: Optional[str] = None):
        """Connect two points with a wire and optional label"""
        self.add_wire([start, end])
        if label:
            # Add label at midpoint
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2
            self.add_label(label, mid_x, mid_y)
        return self
        
    def create_bus(self, points: List[Tuple[float, float]], name: str):
        """Create a bus with a name"""
        # KiCad uses thick lines for buses
        # This would need bus-specific implementation
        pass
        
    def grid_align(self, value: float, grid: float = 2.54) -> float:
        """Align a coordinate to the grid (default 2.54mm/100mil)"""
        return round(value / grid) * grid


# Convenience functions for common operations
def create_resistor_divider(sch: SchematicEditor, x: float, y: float, 
                           r1_value: str = "10k", r2_value: str = "10k",
                           prefix: str = "R"):
    """Create a voltage divider"""
    # Add resistors
    r1 = sch.add_symbol("Device:R", f"{prefix}1", x, y)
    r2 = sch.add_symbol("Device:R", f"{prefix}2", x, y + 10)
    
    # Connect them
    sch.add_wire([(x, y + 2.54), (x, y + 7.46)])
    
    # Add junction at center
    sch.add_junction(x, y + 5)
    
    return r1, r2


def create_bypass_cap(sch: SchematicEditor, x: float, y: float, 
                     value: str = "100n", ref: str = "C1"):
    """Add a bypass capacitor between power and ground"""
    cap = sch.add_symbol("Device:C", ref, x, y, orientation=90)
    
    # Add power labels
    sch.add_label("VCC", x - 2.54, y, global_label=True)
    sch.add_label("GND", x + 2.54, y, global_label=True)
    
    # Connect
    sch.add_wire([(x - 2.54, y), (x - 1.27, y)])
    sch.add_wire([(x + 1.27, y), (x + 2.54, y)])
    
    return cap


def connect_i2c_bus(sch: SchematicEditor, devices: List[Tuple[str, str, str]]):
    """Connect multiple devices to I2C bus
    
    Args:
        devices: List of (reference, sda_pin, scl_pin) tuples
    """
    # This would connect all devices to common SDA/SCL buses
    pass


# Example of a reusable pattern
def create_connector(sch: SchematicEditor, conn_type: str, pin_count: int, 
                    x: float, y: float, ref: str = "J1"):
    """Create a connector with labels"""
    if conn_type == "pin_header":
        if pin_count == 2:
            symbol_ref = "Connector:Conn_01x02_Pin"
        elif pin_count == 3:
            symbol_ref = "Connector:Conn_01x03_Pin"
        # ... etc
    elif conn_type == "socket_header":
        if pin_count == 2:
            symbol_ref = "Connector:Conn_01x02_Socket"
        # ... etc
            
    return sch.add_symbol(symbol_ref, ref, x, y)
