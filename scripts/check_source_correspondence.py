#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, subprocess, sys, tomllib
from pathlib import Path

class AuditError(ValueError): pass

def read_toml(path: Path):
    with path.open('rb') as f: return tomllib.load(f)

def git_head(root: Path) -> str:
    p=subprocess.run(['git','-C',str(root),'rev-parse','HEAD'],text=True,capture_output=True)
    if p.returncode: raise AuditError(f'cannot resolve source HEAD: {p.stderr.strip()}')
    return p.stdout.strip()

def cargo_workspace_subjects(root: Path):
    doc=read_toml(root/'Cargo.toml'); ws=doc.get('workspace',{}); members=ws.get('members')
    if not isinstance(members,list): raise AuditError('workspace.members missing')
    out=set()
    for member in members:
        manifest=(root/member/'Cargo.toml') if member!='.' else root/'Cargo.toml'
        if not manifest.is_file(): raise AuditError(f'missing member manifest: {member}/Cargo.toml')
        pkg=read_toml(manifest).get('package',{}).get('name')
        if not isinstance(pkg,str) or not pkg: raise AuditError(f'member {member} has no package.name')
        out.add(pkg)
    return out

def ontology_crate_subjects(path: Path, type_iri: str):
    text=path.read_text()
    pat=re.compile(r'(?ms)^\s*[^#\s][^\n]*\n(?:.*?\n)*?\s*a\s+'+re.escape(type_iri)+r'\s*;.*?rdfs:label\s+"([^"]+)"')
    return set(pat.findall(text))

def clap_commands(root: Path, source_dir: str):
    out=set(); base=root/source_dir
    for path in sorted(base.glob('*.rs')):
        if path.name=='mod.rs': continue
        noun=path.stem
        for verb in re.findall(r'#\s*\[\s*verb\s*\(\s*"([^"]*)"\s*\)\s*\]',path.read_text()):
            out.add((noun,verb))
    return out

def ontology_commands(path: Path, command_type: str, noun_pred: str, verb_pred: str):
    text=path.read_text(); out=set()
    # Marketplace command rows are deliberately one Turtle statement per line.
    for stmt in text.splitlines():
        if re.search(r'\ba\s+'+re.escape(command_type)+r'\s*;',stmt):
            n=re.search(re.escape(noun_pred)+r'\s+"([^"]*)"',stmt)
            v=re.search(re.escape(verb_pred)+r'\s+"([^"]*)"',stmt)
            if n and v: out.add((n.group(1),v.group(1)))
    return out

def audit(contract: Path, marketplace: Path, source: Path):
    c=read_toml(contract); expected=c['source']['sha']; observed=git_head(source)
    if observed!=expected: raise AuditError(f'REFUSED_SOURCE_SHA expected={expected} observed={observed}')
    ontology=marketplace/c['projection']['ontology']
    kind=c['audit']['kind']
    if kind=='cargo-workspace':
        actual=cargo_workspace_subjects(source)
        modeled=ontology_crate_subjects(ontology,c['projection']['type'])
    elif kind=='clap-noun-verb':
        actual=clap_commands(source,c['audit'].get('source_dir','src/nouns'))
        modeled=ontology_commands(ontology,c['projection']['type'],c['projection']['noun_predicate'],c['projection']['verb_predicate'])
        ignored={tuple(x) for x in c.get('audit',{}).get('ignored_commands',[])}
        modeled-=ignored
    else: raise AuditError(f'unsupported audit.kind: {kind}')
    missing=sorted(actual-modeled); orphan=sorted(modeled-actual)
    receipt={'contract':contract.as_posix(),'source_sha':observed,'kind':kind,'actual_count':len(actual),'modeled_count':len(modeled),'missing':missing,'orphan':orphan,'status':'ALIVE' if not missing and not orphan else 'REFUSED_SOURCE_DRIFT'}
    print(json.dumps(receipt,sort_keys=True))
    if missing or orphan: raise AuditError(f"REFUSED_SOURCE_DRIFT missing={missing} orphan={orphan}")

def main():
    p=argparse.ArgumentParser(); p.add_argument('contract',type=Path); p.add_argument('--marketplace-root',type=Path,default=Path('.')); p.add_argument('--source-root',type=Path,required=True); a=p.parse_args()
    try: audit(a.contract,a.marketplace_root,a.source_root)
    except AuditError as e: print(str(e),file=sys.stderr); return 2
    return 0
if __name__=='__main__': raise SystemExit(main())
