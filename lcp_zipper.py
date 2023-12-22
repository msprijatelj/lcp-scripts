#!/usr/bin/env python
'''
Original code by withalwhere on Discord, used under MIT License.
'''
import argparse
import dataclasses
from copy import deepcopy
import json
from typing import List, Optional
import zipfile
import fnmatch
import os
from sys import exit

@dataclasses.dataclass
class Dependency:
    name: str
    version: str
    link: str

    def __eq__(self, other):
        return self.name == other.name and self.version == other.version

    def satisfied(self, candidate: "Dependency | Manifest") -> bool:
        return self.name == candidate.name and self.version <= candidate.version
    
    def __str__(self):
        return f"{self.name}-({self.version})"
    

@dataclasses.dataclass
class Manifest:
    name: str
    author: str
    description: str
    version: str
    item_prefix: str = ""
    image_url: str = ""
    website: str = ""
    dependencies: List[Dependency] = dataclasses.field(default_factory=lambda: [])

    def __post_init__(self):
        # dataclasses doesn't handle nested dataclasses well
        self.dependencies = [Dependency(**d) if isinstance(d, dict) else d for d in self.dependencies]
    
    def __str__(self):
        return (f"{self.name} ({self.item_prefix}): {self.description}\n"
                f"Requires: {', '.join(str(d) for d in self.dependencies)}")


    def merge(self, other: "Manifest", name: str = None, combine_prefix: bool = True) -> "Manifest":
        if name is None:
            name = self.name + " + " + other.name
        author = self.author + ", " + other.author
        description = self.description + "\n" + other.name + ": " + other.description
        item_prefix = self.item_prefix + "-" + other.item_prefix if combine_prefix else self.item_prefix
        version = self.version
        image_url = self.image_url
        website = self.website
        # We need to prune out redundant dependencies
        # First, remove our dependency on the other LCP, if we have one
        dependencies = [d for d in self.dependencies if not d.satisfied(other)]
        # Second, remove their dependency on us and any redundant (<= version) dependencies
        dependencies.extend(
            d for d in other.dependencies if not d.satisfied(self) and not any(d.satisfied(d2) for d2 in dependencies)
        )
        return Manifest(name, author, description, item_prefix, version, image_url, website, dependencies)


class LCP:
    def __init__(self, manifest: dict|Manifest, files: dict):
        if type(manifest) == dict:
            self.manifest = Manifest(**manifest)
        else:
            self.manifest = manifest
        self.files = files

    def merge(self, other: "LCP", name: str = None, combine_prefix: bool = True) -> "LCP":
        manifest = self.manifest.merge(other.manifest, name, combine_prefix)
        files = deepcopy(self.files)
        for name, data in other.files.items():
            if name in files:
                files[name].extend(data)
            else:
                files[name] = data
        return LCP(manifest, files)

    def __str__(self):
        return (f"LCP {self.manifest}\n"
                f"Files:\n  {'\n  '.join(f for f in self.files)}")

    @classmethod
    def load(cls, filepath):
        with zipfile.ZipFile(filepath, 'r') as lcp:
            manifest = None
            files = {}
            for f in lcp.namelist():
                data = json.load(lcp.open(f))
                if f == "lcp_manifest.json":
                    manifest = data
                else:
                    files[f] = (data)
            return LCP(manifest, files)
    
    def dump(self, filepath: Optional[str]=None):
        if filepath is None:
            filepath = self.manifest.name + "-" + self.manifest.version + ".lcp"
        with zipfile.ZipFile(filepath, 'w') as lcp:
            with lcp.open("lcp_manifest.json", 'w') as stream:
                data = json.dumps(dataclasses.asdict(self.manifest), ensure_ascii=False, indent=4).encode('utf-8')
                stream.write(data)
            
            for f, d in self.files.items():
                with lcp.open(f, 'w') as stream:
                    data = json.dumps(d, ensure_ascii=False, indent=4).encode('utf-8')
                    stream.write(data)


def get_parser():
    parser = argparse.ArgumentParser(description="A quick hack to zip together multiple .lcp files for easy distribution/installation.")
    parser.add_argument("-n", "--name", type=str, default="new-lcp", help="Name for the resulting LCP")
    parser.add_argument("-dir", "--directory", type=str, default="./lcps", help="Target directory housing the LCPs to merge")
    parser.add_argument("-d", "--description", type=str, default="A zipped LCP file.", help="Optional description for the resulting LCP")
    parser.add_argument("-v", "--version", type=str, default="0.0.0",
                        help="Optional semantic X.Y.Z version for the resulting LCP")
    parser.add_argument("-i", "--item-prefix", type=str, default="", help="Optional item-prefix for sorting")
    parser.add_argument("-m", "--image-url", type=str, default="", help="Optional Image URL")
    parser.add_argument("-w", "--website", type=str, default="", help="Optional Website URL")
    parser.add_argument("-lcps", type=str, nargs="+", help="Two or more LCP filepaths to merge")
    return parser


def _main():
    parser = get_parser()
    args = parser.parse_args()

    if (args.lcps is None):
        fps = [f'{args.directory}/{file}' for file in os.listdir(args.directory) if fnmatch.fnmatch(file, '*.lcp')]
    else:
        fps = args.lcps

    if (len(fps) < 2):
        print("Two or more LCP files are required")
        return 1

    lcps = []
    for lpath in fps:
        lcps.append(LCP.load(lpath))
    combined_manifest = Manifest(name=args.name,
                                author="",
                                description=args.description + " Contains the following LCPs:",
                                item_prefix=args.item_prefix,
                                version=args.version,
                                image_url=args.image_url,
                                website=args.website)
    combined_lcp = LCP(combined_manifest, {})
    for lcp in lcps:
        combined_lcp = combined_lcp.merge(lcp, args.name, combine_prefix=False)
    
    print(combined_lcp)
    combined_lcp.dump()


if __name__ == "__main__":
    exit(_main())