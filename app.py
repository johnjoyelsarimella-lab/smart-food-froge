import os
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Demo knowledge base. The engine scores candidates against the user's target.
CATALOG = {
    'Dairy': [
        ('HDPE bottle with foil seal','Rigid bottle','₹2–3','High','temperature + barrier','Medium','recyclable plastic',3),
        ('Glass bottle with crimp seal','Rigid bottle','₹5–7','High','oxygen + temperature','Low','highly recyclable',5),
        ('Multi-layer PE/PET barrier pouch','Flexible pouch','₹1.5–2.5','Very high','oxygen + moisture','High','multi-layer plastic',2),
        ('PP tub with snap lid','Rigid tub','₹2.5–4','High','moisture + impact','Medium','recyclable plastic',3),
    ],
    'Fruits': [
        ('Micro-perforated MAP film','Flexible film','₹1.5–3','High','gas + moisture','Medium','material efficient',3),
        ('Perforated biodegradable PLA bag','Bio-based film','₹2–4','Medium','breathability','Low','compostable option',5),
        ('Clamshell PET with humidity control','Rigid clamshell','₹3–5','High','impact + humidity','Medium','recyclable plastic',2),
        ('Corrugated ventilated crate','Fiber crate','₹4–8','Medium','ventilation + impact','Low','recyclable fiber',5),
    ],
    'Meat': [
        ('Vacuum-sealed MAP tray film','Barrier tray','₹4–7','Very high','oxygen + leak control','High','multi-material',2),
        ('High-barrier EVOH/PA laminate','Barrier film','₹3–6','Very high','oxygen + moisture','High','multi-layer plastic',2),
        ('Butcher paper wrap','Fiber wrap','₹2–4','Low','basic moisture','Low','paper-based',5),
        ('Nitrogen-flushed foil pouch','Foil pouch','₹3–5','Very high','oxygen + light','High','harder to recycle',2),
    ],
    'Grains': [
        ('Resealable stand-up pouch','Flexible pouch','₹2–4','High','moisture + pests','Medium','recyclable mono-material option',3),
        ('Foil-laminated stand-up pouch','Barrier pouch','₹2.5–5','Very high','oxygen + moisture + light','High','multi-layer',2),
        ('Kraft paper multiwall bag','Fiber bag','₹1.5–3','Medium','basic moisture','Low','paper-based',5),
        ('Woven PP bag with PE liner','Woven bag','₹2–4','High','moisture + impact','Medium','reusable plastic',3),
    ],
    'Bakery': [
        ('PP clamshell','Rigid clamshell','₹2–4','High','impact + moisture','Medium','recyclable plastic',3),
        ('Metallized OPP film bag','Flexible film','₹1–2.5','High','moisture + oxygen','High','multi-layer film',3),
        ('Wax paper bag','Paper bag','₹1–2','Medium','basic moisture','Low','paper-based',5),
        ('Modified atmosphere PP tray','Barrier tray','₹3–5','Very high','gas + impact','Medium','recyclable PP base',3),
    ]
}

STORAGE_BONUS = {'Room': {'moisture': 10}, 'Refrigerated': {'temperature': 12}, 'Frozen': {'temperature': 18}}
PRIORITY = {
    'Balanced': {'protection':.35,'cost':.25,'eco':.25,'shelf':.15},
    'Eco-first': {'protection':.20,'cost':.15,'eco':.50,'shelf':.15},
    'Budget-first': {'protection':.20,'cost':.50,'eco':.20,'shelf':.10},
    'Max protection': {'protection':.55,'cost':.10,'eco':.10,'shelf':.25},
}

def candidate_score(item, commodity, days, storage, priority):
    name, typ, cost, protection, psub, footprint, fsub, eco = item
    # Transparent normalized heuristics for the prototype.
    cost_num = float(cost.replace('₹','').split('–')[0].replace('₹',''))
    cost_score = max(35, 100 - cost_num * 13)
    protection_score = {'Low':48,'Medium':68,'High':84,'Very high':96}[protection]
    shelf_score = min(100, 68 + days * (0.55 if protection in ('High','Very high') else 0.25))
    eco_score = eco * 20
    if storage == 'Frozen' and protection in ('High','Very high'): protection_score += 3
    # Product/storage compatibility gives a small domain-specific boost so a
    # material that is technically strong but poorly matched does not win only
    # because it is cheap or highly protective.
    compatibility = 0
    if commodity == 'Dairy' and storage == 'Refrigerated':
        compatibility = {'HDPE bottle with foil seal': 11, 'Glass bottle with crimp seal': 7, 'Multi-layer PE/PET barrier pouch': 0, 'PP tub with snap lid': 5}.get(name, 0)
    w=PRIORITY.get(priority, PRIORITY['Balanced'])
    score=round(protection_score*w['protection'] + cost_score*w['cost'] + eco_score*w['eco'] + shelf_score*w['shelf'] + compatibility)
    return max(55,min(97,score)), {'Protection':round(protection_score),'Cost':round(cost_score),'Sustainability':round(eco_score),'Shelf-life fit':round(shelf_score)}

def make_result(commodity, days, storage, priority):
    items=CATALOG.get(commodity,CATALOG['Dairy'])
    ranked=[]
    for item in items:
        score, profile=candidate_score(item,commodity,days,storage,priority); ranked.append((score,profile,item))
    ranked.sort(key=lambda x:x[0], reverse=True)
    score,profile,item=ranked[0]
    name,typ,cost,protection,psub,footprint,fsub,eco=item
    if priority=='Eco-first': reason=f"Selected for a lower environmental footprint while keeping enough barrier performance for {days} days in {storage.lower()} storage."
    elif priority=='Budget-first': reason=f"Selected for practical unit economics while still meeting the protection needed for a {days}-day target in {storage.lower()} storage."
    elif priority=='Max protection': reason=f"Selected because barrier and temperature protection are weighted highest for this {days}-day target in {storage.lower()} storage."
    else: reason=f"For {commodity.lower()} stored {storage.lower()} for {days} days, this option gives the strongest overall balance of protection, cost and sustainability."
    why=[f"{protection} protection fits the selected {storage.lower()} storage condition.",f"The material profile is suitable for the requested {days}-day shelf-life target.",f"Its cost and sustainability trade-offs match the '{priority.lower()}' preference."]
    badge='Eco-Friendly' if eco>=4 else ('Balanced' if priority=='Balanced' else 'Practical Choice')
    alternatives=[]
    for s,p,a in ranked[1:]:
        alternatives.append({'material':a[0],'type':a[1],'score':s,'stars':a[7],'badge':('Eco-Friendly' if a[7]>=4 else ('Budget Pick' if float(a[2].replace('₹','').split('–')[0])<=2.5 else 'Balanced')),'badgeClass':('eco' if a[7]>=4 else ('budget' if float(a[2].replace('₹','').split('–')[0])<=2.5 else 'balanced'))})
    return {'material':name,'commodity':commodity,'storage':storage,'shelf_life_days':days,'priority':priority,'score':score,'reason':reason,'badge':badge,'cost':cost,'protection':protection,'protection_sub':psub,'footprint':footprint,'footprint_sub':fsub,'suitability':'Excellent' if score>=82 else ('Strong' if score>=72 else 'Good'),'why':why,'profile':profile,'alternatives':alternatives,'source':'rules'}

@app.get('/')
def index(): return render_template('index.html')

@app.post('/api/recommend')
def recommend():
    data=request.get_json(silent=True) or {}
    commodity=data.get('commodity','Dairy'); storage=data.get('storage','Refrigerated'); priority=data.get('priority','Balanced')
    try: days=max(1,min(90,int(data.get('shelf_life_days',10))))
    except (TypeError,ValueError): days=10
    return jsonify(make_result(commodity,days,storage,priority))

@app.get('/api/health')
def health(): return jsonify({'status':'ok','app':'Smart Food Forge','engine':'explainable packaging recommender'})

if __name__=='__main__': app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)),debug=False)
