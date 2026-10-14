"""Reproduce original case prompts; --live is required for charged calls."""
from pathlib import Path
import argparse,base64,json,os,time,hashlib,urllib.request
from decimal import Decimal
from contextlib import ExitStack
from toapis_async import ToAPIsClient,normalize_origin,NoRedirect

SIZES={'1:1':'1024x1024','16:9':'1024x576','9:16':'576x1024'}
def main():
    p=argparse.ArgumentParser();p.add_argument('--live',action='store_true');p.add_argument('--output',type=Path,default=Path('results'));p.add_argument('--case',default='all');a=p.parse_args()
    cases=json.loads((Path(__file__).resolve().parent.parent/'cases/briefs.json').read_text(encoding='utf-8'))
    cases=[x for x in cases if a.case in ('all',x['id'])]
    if not cases:raise SystemExit('Unknown case')
    if not a.live:
        print(json.dumps({'mode':'dry-run','cases':cases},ensure_ascii=False,indent=2));return
    key=os.environ.get('TOAPIS_API_KEY');assert key,'Configure TOAPIS_API_KEY privately'
    origin=normalize_origin(os.environ.get('TOAPIS_BASE_URL','https://toapis.cn'))
    req=urllib.request.Request(origin+'/v1/pricing?model=gpt-image-2-vip',headers={'Authorization':'Bearer '+key})
    with urllib.request.build_opener(NoRedirect).open(req,timeout=30) as r:catalog=json.load(r)
    prices=[x for m in catalog.get('data',[]) for x in m.get('prices',[]) if x.get('unit')=='request' and str(x.get('conditions',{}).get('resolution','')).upper()=='1K' and x.get('conditions',{}).get('quality')=='low' and x.get('conditions',{}).get('n',1)==1]
    assert prices,'No exact low/1K/n=1 quote; stop before submission'
    rate=max(Decimal(x['unit_price']) for x in prices)
    if rate*len(cases)>Decimal('0.10'):raise SystemExit('This demo exceeds its $0.10 sub-cap; stopped')
    a.output.mkdir(parents=True,exist_ok=True);(a.output/'pricing.json').write_text(json.dumps({'checked_at':time.strftime('%Y-%m-%d %H:%M:%S'),'unit_quote_usd':str(rate),'data':catalog},ensure_ascii=False,indent=2),encoding='utf-8')
    records=[]
    for c in cases:
        folder=a.output/c['id'];folder.mkdir(exist_ok=True);evidence=folder/'evidence.json'
        if evidence.exists():records.append(json.loads(evidence.read_text(encoding='utf-8')));continue
        os.environ['TOAPIS_RUN_ID']=c['id'];start=time.monotonic();client=ToAPIsClient(key,origin,'1K',a.output/'private-state')
        with ExitStack() as stack:
            params=dict(model=c['model'],prompt=c['prompt'],quality=c['quality'],size=SIZES[c['size']],n=1,output_format='png')
            if c.get('reference'):params['image']=[stack.enter_context(open(a.output/c['reference']/'result.png','rb'))]
            data=client.edit(**params) if c.get('reference') else client.generate(**params)
        raw=base64.b64decode(data.data[0].b64_json);(folder/'result.png').write_bytes(raw)
        receipt=client.last_receipt
        row={'case_id':c['id'],'date':'2026-10-14','task_id':receipt['task_id'],'request':receipt['request'],'status':receipt['state'],'billing':receipt.get('billing'),'actual_cost_usd':(receipt.get('billing') or {}).get('cost_usd'),'unit_quote_usd':str(rate),'sha256':hashlib.sha256(raw).hexdigest(),'elapsed_seconds':round(time.monotonic()-start,2),'observations':receipt['observations'],'scope':'External API asset generation only; not native app validation'}
        evidence.write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8');records.append(row);print(json.dumps({k:row[k] for k in ['case_id','task_id','status','billing']}),flush=True)
    (a.output/'runs.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
