import sys
import json
import copy
import os

def reduceHeat(npc_classes_data):
    for npc_class in npc_classes_data:
        if heatcap := npc_class['stats'].get('heatcap'):
            npc_class['stats']['heatcap'] = [hc - 2 for hc in heatcap]

def readData(fn):
    data = None
    if os.path.exists(fn):
        with open(fn, 'r+', encoding="utf-8") as f:
            data = json.load(f)
    return data

def writeData(data, fn):
    with open(fn, "w+", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def getHeatCap(npc_class_name, npc_classes_data):
    heat_cap = 0
    for npc_class in npc_classes_data:
        if npc_class["name"] == npc_class_name:
            heat_cap = npc_class["stats"]["heatcap"][0]
    return heat_cap

def addHeatSelf(npc_features_data, npc_classes_data, keep_recharge=True):
    avg_rounds = 8
    avg_heat_cap = 6
    rchg_die_size = 6
    for npc_feature in npc_features_data:
        origin = npc_feature["origin"]
        if origin["type"].lower() == "class":
            heat_cap = getHeatCap(origin["name"], npc_classes_data)
        else:
            heat_cap = avg_heat_cap
        tags = npc_feature.get("tags", [])
        for i, tag in enumerate(tags):
            if tag["id"] == "tg_recharge":
                recharge_val = tag["val"]
                num_uses = (rchg_die_size+1-recharge_val)*avg_rounds/rchg_die_size
                heat_cost = int(heat_cap/num_uses)
                heat_self_tag = {
                    "id": "tg_heat_self",
                    "val": heat_cost
                }
                if keep_recharge:
                    tags.append(heat_self_tag)
                else:
                    tags[i] = heat_self_tag


def main(src, dest):
    npc_classes_data = readData(f"{src}/npc_classes.json")
    npc_features_data = readData(f"{src}/npc_features.json")
    npc_templates_data = readData(f"{src}/npc_templates.json")

    if not os.path.exists(dest):
        os.mkdir(dest)

    reduce_heat = True
    add_heat_self = True
    keep_recharge = True

    if npc_classes_data:
        reduceHeat(npc_classes_data) if reduce_heat else None
        writeData(npc_classes_data, f"{dest}/npc_classes.json")

    if npc_features_data:
        addHeatSelf(npc_features_data, npc_classes_data, keep_recharge=keep_recharge) if add_heat_self else None
        writeData(npc_features_data, f"{dest}/npc_features.json")

    if npc_templates_data:
        writeData(npc_templates_data, f"{dest}/npc_templates.json")


if __name__ == "__main__":
    src = sys.argv[1]
    dest = sys.argv[2]
    main(src, dest)