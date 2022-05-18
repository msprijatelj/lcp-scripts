import json
import sys

def add_parent_id(data, frame_map):
    for d in data:
        license_id = ""
        license_name = d.get('license')
        if license_name and license_name != 'GMS' and d.get('source'):
            license_id = frame_map[license_name]
        elif variant_name := d.get('variant'):
            license_id = frame_map[variant_name]
        elif "mechtype" in d:
            license_id = d['id']
        d["license_id"] = license_id

def add_parent_ids_to_file(filename, frame_file):
    with open(filename, 'r+', encoding='utf-8') as f:
        data = json.load(f)
    
    with open(frame_file, 'r+', encoding='utf-8') as f:
        frame_data = json.load(f)
    
    frame_map = {f['name']: f['id'] for f in frame_data}
    add_parent_id(data, frame_map)

    outfilename = f"{filename.split('.json')[0]}_new.json"
    with open(outfilename, 'w+', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    frame_fn = sys.argv[1] # path/filename for the `frames.json` to pull from
    fn = sys.argv[2] # path/filename for the licensed gear/variant frames
    add_parent_ids_to_file(fn, frame_fn)