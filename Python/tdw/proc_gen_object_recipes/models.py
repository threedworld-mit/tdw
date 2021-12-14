BREAD = {'b03_loafbread': [0.15148828, 0.09381004, 0.3470852],
         'bread': [0.2035294, 0.11276271, 0.2124076]}
COFFEE_GRINDERS = {'b05_coffee_grinder': [0.2721527, 0.2983497, 0.19045453],
                   'cafe_2010': [0.2010554, 0.26667593, 0.13285805],
                   'cgaxis_models_61_17_vray': [0.11897779, 0.2590645, 0.11897781],
                   'coffee_grinder': [0.17285534, 0.2945589, 0.07320619],
                   'juicer': [0.2056412, 0.28587507, 0.2247637],
                   'kitchen_aid_coffee_grinder': [0.2979244, 0.40342001, 0.17610921]}
TABLE_LAMPS = {'kevin_reilly_pattern_table_lamp': [0.4218154, 0.78700153, 0.3691399],
               'lamp_02': [0.4670802, 0.6642901, 0.4670806],
               'spunlight_designermesh_lamp': [0.3978088, 0.5867645, 0.4]}
SOAP_DISPENSERS = {'b05_bathroom_dispenser': [0.04740774, 0.1708347, 0.04748672],
                   'b05_gold_glass_soap_dispenser(max)': [0.09301383, 0.22093621, 0.07729675],
                   'blue_edition_liquid_soap02': [0.07494182, 0.1512459, 0.07495788],
                   'filler_2010': [0.09291648, 0.221072, 0.0912154],
                   'kosmos_black_soap_dispenser': [0.05721118, 0.1808983, 0.1152012],
                   'soap_dispenser_01': [0.09130011, 0.1850001, 0.07102962]}
DISHWASHERS = {'b03_db_apps_tech_08_04_composite': [0.6075255, 0.8113788, 0.6072918],
               'b03_db_apps_tech_08_07_composite': [0.5861948, 0.80912516, 0.6202008],
               'b03_db_apps_tech_08_08_composite': [0.622282, 0.85002966, 0.6418053],
               'b04_db_apps_tech_08_03': [0.6013624, 0.84944736, 0.5987592],
               'b05_db_apps_tech_08_09': [0.6442321, 0.88849706, 0.6115834],
               'b05_db_apps_tech_08_09_composite': [0.644232, 0.88849706, 0.611584],
               'dishwasher_4': [0.5912286, 0.80018996, 0.6539202],
               'vray_032': [0.5681047, 1.00033406, 0.5080086]}
REFRIGERATORS = {'b03_ka90ivi20r_2013__vray': [0.9108776, 1.76716712, 0.6892624],
                 'b05_db_apps_tech_06_02_2': [0.8143889, 1.60927512, 0.6852298],
                 'b05_ikea_nutid_side_by_side_refrigerator': [1.1336582, 1.75141412, 1.0578756],
                 'fridge_large': [0.9118316, 1.76000006, 0.7813477]}

q = {"bread": BREAD,
     "coffee_grinder": COFFEE_GRINDERS,
     "table_lamp": TABLE_LAMPS,
     "soap_dispenser": SOAP_DISPENSERS,
     "dishwasher": DISHWASHERS,
     "refridgerator": REFRIGERATORS}
from pathlib import Path
import json
Path("models.json").write_text(json.dumps(q, sort_keys=True, indent=2))
