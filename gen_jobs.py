#!/usr/bin/python
# gen_jobs.py - Generate updated Jobs file based on the Remap Schema
import argparse
import pandas as pd
import os

INPUT_PATH = "input/"
OUTPUT_ROOT = "output_package/addons/"
JOBS_PATH = "types/"
OUTPUT_FILENAME = "Jobs.txt"


parser = argparse.ArgumentParser(description="This utility generates the updated Jobs file needed for the new map.")
parser.add_argument("--version", action='version', version='%(prog)s 1.0')
parser.add_argument("--inputjobs", default="Jobs.txt", help="Source Jobs File: input file name")
parser.add_argument("--inputschema", default="remap_schema.csv", help="Input file name for remap schema.")
args = parser.parse_args()

print "Jobs Update Utility: Loading original Jobs file"

# Load Jobs from CSV into a pandas DataFrame (powerful associative table)
jobs = pd.read_csv(INPUT_PATH + args.inputjobs, header=None, delimiter=';', skiprows=1)

# attach column labels
jobs.columns = ["job_id","identifier","max_count","max_per_second","job_script","config_script","job_text_id","unique_ship","override_ship_name","show_race_name","show_corp_name","show_ship_type","show_variant_name","wing_id","ware_list_id","jump_range","idle_rate","respawn_time","ship_subtype","m1","m2","m3","m4","m5","m6","m7","m8","tp","ts","tl","special_tl_flag","ship_type_argon","ship_type_boron","ship_type_split","ship_type_paranid","ship_type_teladi","ship_type_xenon","ship_type_pirate","ship_type_khaak","ship_type_goner","ship_type_atf","ship_type_terran","ship_type_yaki","variant_0_basic","variant_1_vanguard","variant_2_sentinel","variant_3_raider","variant_4_hauler","variant_5_miner","variant_6_super_f","variant_7_tanker","variant_8_tug","variant_9_lux_cruiser","variant_10_slave_trans","variant_11_mil_trans","variant_12_xl","variant_13_extended","variant_14_tanker_xl","variant_15_super_f_xl","variant_advanced","hue_modifier","saturation_modifier","chance_random_race","is_owner_sector","is_core_sector","has_shipyard","has_owner_stations","not_enemy_sector","is_border_sector","limit_to_common_wealth","no_war_sector","invert_flags","sector_x","sector_y","create_in_shupyard","create_in_gate","create_inside_sector","create_outside_sector","create_in_null","chance_ship_docked","reserved","cargo_ext","engine_tuning","rudder_opt.","rotation_accel_limit","owner_race_argon","owner_race_boron","owner_race_split","owner_race_paranid","owner_race_teladi","owner_race_xenon","owner_race_khaak","owner_race_goner","owner_race_atf","owner_race_terran","owner_race_yaki","owner_race_pirate","shield_strength","laser_strength","missile_strength","use_fighter_drones","chance_to_start","trade_skill","agression","morale","fight_skill","npc_id","is_invincible","don't_rebuild","is_hidden_pirate","destroy_oos","rebuild_in_new_sector","fly_average_speed","no_race_logic","military","trader","civilian","fighter","?"]

print "Loading the Remap Schema"
# Load map schema table from CSV into a pandas DataFrame
map_schema = pd.read_csv(INPUT_PATH + args.inputschema)
map_schema.sort_index(inplace=True)

print "Reassign jobs to new sector coordinates"

del_jobs = []
for index, row in jobs.iterrows():
    #skip jobs with no home sector assignment
    if row.sector_x == -1:
        continue

    x = row.sector_x
    y = row.sector_y

    # find matching sector in remap schema
    sector_schema = map_schema.query('x1 == ' + str(x) + ' & y1 == ' + str(y))

    # check if sector is on delete list
    if sector_schema.iloc[0]['action'] == -1:
        # Assign job to new sector if flagged for transfer
        if sector_schema.iloc[0]['transfer_job'] == 1:
            row.sector_x = sector_schema.iloc[0]['job_x']
            row.sector_y = sector_schema.iloc[0]['job_y']
        else:
            # otherwise flag the job for deletion
            del_jobs.append(row.job_id)
    else:
        row.sector_x = sector_schema.iloc[0]['x2']
        row.sector_y = sector_schema.iloc[0]['y2']

# delete any jobs previously flagged for removal
if del_jobs:
    jobs = jobs[jobs.job_id.isin(del_jobs) == False]

# save updated jobs file to a temp file
jobs.to_csv(OUTPUT_ROOT + JOBS_PATH + OUTPUT_FILENAME + '_TMP', ';', index=False, header=False)

# and prep the final file, including the special header required by X3
with open(OUTPUT_ROOT + JOBS_PATH + OUTPUT_FILENAME + '_TMP', 'r') as temp_jobs: 
    data = temp_jobs.read()
with open(OUTPUT_ROOT + JOBS_PATH + OUTPUT_FILENAME, 'w') as f:
    f.write("16; // Jobs Updated and Exported by the X3 Map Surgeon utility\n" + data)
f.close()
temp_jobs.close()
os.remove(OUTPUT_ROOT + JOBS_PATH + OUTPUT_FILENAME + '_TMP')

print "\nUpdated Jobs saved to disk. \n\nYou may still need to make other adjustments to the Jobs, \nsuch as altering Max Count for specific jobs that need different spawn rates. \nLitcube's Jobs Editor is highly recommended for this task \n(See included documentation for details.)"




