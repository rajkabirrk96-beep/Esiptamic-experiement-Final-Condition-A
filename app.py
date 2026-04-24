<!DOCTYPE html>
<html>
<head>
    <title>Investment Session - Round {{ rnd }}</title>
    <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    <style>
        :root {
            --stock-a-color: #00b050; /* Professional Green */
            --stock-b-color: #3366cc; /* Royal Blue (Not Red/Danger!) */
        }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background: #f4f7f6; }
        .container { max-width: 900px; margin: auto; background: white; padding: 30px; border-radius: 12px; shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
        .chart-card { border: 1px solid #ddd; padding: 15px; border-radius: 8px; }
        .label-a { color: var(--stock-a-color); font-weight: bold; }
        .label-b { color: var(--stock-b-color); font-weight: bold; }
        .allocation-section { background: #f9f9f9; padding: 20px; border-radius: 8px; border-top: 4px solid var(--stock-b-color); }
        input[type=range] { width: 100%; margin: 15px 0; }
    </style>
</head>
<body>

<div class="container">
    <h2>Round {{ rnd }} of {{ total_rounds }}</h2>
    <p>{{ ai_text|safe }}</p>

    <div class="chart-grid">
        <div class="chart-card">
            <h3 class="label-a">{{ sa }}</h3>
            <p>Real-Time Price Action: <strong>{{ change_a }}</strong></p>
            <div id="chartA"></div>
        </div>

        <div class="chart-card">
            <h3 class="label-b">{{ sb }}</h3>
            <p>Real-Time Price Action: <strong>{{ change_b }}</strong></p>
            <div id="chartB"></div>
        </div>
    </div>

    <form action="/round/{{ rnd }}/submit" method="POST" class="allocation-section">
        <h3>Allocate Your $1,000</h3>
        <p>Move the slider to split your investment between Stock A and <span class="label-b">Stock B</span>.</p>
        
        <div style="display: flex; justify-content: space-between;">
            <span class="label-a">{{ sa }}: $<span id="valA">500</span></span>
            <span class="label-b">{{ sb }}: $<span id="valB">500</span></span>
        </div>
        
        <input type="range" name="alloc_a" id="allocSlider" min="0" max="1000" value="500" oninput="updateAlloc(this.value)">

        <p>How confident are you in this decision? (0-100%)</p>
        <input type="range" name="confidence" min="0" max="100" value="50">
        
        <button type="submit" style="background: #222; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%;">Confirm Allocation</button>
    </form>
</div>

<script>
    // DISABLE BACK BUTTON
    history.pushState(null, null, location.href);
    window.onpopstate = function () {
        history.go(1);
    };

    function updateAlloc(val) {
        document.getElementById('valA').innerText = val;
        document.getElementById('valB').innerText = 1000 - val;
    }

    // INTERACTIVE CHARTS
    const optionsA = {
        chart: { type: 'line', height: 200, toolbar: {show: false}, animations: {enabled: false} },
        series: [{ name: 'Price', data: {{ traj_a|safe }} }],
        colors: ['#00b050'],
        stroke: { curve: 'smooth', width: 2 },
        tooltip: { x: { show: true }, marker: { show: false } }
    };

    const optionsB = {
        chart: { type: 'line', height: 200, toolbar: {show: false}, animations: {enabled: false} },
        series: [{ name: 'Price', data: {{ traj_b|safe }} }],
        colors: ['#3366cc'], // Blue for Stock B
        stroke: { curve: 'smooth', width: 2 },
        tooltip: { x: { show: true }, marker: { show: false } }
    };

    new ApexCharts(document.querySelector("#chartA"), optionsA).render();
    new ApexCharts(document.querySelector("#chartB"), optionsB).render();
</script>

</body>
</html>
