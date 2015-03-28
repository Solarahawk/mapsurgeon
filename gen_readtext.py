#!/usr/bin/python
# gen_readtext.py - Generate updated ReadText file for sector names and descriptions based on the Remap Schema
import os
from ConfigParser import SafeConfigParser
import argparse
import xml.etree.cElementTree as ET
from xml.dom import minidom
import pandas as pd

# excel worksheets to load files from
REMAP_SHEET = "export_schema"
PREPEND_SHEET = "prepend_textnames"
TEXTNAMES_SHEET = "export_textnames"
TEXTDESCR_SHEET = "export_textdescr"

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

    if parser.has_option('paths', 'output_root'):
        OUTPUT_ROOT = parser.get('paths', 'output_root')
    else:
        print "Configuration error: the mapsurgeon.ini file is missing the 'output_root' setting. Please fix or restore the settings and try again."
        quit()

    if parser.has_option('paths', 'text_path'):
        TEXT_PATH = parser.get('paths', 'text_path')
    else:
        print "Configuration error: the mapsurgeon.ini file is missing the 'text_path' setting. Please fix or restore the settings and try again."
        quit()
else:
    print "Configuration error: the mapsurgeon.ini file is missing the [paths] section. Please fix or restore the settings and try again."
    quit()

if parser.has_section('filenames'):
    if parser.has_option('filenames', 'prepend_readtext'):
        PREPEND_READTEXT = parser.get('filenames', 'prepend_readtext')
    else:
        print "Configuration error: the mapsurgeon.ini file is missing the 'prepend_readtext' setting. Please fix or restore the settings and try again."
        quit()

    if parser.has_option('filenames', 'output_readtext'):
        OUTPUT_READTEXT = parser.get('filenames', 'output_readtext')
    else:
        print "Configuration error: the mapsurgeon.ini file is missing the 'output_readtext' setting. Please fix or restore the settings and try again."
        quit()

    if parser.has_option('filenames', 'remap_schema'):
        REMAP_SCHEMA = parser.get('filenames', 'remap_schema')
    else:
        print "Configuration error: the mapsurgeon.ini file is missing the 'remap_schema' setting. Please fix or restore the settings and try again."
        quit()
else:
    print "Configuration error: the mapsurgeon.ini file is missing the [filenames] section. Please fix or restore the settings and try again."
    quit()


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ", encoding="utf-8")


parser = argparse.ArgumentParser(description="This utility generates the updated ReadText file needed for the new map.")
parser.add_argument("--version", action='version', version='%(prog)s 1.0')
parser.add_argument("--inputschema", default=REMAP_SCHEMA, help="Input file name for remap schema. (Default: " + REMAP_SCHEMA + ")")
parser.add_argument("--outputtext", default=OUTPUT_READTEXT, help="Output ReadText File: file name. (Default: " + OUTPUT_READTEXT + ")")
args = parser.parse_args()

# Verify input files exist
if not os.path.exists(os.path.join(INPUT_PATH, args.inputschema)):
    print "Input Remap Schema,", os.path.join(INPUT_PATH, args.inputschema), "does not exist. Unable to proceed."
    quit()
if not os.path.exists(os.path.join(OUTPUT_ROOT, TEXT_PATH)):
    print "Output ReadText save path,", os.path.join(OUTPUT_ROOT, TEXT_PATH), "does not exist. Unable to proceed."
    quit()


print "ReadText Update Utility: Loading updated readtext values"

# Load values for sector names and descriptions from CSV
readtext_pre = pd.read_excel(os.path.join(INPUT_PATH, args.inputschema), PREPEND_SHEET, header=0, index_col=None)
readtext_names = pd.read_excel(os.path.join(INPUT_PATH, args.inputschema), TEXTNAMES_SHEET, header=0, index_col=None)
readtext_descr = pd.read_excel(os.path.join(INPUT_PATH, args.inputschema), TEXTDESCR_SHEET, header=0, index_col=None)

print "Loading the Remap Schema"
# Load map schema table from CSV into a pandas DataFrame
map_schema = pd.read_excel(os.path.join(INPUT_PATH, args.inputschema), REMAP_SHEET, header=0, index_col=None)
map_schema.sort_index(inplace=True)
# remove empty rows and sort
map_schema.dropna(inplace=True, how='all')

names_root = ET.Element('language')
names_root.set('id', '44')

page = ET.SubElement(names_root, 'page')
page.set('id', '350007')
page.set('title', 'Boardcomp. Sectornames')
page.set('descr', 'Names of all sectors (spoken by Boardcomputer)')
page.set('voice', 'yes')

for index, row in readtext_pre.iterrows():
    if row[0] > 0:
        element = ET.SubElement(page, 't', {"id": str(row[0])})
        element.text = row[1]

# append sector names
for index, row in readtext_names.iterrows():
    if row[0] > 0:
        element = ET.SubElement(page, 't', {"id": str(row[0])})
        element.text = row[1]


page = ET.SubElement(names_root, 'page')
page.set('id', '350019')
page.set('title', 'Sector Descriptions WIP')
page.set('descr', 'Sector descriptions for galaxy map')
page.set('voice', 'no')

# append sector descriptions
for index, row in readtext_descr.iterrows():
    if row[0] > 0:
        element = ET.SubElement(page, 't', {"id": str(row[0])})
        element.text = row[1]


with open(os.path.join(OUTPUT_ROOT, TEXT_PATH, args.outputtext), 'w') as f:
    f.write(prettify(names_root))
f.close()

print "Updated readtext file saved to: " + os.path.join(OUTPUT_ROOT, TEXT_PATH, args.outputtext)

