"""Summarize the complete predeclared diagnoses; preserve all old qualification."""
from pathlib import Path
import json,statistics

H=Path(__file__).resolve().parent
load=lambda n:json.loads((H/n).read_text())
rows=load('window-summary.json')['rows'];changes=[]
for arch in ['arm64','x86_64']:
 for k in [1,16]:
  for case in ['hit','native-pin']:
   for kind in ['same-image','cross-image']:
    d={r['cell']:r for r in rows if (r['arch'],r['K'],r['case'])==(arch,k,case)}
    a,b=d[kind+'-64ms'],d[kind+'-512ms']
    changes.append({'arch':arch,'K':k,'case':case,'kind':kind,
     'sd64ms':a['paired_log_throughput_sd'],'sd512ms':b['paired_log_throughput_sd'],
     'relative_sd_reduction':1-b['paired_log_throughput_sd']/a['paired_log_throughput_sd']})
assert len(changes)==16 and all(r['relative_sd_reduction']>0 for r in changes)
counts={c:sum(r['descriptively_inside_2pct'] for r in rows if r['cell']==c) for c in {r['cell'] for r in rows}}
assert counts=={'same-image-64ms':2,'cross-image-64ms':2,'same-image-512ms':6,'cross-image-512ms':6}
residual=[r for r in rows if r['cell'].endswith('512ms') and not r['descriptively_inside_2pct']]
report={'window_changes':changes,'descriptive_counts':counts,'residual512ms':residual,
 'relative_sd_reduction_range':[min(r['relative_sd_reduction'] for r in changes),max(r['relative_sd_reduction'] for r in changes)],
 'median_relative_sd_reduction':statistics.median(r['relative_sd_reduction'] for r in changes),
 'interpretation':'Accumulation-window improvement observed consistently in16/16 diagnosis combinations. Not a production time gain or formal family confidence claim. QoS and seed interventions do not consistently resolve variation.',
 'finite_diagnosis_complete':True,'measurement_resolution_fully_fixed':False,
 'new_formal_matrix_started':False,'old_qualification_changed':False,
 'verification':load('verification.json'),'M6_complete':False,'persistent_default_enabled':False}
(H/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
required={'authority':'92 section6.1, current product38834c4e26; scoped difference, not full CP0 census',
 'requirements':[
  {'id':'D1_retrospective','status':'complete1600_prior_processes_all_vectors_verified_no_requalification'},
  {'id':'D2_images_qos','status':'complete768_processes; unchanged A/A2/8 descriptive ±2%; original QoS33, no consistent intervention fix'},
  {'id':'D3_hash_layout','status':'complete384_processes; no consistent native-pin variance fix; production hash unchanged'},
  {'id':'D4_window','status':'complete768_processes;16/16 SD reduction, descriptive ±2% combinations4/16→12/16'},
  {'id':'F1_full_calibration_resolution','status':'open4_of16_long_window_diagnosis_combinations_not_inside2pct; no new formal matrix'},
  {'id':'V1_unchanged_inputs_work_exit','status':'complete2504_inputs,1992_new_processes,10982226_operation_vectors; sample body unchanged'},
  {'id':'formal_calibration','status':'unchanged2_of20_equivalent18_inconclusive_from_previous_frozen_package'},
  {'id':'hit_and_miss','status':'unchanged_numeric4_of4_and16_of16; jointly_calibrated0_of4_and2_of16'},
  {'id':'protected_fresh_and_history','status':'unchanged8_of8_pass_current_frozen_product'},
  {'id':'current_safety_resources_structure','status':'inherited_verified_same_inputs11180_0_0_safety6_resources_and_structure_tool_checks; not rerun'},
  {'id':'metadata_common_record_25pct','status':'open_comparable_pre_reconstruction_used_reserved_slack_residency_denominator'},
  {'id':'CP0_full_required_and_applicable_builds','status':'open'},
  {'id':'natural_producer_business_distribution_GPU_M7_M8_defaults','status':'not_qualified'}
 ],'finite_diagnostic_package_complete':True,'M6_complete':False,'persistent_default_enabled':False}
(H/'required-matrix.json').write_text(json.dumps(required,indent=2)+'\n')
print('Complete diagnosis:16/16 variation reduction;12/16 descriptive long controls; formal calibration remains2/20')
