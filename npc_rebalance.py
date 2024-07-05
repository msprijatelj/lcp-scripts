import sys
import json
import os

def reduceHeat(npc_classes_data):
    for npc_class in npc_classes_data:
        if heatcap := npc_class['stats'].get('heatcap'):
            npc_class['stats']['heatcap'] = [hc - 2 for hc in heatcap]

def reduceArmor(npc_classes_data):
    for npc_class in npc_classes_data:
        if armor := npc_class['stats'].get('armor'):
            npc_class['stats']['armor'] = [max(0, arm - 1) for arm in armor]

def readData(fn):
    data = None
    if os.path.exists(fn):
        with open(fn, 'r+', encoding="utf-8") as f:
            data = json.load(f)
    return data

def writeData(data, fn):
    with open(fn, "w+", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def markHb(data, id_prefix="", name_prefix=""):
    for item in data:
        item['id'] = f"{id_prefix}{item['id']}"
        item['name'] = " ".join([name_prefix, item['name']])
        if origin_name := item.get("origin", {}).get("name"):
            item["origin"]["name"] = " ".join([name_prefix, origin_name])
        if base_features := item.get("base_features"):
            item["base_features"] = [f"{id_prefix}{feat}" for feat in base_features]
        if optl_features := item.get("optional_features"):
            item["optional_features"] = [f"{id_prefix}{feat}" for feat in optl_features]               

def getHeatCap(npc_class_name, npc_classes_data):
    heat_cap = 0
    for npc_class in npc_classes_data:
        if npc_class["name"] == npc_class_name:
            heat_cap = npc_class["stats"]["heatcap"][0]
    return heat_cap

def addHeatSelf(npc_features_data, keep_recharge=True):
    rchg_to_heat_map = {
        4: 2,
        5: 3,
        6: 4
    }
    for npc_feature in npc_features_data:
        tags = npc_feature.get("tags", [])
        for i, tag in enumerate(tags):
            if tag["id"] == "tg_recharge":
                recharge_val = tag["val"]
                heat_cost = rchg_to_heat_map[recharge_val]
                heat_self_tag = {
                    "id": "tg_heat_self",
                    "val": heat_cost
                }
                if keep_recharge:
                    tags.append(heat_self_tag)
                else:
                    tags[i] = heat_self_tag

def reduceReliable(npc_features_data):
    for npc_feature in npc_features_data:
        tags = npc_feature.get("tags", [])
        for tag in tags:
            if tag["id"] == "tg_reliable":
                reliable_val = tag["val"]
                rel_vals = reliable_val.strip("{}").split("/")
                new_rel_vals = [str(int(v)-1) for v in rel_vals]
                new_rel_val = "{%s}" % ("/".join(new_rel_vals))
                tag["val"] = new_rel_val

def dataArraytoDict(fn):
    with open(fn, 'r+', encoding="utf-8") as f:
        content = json.load(f)
        items = {item['id']: item for item in content}
        for v in items.values():
            del v['id']
    return items

def mergeClasses(npc_classes_data, mergeDir):
    customClassData = dataArraytoDict(f"{mergeDir}/npc_classes.json")
    for item in npc_classes_data:
        classId = item['id']
        customClassStats = customClassData.get(classId, {'stats': {}})
        item['stats'] = {**item['stats'], **customClassStats['stats']}

def mergeFeatures(npc_features_data, mergeDir):
    customFeatureData = dataArraytoDict(f"{mergeDir}/npc_features.json")
    for i, item in enumerate(npc_features_data):
        featureId = item['id']
        customFeatureStats = customFeatureData.get(featureId, {})
        item = {**item, **customFeatureStats}
        npc_features_data[i] = item

def main(src, dest):
    npc_classes_data = readData(f"{src}/npc_classes.json")
    npc_features_data = readData(f"{src}/npc_features.json")
    npc_templates_data = readData(f"{src}/npc_templates.json")

    if not os.path.exists(dest):
        os.mkdir(dest)

    mark_as_hb = True
    hb_id_prefix = "valk-hr-"
    hb_name_prefix = "!V!"

    reduce_heat = False
    reduce_reliable = True
    reduce_armor = True
    add_heat_self = True
    keep_recharge = True

    merge_classes = False
    merge_features = False
    merge_dir = "merge"

    if npc_classes_data:
        reduceHeat(npc_classes_data) if reduce_heat else None
        reduceArmor(npc_classes_data) if reduce_armor else None
        mergeClasses(npc_classes_data, merge_dir) if merge_classes else None
        markHb(npc_classes_data, id_prefix=hb_id_prefix, name_prefix=hb_name_prefix) if mark_as_hb else None
        writeData(npc_classes_data, f"{dest}/npc_classes.json")

    if npc_features_data:
        addHeatSelf(npc_features_data, keep_recharge=keep_recharge) if add_heat_self else None
        reduceReliable(npc_features_data) if reduce_reliable else None
        mergeFeatures(npc_features_data, merge_dir) if merge_features else None
        markHb(npc_features_data, id_prefix=hb_id_prefix, name_prefix=hb_name_prefix) if mark_as_hb else None
        writeData(npc_features_data, f"{dest}/npc_features.json")

    if npc_templates_data:
        markHb(npc_templates_data, id_prefix=hb_id_prefix, name_prefix=hb_name_prefix) if mark_as_hb else None
        writeData(npc_templates_data, f"{dest}/npc_templates.json")


if __name__ == "__main__":
    src = sys.argv[1]
    dest = sys.argv[2]
    main(src, dest)