# lcp-scripts
Scratchpad repo for scripts that handle Lancer Content Packs.

## modify_lcp
This Python 3.8+ script currently takes the path to a `frames.json` file and licensed item file (e.g. `weapons.json`, `systems.json`, `mods.json`) and adds a `license_id` field to all objects in to the licensed item file corresponding to the matching frame in the `frames.json` file.  Move the script to the same directory as your LCP files and run in a command line:
```bash
python modify_lcp.py ./frames.json ./{weapons|systems|mods}.json
```
The script will output the changes to a new file with `_new` appended to the filename, e.g. `weapons_new.json`.
