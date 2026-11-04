#!/usr/bin/env python3
"""Mint ontology.ttl from the vendored bicep-types-az frozen manifest.

The ontology is GENERATED, never hand-edited: every typer:TyperSubApp /
typer:TyperOption row is minted from sources/vendor/bicep-types/storage.json
(real Microsoft bicep-types-az schema). Re-run after re-vendoring:

    python3 sources/mint_ontology.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "vendor/bicep-types/storage.json")
OUT = os.path.join(os.path.dirname(HERE), "ontology.ttl")

# ObjectTypePropertyFlags (bicep-types): bitmask
REQUIRED = 1
READ_ONLY = 2
DEPLOY_TIME_CONSTANT = 8


def kebab(name):
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", name)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s1)
    return s2.lower()


def snake(name):
    return kebab(name).replace("-", "_")


def resolve(manifest, node, depth=0):
    """Follow $ref until a concrete type node."""
    while isinstance(node, dict) and "$ref" in node and depth < 32:
        node = manifest[int(node["$ref"].split("/")[-1])]
    return node


def enum_values(manifest, node):
    """UnionType of StringLiterals (optionally + StringType open end)."""
    if not (isinstance(node, dict) and node.get("$type") == "UnionType"):
        return None
    values = []
    open_ended = False
    for el in node.get("elements", []):
        t = resolve(manifest, el)
        tt = t.get("$type")
        if tt == "StringLiteralType":
            values.append(t["value"])
        elif tt == "StringType":
            open_ended = True
        else:
            return None
    return values, open_ended


def python_type(manifest, node):
    t = resolve(manifest, node)
    tt = t.get("$type")
    if tt == "StringType" or tt == "StringLiteralType":
        return "str"
    if tt == "IntegerType":
        return "int"
    if tt == "BooleanType":
        return "bool"
    if tt == "ArrayType":
        return "list[str]"
    return "str"  # Any / ObjectType without flattening -> JSON string


SCALAR = ("StringType", "IntegerType", "BooleanType", "StringLiteralType", "AnyType")


def options_for_object(manifest, obj, prefix=""):
    """Yield (flag, pyname, ptype, required, help, choices, open_enum).

    Mechanical rule: every writable-or-required property becomes a Typer
    option. ReadOnly / DeployTimeConstant-only properties are excluded
    (id / type / apiVersion). Object-typed writable properties are flattened
    one level: their scalar/enum children become --<parent>-<child> flags.
    """
    rows = []
    for pname, prop in obj.get("properties", {}).items():
        flags = prop.get("flags", 0)
        required = bool(flags & REQUIRED)
        if not required and (flags & READ_ONLY or flags & DEPLOY_TIME_CONSTANT):
            continue
        t = resolve(manifest, prop.get("type", {}))
        tt = t.get("$type")
        en = enum_values(manifest, t)
        flat_prefix = prefix + kebab(pname)
        if tt == "ObjectType" and not en:
            body = t
            child_rows = []
            for cp, cprop in body.get("properties", {}).items():
                cf = cprop.get("flags", 0)
                creq = bool(cf & REQUIRED)
                if cf & READ_ONLY or cf & DEPLOY_TIME_CONSTANT:
                    continue
                ct = resolve(manifest, cprop.get("type", {}))
                ctt = ct.get("$type")
                cen = enum_values(manifest, ct)
                if ctt in SCALAR or cen:
                    ptype = "str"
                    if ctt == "IntegerType":
                        ptype = "int"
                    elif ctt == "BooleanType":
                        ptype = "bool"
                    child_rows.append(
                        (
                            "--" + flat_prefix + "-" + kebab(cp),
                            prefix + pname + "_" + cp,
                            ptype,
                            creq,
                            cprop.get("description", ""),
                            cen[0] if cen else None,
                            cen[1] if cen else False,
                        )
                    )
            if child_rows:
                rows.extend(child_rows)
                continue
        ptype = "str"
        if tt == "IntegerType":
            ptype = "int"
        elif tt == "BooleanType":
            ptype = "bool"
        elif tt == "ArrayType":
            ptype = "print-json-list"
        rows.append(
            (
                "--" + flat_prefix,
                prefix + pname,
                ptype,
                required,
                prop.get("description", ""),
                en[0] if en else None,
                en[1] if en else False,
            )
        )
    return rows


def ttl_escape(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def emit():
    manifest = json.load(open(MANIFEST))
    root = 179  # ResourceType index in the frozen manifest
    res = manifest[root]
    if res.get("$type") != "ResourceType":
        raise SystemExit("frozen manifest root is not the ResourceType")
    body = resolve(manifest, res["body"])
    name = res["name"]  # Microsoft.Storage/storageAccounts@2022-09-01
    rp, rest = name.split("/", 1)
    resource, api = rest.split("@")
    app_name = snake(rp.split(".")[1].lower() + "_" + resource.split("/")[-1])
    rows = options_for_object(manifest, body)

    L = []
    A = L.append
    A("@prefix typer: <https://ggen.io/ontology/typer-azure#> .")
    A("@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .")
    A("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .")
    A("@prefix sh:   <http://www.w3.org/ns/shacl#> .")
    A("@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .")
    A("@prefix dct:  <http://purl.org/dc/terms/> .")
    A("")
    A("#################################################################")
    A("# GENERATED by sources/mint_ontology.py from the vendored")
    A("# bicep-types-az frozen manifest")
    A("# (sources/vendor/bicep-types/storage.json; upstream microsoft/")
    A("# bicep-types-az generated/storage_0/microsoft.storage/")
    A("# 2022-09-01/types.json @ 03f72b6d1309458d28f4369d382d701e638b904f).")
    A("# Do not hand-edit: edit upstream schema and re-mint.")
    A("#################################################################")
    A("")
    A("typer:ResourceType a rdfs:Class ; rdfs:label \"bicep resource type\" .")
    A("typer:Property a rdfs:Class ; rdfs:label \"bicep object type property\" .")
    A("typer:TyperSubApp a rdfs:Class ; rdfs:label \"Typer sub-application\" .")
    A("typer:TyperOption a rdfs:Class ; rdfs:label \"Typer command option\" .")
    A("typer:GenerationRule a rdfs:Class ; rdfs:label \"generation rule binding\" .")
    A("")
    A("typer:appName a rdf:Property .")
    A("typer:resourceType a rdf:Property .")
    A("typer:apiVersion a rdf:Property .")
    A("typer:flagName a rdf:Property .")
    A("typer:pythonName a rdf:Property .")
    A("typer:pythonType a rdf:Property .")
    A("typer:required a rdf:Property .")
    A("typer:help a rdf:Property .")
    A("typer:choice a rdf:Property .  # flattened sh:in equivalent")
    A("typer:openEnum a rdf:Property .  # union also admits arbitrary strings")
    A("")
    A("typer:StorageCommandsRule a typer:GenerationRule ;")
    A('    rdfs:label "bicep resource type -> Typer sub-app generation rule" ;')
    A('    typer:fromClass typer:TyperSubApp ;')
    A('    typer:query "queries/typer.rq" ;')
    A('    typer:template "templates/typer_commands.py.tera" ;')
    A('    typer:output "generated/typer_storage.py" .')
    A("")
    A("typer:%s a typer:TyperSubApp ;" % app_name)
    A('    typer:appName "%s" ;' % app_name)
    A('    typer:resourceType "%s" ;' % resource)
    A('    typer:apiVersion "%s" ;' % api)
    A('    typer:commandName "create" ;')
    A('    rdfs:label "az %s create sub-app" .' % kebab(resource.split("/")[-1]))
    for flag, pyname, ptype, required, help_, choices, open_enum in rows:
        indiv = "typer:" + snake(pyname) + "_option"
        A("")
        A("%s a typer:TyperOption ;" % indiv)
        A('    typer:flagName "%s" ;' % flag)
        A('    typer:pythonName "%s" ;' % pyname)
        if ptype == "print-json-list":
            A('    typer:pythonType "list[str] (JSON-encoded)" ;')
        else:
            A('    typer:pythonType "%s" ;' % ptype)
        A('    typer:required "%s"^^xsd:boolean ;' % ("true" if required else "false"))
        if help_:
            A('    typer:help "%s" ;' % ttl_escape(help_[:200]))
        if choices:
            A('    typer:choice "%s" ;' % (" , ".join(choices)))
            if open_enum:
                A('    typer:openEnum "true"^^xsd:boolean ;')
        A("    typer:belongsTo typer:%s ." % app_name)
    with open(OUT, "w") as f:
        f.write("\n".join(L) + "\n")
    print("minted %s: 1 sub-app, %d options" % (OUT, len(rows)))


if __name__ == "__main__":
    emit()
