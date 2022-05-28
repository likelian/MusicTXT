// Load txt file to text area
var fname = document.getElementById("fname_ref").innerText;
window.onload = function loadTxt() {
    console.log(fname);
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("myTextArea").innerHTML = this.responseText;
        }
    };
    xhttp.open("GET", "../media/"+fname+".txt", true);
    xhttp.send();
    console.log("txt loaded");
}

// everytime when press "run" button
// step 1: client submit the form
// step 2: server save the form as txt
// step 3: server convert txt to lily, then to pdf and midi
// django requires a csrf token, it needs to be set in requestheader
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

function sendTxt() {
    var fname = document.getElementById("fname_ref").innerText;
    var xhr = new XMLHttpRequest();
    var fd = new FormData();
    var data = document.getElementById("myTextArea").value;
    fd.append('data', data);
    fd.append('fname', fname);
    xhr.addEventListener('load', function(e) {
        document.getElementById("runStatus").innerHTML = "Successfully Run!";
    });
    xhr.addEventListener('error', function(e) {
        alert('request failed for some reason, please look into the sendText()');
    });
    xhr.open('POST', '../update/');
    xhr.setRequestHeader('X-CSRFToken', csrftoken);
    xhr.setRequestHeader('mode', 'same-origin');
    xhr.send(fd);
}
