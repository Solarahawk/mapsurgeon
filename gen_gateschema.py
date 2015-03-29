#!/usr/bin/python
# gen_gateschema.py - Generate Gate Schema XML file for the X3 Remapper utility
import os
from ConfigParser import SafeConfigParser
import argparse
import xml.etree.cElementTree as ET
import pandas
from xml.dom import minidom

# excel worksheets to load files from
REMAP_SHEET = "export_schema"

parser = SafeConfigParser()
found_config = parser.read('mapsurgeon.ini')
if not found_config:
    print "Unable to read 'mapsurgeon.ini'. Now exiting. Please verify the config file is present and readable."
    quit()

if parser.has_section('paths'):
    if parser.has_option('paths', 'input_path'):
        INPUT_PATH = parser.get('paths', 'input_path')
    else:
        print "Configuration error: the mapsurgeon.ini file is missing the 'input_path' setting. Please fix or restore the settings and try again."
        quit()
else:
    print "Configuration error: the mapsurgeon.ini file is missing the [paths] section. Please fix or restore the settings and try again."
    quit()

if parser.has_section('filenames'):
    if parser.has_option('filenames', 'reference_map'):
        REFERENCE_MAP = parser.get('filenames', 'reference_map')
    else:
        print "Configuration error: the mapsurgeon.ini file is missing the 'reference_map' setting. Please fix or restore the settings and try again."
        quit()
    if parser.has_option('filenames', 'remap_schema'):
        REMAP_SCHEMA = parser.get('filenames', 'remap_schema')
    else:
        print "Configuration error: the mapsurgeon.ini file is missing the 'remap_schema' setting. Please fix or restore the settings and try again."
        quit()
 
    if parser.has_option('filenames', 'gate_schema'):
        GATE_SCHEMA = parser.get('filenames', 'gate_schema')
    else:
        print "Configuration error: the mapsurgeon.ini file is missing the 'gate_schema' setting. Please fix or restore the settings and try again."
        quit()
else:
    print "Configuration error: the mapsurgeon.ini file is missing the [filenames] section. Please fix or restore the settings and try again."
    quit()


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ")


parser = argparse.ArgumentParser(description="This utility generates the Gate Network Schema file used by the X3 Remapper Utility.")
parser.add_argument("--version", action='version', version='%(prog)s 1.0')
parser.add_argument("-r", "--referencemap", default=REFERENCE_MAP, help="Reference map: input file name (Default: " + REFERENCE_MAP + ")")
parser.add_argument("-g", "--gatesout", default=GATE_SCHEMA, help="Generate gates schema: output file name (Default: " + GATE_SCHEMA + ")")
args = parser.parse_args()

# Verify input files exist
if not os.path.exists(os.path.join(INPUT_PATH, args.referencemap)):
    print "Input Reference Map,", os.path.join(INPUT_PATH, args.referencemap), "does not exist. Unable to proceed."
    quit()

print "Gate Schema Generator: Loading reference map containing all remapped sectors."

# Load reference map via Element Tree 
map_tree = ET.parse(os.path.join(INPUT_PATH, args.referencemap))
map_root = map_tree.getroot()

# Create a new XML root for exporting
schema_export = ET.Element('universe')

# Iterate through sectors
for sector in map_root.findall('o'):
    sector_out = ET.SubElement(schema_export, 'o', sector.attrib)

    for gate in sector.findall(".//o[@t='18']"):
        gate_out = ET.SubElement(sector_out, 'o', gate.attrib)

print "Saving gate schema to disk."

# Output XML to disk
with open(os.path.join(INPUT_PATH, args.gatesout), 'w') as f:
    f.write(prettify(schema_export))
f.close()

print "\nGate Schema XML saved to disk. \n\nWhen running remap_cli.py, use the '-g 1' argument to implement gates using this schema."
