import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const [input, output] = process.argv.slice(2);
if (!input || !output || fs.existsSync(output)) throw Error('Expected manifest and new analysis path');
const m = JSON.parse(fs.readFileSync(input));
if (!m.completed) throw Error('Incomplete experiment');
const runs = m.runs.filter(x => x.pair !== undefined), p = m.protocol;
const fixtures = m.phase === 'registry' ? p.patterns : p.tile_cases;
if (runs.length !== fixtures.length*p.pairs*2) throw Error('Wrong number of runs');
let seed = p.bootstrap_seed;
const random = () => {seed ^= seed << 13; seed ^= seed >>> 17; seed ^= seed << 5; return (seed >>> 0)/4294967296;};
const median = a => {a = [...a].sort((x,y)=>x-y); const i = Math.floor(a.length/2); return a.length % 2 ? a[i] : (a[i-1]+a[i])/2;};
function summary(pairs) {
  const ratios = pairs.map(x=>x[1]/x[0]), draws = [];
  for (let i=0; i<p.bootstrap_resamples; ++i) draws.push(median(ratios.map(()=>ratios[Math.floor(random()*ratios.length)])));
  draws.sort((a,b)=>a-b);
  return {before_median: median(pairs.map(x=>x[0])), after_median: median(pairs.map(x=>x[1])),
    paired_median_ratio: median(ratios), exploratory_95_interval: [draws[Math.floor(draws.length*.025)],draws[Math.floor(draws.length*.975)]], pair_ratios: ratios};
}
const results = [];
for (const fixture of fixtures) {
  const pairs = Array.from({length:p.pairs},(_,pair)=>['before','after'].map(label=>{
    const records = runs.filter(x=>x.fixture===fixture && x.pair===pair && x.label===label);
    if(records.length!==1)throw Error('Duplicate/missing pair');
    const r=records[0], txt=fs.readFileSync(path.join(path.dirname(input),r.file),'utf8');
    const prefix=m.phase==='registry'?'COMPLETION_BASELINE ':'CPU_BASELINE ';
    const lines=txt.split('\n').filter(x=>x.includes(prefix+'{'));
    if(lines.length!==1 || !/Totals: 3 passed, 0 failed/.test(txt))throw Error('Invalid log');
    const value=JSON.parse(lines[0].slice(lines[0].indexOf(prefix)+prefix.length));
    if(JSON.stringify(value)!==JSON.stringify(r.result)||value.correctness!=='Pass'||value.wall_ns<p.minimum_window_ns)throw Error('Wrong data');
    if(m.phase==='registry'&&value.completed_operations!==p.loops)throw Error('Wrong work');
    if(m.phase==='registry') {
      const gap=fixture==='pending-gap'?1:0;
      if(value.pattern!==fixture || value.allocated_tickets!==p.loops+gap ||
          value.pending_tickets!==gap || value.terminal_tickets!==p.loops ||
          value.scope!=='completion-registry-lifecycle; allocate-complete-status; no provider/root/drain')throw Error('Wrong registry scope');
      const variant=m.identities[label].variant;
      const expected=variant==='before'?p.loops+gap:
        fixture==='success'||fixture==='pending-gap'?1:
        variant==='after-sparse'?(fixture==='alternating'?p.loops/2+1:p.loops/1024+1):
        fixture==='alternating'?p.loops:p.loops/512;
      if(value.storage_records!==expected)throw Error('Wrong structural record count');
    } else if(value.fixture!==fixture || value.measurement!=='completed-throughput' ||
        value.threads!==1 || value.in_flight!==1 || value.retained_history_roots!==0 ||
        value.access_path!=='native-CpuRam' || value.rate_check_interval!==64 ||
        value.wall_ns<p.tile_rate_ms*1000000 || value.completed_operations<=0 ||
        value.endpoint!==(fixture.startsWith('guard')?'GuardReleased':'CpuReadable') ||
        value.evidence_class!==(fixture.startsWith('guard')?'M':'E'))throw Error('Wrong tile scope');
    return value;
  }));
  const row={fixture};
  if(m.phase==='registry') {
    row.wall_ns_per_operation=summary(pairs.map(a=>a.map(x=>x.wall_ns/x.completed_operations)));
    row.process_cpu_ns_per_operation=summary(pairs.map(a=>a.map(x=>x.process_cpu_ns/x.completed_operations)));
    row.records={before: pairs.map(a=>a[0].storage_records), after: pairs.map(a=>a[1].storage_records)};
  } else row.completed_operations_per_second=summary(pairs.map(a=>a.map(x=>x.completed_operations*1e9/x.wall_ns)));
  results.push(row); console.log(JSON.stringify(row));
}
fs.writeFileSync(output, JSON.stringify({phase:m.phase, manifest_sha256:crypto.createHash('sha256').update(fs.readFileSync(input)).digest('hex'), results,
  qualification:'Diagnostic slice only; not upstream NI/product/tail/GPU/UMA'},null,2)+'\n',{flag:'wx'});
