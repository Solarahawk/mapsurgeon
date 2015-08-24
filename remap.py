#!/usr/bin/python
# -*- coding: utf-8 -*-
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

    if parser.has_option('paths', 'output_root'):
        OUTPUT_ROOT = parser.get('paths', 'output_root')
    else:
        print "Configuration error: the mapsurgeon.ini file is missing the 'output_root' setting. Please fix or restore the settings and try again."
        quit()

    if parser.has_option('paths', 'map_path'):
        MAP_PATH = parser.get('paths', 'map_path')
    else:
        print "Configuration error: the mapsurgeon.ini file is missing the 'map_path' setting. Please fix or restore the settings and try again."
        quit()
else:
    print "Configuration error: the mapsurgeon.ini file is missing the [paths] section. Please fix or restore the settings and try again."
    quit()

if parser.has_section('filenames'):
    if parser.has_option('filenames', 'source_map'):
        SOURCE_MAP = parser.get('filenames', 'source_map')
    else:
        print "Configuration error: the mapsurgeon.ini file is missing the 'source_map' setting. Please fix or restore the settings and try again."
        quit()

    if parser.has_option('filenames', 'output_map'):
        OUTPUT_MAP = parser.get('filenames', 'output_map')
    else:
        print "Configuration error: the mapsurgeon.ini file is missing the 'output_map' setting. Please fix or restore the settings and try again."
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


def export_sorted_map(tree):
    """Sort sectors and gates, and output map to disk
       Sorting is probably not strictly necessary, but it helps with ensuring
       human-readability, and to maintain consistency with the vanilla map
       (as much as is possible.)
    """

    print "Preparing to export the new map to disk..."
    map_export = ET.Element('universe')

    root = tree.getroot()

    print "Sorting sectors by coordinates..."
    # sort sectors by Y,X coordinates
    data = []
    for elem in root:
        y = int(elem.get('y'))
        x = int(elem.get('x'))
        data.append((y, x, elem))

    data.sort()

    # insert the last item from each tuple
    root[:] = [item[-1] for item in data]

#    print "Reformatting sector entries in XML..."
    # now iterate through sorted sectors and append to map_export tree
    # we export map elements in the following order to reorder the new gates
    # which were appended to the end of the sector element. This
    # places them back in front of the other sector objects, behind the sector
    # background settings.
#    for sector in root:
#        sector_out = ET.SubElement(map_export, 'o', sector.attrib)
#        for background in sector.findall(".//o[@t='2']"):
#            ET.SubElement(sector_out, 'o', background.attrib)
#            # Remove elements from original sector so we later we can easily copy remaining children
#            sector.remove(background)

#        for gate in sector.findall(".//o[@t='18']"):
#            ET.SubElement(sector_out, 'o', gate.attrib)
#            sector.remove(gate)

#        for child in sector:
#            allchildren = list(child.iter())
#            ET.SubElement(sector_out, allchildren)

    # write map_export to disk
    print "Saving the new map to disk..."
    with open(os.path.join(OUTPUT_ROOT, MAP_PATH, OUTPUT_MAP), 'w') as f:
        f.write(prettify(root))
    f.close()

    print "\nMap Surgeon: Done! Your new map has been saved to the Output Package folder: 'output_package\\addons\maps'.\n"
    if gates_default:
        print "New gates added to sectors were placed in default locations."
        print "You need to load your new map in-game, and visually verify each gate is in an appropriate location.\n"
    print "After verifying your map in-game, if you make any adjustments using the Galaxy Editor,\nexport your updated map, and use the provided gen_schema.py utility to generate a Gate\nSchema. This will ensure future map runs will use your adjusted gates."


# Begin of main program routine

parser = argparse.ArgumentParser(description="This utility generates a new X3 universe map using the sector and gate network schema input files.")
parser.add_argument("--version", action='version', version='%(prog)s 1.0')
parser.add_argument("-g", "--usegateschema", help="Use a Gate Schema for gate placement? (0 or 1)", required=True)

parser.add_argument("--inputmap", default=SOURCE_MAP, help="Input file name for original map. (Default: " + SOURCE_MAP + ")")
parser.add_argument("--inputschema", default=REMAP_SCHEMA, help="Input file name for remap schema. (Default: " + REMAP_SCHEMA + ")")
parser.add_argument("--inputnewsectors", default=NEW_SECTORS, help="Input file name for new sectors schema. (Default: " + NEW_SECTORS + ")")
parser.add_argument("--inputgates", default=GATE_SCHEMA, help="Input file name for new gate schema. (Default: " + GATE_SCHEMA + ")")
parser.add_argument("--outputmap", default=OUTPUT_MAP, help="Output file name for new map. (Default: " + OUTPUT_MAP + ")")
args = parser.parse_args()

# Verify input files exist
if not os.path.exists(os.path.join(INPUT_PATH, args.inputmap)):
    print "Source Map,", os.path.join(INPUT_PATH, args.inputmap), "does not exist. Unable to proceed."
    quit()
if not os.path.exists(os.path.join(INPUT_PATH, args.inputschema)):
    print "Remap Schema,", os.path.join(INPUT_PATH, args.inputschema), "does not exist. Unable to proceed."
    quit()
if not os.path.exists(os.path.join(INPUT_PATH, args.inputnewsectors)):
    print "New sectors schema,", os.path.join(INPUT_PATH, args.inputnewsectors), "does not exist. Unable to proceed."
    quit()
if not os.path.exists(os.path.join(INPUT_PATH, args.inputgates)):
    print "Gate Schema,", os.path.join(INPUT_PATH, args.inputgates), "does not exist. Unable to proceed."
    quit()
if not os.path.exists(os.path.join(OUTPUT_ROOT, MAP_PATH)):
    print "Output Map save path,", os.path.join(OUTPUT_ROOT, MAP_PATH), "does not exist. Unable to proceed."
    quit()


print "Map Surgeon: Loading source map: " + os.path.join(INPUT_PATH, args.inputmap)

# Load original universe map via Element Tree 
map_tree = ET.parse(os.path.join(INPUT_PATH, args.inputmap))
map_root = map_tree.getroot()

print "Loading Remap Schema: " + os.path.join(INPUT_PATH, args.inputschema)

# Load map schema table from CSV into a pandas DataFrame (powerful associative table)
map_schema = pd.read_excel(os.path.join(INPUT_PATH, args.inputschema), REMAP_SHEET, header=0, index_col=None)
map_schema.sort_index(inplace=True)

# remove empty rows
map_schema.dropna(inplace=True, how='all')

# Load gate network schema file, if provided
if int(args.usegateschema) == 1:
    print "Gate Schema has been provided. It will direct the locations of all new gates: ", os.path.join(INPUT_PATH, args.inputgates)
    gates_default = False   # flag to indicate whether default gate attributes, instead of the gate schema
    gate_schema_tree = ET.parse(os.path.join(INPUT_PATH, args.inputgates))
    gate_schema_root = gate_schema_tree.getroot()

else:
    print "No Gate Schema provided. Default gate positions will be used when placing new gates in sectors."    
    gates_default = True

# Loop through sectors flagged in map schema for removal and find each sector in the XML tree
# then remove it and its children
print "Deleting unneeded sectors..."
del_sectors = map_schema[map_schema.action == -1]
for index, row in del_sectors.iterrows():
    # because Excel stores all numbers as floats, we have pass all retrieved integer values through float() and int() to convert them properly
    x = int(float(row['x1']))
    y = int(float(row['y1']))
    sector = map_root.find(".//o[@x='" + str(x) + "'][@y='" + str(y) + "']")
    map_root.remove(sector)

print "Reassigning sector coordinates and updating gate network..."
# Loop through XML tree again, this time to reassign sector coordinates
for sector in map_root.findall('o'):
    x1 = sector.get('x')    # sector's old x
    y1 = sector.get('y')    # sector's old y

    # lookup current sector in map schema
    sector_schema = map_schema.query('x1 == ' + x1 + ' & y1 == ' + y1)
    current_sector_x = int(float(sector_schema.iloc[0]['x2']))
    current_sector_y = int(float(sector_schema.iloc[0]['y2']))

    sector.set('x', str(current_sector_x))
    sector.set('y', str(current_sector_y))

    # Loop through gate positions (N, S, W, E) and update gates according to map schema
    gate_position = {0: 'gate_n', 1: 'gate_s', 2: 'gate_w', 3: 'gate_e'}
    for gid in gate_position:
        gate = sector.find(".//o[@t='18'][@gid='" + str(gid) + "']")
        gate_here = int(float(sector_schema.iloc[0][gate_position[gid]]))

        if gate is not None:  # There is a gate here
            # check if map schema specifies a gate to be here
            if gate_here == 0:  # No: Remove this gate
                sector.remove(gate)

            else: #YES: Keep this gate and update coordinates, if needed
                if not gates_default:   # we have a gate schema to verify/update this gate (otherwise move on)
                    # Lookup current sector in map schema
                    lookup_sector = gate_schema_root.find(".//o[@x='" + str(current_sector_x) + "'][@y='" + str(current_sector_y) + "']")

                    # then find this gate schema
                    lookup_gate = lookup_sector.find(".//o[@t='18'][@gid='" + str(gid) + "']")

                    # assign schema attributes to current gate
                    gate.attrib = lookup_gate.attrib


        else:  # There is no gate here
            if gate_here == 1:  # Yes: Add a gate here
                if gates_default:  # we don't have a gate schema, so just apply default attributes
                    # First, get the sector size. This will be used to set the position of the gate at the edge of the sector
                    sector_size = sector.get('size')
                    if gid == 0:
                        gate_attrib = {"f" : "1", "t": "18", "s": "0", "x": "0", "y": "0", "z": sector_size, "gid": "0", "gx": str(int(float(sector_schema.iloc[0]['target_n_x']))), "gy": str(int(float(sector_schema.iloc[0]['target_n_y']))), "gtid": "1", "a": "0", "b": "0", "g": "0"}
                    elif gid == 1:
                        gate_attrib = {"f" : "1", "t": "18", "s": "1", "x": "0", "y": "0", "z": "-" + sector_size, "gid": "1", "gx": str(int(float(sector_schema.iloc[0]['target_s_x']))), "gy": str(int(float(sector_schema.iloc[0]['target_s_y']))), "gtid": "0", "a": "32768", "b": "0", "g": "0"}
                    elif gid == 2:
                        gate_attrib = {"f" : "1", "t": "18", "s": "2", "x": "-" + sector_size, "y": "0", "z": "0", "gid": "2", "gx": str(int(float(sector_schema.iloc[0]['target_w_x']))), "gy": str(int(float(sector_schema.iloc[0]['target_w_y']))), "gtid": "3", "a": "16384", "b": "0", "g": "0"}
                    else:
                        gate_attrib = {"f" : "1", "t": "18", "s": "3", "x": sector_size, "y": "0", "z": "0", "gid": "3", "gx": str(int(float(sector_schema.iloc[0]['target_e_x']))), "gy": str(int(float(sector_schema.iloc[0]['target_e_y']))), "gtid": "2", "a": "-16384", "b": "0", "g": "0"}

                    # append gate to current sector
                    ET.SubElement(sector, 'o', gate_attrib)  

                else: # use gate schema
                    # find current sector in gate schema
                    lookup_sector = gate_schema_root.find(".//o[@x='" + str(current_sector_x) + "'][@y='" + str(current_sector_y) + "']")

                    # then find this gate element
                    #print ".//o[@t='18'][@gid='" + str(int(float(gid))) + "']"
                    lookup_gate = lookup_sector.find(".//o[@t='18'][@gid='" + str(gid) + "']")

                    # and append gate to current sector
                    ET.SubElement(sector, 'o', lookup_gate.attrib)


# Finally, load new sectors data and append to map
print "Adding new sectors: ", os.path.join(INPUT_PATH, args.inputnewsectors)
newsectors_tree = ET.parse(os.path.join(INPUT_PATH, args.inputnewsectors))
newsectors_root = newsectors_tree.getroot()

# Loop through sectors flagged in map schema for addition and find each sector
# in the new sector tree and append itand its children to the map
add_sectors = map_schema[map_schema.action == 1]
for index, row in add_sectors.iterrows():
    x = int(float(row['x2']))
    y = int(float(row['y2']))
    newsector = newsectors_root.find(".//o[@x='" + str(x) + "'][@y='" + str(y) + "']")

    newsector_out = ET.SubElement(map_root, 'o', newsector.attrib)
    for child in newsector:
        ET.SubElement(newsector_out, 'o', child.attrib)    

export_sorted_map(map_tree)
