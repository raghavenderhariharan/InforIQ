import json, random, datetime as dt, math
random.seed(7)
end = dt.date(2026,10,8); days=[end-dt.timedelta(d) for d in range(29,-1,-1)]
def w(n,o): json.dump(o,open(n,'w'),indent=0)
comp=[
 # id,name,stage,layer,status,lag,throughput,to,note
 ("syteline","Syteline ERP",0,"Source ERP","ok",None,"412K rows/day","s3_syteline","CloudSuite Industrial (Syteline) system of record."),
 ("ft","FT",0,"Source ERP","ok",None,"96K rows/day","s3_ft","FT application database."),
 ("cpq","CPQ",0,"Source ERP","warn",None,"58K rows/day","s3_cpq","Configure-price-quote; extract job ran late twice this week."),
 ("s3_syteline","Syteline raw",1,"S3 data lake (slow)","ok",42,"412K rows/day","ice_syteline","Raw landing zone in S3. Batch, slow to query."),
 ("s3_ft","FT raw",1,"S3 data lake (slow)","ok",38,"96K rows/day","ice_ft","Raw landing zone in S3."),
 ("s3_cpq","CPQ raw",1,"S3 data lake (slow)","warn",71,"58K rows/day","ice_cpq","Raw landing zone in S3; lag above the 60-minute target."),
 ("ice_syteline","Syteline Iceberg",2,"Iceberg tables (faster)","ok",9,"405K rows/day","po so canonical","Curated Iceberg tables; fast, versioned reads."),
 ("ice_ft","FT Iceberg",2,"Iceberg tables (faster)","ok",7,"95K rows/day","po canonical","Curated Iceberg tables."),
 ("ice_cpq","CPQ Iceberg",2,"Iceberg tables (faster)","warn",14,"55K rows/day","so canonical","Curated Iceberg tables; inherits CPQ lag."),
 ("canonical","Canonical model",3,"Canonical model","ok",12,"18 entities","rules","Infor's standardised data model in Data Fabric; IQ reads this, never the live ERP."),
 ("po","Purchase orders",3,"Canonical model","ok",11,"8.4K changes/day","events","Canonical PO entity; changes emit events."),
 ("so","Sales orders",3,"Canonical model","ok",13,"6.1K changes/day","events","Canonical SO entity; changes emit events."),
 ("fde","FDE",3,"Event producers","ok",None,"1.2K events/day","events","Forward-deployed engineering producers."),
 ("cust","Customer",3,"Event producers","ok",None,"2.9K events/day","events","Customer-side event producers."),
 ("dev","Developer",3,"Event producers","ok",None,"0.6K events/day","events","Developer and test event producers."),
 ("events","Event hub",4,"Events","ok",2,"19K events/day","erx","Publishes business events after commit to the reasoning layer."),
 ("rules","Rules and ontology",4,"Infor IQ","ok",None,"412 rules","erx","Ontology, tenant overlays and business rules that ground every answer."),
 ("erx","ERX reasoning",5,"Infor IQ","ok",1,"5.2K decisions/day","hitl agents rules","Evaluates events against rules; returns AUTHORIZED, DENIED or REQUIRES_ESCALATION."),
 ("hitl","Human in the loop",5,"Governance","bad",None,"queue","agents","Reviewers clear escalations; queue age is over the 24-hour target."),
 ("agents","Agents (A)",6,"Agents","ok",None,"4.6K actions/day","erp_mcp","AI agents act only after IQ authorises."),
 ("erp_mcp","ERP via MCP tools",6,"Execution","ok",None,"4.6K actions/day","","The agent performs the action through ERP MCP tools; the ERP stays the final arbiter."),
]
w("components.json",[dict(id=c[0],name=c[1],stage=c[2],layer=c[3],status=c[4],lag_minutes=c[5],throughput=c[6],feeds=c[7],note=c[8]) for c in comp])
base={"Syteline":412000,"FT":96000,"CPQ":58000}
ing=[]
for i,d in enumerate(days):
  wk = 0.55 if d.weekday()>=5 else 1
  for s,b in base.items():
    r=int(b*wk*(1+0.004*i)*random.uniform(.9,1.1))
    loss=random.uniform(.005,.02) if s!="CPQ" else random.uniform(.02,.08)
    if s=="CPQ" and i in (24,27): loss=.35
    ing.append(dict(day=d.isoformat(),source=s,rows_s3=r,rows_iceberg=int(r*(1-loss))))
w("ingest_daily.json",ing)
fr=[]
for s,l in {"Syteline":(42,9,12),"FT":(38,7,10),"CPQ":(71,14,19)}.items():
  for st,v in zip(["S3 raw","Iceberg","Canonical"],l): fr.append(dict(source=s,stage=st,lag_minutes=v))
w("freshness.json",fr)
ev=[];dec=[]
for i,d in enumerate(days):
  wk = 0.5 if d.weekday()>=5 else 1
  for ch,b in {"Canonical changes":14500,"Customer":2900,"FDE":1200,"Developer":600}.items():
    ev.append(dict(day=d.isoformat(),channel=ch,events=int(b*wk*(1+.006*i)*random.uniform(.85,1.15))))
  tot=int(5200*wk*(1+.006*i)*random.uniform(.9,1.1))
  esc=.06-.0008*i+random.uniform(-.01,.01); den=.09+random.uniform(-.015,.015)
  e=int(tot*esc); dn=int(tot*den)
  dec+= [dict(day=d.isoformat(),outcome="Authorized",decisions=tot-e-dn),dict(day=d.isoformat(),outcome="Denied",decisions=dn),dict(day=d.isoformat(),outcome="Escalated",decisions=e)]
w("events_daily.json",ev); w("decisions_daily.json",dec)
vend=["Acme","Beta","Gamma","Delta","Orion","Kestrel","Nimbus","Vega","Atlas","Corvid","Halcyon","Juno"]
reasons=["Amount above agent limit","Vendor risk score 3 or more","Lines on backorder","New vendor, no history","Price variance above 5%","Duplicate PO suspected"]
q=[]
for k in range(14):
  amt=random.choice([12,18,24,31,45,52,63,78,94,120])*1000+random.randint(0,999)
  age=round(random.choice([1.5,3,6,9,14,20,27,31,38,46])+random.random(),1)
  q.append(dict(case=f"ESC-{3100+k}",po=f"PO-{4500+k*7}",vendor=vend[k%len(vend)],amount=amt,reason=random.choice(reasons),age_hours=age,assigned_role=random.choice(["Purchasing manager","VP procurement","Purchasing manager"]),status="Overdue" if age>24 else "Open"))
w("hitl_queue.json",q)
