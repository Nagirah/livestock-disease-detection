"""PentAI D01-D04: species-separated, fail-closed dataset pipeline."""
import argparse, csv, hashlib, json, random, shutil, subprocess
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image, ImageOps, UnidentifiedImageError

SPECIES=('goats','cattle')
EXT={'.jpg','.jpeg','.png','.bmp','.webp','.tif','.tiff'}
SPLIT_DIRS={'train','training','valid','validation','val','test','testing','images','image','data','raw'}
FIELD=['species','relative_path','raw_label','canonical_label','status','reason','width','height','format','sha256','group_id','source_id','animal_id','source_group','image_modality']

def write_csv(path, records, fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(records)

def read_csv(path):
    with Path(path).open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def label_from_path(rel):
    dirs=Path(rel).parts[:-1]
    candidates=[s for s in dirs if s.lower() not in SPLIT_DIRS]
    return candidates[-1] if candidates else ''

def extra_meta(folder):
    path=folder/'config'/'image_metadata.csv'
    if not path.exists():return {}
    records=read_csv(path)
    return {(r.get('species','').strip(),r.get('relative_path','').replace('\\','/').strip()):r for r in records}

def audit(root):
    root=Path(root); meta=extra_meta(root); all_records=[]
    for species in SPECIES:
        raw=root/'data'/'raw'/species
        if not raw.exists(): raise SystemExit(f'Missing folder: {raw} (extract ORIGINAL archive there)')
        rows=[]
        for p in sorted(raw.rglob('*')):
            if not p.is_file() or p.suffix.lower() not in EXT:continue
            rel=p.relative_to(raw).as_posix();md=meta.get((species,rel),{})
            r=dict.fromkeys(FIELD,'');r.update(species=species,relative_path=rel,raw_label=md.get('raw_label','').strip() or label_from_path(rel),status='needs_review',source_id=md.get('source_id','').strip(),animal_id=md.get('animal_id','').strip(),source_group=md.get('source_group','').strip(),image_modality=md.get('image_modality','').strip())
            try:
                with Image.open(p) as im:
                    im.verify()
                with Image.open(p) as im:
                    im.load();r.update(width=str(im.width),height=str(im.height),format=str(im.format or ''),sha256=digest(p))
                r['reason']='unmapped_label'
            except (OSError,ValueError,UnidentifiedImageError) as e:
                r.update(status='exclude',reason='corrupt_or_unreadable:'+type(e).__name__)
            rows.append(r)
        hashes=defaultdict(list)
        for r in rows:
            if r['sha256']:hashes[r['sha256']].append(r)
        for same in hashes.values():
            if len(same)>1:
                for r in same[1:]:r['reason']='exact_duplicate_review'
        out=root/'data'/'reports'/('goat_dataset_audit' if species=='goats' else 'cattle_dataset_audit')
        write_csv(out/'audit_manifest.csv',rows,FIELD)
        counts=Counter(r['raw_label'] or 'UNRESOLVED' for r in rows)
        write_csv(out/'raw_class_counts.csv',[{'raw_label':k,'count':v} for k,v in sorted(counts.items())],['raw_label','count'])
        write_csv(out/'duplicate_candidates.csv',[{'sha256':k,'count':len(v),'paths':' | '.join(x['relative_path'] for x in v)} for k,v in hashes.items() if len(v)>1],['sha256','count','paths'])
        (out/'summary.json').write_text(json.dumps({'species':species,'images_found':len(rows),'raw_class_counts':counts,'unreadable':sum(x['status']=='exclude' for x in rows),'exact_duplicate_groups':sum(len(x)>1 for x in hashes.values()),'unresolved_labels':sum(not x['raw_label'] for x in rows)},indent=2),encoding='utf-8')
        print(species,dict(counts),'total',len(rows)); all_records.extend(rows)
    report=root/'data'/'reports'/'consolidated_reports'
    write_csv(report/'combined_audit_manifest.csv',all_records,FIELD)
    print('Audit only: raw files unchanged. Review labels, annotation format, licenses and source provenance.')

def prepare(root,size):
    root=Path(root); mapping_path=root/'config'/'label_mapping.csv'
    maps={(r['species'].strip(),r['raw_label'].strip()):r for r in read_csv(mapping_path) if r.get('approved','').strip().lower()=='yes'}
    metas=extra_meta(root)
    for species in SPECIES:
        folder=root/'data'/'reports'/('goat_dataset_audit' if species=='goats' else 'cattle_dataset_audit')
        rows=read_csv(folder/'audit_manifest.csv'); hashes=set();out=[]
        for r in rows:
            r['canonical_label']='';p=root/'data'/'raw'/species/r['relative_path']
            key=(species,r['raw_label']);m=maps.get(key)
            if r['status']=='exclude':pass
            elif not m:r.update(status='exclude',reason='unapproved_or_unmapped_label')
            elif m.get('canonical_label','').strip()=='':r.update(status='exclude',reason='empty_canonical_label')
            elif r['sha256'] in hashes:r.update(status='exclude',reason='exact_duplicate')
            else:
                r['canonical_label']=m['canonical_label'].strip();r['status']='include';r['reason']='';hashes.add(r['sha256'])
                # Exact duplicates are safely kept in one group and only one copy is processed.
                outpath=root/'data'/'processed'/species/(r['sha256']+'.png')
                outpath.parent.mkdir(parents=True,exist_ok=True)
                with Image.open(p) as im:
                    im=ImageOps.exif_transpose(im).convert('RGB');im.thumbnail((size,size))
                    canvas=Image.new('RGB',(size,size),(0,0,0));canvas.paste(im,((size-im.width)//2,(size-im.height)//2));canvas.save(outpath)
                r['group_id']=r.get('animal_id') or r.get('source_group') or r['sha256']
            out.append(r)
        write_csv(folder/'clean_manifest.csv',out,FIELD)
        write_csv(folder/'exclusion_manifest.csv',[r for r in out if r['status']!='include'],FIELD)
        print(species,'included',sum(x['status']=='include' for x in out),'excluded',sum(x['status']!='include' for x in out))
    (root/'config'/'preprocessing.json').write_text(json.dumps({'size':[size,size],'mode':'RGB','resize':'aspect_preserving_thumbnail_black_padding','interpolation':'Pillow_default','raw_unchanged':True},indent=2))

def assign_groups(rows,seed):
    # Stratification heuristic: allocate intact groups, minimize per-class and total split deviation.
    groups=defaultdict(list)
    for r in rows:
        g='|'.join([r['species'],r.get('source_id',''),r['group_id']]);groups[g].append(r)
    names=['train','validation','test'];targets={'train':.7,'validation':.15,'test':.15}
    allclasses=Counter(r['canonical_label'] for r in rows)
    byclass={c:sum(any(x['canonical_label']==c for x in g) for g in groups.values()) for c in allclasses}
    if any(n<3 for n in byclass.values()):
        raise ValueError(f'Cannot form three independent grouped splits: class group counts {byclass}')
    best=None
    for trial in range(150):
        rng=random.Random(seed+trial);groupitems=list(groups.items());rng.shuffle(groupitems)
        groupitems.sort(key=lambda z:-len(z[1]))
        current={x:Counter() for x in names}; totals=Counter();allocation={}
        for key,grp in groupitems:
            local=Counter(x['canonical_label'] for x in grp)
            choices=[]
            for name in names:
                after=totals.copy();after[name]+=len(grp)
                score=sum((after[n]/len(rows)-targets[n])**2 for n in names)*2
                for cl,num in allclasses.items():
                    for n in names:
                        v=current[n][cl]+(local[cl] if n==name else 0)
                        score+=(v/num-targets[n])**2
                choices.append((score,rng.random(),name))
            chosen=min(choices)[2];allocation[key]=chosen;totals[chosen]+=len(grp);current[chosen].update(local)
        missing=sum(current[n][cl]==0 for cl in allclasses for n in names)
        score=missing*100+sum((totals[n]/len(rows)-targets[n])**2 for n in names)
        if best is None or score<best[0]:best=(score,allocation,current,groups)
        if missing==0:break
    if any(best[2][n][cl]==0 for cl in allclasses for n in names):
        raise ValueError('Group-aware stratification cannot cover all classes in every split. Add verified independent groups; do not force a leaky split.')
    return best[1],best[3]

def split(root,seed):
    root=Path(root);combined=[];review=[]
    for species in SPECIES:
        folder=root/'data'/'reports'/('goat_dataset_audit' if species=='goats' else 'cattle_dataset_audit')
        rows=[r for r in read_csv(folder/'clean_manifest.csv') if r['status']=='include']
        if not rows:raise SystemExit(f'No clean images for {species}')
        if any(not r['group_id'] for r in rows):raise SystemExit('Missing grouping key')
        alloc,groups=assign_groups(rows,seed)
        for key,grp in groups.items():
            for r in grp:r['split']=alloc[key]
        all_hash=defaultdict(set);all_group=defaultdict(set)
        for r in rows:
            all_hash[r['sha256']].add(r['split']);all_group['|'.join([r['species'],r.get('source_id',''),r['group_id']])].add(r['split'])
        if any(len(v)>1 for v in all_hash.values()) or any(len(v)>1 for v in all_group.values()):raise AssertionError('LEAKAGE DETECTED')
        write_csv(folder/'split_manifest.csv',rows,FIELD+['split'])
        counts=Counter((r['canonical_label'],r['split']) for r in rows)
        write_csv(folder/'split_counts.csv',[{'canonical_label':c,'split':s,'count':n} for (c,s),n in sorted(counts.items())],['canonical_label','split','count'])
        combined.extend(rows);review.append({'species':species,'images':len(rows),'groups':len(groups),'class_counts':dict(Counter(r['canonical_label'] for r in rows)),'leakage_detected':False,'warning':'Grouping uses available animal_id/source_group or exact hash. Verify source/animal identity manually; absent metadata cannot prove independence.'})
    out=root/'data'/'reports'/'consolidated_reports';write_csv(out/'split_manifest.csv',combined,FIELD+['split'])
    (out/'leakage_audit.json').write_text(json.dumps({'seed':seed,'results':review},indent=2))
    print('Split manifests generated. Independent animal/source review still required.')

def freeze(root,seed):
    root=Path(root);report=root/'data'/'reports'/'consolidated_reports';required=[report/'split_manifest.csv',report/'leakage_audit.json',root/'config'/'label_mapping.csv',root/'config'/'preprocessing.json']
    if any(not x.exists() for x in required):raise SystemExit('Missing required artifacts: '+str([str(x) for x in required if not x.exists()]))
    rows=read_csv(report/'split_manifest.csv')
    if not rows or set(r['species'] for r in rows)!=set(SPECIES):raise SystemExit('Both species required for freeze')
    try:commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True,stderr=subprocess.DEVNULL).strip()
    except Exception:commit='NOT_RECORDED: Run from the Git repository after committing code.'
    metadata={'dataset_version':'v1','species':list(SPECIES),'split_seed':seed,'code_commit':commit,'image_count':len(rows),'counts_by_species':dict(Counter(r['species'] for r in rows)),'files':{str(p.relative_to(root)):digest(p) for p in required},'approval':'PENDING: inspect labels, provenance, licenses, grouping and independent rerun','data_policy':'raw and processed images excluded from Git; store in access-controlled shared storage'}
    target=root/'data'/'reports'/'dataset_v1_metadata.json';target.write_text(json.dumps(metadata,indent=2))
    print('Version metadata drafted (PENDING APPROVAL); no claim of independently verified rerun.')

def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['audit','prepare','split','freeze']);p.add_argument('--root',default='.');p.add_argument('--size',type=int,default=256);p.add_argument('--seed',type=int,default=42);a=p.parse_args()
    {'audit':lambda:audit(a.root),'prepare':lambda:prepare(a.root,a.size),'split':lambda:split(a.root,a.seed),'freeze':lambda:freeze(a.root,a.seed)}[a.command]()
if __name__=='__main__':main()
