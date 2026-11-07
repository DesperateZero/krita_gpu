#!/usr/bin/env python3
"""Check scheduling mathematics, not product pixels or product performance."""
import hashlib,json,random
from collections import defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent
TILE=64
def intersection(a,b):
    x,y=max(a[0],b[0]),max(a[1],b[1]);r,d=min(a[0]+a[2],b[0]+b[2]),min(a[1]+a[3],b[1]+b[3])
    return (x,y,r-x,d-y) if x<r and y<d else None
def old_fragments(dabs,clips,offset):
    result=[]
    for i,dab in enumerate(dabs):
        for j,clip in enumerate(clips):
            rc=intersection(dab,clip)
            if not rc:continue
            x,y,w,h=rc;bottom=y+h;right=x+w
            while y<bottom:
                row=(y-offset[1])//TILE;end_y=min(bottom,offset[1]+(row+1)*TILE)
                col_x=x
                while col_x<right:
                    col=(col_x-offset[0])//TILE;end_x=min(right,offset[0]+(col+1)*TILE)
                    result.append(((col,row),i,j,(col_x,y,end_x-col_x,end_y-y)))
                    col_x=end_x
                y=end_y
    return result
def oracle(dabs,clips):
    # Original semantic input order, independent of tile splitting/grouping.
    pixels=defaultdict(list)
    for i,(x,y,w,h) in enumerate(dabs):
        for j,(cx,cy,cw,ch) in enumerate(clips):
            for py in range(y,y+h):
                for px in range(x,x+w):
                    if cx<=px<cx+cw and cy<=py<cy+ch:pixels[(px,py)].append((i,j))
    return dict(pixels)
def visits(fragments):
    previous=None;count=0
    for key,*_ in fragments:
        if key!=previous:count+=1
        previous=key
    return count
def render(fragments):
    pixels=defaultdict(list)
    for key,i,j,(x,y,w,h) in fragments:
        for py in range(y,y+h):
            for px in range(x,x+w):pixels[(px,py)].append((i,j))
    return dict(pixels)
def digest(value):return hashlib.sha256(json.dumps(sorted((k,v) for k,v in value.items())).encode()).hexdigest()
cases=[
    dict(name='same_page_100_dabs',dabs=[(2,3,20,18)]*100,clips=[(0,0,64,64)],offset=(0,0)),
    dict(name='four_pages_100_dabs',dabs=[(0,0,128,128)]*100,clips=[(0,0,128,128)],offset=(0,0)),
    dict(name='disjoint_pages',dabs=[(64*i,0,24,12) for i in range(16)],clips=[(0,0,1024,64)],offset=(0,0)),
    dict(name='overlapping_clips_preserve_multiplicity',dabs=[(-20,-15,90,82),(0,0,67,72),(-2,-8,76,80)],
         clips=[(-32,-32,128,128),(2,3,28,19)],offset=(7,-11)),
    dict(name='negative_coordinates_and_offset',dabs=[(-81+i*5,-35+i*3,48,48) for i in range(12)],
         clips=[(-128,-96,96,192),(-32,-96,128,192)],offset=(-17,9)),
    dict(name='empty_and_edge',dabs=[(63,63,2,2),(0,0,0,1),(64,64,1,1)],clips=[(0,0,128,128)],offset=(0,0))]
rng=random.Random(261007144)
for k in range(24):
    cases.append(dict(name=f'generated_{k:02}',dabs=[(rng.randrange(-75,90),rng.randrange(-75,90),rng.randrange(1,50),rng.randrange(1,50)) for _ in range(9)],
        clips=[(-100,-100,240,240),(-13,-17,23,19)] if k%3==0 else [(-100,-100,240,240)],
        offset=(rng.randrange(-32,33),rng.randrange(-32,33))))
reports=[]
for case in cases:
    old=old_fragments(case['dabs'],case['clips'],case['offset']);groups=defaultdict(list)
    for fragment in old:groups[fragment[0]].append(fragment)
    new=[f for page in sorted(groups) for f in groups[page]]
    expected=oracle(case['dabs'],case['clips'])
    assert render(old)==expected and render(new)==expected
    assert sorted(old)==sorted(new) # exact original rectangles, not just same final pixels
    assert visits(new)==len(groups)
    reports.append(dict(name=case['name'],fragment_count=len(old),distinct_pages=len(groups),
        old_body_pins=visits(old),new_body_pins=visits(new),deleted_pin_pairs=visits(old)-visits(new),
        original_kernel_rectangles_preserved=True,per_pixel_sequence_sha256=digest(expected),
        max_simultaneous_pins=1 if groups else 0))
control=old_fragments([(0,0,3,2)]*2,[(0,0,3,2)],(0,0))
assert render(control)!=render(list(reversed(control)))
(H/'model-inputs.json').write_text(json.dumps(cases,indent=2)+'\n')
(H/'model-results.json').write_text(json.dumps(dict(cases=reports,negative_control_reversed_same_pixel_order_detected=True,
    scope='Algorithm-only exact rectangle and per-pixel sequence oracle. No product compositor, failures, pressure, timing, or formal qualification.'),indent=2)+'\n')
base_pins=2420;cold=76;conditional_pages=76;delta=base_pins-cold-conditional_pages;denominator_ms=8.103
rows=[]
for critical in [0.25,0.5,1.0]:
    for pair_us in [0.1,0.25,0.5,1.0]:
        for added_ms in [0,0.1,0.25]:
            cpu_saved=delta*pair_us/1000-added_ms
            rows.append(dict(critical_path_fraction=critical,pair_cost_us=pair_us,added_geometry_and_storage_ms=added_ms,
                net_cpu_saved_ms=cpu_saved,illustrative_wall_saved_ms=critical*cpu_saved,
                illustrative_stroke_gain_percent=100*critical*cpu_saved/denominator_ms))
(H/'prediction.json').write_text(json.dumps(dict(observed_node_pins=base_pins,observed_node_generations=cold,
    conditional_eligible_page_sum=conditional_pages,conditional_target_pins=cold+conditional_pages,
    conditional_deleted_pin_pairs=delta,conditional_pin_reduction_percent=100*delta/base_pins,
    proof_obligations=['All counted pins must be attributed to eligible cold preflight/body operations.',
        'Per-operation actual page union must sum to76; generation count alone does not establish this.',
        'Geometry/storage overhead and critical-path pair cost require independent measurement.'],
    frozen_cp0_stroke_marginal_median_ms=denominator_ms,denominator_is_not_current_candidate_measurement=True,
    sensitivity=rows,claim='Scenario calculation, not measured gain, confidence interval, or formal bound.'),indent=2)+'\n')
completion=[]
for n in [1,2,16,76,132,256]:
    # Success-prefix compression with all retirement tickets still Pending.
    shared=['Succeeded' if i%2==0 else 'Pending' for i in range(2*n)]
    prefix=0
    while prefix<len(shared) and shared[prefix]=='Succeeded':prefix+=1
    shared_nodes=len(shared)-prefix
    split_nodes=n # Work source is fully successful; retirement owns n Pending nodes.
    assert shared_nodes==2*n-1 and shared_nodes-split_nodes==n-1
    completion.append(dict(allocations=n,shared_live_interval_nodes=shared_nodes,
        split_live_interval_nodes=split_nodes,removed_live_nodes=n-1,
        node_allocations_both=2*n,extra_source_records=1))
(H/'completion-model.json').write_text(json.dumps(dict(rows=completion,
    premise='Serialized successful CPU preparation; no retirement completed yet. Failure/cancellation exceptions remain separately recorded.',
    interpretation='Source-lifetime interference model only. Not measured retention in the replay; splitting changes live nodes/free timing, not total allocatePending node allocations.'),indent=2)+'\n')
print(json.dumps(dict(model_cases=len(reports),negative_control='detected',conditional_deleted_pin_pairs=delta)))
