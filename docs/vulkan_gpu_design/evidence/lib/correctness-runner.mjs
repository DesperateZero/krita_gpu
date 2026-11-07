import fs from 'node:fs';
import path from 'node:path';
import {spawn} from 'node:child_process';

export async function runCheckpoint({here, groups}) {
  const workspace = path.resolve(here, '../../../..');
  const source = path.join(workspace, 'krita');
  const [mode, label = mode] = process.argv.slice(2);
  if (!['build','focus','full'].includes(mode) || !/^[a-z0-9-]+$/.test(label)) throw Error('Invalid mode/label');
  const output = path.join(here, `${label}-results.json`);
  if (fs.existsSync(output)) throw Error('Preserve existing evidence');
  const report = {kind:'correctness-only',started:new Date().toISOString(),runs:[]};
  const names = ['kis_iterator_test','kis_iterators_ng_test','KisPageStoreFoundationTest','KisPageStoreReferenceTest',
    'KisPageStoreCpuMutationTest','KisPageStoreResidentReadTest','KisPageStorePhysicalClaimTest','KisCompletionRegistryTest',
    'kis_tile_data_pooler_test','kis_tile_data_store_test','kis_swapped_data_store_test','kis_low_memory_tests',
    'kis_tiled_data_manager_test','kis_painter_test','KisVulkanFoundationContractsTest'];
  async function execute(binary,args,suffix,environment,timeout=180000) {
    const log=path.join(here,`${label}-${suffix}.log`),fd=fs.openSync(log,'wx');
    const result=await new Promise((resolve,reject)=>{const child=spawn(binary,args,{cwd:workspace,env:{...process.env,...environment},stdio:['ignore',fd,fd]});
      const deadline=setTimeout(()=>child.kill('SIGTERM'),timeout); child.on('error',reject);
      child.on('close',(exitCode,signal)=>{clearTimeout(deadline);resolve({exitCode,signal});});}).finally(()=>fs.closeSync(fd));
    return {binary,args,environment,log,...result};
  }
  async function test(name,args=[],suffix=name) {
    const tree=name==='KisVulkanFoundationContractsTest'?'_build':'_build-br0-cpu';
    const environment={QT_QPA_PLATFORM:'offscreen',KIS_TEST_PREFIX_PATH:path.join(source,'_install'),KIS_TEST_PLUGIN_PATH:path.join(source,tree,'bin')};
    if(name==='kis_iterators_ng_test'||name==='kis_painter_test') environment.DYLD_PRINT_LIBRARIES='1';
    const r=await execute(path.join(source,tree,'bin',name),args,suffix,environment),text=fs.readFileSync(r.log,'utf8'); r.name=name;
    r.totals=text.match(/^Totals: (\d+) passed, (\d+) failed, (\d+) skipped, (\d+) blacklisted/m)?.slice(1).map(Number);
    r.passed=r.exitCode===0&&!r.signal&&!!r.totals&&r.totals.slice(1).every(n=>n===0)&&!/SAFE ASSERT|FAIL!|QFATAL|Received signal/.test(text);
    report.runs.push(r); console.log(`${suffix}: ${r.passed?'PASS':'FAIL'} (${r.totals?.[0]??'no totals'})`);
  }
  if(mode==='build') {
    for(const [tree,targets] of [['_build-br0-cpu',[...names.filter(n=>n!=='KisVulkanFoundationContractsTest'),'kis_paint_device_test','kritaselectiontools','KisPageStoreReadBaselineTest','kis_tiles3_cpu_baseline_test']],['_build',['KisVulkanFoundationContractsTest']]]) {
      const r=await execute(path.join(workspace,'.venv/bin/cmake'),['--build',path.join(source,tree),'--target',...targets,'-j4'],tree.slice(1),
        {MACOSX_DEPLOYMENT_TARGET:'12',CMAKE_PREFIX_PATH:path.join(source,'_install')},900000); r.passed=r.exitCode===0&&!r.signal; report.runs.push(r);
      console.log(`${tree}: ${r.passed?'PASS':'FAIL'}`); if(!r.passed) break;
    }
  } else {
    const builds=fs.readdirSync(here).filter(n=>n.endsWith('-build-results.json')).map(n=>JSON.parse(fs.readFileSync(path.join(here,n),'utf8')))
      .sort((a,b)=>Date.parse(b.finished)-Date.parse(a.finished));
    if(!builds.length||builds[0].runs.length!==2||builds[0].runs.some(r=>!r.passed)) throw Error('Missing/failed latest build');
    if(mode==='focus') for(const [group,name,args] of groups) await test(name,args,group);
    else {
      const queue=[...names]; await Promise.all(Array.from({length:4},async()=>{while(queue.length)await test(queue.shift());}));
      await test('kis_paint_device_test',['testPlanarReadWrite','testReadBytesWrapAround','testWrappedRandomAccessor','testWrappedHLineIterator',
        'testWrappedVLineIterator','testWrappedHLineIteratorReadMoreThanBounds','testWrappedVLineIteratorReadMoreThanBounds'],'paint-device-selected');
      for(let i=1;i<=20;++i)for(const [group,name,args] of groups)await test(name,args,`${group}-${i}`);
    }
  }
  report.finished=new Date().toISOString(); fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
  if(report.runs.some(r=>!r.passed)) process.exitCode=1;
}
