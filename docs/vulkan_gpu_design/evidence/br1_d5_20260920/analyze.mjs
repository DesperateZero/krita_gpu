import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const input = path.resolve(process.argv[2] || '');
const output = process.argv[3];
if (!output) throw Error('Usage: node analyze.mjs paired/manifest.json new-analysis.json');
if (fs.existsSync(output)) throw Error('Refusing to overwrite analysis');
const manifest = JSON.parse(fs.readFileSync(input));
if (!['paired', 'rate'].includes(manifest.phase) || !manifest.completed) throw Error('Incomplete experiment');
const protocol = manifest.protocol;
const median = values => {
  const sorted = [...values].sort((a, b) => a - b);
  const i = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[i] : (sorted[i-1] + sorted[i]) / 2;
};
let state = protocol.bootstrap.seed >>> 0;
const random = () => {
  state ^= state << 13; state ^= state >>> 17; state ^= state << 5;
  return (state >>> 0) / 4294967296;
};
function summarizeRatios(pairs) {
  const values = pairs.map(([upstream, current]) => current / upstream);
  const draws = [];
  for (let i = 0; i < protocol.bootstrap.resamples; ++i) {
    draws.push(median(values.map(() => values[Math.floor(random() * values.length)])));
  }
  draws.sort((a, b) => a - b);
  return {upstream_median: median(pairs.map(x => x[0])),
    current_median: median(pairs.map(x => x[1])), paired_median_ratio: median(values),
    exploratory_paired_95_interval: [draws[Math.floor(draws.length * 0.025)], draws[Math.floor(draws.length * 0.975)]],
    pair_ratios: values};
}

const runs = manifest.runs.filter(x => x.pair !== undefined);
const measurements = manifest.phase === 'rate' ? ['rate'] : ['time', 'rate'];
if (runs.length !== protocol.cases.length * protocol.pairs * 2 * measurements.length) throw Error('Wrong run count');
const results = [];
for (const fixture of protocol.cases) {
  const row = {fixture};
  for (const measurement of measurements) {
    const get = (pair, label) => {
      const matching = runs.filter(x => x.pair === pair && x.fixture === fixture && x.label === label && x.measurement === measurement);
      if (matching.length !== 1) throw Error(`Missing/duplicate ${fixture}/${pair}/${label}/${measurement}`);
      const record = matching[0];
      const log = fs.readFileSync(path.join(path.dirname(input), record.file), 'utf8');
      const lines = log.split('\n').filter(x => x.includes('CPU_BASELINE {'));
      if (lines.length !== 1 || !/Totals: 3 passed, 0 failed/.test(log)) throw Error('Bad log');
      const actual = JSON.parse(lines[0].slice(lines[0].indexOf('CPU_BASELINE ') + 13));
      if (JSON.stringify(actual) !== JSON.stringify(record.result)) throw Error('Manifest/log mismatch');
      if (actual.correctness !== 'Pass' || actual.wall_ns < protocol.fixed_work_minimum_ns || actual.threads !== 1 ||
          actual.in_flight !== 1 || actual.retained_history_roots !== 0 || actual.pixel_bytes < 4) throw Error('Bad scope');
      if (measurement === 'time' && actual.completed_operations !== manifest.loops[fixture]) throw Error('Wrong loop count');
      if (actual.measurement !== (measurement === 'time' ? 'fixed-work-amortized-time' : 'completed-throughput')) throw Error('Wrong endpoint');
      return actual;
    };
    const pairs = Array.from({length: protocol.pairs}, (_, pair) => [get(pair, 'upstream'), get(pair, 'current')]);
    for (const [a, b] of pairs) {
      for (const key of ['fixture', 'total_pages', 'work_pages', 'pixel_bytes', 'metric_scope', 'endpoint', 'evidence_class', 'access_path']) {
        if (a[key] !== b[key]) throw Error(`Mismatched ${key}`);
      }
    }
    row.evidence_class = pairs[0][0].evidence_class;
    row.metric_scope = pairs[0][0].metric_scope;
    if (measurement === 'time') {
      row.wall_ns_per_operation = summarizeRatios(pairs.map(pair => pair.map(x => x.wall_ns / x.completed_operations)));
      row.thread_cpu_ns_per_operation = summarizeRatios(pairs.map(pair => pair.map(x => x.thread_cpu_ns / x.completed_operations)));
      row.process_cpu_ns_per_operation = summarizeRatios(pairs.map(pair => pair.map(x => x.process_cpu_ns / x.completed_operations)));
      row.process_peak_rss_bytes = {upstream: median(pairs.map(x => x[0].process_peak_rss_bytes)),
        current: median(pairs.map(x => x[1].process_peak_rss_bytes))};
      row.fixed_operations = manifest.loops[fixture];
    } else {
      row.completed_operations_per_second = summarizeRatios(pairs.map(pair => pair.map(x => x.completed_operations * 1e9 / x.wall_ns)));
      row.rate_window_thread_cpu_ns_per_completed_operation = summarizeRatios(pairs.map(pair => pair.map(x => x.thread_cpu_ns / x.completed_operations)));
      row.rate_window_process_cpu_ns_per_completed_operation = summarizeRatios(pairs.map(pair => pair.map(x => x.process_cpu_ns / x.completed_operations)));
      row.rate_window_completed_operations = {upstream: median(pairs.map(x => x[0].completed_operations)), current: median(pairs.map(x => x[1].completed_operations))};
      row.rate_process_peak_rss_bytes = {upstream: median(pairs.map(x => x[0].process_peak_rss_bytes)), current: median(pairs.map(x => x[1].process_peak_rss_bytes))};
    }
  }
  row.qualification = 'NotQualified: limited diagnostic scope, not formal M/K/E or BR1-PERF closure';
  results.push(row);
}
const report = {schema: 1, manifest_sha256: crypto.createHash('sha256').update(fs.readFileSync(input)).digest('hex'),
  purpose: protocol.purpose, phase: manifest.phase, runs: runs.length, pairs_per_case: protocol.pairs,
  limitations: protocol.qualification_limits, results};
fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n', {flag: 'wx'});
for (const x of results) {
  const w = x.wall_ns_per_operation, t = x.completed_operations_per_second;
  console.log(`${x.fixture}: ${t.upstream_median.toFixed(0)} -> ${t.current_median.toFixed(0)} completed ops/s; rate ratio ${t.paired_median_ratio.toFixed(4)} [${t.exploratory_paired_95_interval.map(v => v.toFixed(4)).join(', ')}]${w ? '; fixed-work time ratio ' + w.paired_median_ratio.toFixed(3) : '; fixed-work time/tail NotMeasured'}`);
}
