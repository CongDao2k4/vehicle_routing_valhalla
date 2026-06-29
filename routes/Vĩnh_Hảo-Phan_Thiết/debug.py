import json

with open("station_tree.json", encoding="utf-8") as f:
    tree = json.load(f)

print(len(tree))

for k in sorted(tree.keys()):
    print(repr(k))

print("kiểm tra csv")

import pandas as pd

df = pd.read_csv("merged_Phan Thiết - Dầu Giây.csv")

for x in sorted(df["epass_name"].dropna().unique()):
    print(repr(str(x)))

print("kiểm tra edges.json")

import json

with open("edges.json", encoding="utf-8") as f:
    edges = json.load(f)

names = set()

for e in edges:
    names.add(e["source"])
    names.add(e["target"])

for x in sorted(names):
    print(repr(x))


print("Kiểm tra sâu")

import json
import unicodedata

with open("edges.json", encoding="utf-8") as f:
    edges = json.load(f)

for e in edges:
    if "Phan Thiết" in e["source"]:
        print("EDGE:")
        print(repr(e["source"]))
        print(
            [hex(ord(c)) for c in e["source"]]
        )

print()

with open("station_tree.json", encoding="utf-8") as f:
    tree = json.load(f)

for k in tree.keys():
    if "Phan Thiết" in k:
        print("TREE:")
        print(repr(k))
        print(
            [hex(ord(c)) for c in k]
        )