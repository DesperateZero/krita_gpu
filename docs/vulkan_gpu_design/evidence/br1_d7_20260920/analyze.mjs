import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const [input, output] = process.argv.slice(2);
if (!input || !output || fs.existsSync(output)) throw Error('Expected manifest and new output file');
const m = JSON.parse(fs.readFileSync(input)), p = m.protocol;
if (!m.completed) throw Error('Incomplete experiment');
const variants = m.phase === 'component' ? ['legacy','captured'] : ['before','after'];
const prefix = m.phase === 'component' ? 'READ_SCOPE ' : m.phase === 'native' ? 'CPU_BASELINE ' : 'READ_BASELINE ';
const cases = p[m.phase+'_cases'], runs = m.runs.filter(r=>r.pair !== undefined);
if (runs.length !== cases.length*p.pairs*2) throw Error('Wrong sample count');
let seed = p.bootstrap_seed;
const random = () => { seed ^= seed<<13; seed ^= seed>>>17; seed ^= seed<<5; return (seed>>>0)/4294967296; };
const median = values => { const a=[...values].sort((x,y)=>x-y),i=a.length>>1; return a.length%2?a[i]:(a[i-1]+a[i])/2; };
function summary(pairs) {
  const ratios=pairs.map(a=>a[1]/a[0]), samples=[];
  for(let n=0;n<p.bootstrap_resamples;++n) samples.push(median(ratios.map(()=>ratios[Math.floor(random()*ratios.length)])));
  samples.sort((a,b)=>a-b);
  return {baseline_median:median(pairs.map(a=>a[0])),candidate_median:median(pairs.map(a=>a[1])),paired_median_ratio:median(ratios),
    exploratory_95_interval:[samples[Math.floor(samples.length*.025)],samples[Math.floor(samples.length*.975)]],pair_ratios:ratios};
}
const results=[];
for (const fixture of cases) {
  const pairs=Array.from({length:p.pairs},(_,pair)=>variants.map(variant=>{
    const found=runs.filter(r=>r.fixture===fixture&&r.pair===pair&&r.variant===variant);
    if(found.length!==1) throw Error('Missing/duplicate pair');
    const r=found[0],log=fs.readFileSync(path.join(path.dirname(input),r.file),'utf8');
    const lines=log.split('\n').filter(x=>x.includes(prefix+'{'));
    if(lines.length!==1||r.status!==0||!/Totals: 3 passed, 0 failed/.test(log)) throw Error('Bad log');
    const value=JSON.parse(lines[0].slice(lines[0].indexOf(prefix)+prefix.length));
    const match=fixture.match(/-n(\d+)-k(\d+)-h(\d+)$/);
    if(JSON.stringify(value)!==JSON.stringify(r.result)||value.correctness!=='Pass'||value.measurement!=='completed-throughput'||
       value.wall_ns<p.rate_ms*1000000||value.completed_operations<=0) throw Error('Bad data/scope');
    if(m.phase!=='native'&&(!match||value.N!==+match[1]||value.K!==+match[2]||value.H!==+match[3])) throw Error('Bad workload');
    if(m.phase==='component') {
      if(variant==='captured'&&(value.gc_pages_visited!==0||value.captured_scopes!==(fixture.startsWith('scope')?value.completed_operations:0))) throw Error('Wrong captured complexity');
      const expected=fixture.startsWith('lookup')?'retained-identity-lookup; excludes-capture-release; no-pixels':
        'identity-scope-lifecycle; capture-lookup-release; no-pixels; legacy-owning-manifest-included';
      if(value.scope!==expected) throw Error('Wrong component scope');
    } else if(m.phase==='native') {
      if(value.fixture!==fixture||value.threads!==1||value.in_flight!==1||value.retained_history_roots!==0||value.access_path!=='native-CpuRam'||
         value.rate_check_interval!==64||value.endpoint!==(fixture.startsWith('guard')?'GuardReleased':'CpuReadable')) throw Error('Wrong native scope');
    } else if(value.read_requests!==value.completed_operations*value.K||value.threads!==1||value.in_flight!==1||value.BPP!==1||
        value.endpoint!=='CpuReadable-and-session-released'||value.scope!=='lifecycle-inclusive; generic-read-session; CpuRam; H-retention-release-and-close-separate') throw Error('Wrong integration scope');
    return value;
  }));
  const row={fixture,completed_operations_per_second:summary(pairs.map(a=>a.map(x=>x.completed_operations*1e9/x.wall_ns))),
    process_cpu_ns_per_completed_operation:summary(pairs.map(a=>a.map(x=>x.process_cpu_ns/x.completed_operations)))};
  if(m.phase==='component') row.gc_pages_visited=pairs.map(a=>a.map(x=>x.gc_pages_visited));
  else if(m.phase==='integration') row.history_release_close_ns=pairs.map(a=>a.map(x=>x.history_release_close_ns));
  results.push(row); console.log(JSON.stringify(row));
}
const result={phase:m.phase,manifest_sha256:crypto.createHash('sha256').update(fs.readFileSync(input)).digest('hex'),results,
  qualification:'Diagnostic only; not upstream NI, per-operation latency, native pixel guard, product/GPU/UMA qualification'};
fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
