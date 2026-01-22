async function loadData() {
    try {
        const res = await fetch("/data");
        const data = await res.json();

        document.getElementById("hive_id").innerText = data.hive_id;
        document.getElementById("status").innerText = data.status;
        document.getElementById("temperature").innerText = data.temperature;
        document.getElementById("humidity").innerText = data.humidity;
        document.getElementById("weight1").innerText = data.weight1;
        document.getElementById("weight2").innerText = data.weight2;
        document.getElementById("total_weight").innerText = data.total_weight;
        document.getElementById("timestamp").innerText = data.timestamp;
    } catch (e) {
        console.error("Error loading data", e);
    }
}

loadData();
setInterval(loadData, 5000); // auto refresh every 5 sec
