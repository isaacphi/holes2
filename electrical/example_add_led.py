#!/usr/bin/env python3
"""Example: Add a resistor and LED to a schematic"""

from kicad_utils import SchematicEditor

# Open schematic
sch = SchematicEditor("/Users/phil/dev/holes2/electrical/holes/holes.kicad_sch")

# Add an LED with current limiting resistor
led = sch.add_symbol("Device:LED", "D1", 100, 100)
resistor = sch.add_symbol("Device:R", "R1", 100, 90)

# Connect them
sch.add_wire([(100, 92.54), (100, 97.46)])

# Add power connections
sch.add_label("VCC", 100, 87.46, global_label=True)
sch.add_label("GND", 100, 102.54, global_label=True)

# Connect to power
sch.add_wire([(100, 87.46), (100, 87.46)])
sch.add_wire([(100, 102.54), (100, 102.54)])

# Save
sch.save()
