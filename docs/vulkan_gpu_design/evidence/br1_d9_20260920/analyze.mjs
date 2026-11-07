import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const [input,output]=process.argv.slice(2);
if(!input||!output||fs.existsSync(output))throw Error('Expected manifest and new output');
const m=JSON.parse(fs.readFileSync(input)),p=m.protocol;
if(!m.completed)throw Error('Incomplete experiment');
const cases=p[m.phase+'_cases'],runs=m.runs.filter(r=>r.pair!==undefined);
if(runs.length!==cases.length*p.pairs*2)throw Error('Wrong run count');
let seed=p.bootstrap_seed;
const random=()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return(seed>>>0)/4294967296;};
const median=a=>{a=[...a].sort((x,y)=>x-y);const i=a.length>>1;return a.length%2?a[i]:(a[i-1]+a[i])/2;};
function summary(pairs){
  const ratios=pairs.map(a=>a[1]/a[0]),samples=[];
  for(let n=0;n<p.bootstrap_resamples;++n)samples.push(median(ratios.map(()=>ratios[Math.floor(random()*ratios.length)])));
  samples.sort((a,b)=>a-b);
  return{baseline_median:median(pairs.map(a=>a[0])),candidate_median:median(pairs.map(a=>a[1])),paired_median_ratio:median(ratios),
    exploratory_95_interval:[samples[Math.floor(samples.length*.025)],samples[Math.floor(samples.length*.975)]],pair_ratios:ratios};
}
const results=[];
for(const fixture of cases){
  const pairs=Array.from({length:p.pairs},(_,pair)=>['before','after'].map(variant=>{
    const found=runs.filter(r=>r.fixture===fixture&&r.pair===pair&&r.variant===variant);if(found.length!==1)throw Error('Missing/duplicate run');
    const r=found[0],log=fs.readFileSync(path.join(path.dirname(input),r.file),'utf8');
    const prefix=m.phase.startsWith('native')?'CPU_BASELINE ':m.phase.startsWith('cold')?'READ_COLD ':'READ_BASELINE ',lines=log.split('\n').filter(x=>x.includes(prefix+'{'));
    if(lines.length!==1||r.status!==0||!/Totals: 3 passed, 0 failed/.test(log))throw Error('Bad log');
    const v=JSON.parse(lines[0].slice(lines[0].indexOf(prefix)+prefix.length));
    if(JSON.stringify(v)!==JSON.stringify(r.result)||v.correctness!=='Pass'||v.fixture!==fixture||v.measurement!=='completed-throughput'||
       v.wall_ns<p.rate_ms*1e6||v.completed_operations<=0||v.threads!==1||v.in_flight!==1)throw Error('Bad data');
    if(m.phase==='integration'){
      const match=fixture.match(/-n(\d+)-k(\d+)-h(\d+)(?:-(cpu|tiles3)-b(\d+))?$/);
      if(!match||v.N!==+match[1]||v.K!==+match[2]||v.H!==+match[3]||v.BPP!==+(match[5]||1)||v.provider!==(match[4]||'cpu')||
         v.read_requests!==0||v.expected_requests_per_page!==0||
         v.endpoint!=='CpuReadable-and-session-released'||v.scope!=='lifecycle-inclusive; read-session; CpuRam; payload-and-binding-warm; H-release-and-close-separate')throw Error('Wrong integration scope');
    }else if(m.phase.startsWith('cold')){
      const match=fixture.match(/^cycle-n64-k(0|1|16)-(cpu|tiles3)-b(4|16)$/);
      if(!match||v.N!==64||v.K!==+match[1]||v.provider!==match[2]||v.BPP!==+match[3]||
         v.read_phase_requests!==0||v.endpoint!=='Published-CpuReadable-and-session-released'||
         v.phase_profile!==(m.phase==='cold_profile'||(m.phase==='cold_perturbation'&&variant==='after'))||
         v.scope!=='generation-cycle; fill64-publish-first-read-release; CpuRam; payload-ready-binding-cold; setup-close-separate'||
         v.lifecycle_ns<v.wall_ns+v.setup_ns+v.close_ns||v.background_drain!=='NotMeasured')throw Error('Wrong cold scope');
    }else if(v.access_path!=='native-CpuRam'||v.retained_history_roots!==0||v.rate_check_interval!==64||
       v.endpoint!==(fixture.startsWith('guard')?'GuardReleased':'CpuReadable'))throw Error('Wrong native scope');
    return v;
  }));
  const row={fixture,completed_operations_per_second:summary(pairs.map(a=>a.map(v=>v.completed_operations*1e9/v.wall_ns))),
    process_cpu_ns_per_completed_operation:summary(pairs.map(a=>a.map(v=>v.process_cpu_ns/v.completed_operations)))};
  if(m.phase==='integration')row.history_release_close_ns=pairs.map(a=>a.map(v=>v.history_release_close_ns));
  if(m.phase.startsWith('cold')) {
    row.lifecycle_ns_per_cycle=summary(pairs.map(a=>a.map(v=>v.lifecycle_ns/v.completed_operations)));
    row.setup_close_ns=pairs.map(a=>a.map(v=>[v.setup_ns,v.close_ns]));
    if(m.phase==='cold_profile') {
      row.prepare_publish_ns_per_cycle=summary(pairs.map(a=>a.map(v=>v.prepare_publish_ns/v.completed_operations)));
      row.first_read_scope_ns_per_cycle=summary(pairs.map(a=>a.map(v=>v.first_read_scope_ns/v.completed_operations)));
    }
  }
  results.push(row);console.log(JSON.stringify(row));
}
const result={phase:m.phase,manifest_sha256:crypto.createHash('sha256').update(fs.readFileSync(input)).digest('hex'),results,
  qualification:'D8/D9 diagnostic (native_reference D7/D9; cold_perturbation profiled/plain D9); not upstream NI, isolated binding self, single-event tails, full background drain or GPU/UMA qualification'};
fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
