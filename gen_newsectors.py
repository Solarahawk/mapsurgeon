#!/usr/bin/python
# gen_gateschema.py - Generate Gate Schema XML file for the X3 Remapper utility
import os
from ConfigParser import SafeConfigParser
import argparse
import xml.etree.cElementTree as ET
import pandas as pd
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
        
    if parser.has_option('filenames', 'new_sectors'):
        NEW_SECTORS = parser.get('filenames', 'new_sectors')
    else:
        print "Configuration error: the mapsurgeon.ini file is missing the 'new_sectors' setting. Please fix or restore the settings and try again."
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
parser.add_argument("-s", "--inputschema", default=REMAP_SCHEMA, help="Remap schema: input file name (Default: " + REMAP_SCHEMA + ")")
parser.add_argument("-n", "--sectorsout", default=NEW_SECTORS, help="Generate new sectors schema: output file name (Default: " + NEW_SECTORS + ")")
args = parser.parse_args()

# Verify input files exist
if not os.path.exists(os.path.join(INPUT_PATH, args.referencemap)):
    print "Input Reference Map,", os.path.join(INPUT_PATH, args.referencemap), "does not exist. Unable to proceed."
    quit()
if not os.path.exists(os.path.join(INPUT_PATH, args.inputschema)):
    print "Input Remap Schema,", os.path.join(INPUT_PATH, args.inputschema), "does not exist. Unable to proceed."
    quit()


# Load reference map via Element Tree 
map_tree = ET.parse(os.path.join(INPUT_PATH, args.referencemap))
map_root = map_tree.getroot()


# Create a new XML root for exporting
schema_export = ET.Element('universe')

# Load map schema table from Excel into a pandas DataFrame
map_schema = pd.read_excel(os.path.join(INPUT_PATH, args.inputschema), REMAP_SHEET, header=0, index_col=None)
map_schema.sort_index(inplace=True)

# Loop through sectors flagged in schema for addition and lookup each sector in reference map
add_sectors = map_schema[map_schema.action == 1]
for index, row in add_sectors.iterrows():
    x = int(float(row['x2']))
    y = int(float(row['y2']))
    sector = map_root.find(".//o[@x='" + str(x) + "'][@y='" + str(y) + "']")

    # Append sector to New Sectors Schema
    sector_out = ET.SubElement(schema_export, 'o', sector.attrib)
    for child in sector:
        ET.SubElement(sector_out, 'o', child.attrib)

# Output XML to disk
with open(os.path.join(INPUT_PATH, args.sectorsout), 'w') as f:
    f.write(prettify(schema_export))
f.close()
