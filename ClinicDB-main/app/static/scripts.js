function sendPutRequest(event) {
    event.preventDefault();
    var formData = new FormData(document.getElementById('updateForm'));
    var jsonData = {};
    formData.forEach((value, key) => { jsonData[key] = value; });

    fetch('/', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(jsonData)
    })
    .then(response => response.text())
    .then(data => alert(data));
}

function sendDeleteRequest(event) {
    event.preventDefault();
    var patientId = document.getElementById('patient_id').value;

    fetch('/', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ PatientID: patientId })
    })
    .then(response => response.text())
    .then(data => alert(data));
}

function sendPutSocialHistoryRequest(event) {
    event.preventDefault();
    var formData = new FormData(document.getElementById('updateForm'));
    var jsonData = {};
    formData.forEach((value, key) => { jsonData[key] = value; });

    fetch('/socialhistory', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(jsonData)
    })
    .then(response => response.text())
    .then(data => alert(data));
}

function sendPutRequestDrugHistory(event) {
    event.preventDefault();
    var formData = new FormData(document.getElementById('updateForm'));
    var jsonData = {};
    formData.forEach((value, key) => { jsonData[key] = value; });

    fetch('/drughistory', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(jsonData)
    })
    .then(response => response.text())
    .then(data => alert(data));

}