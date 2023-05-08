var counter = 2;
var textBox = "";
var hob = document.getElementById("hob")
function addBox()
{
        var div = document.createElement("div");
        div.setAttribute("class","form-group");
        div.setAttribute("id","box_"+counter);

        var textBox = "<input type='text' name='addresses[]' placeholder='Host Address "+counter+"' class='myinput form-control myinput' id='addresses_"+counter+"'><input class='mybox2' type='button' value='-'  onclick='removeBox(this)'>";

        div.innerHTML = textBox;
        hob.appendChild(div);
        counter++;
}

function removeBox(ele)
{
        ele.parentNode.remove();
}

function putJSON(url, data) {
        var rpc = new XMLHttpRequest();
        rpc.open("PUT", url, false);
        rpc.setRequestHeader("Content-Type", "application/json");

        rpc.onreadystatechange = function() {
                if (rpc.readyState == 4 && rpc.status == 200)
                        return this.responseText;
        }

        rpc.send(data);

        return rpc.status;
}

function getJSON(url) {
        var rpc = new XMLHttpRequest();
        rpc.open("GET", url, false);
        rpc.setRequestHeader("Content-Type", "application/json");

        rpc.onreadystatechange = function() {
                if (rpc.readyState == 4 && rpc.status == 200)
                        return this.responseText;
        }

        rpc.send(data);

        return rpc.status;
}

function createAdminView() {
        var hosts = document.getElementsByTagName("input");
        var data = '{"view": ['
        for (var i = 0; i < hosts.length; i++) {
                if (hosts[i].type == "text")
                        data += '"' + hosts[i].value + '",';
        }
        // remove trailing ,
        data = data.substring(0, data.length - 1);
        data += ']}';
        var http_code=  putJSON("/admin/view", data);
        if (http_code == 200) {
                alert("Successfully created network");
        }else{
                alert("Sorry! Server returned " + http_code);
        }
}

function putData(key, val){
        var data = '{"val": "' + val + '", "causal-metadata": {}}'
        var http_code=  putJSON("/data/" + key, data);
        if (http_code == 200 || http_code == 201) {
                alert("Successfully added key");
        }else{
                alert("Sorry! Server returned " + http_code);
        }
}

function loadFile(doc){
        doc.value = "Hello World";
}
