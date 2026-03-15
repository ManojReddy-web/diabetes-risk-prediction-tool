from flask import Flask, request, render_template_string

app = Flask(__name__)

# -----------------------------
# Risk Calculation Function
# -----------------------------
def calculate_diabetes_risk(age, gender, family, rbs, hba1c, bmi, fbs, ppbs, ogtt, bp, chol_med, pcos):

    score = 0

    if age >= 45:
        score += 15
    elif age >= 35:
        score += 10

    if gender == "male":
        score += 5

    if family == "yes":
        score += 15

    if rbs:
        if rbs >= 200:
            score += 25
        elif rbs >= 140:
            score += 12

    if hba1c:
        if hba1c >= 6.5:
            score += 25
        elif hba1c >= 5.7:
            score += 12

    if bmi:
        if bmi >= 30:
            score += 20
        elif bmi >= 25:
            score += 10

    if fbs:
        if fbs >= 126:
            score += 20
        elif fbs >= 100:
            score += 10

    if ppbs:
        if ppbs >= 200:
            score += 20
        elif ppbs >= 140:
            score += 10

    if ogtt:
        if ogtt >= 200:
            score += 25
        elif ogtt >= 140:
            score += 12

    if bp == "yes":
        score += 10

    if chol_med == "yes":
        score += 10

    if gender == "female" and pcos == "yes":
        score += 10

    return min(score, 100)


# -----------------------------
# Helper function
# -----------------------------
def get_float(value):
    try:
        return float(value)
    except:
        return None


# -----------------------------
# HTML
# -----------------------------
HTML_PAGE = """

<!DOCTYPE html>
<html>
<head>
<title>Type 2 Diabetes Risk Predictor</title>

<style>

body{
font-family:Arial;
background:linear-gradient(120deg,#e3f2fd,#fce4ec);
display:flex;
justify-content:center;
align-items:center;
min-height:100vh;
margin:0;
}

.container{
background:white;
padding:35px;
border-radius:15px;
width:480px;
box-shadow:0 10px 30px rgba(0,0,0,0.15);
}

h2{
text-align:center;
color:#1565c0;
}

label{
font-weight:bold;
margin-top:12px;
display:block;
}

input,select{
width:100%;
padding:10px;
margin-top:6px;
border-radius:7px;
border:1px solid #ccc;
}

button{
width:100%;
margin-top:20px;
padding:12px;
border:none;
border-radius:8px;
background:#1976d2;
color:white;
font-size:16px;
cursor:pointer;
}

button:hover{
background:#0d47a1;
}

.result-card{
margin-top:25px;
padding:20px;
border-radius:10px;
text-align:center;
}

.low{
background:#e8f5e9;
color:#2e7d32;
}

.moderate{
background:#fff8e1;
color:#f57f17;
}

.high{
background:#ffebee;
color:#c62828;
}

.progress{
background:#eee;
height:22px;
border-radius:12px;
margin-top:10px;
overflow:hidden;
}

.progress-bar{
height:100%;
background:linear-gradient(90deg,green,yellow,red);
}

.missing{
color:red;
font-size:13px;
margin-top:10px;
}

.disclaimer{
margin-top:15px;
font-size:12px;
color:#777;
text-align:center;
}

</style>
</head>

<body>

<div class="container">

<h2>Type 2 Diabetes Risk Predictor</h2>

<form method="POST">

<label>Age</label>
<input type="number" name="age" required>

<label>Gender</label>
<select name="gender">
<option value="male">Male</option>
<option value="female">Female</option>
</select>

<label>Family History</label>
<select name="family">
<option value="no">No</option>
<option value="yes">Yes</option>
</select>

<label>Random Blood Sugar (mg/dL)</label>
<input type="number" name="rbs">

<label>HbA1c (%)</label>
<input type="number" step="0.1" name="hba1c">

<label>BMI</label>
<input type="number" step="0.1" name="bmi">

<label>Fasting Blood Sugar</label>
<input type="number" name="fbs">

<label>Post Prandial Blood Sugar</label>
<input type="number" name="ppbs">

<label>OGTT</label>
<input type="number" name="ogtt">

<label>High BP?</label>
<select name="bp">
<option value="no">No</option>
<option value="yes">Yes</option>
</select>

<label>Using Cholesterol Medication?</label>
<select name="chol_med">
<option value="no">No</option>
<option value="yes">Yes</option>
</select>

<label>PCOS (Females Only)</label>
<select name="pcos">
<option value="no">No</option>
<option value="yes">Yes</option>
</select>

<button type="submit">Predict Risk</button>

</form>

{% if result %}

<div class="result-card {{risk_class}}">

<h3>{{result}}</h3>

<div class="progress">
<div class="progress-bar" style="width:{{score}}%"></div>
</div>

<p>{{tips}}</p>

{% if missing %}
<div class="missing">
Missing tests: {{missing}} <br>
Please perform these tests for more accurate prediction.
</div>
{% endif %}

</div>

{% endif %}

<div class="disclaimer">
Educational tool only. Not a medical diagnosis.
</div>

</div>

</body>
</html>
"""

# -----------------------------
# Main Route
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def index():

    result=None
    risk_class=""
    score=0
    tips=""
    missing=""

    if request.method=="POST":

        age=int(request.form["age"])
        gender=request.form["gender"]
        family=request.form["family"]

        rbs=get_float(request.form.get("rbs"))
        hba1c=get_float(request.form.get("hba1c"))
        bmi=get_float(request.form.get("bmi"))
        fbs=get_float(request.form.get("fbs"))
        ppbs=get_float(request.form.get("ppbs"))
        ogtt=get_float(request.form.get("ogtt"))

        bp=request.form["bp"]
        chol_med=request.form["chol_med"]
        pcos=request.form.get("pcos","no")

        if gender=="male":
            pcos="no"

        score=calculate_diabetes_risk(age,gender,family,rbs,hba1c,bmi,fbs,ppbs,ogtt,bp,chol_med,pcos)

        if score>=70:
            result=f"High Risk ({score}%)"
            risk_class="high"
            tips="Consult doctor and confirm with lab tests."

        elif score>=40:
            result=f"Moderate Risk ({score}%)"
            risk_class="moderate"
            tips="Improve diet and exercise regularly."

        else:
            result=f"Low Risk ({score}%)"
            risk_class="low"
            tips="Maintain healthy lifestyle."

        missing_tests=[]
        if not rbs: missing_tests.append("RBS")
        if not hba1c: missing_tests.append("HbA1c")
        if not fbs: missing_tests.append("FBS")
        if not ppbs: missing_tests.append("PPBS")
        if not ogtt: missing_tests.append("OGTT")

        missing=", ".join(missing_tests)

    return render_template_string(HTML_PAGE,result=result,risk_class=risk_class,score=score,tips=tips,missing=missing)


if __name__=="__main__":
    app.run(debug=True)
