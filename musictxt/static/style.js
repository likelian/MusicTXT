// Load txt file to text area
// Start execution as soon as page is loaded
var fname = document.getElementById("fname_ref").innerText;
window.onload = function loadTxt() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("myTextArea").innerHTML = this.responseText;
            console.log(fname, ".txt has been loaded!");
            // sendTxt();
        } else if (this.status == 404) {
            console.log("can't find the txt file, will create a new one from template.");
            var xhttp2 = new XMLHttpRequest();
            xhttp2.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    document.getElementById("myTextArea").innerHTML = this.responseText;
                    console.log("ref.txt has been loaded!");
                    document.getElementById("myIframe").src = "/media/tutorial.pdf";
                    console.log("tutorial.pdf has been loaded");
                    // sendTxt();
                } else if (history.status == 404) {
                    console.log("Can't even find the template text!");
                }
            }
            xhttp2.open("GET", "../media/"+"ref.txt", true);
            xhttp2.send();
        }
    };
    xhttp.open("GET", "../media/"+fname+".txt", true);
    xhttp.send();
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
    // refresh iframe when success
    xhr.addEventListener('load', function(e) {
        document.getElementById("runStatus").innerHTML = "Success!";
        console.log(xhr.response);
        document.getElementById("myIframe").contentWindow.location.reload();
    });
    xhr.addEventListener('loadstart', function(e) {
        document.getElementById("runStatus").innerHTML = "Loading...";
    });
    xhr.addEventListener('error', function(e) {
        alert('request failed for some reason, please look into the sendText()');
    });
    xhr.open('POST', '../update/');
    xhr.setRequestHeader('X-CSRFToken', csrftoken);
    xhr.setRequestHeader('mode', 'same-origin');
    xhr.send(fd);
}
