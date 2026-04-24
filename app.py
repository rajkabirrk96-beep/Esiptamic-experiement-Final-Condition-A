from flask import Flask, render_template, request, session, redirect, url_for
import csv, os, uuid, json, math
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'epistemic_alignment_conditionA_2026' # Updated key

ALL_ROUNDS = {
    "Information Technology": [
        (1,  "Nexora Systems",    142.50, 0.38,  0.05, "Dataflux Inc",      87.20,  0.21,  0.08),
        (2,  "CloudPeak Corp",    156.80, 0.45,  0.06, "ByteWave Ltd",      94.40,  0.12, 0.12),
        (3,  "QuantumBridge Inc", 203.60, 0.31,  0.09, "PixelStream Corp",  118.90, 0.18,  0.11),
        (4,  "CipherCore Ltd",    178.30, 0.78,  0.07, "SoftNova Inc",      132.60, 0.34,  0.10),
        (5,  "GridLogic Corp",    145.20, 0.55,  0.05, "VaultTech Ltd",     159.40, 0.22, 0.08),
        (6,  "NeuralPath Inc",    97.30,  0.89,  0.13, "CodeSpire Corp",    198.70, 0.41,  0.09),
        (7,  "DataSphere Ltd",    122.50, 0.67,  0.10, "SyncWave Inc",      181.90, 0.35,  0.07),
        (8,  "ByteForge Corp",    89.60,  0.91,  0.08, "PulseNet Ltd",      135.80, 0.42,  0.11),
        (9,  "CoreMatrix Inc",    147.80, 0.58,  0.06, "TechSpan Corp",     201.30, 0.33,  0.09),
        (10, "InfiniteLoop Ltd",  162.10, 0.44,  0.07, "NodeBridge Inc",    184.20, 0.27,  0.12),
        (11, "AlphaGrid Corp",    99.80,  0.76,  0.10, "SignalBase Ltd",    125.30, 0.39,  0.08),
        (12, "OmegaStack Inc",    138.40, 0.52,  0.09, "ProtoCore Corp",    149.90, 0.25,  0.06),
        (13, "ZenithTech Ltd",    204.70, 0.38,  0.11, "ApexFlow Inc",      91.20,  0.71,  0.07),
        (14, "VectorNet Corp",    186.50, 0.83,  0.08, "PrismData Ltd",     102.10, 0.46,  0.13),
        (15, "HelixSoft Inc",     152.30, 0.08,  0.05, "TerraLogic Corp",   127.80, 0.39,  0.10),
    ],
    # Rounds simplified to represent intraday (smaller % changes)
}

def generate_trajectory(start_price, growth_pct, volatility, seed):
    import random
    random.seed(seed)
    # Using 60 points to represent 60 minutes of "Real-Time Price Action"
    minutes = 60 
    daily_drift = (growth_pct / 100) / minutes
    daily_vol   = (volatility / 100)
    prices = [start_price]
    for _ in range(minutes):
        r = random.gauss(daily_drift, daily_vol)
        prices.append(round(prices[-1] * (1 + r), 2))
    return prices

def get_final_change(start, growth_pct):
    # This reflects the "Real-Time Price Action" label
    end = start * (1 + growth_pct/100)
    change = ((end - start) / start) * 100
    sign = "+" if change >= 0 else ""
    return f"{sign}{change:.2f}%", end

def build_ai_text(rnd, sa, sb, goal, risk, hold, rd):
    # REMOVED: All IRB and formal regulatory language
    return (
        f"Based on your <strong>{goal}</strong> goal and <strong>{risk}</strong> preference, "
        f"the engine identifies <strong>{sa}</strong> and <strong>{sb}</strong> "
        f"as optimal signals for this session."
    )

DATA_FILE = "/data/responses_A.csv"
CSV_HEADERS = (
    ["participant_id","condition","sector","hold_duration",
     "investment_goal","risk_tolerance","prolific_id",
     "started_at","completed_at"] +
    [f"R{r}_{f}" for r in range(1,16)
     for f in ["stock_a","stock_b","alloc","conf","aci","return"]] +
    ["total_return","benchmark_return","portfolio_score",
     "mean_confidence","mean_accuracy","oci","mean_aci","correct_rounds"] +
    ["age","gender","education","experience",
     "robo_prior","manipulation_check","open_text"]
)

def ensure_csv():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE,'w',newline='') as f:
            csv.DictWriter(f,fieldnames=CSV_HEADERS).writeheader()

def save_response(data):
    ensure_csv()
    with open(DATA_FILE,'a',newline='',encoding='utf-8') as f:
        csv.DictWriter(f,fieldnames=CSV_HEADERS, extrasaction='ignore').writerow(data)

@app.route('/')
def index():
    session.clear()
    session['participant_id']=str(uuid.uuid4())[:8]
    session['prolific_id']=request.args.get('PROLIFIC_PID','')
    session['condition']='A'
    session['started_at']=datetime.now().isoformat()
    session['rd']={}
    return render_template('welcome.html')

@app.route('/sector', methods=['GET', 'POST'])
def sector_page():
    if request.method == 'POST':
        session['sector']=request.form.get('sector_choice','Information Technology')
        return redirect(url_for('prestudy'))
    return render_template('sector.html')

@app.route('/prestudy', methods=['GET', 'POST'])
def prestudy():
    if request.method == 'POST':
        session['hold_duration']=request.form.get('hold_duration','')
        session['investment_goal']=request.form.get('investment_goal','')
        session['risk_tolerance']=request.form.get('risk_tolerance','')
        return redirect(url_for('round_page',rnd=1))
    return render_template('prestudy.html')

@app.route('/round/<int:rnd>')
def round_page(rnd):
    # BACK-BUTTON PROTECTION: If they try to go to a finished round, force them forward
    current_progress = len(session.get('rd', {})) // 6 # Each round saves 6 fields
    if rnd <= current_progress:
        return redirect(url_for('round_page', rnd=current_progress + 1))
        
    if rnd<1 or rnd>15: return redirect(url_for('final_results'))
    sector=session.get('sector','Information Technology')
    row=ALL_ROUNDS.get(sector,ALL_ROUNDS["Information Technology"])[rnd-1]
    rnd_num,sa,pa,ga,va,sb,pb,gb,vb=row
    
    # Label changed to "Real-Time Price Action"
    change_a,_=get_final_change(pa,ga)
    change_b,_=get_final_change(pb,gb)
    
    rd=session.get('rd',{})
    ai_text=build_ai_text(rnd,sa,sb,
        session.get('investment_goal',''),
        session.get('risk_tolerance',''),
        session.get('hold_duration',''),rd)
    
    traj_a=generate_trajectory(pa,ga,va,seed=rnd*100+1)
    traj_b=generate_trajectory(pb,gb,vb,seed=rnd*100+2)
    
    return render_template('round.html',
        rnd=rnd,sa=sa,sb=sb,pa=pa,pb=pb,
        change_a=change_a,change_b=change_b,
        traj_a=json.dumps(traj_a),
        traj_b=json.dumps(traj_b),
        ai_text=ai_text,
        total_rounds=15,sector=sector)

@app.route('/round/<int:rnd>/submit',methods=['POST'])
def round_submit(rnd):
    sector=session.get('sector','Information Technology')
    alloc_a=float(request.form.get('alloc_a',500))
    alloc_pct=alloc_a/10
    conf=float(request.form.get('confidence',50))
    
    row=ALL_ROUNDS.get(sector,ALL_ROUNDS["Information Technology"])[rnd-1]
    ra=row[3]/100; rb=row[6]/100
    alloc_b=1000-alloc_a
    actual=(alloc_a*ra)+(alloc_b*rb)
    
    rd=session.get('rd',{})
    rd[f'R{rnd}_stock_a']=row[1]
    rd[f'R{rnd}_stock_b']=row[5]
    rd[f'R{rnd}_alloc']=alloc_pct
    rd[f'R{rnd}_conf']=conf
    rd[f'R{rnd}_return']=round(actual,2)
    session['rd']=rd
    
    return redirect(url_for('trajectory',rnd=rnd))

@app.route('/trajectory/<int:rnd>')
def trajectory(rnd):
    sector=session.get('sector','Information Technology')
    row=ALL_ROUNDS.get(sector,ALL_ROUNDS["Information Technology"])[rnd-1]
    rnd_num,sa,pa,ga,va,sb,pb,gb,vb=row
    change_a,_=get_final_change(pa,ga)
    change_b,_=get_final_change(pb,gb)
    traj_a=generate_trajectory(pa,ga,va,seed=rnd*100+1)
    traj_b=generate_trajectory(pb,gb,vb,seed=rnd*100+2)
    
    if rnd==15: next_url=url_for('final_results')
    else: next_url=url_for('round_page',rnd=rnd+1)
    
    return render_template('trajectory.html',
        rnd=rnd,sa=sa,sb=sb,pa=pa,pb=pb,
        change_a=change_a,change_b=change_b,
        traj_a=json.dumps(traj_a),
        traj_b=json.dumps(traj_b),
        next_url=next_url,sector=sector)

# Remaining routes for results and data downloading...
@app.route('/final_results')
def final_results():
    return render_template('final_results.html')

if __name__=='__main__':
    ensure_csv()
    app.run(debug=True,port=5000)
