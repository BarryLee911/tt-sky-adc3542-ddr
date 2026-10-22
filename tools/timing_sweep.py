"""Explicit assumed envelopes. These are not translator/PVT timing specifications."""
from run_tests import *
import concurrent.futures, csv, itertools
def compile_timing():
    cmd=[str(IVER),'-g2012','-s','tb_timing','-o',str(HERE/'tb_timing.vvp'),str(SRC/'adc3542_rx7.v'),str(HERE/'tb_timing.v')]
    p=subprocess.run(cmd,cwd=HERE,capture_output=True,text=True)
    (OUT/'timing_compile.log').write_text(p.stdout+p.stderr,encoding='utf-8')
    save(OUT/'timing_compile.json',dict(command=cmd,exit_code=p.returncode))
    assert p.returncode==0,p.stdout+p.stderr
def sweep():
    # ADC tPD corners, aggregate data-DCLK skew, assumed output duty distortion.
    # Direct: no extra delay. Illustrative translation: total added common delay 3..5ns.
    phases=[i*.5 for i in range(49)]
    scenarios=[(env,phase,tpd,extra,skew,duty) for env,extras in [('direct',[0]),('illustrative_translation',[3,5])]
               for phase,tpd,extra,skew,duty in itertools.product(phases,[3,5,7],extras,[-1,0,1],[-2,0,2])]
    def one(s):
        env,phase,tpd,extra,skew,duty=s
        cmd=[str(VVP),str(HERE/'tb_timing.vvp'),f'+PHASE={phase}',f'+TPD={tpd}',f'+EXTRA={extra}',f'+SKEW={skew}',f'+DUTY={duty}']
        p=subprocess.run(cmd,cwd=HERE,capture_output=True,text=True)
        assert p.returncode==0 and 'TIMING_RESULT' in p.stdout,p.stdout+p.stderr
        values={k:float(v) for k,v in re.findall(r'([a-z_]+)=(-?[\d.]+)',p.stdout)}
        return dict(envelope=env,phase_ns=phase,tpd_ns=tpd,extra_ns=extra,skew_ns=skew,duty_ns=duty,**values,
            passed=values['bad']==0 and values['aperture']==0 and values['checks']>=120)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows=list(pool.map(one,scenarios))
    with (OUT/'timing_sweep.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary={}
    for env in ['direct','illustrative_translation']:
        good=[p for p in phases if all(r['passed'] for r in rows if r['envelope']==env and r['phase_ns']==p)]
        assert good
        groups=[]
        for p in good:
            if not groups or p>groups[-1][1]+.5:groups.append([p,p])
            else:groups[-1][1]=p
        summary[env]=dict(all_corner_good_phases_ns=good,grid_intervals_ns=groups,
            scenarios=sum(r['envelope']==env for r in rows),
            analytic_unwrapped_open_interval_ns=[11.5,23.4140625] if env=='direct' else [16.5,26.4140625],
            analytic_explanation='latest launch+skew+setup+uncertainty < phase < H+earliest next launch+skew-duty-hold-uncertainty')
    # Since phase is modulo H, only tested phase 0..24ns is reported, not an extrapolated eye.
    save(OUT/'timing_validation.json',dict(status='BEHAVIOURAL_MODEL_ONLY',clock_period_ns=24.4140625,
      adc_period_ns=48.828125,scenarios=len(rows),setup_ns=1,hold_ns=.5,uncertainty_ns=.5,
      assumed_skew_ns=[-1,1],assumed_output_duty_distortion_ns=[-2,2],summary=summary,
      limits='No library, PCB, translator PVT, input slew, CTS, metastability or measured duty guarantee. Not physical timing closure.'))
    print('TIMING_SWEEP_DONE',len(rows),summary,flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['compile','run']);a=ap.parse_args()
    (compile_timing if a.action=='compile' else sweep)()
