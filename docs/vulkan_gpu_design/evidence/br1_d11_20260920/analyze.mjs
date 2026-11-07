import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const [input,output]=process.argv.slice(2);
if(!input||!output||fs.existsSync(output))throw Error('Expected manifest and new output');
const m=JSON.parse(fs.readFileSync(input)),p=m.protocol,diag=m.phase==='diagnostic';
if(!m.completed)throw Error('Incomplete experiment');
const cases=p[m.phase+'_cases'],count=diag?p.diagnostic_pairs:p.pairs,runs=m.runs.filter(r=>r.pair!==undefined);
if(runs.length!==cases.length*count*2)throw Error('Wrong run count');
let seed=p.bootstrap_seed;
const random=()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return(seed>>>0)/4294967296;};
const median=a=>{a=[...a].sort((x,y)=>x-y);const i=a.length>>1;return a.length%2?a[i]:(a[i-1]+a[i])/2;};
function summary(pairs){
  const ratios=pairs.map(a=>a[1]/a[0]),samples=[];
  for(let n=0;n<p.bootstrap_resamples;++n)samples.push(median(ratios.map(()=>ratios[Math.floor(random()*ratios.length)])));
  samples.sort((a,b)=>a-b);
  return {baseline_median:median(pairs.map(a=>a[0])),candidate_median:median(pairs.map(a=>a[1])),paired_median_ratio:median(ratios),
    exploratory_95_interval:[samples[Math.floor(samples.length*.025)],samples[Math.floor(samples.length*.975)]],pair_ratios:ratios};
}
const results=[];
for(const fixture of cases){
  const pairs=Array.from({length:count},(_,pair)=>['before','after'].map(variant=>{
    const found=runs.filter(r=>r.fixture===fixture&&r.pair===pair&&r.variant===variant);if(found.length!==1)throw Error('Missing/duplicate run');
    const r=found[0],log=fs.readFileSync(path.join(path.dirname(input),r.file),'utf8'),prefix=diag?'BR1_FIXED ':'CPU_BASELINE ';
    const lines=log.split('\n').filter(x=>x.includes(prefix+'{'));
    if(lines.length!==1||r.status!==0||!/Totals: 3 passed, 0 failed/.test(log)||/SAFE ASSERT/.test(log))throw Error('Bad log');
    const v=JSON.parse(lines[0].slice(lines[0].indexOf(prefix)+prefix.length));
    if(JSON.stringify(v)!==JSON.stringify(r.result))throw Error('Manifest differs from log');
    if(diag){
      if(v.case!==fixture||v.loops!==p.diagnostic_loops||v.stage_profile!==(variant==='after')||
         v.write_requests!==0||v.native_generations_reserved!==v.K*v.loops||v.native_pages_sealed!==v.K*v.loops||
         v.native_guards_released!==v.K*v.loops||v.commits!==v.loops||v.native_duplicate_pages!==v.K*v.loops||
         v.native_duplicate_bytes!==v.K*v.loops*64*64*v.bpp||v.explicit_copy_pages!==0||v.default_initialized_pages!==0)throw Error('Invalid structure');
    }else{
      const tag=fixture.match(/^(\w+)-n(\d+)-k(\d+)-b(\d+)$/);if(!tag)throw Error('Bad fixture');
      const mode=tag[1],kind=['guard','lookup','blank','intent'].includes(mode)?'M':mode==='kernel'?'K':'E';
      const endpoint=kind==='M'?'GuardReleased':kind==='K'?'CopyCompletePrebound':'CpuReadable';
      if(v.correctness!=='Pass'||v.fixture!==fixture||v.mode!==mode||v.evidence_class!==kind||v.endpoint!==endpoint||
        v.total_pages!==+tag[2]||v.work_pages!==+tag[3]||v.pixel_bytes!==+tag[4]||v.measurement!=='completed-throughput'||
        v.wall_ns<p.rate_ms*1e6||v.completed_operations<=0||v.threads!==1||v.in_flight!==1||v.rate_check_interval!==64||
        v.access_path!=='native-CpuRam'||v.retained_history_roots!==0||v.background_drain!=='NotMeasured'||v.per_event_tail!=='NotMeasured')throw Error('Wrong scope');
    }return v;
  }));
  let row;
  if(diag){
    row={fixture,fixed_work_operation_ms:summary(pairs.map(a=>a.map(v=>v.operation_ms))),
      sampled_operations:pairs.map(a=>a[1].sampled_operations),sampled_stage_metrics:pairs.map(a=>a[1].phases),
      plain_structure:pairs.map(a=>({reserved:a[0].native_generations_reserved,sealed:a[0].native_pages_sealed,
        requests:a[0].write_requests,commits:a[0].commits,cow_bytes:a[0].native_duplicate_bytes,
        retained_release_ms:a[0].release_retained_ms}))};
  }else row={fixture,evidence_class:pairs[0][0].evidence_class,endpoint:pairs[0][0].endpoint,
    completed_operations_per_second:summary(pairs.map(a=>a.map(v=>v.completed_operations*1e9/v.wall_ns))),
    process_cpu_ns_per_completed_operation:summary(pairs.map(a=>a.map(v=>v.process_cpu_ns/v.completed_operations))),
    wall_ns_per_completed_operation:summary(pairs.map(a=>a.map(v=>v.wall_ns/v.completed_operations)))};
  results.push(row);
}
const result={phase:m.phase,manifest_sha256:crypto.createHash('sha256').update(fs.readFileSync(input)).digest('hex'),results,
  interpretation:diag?'Sampled inclusive phase diagnostics and perturbation, not fine self/wait/hold attribution.':
    'Completed throughput and per-completed-op CPU/work amortization. Not event latency, formal NI, all production entry points or full drain.'};
fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
for(const r of results)console.log(JSON.stringify({fixture:r.fixture,...(diag?{plain_ms:r.fixed_work_operation_ms.baseline_median,
  sampled_ms:r.fixed_work_operation_ms.candidate_median,perturbation:r.fixed_work_operation_ms.paired_median_ratio}:
  {ratio:r.completed_operations_per_second.paired_median_ratio,ci:r.completed_operations_per_second.exploratory_95_interval,
    base_ops:r.completed_operations_per_second.baseline_median,after_ops:r.completed_operations_per_second.candidate_median})}));
