#!/usr/bin/env python3
"""Vendor a minimal bicep-types-az excerpt into the pack.

Extracts the ResourceType Microsoft.Storage/storageAccounts@2022-09-01 plus
the transitive $ref closure of its body from a bicep-types-az types.json,
re-indexes the closure consistently, and writes the frozen manifest
sources/vendor/bicep-types/storage.json.

Frozen-manifest law: the output is ONE self-contained JSON manifest with
internally consistent #/N indices; consumers read it whole (concatenate),
never import type nodes across manifests.
"""
import json
import os

UPSTREAM = os.environ.get(
    "BICEP_TYPES_AZ",
    "/Users/sac/bicep-types-az/generated/storage_0/"
    "microsoft.storage/2022-09-01/types.json",
)
OUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "vendor/bicep-types/storage.json"
)


def collect_refs(node, acc):
    if isinstance(node, dict):
        if "$ref" in node:
            acc.append(int(node["$ref"].split("/")[-1]))
        for v in node.values():
            collect_refs(v, acc)
    elif isinstance(node, list):
        for v in node:
            collect_refs(v, acc)


def remap(node, index):
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            if k == "$ref":
                out[k] = "#/" + str(index[int(v.split("/")[-1])])
            else:
                out[k] = remap(v, index)
        return out
    if isinstance(node, list):
        return [remap(v, index) for v in node]
    return node


def main():
    src = json.load(open(UPSTREAM))
    root = None
    for i, t in enumerate(src):
        if t.get("$type") == "ResourceType" and t.get("name") == RESOURCE_NAME:
            root = i
            break
    if root is None:
        raise SystemExit("resource type not found: " + RESOURCE_NAME)
    keep = {root}
    stack = [root]
    while stack:
        i = stack.pop()
        refs = []
        collect_refs(src[i], refs)
        for r in refs:
            if r not in keep:
                keep.add(r)
                stack.append(r)
    index = {}
    for new, old in enumerate(sorted(keep)):
        index[old] = new
    out = []
    for old in sorted(keep):
        out.append(remap(src[old], index))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    print("vendored %d -> %d type nodes; root #%d" % (len(src), len(out), index[root]))


RESOURCE_NAME = "Microsoft.Storage/storageAccounts@2022-09-01"

if __name__ == "__main__":
    main()
