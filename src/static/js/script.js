var counter = 2;
var textBox = "";
function addBox()
{
        var hob = document.getElementById("hob")
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
        counter--;
        ele.parentNode.remove();
}

function dropdownChange() {
        var dropdown = document.getElementById("dropdown");
        var textarea = document.getElementById("document");
        textarea.readOnly = true;
        dropdown.addEventListener("change", function () {
                textarea.readOnly = (dropdown.value === "View");
        });
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

function getJSON(url, data) {
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

function getData(key){
        var data = '{"causal-metadata": {}}'
        var response =  getJSON("/data/" + key, data);

        return response;
}

function loadFile(doc){
        doc.value = getData("test");
}

 function filterList(){
        const searchInput = document.querySelector('#search');
        const filter = searchInput.value.toLowerCase();
        const listItems = document.querySelectorAll('.list-group-item');
        listItems.forEach((item) =>{
                let text = item.textContent;
                if(text.toLowerCase().includes(filter.toLowerCase())){
                     item.style.display = '';
                   } else{
                     item.style.display = 'none';
                   }
       });
}

document.addEventListener("DOMContentLoaded", function() {
  var searchInput = document.getElementById("search");
  var searchBox = document.querySelector(".search-box");
  var searchIcon = document.querySelector(".search-icon");
  var goIcon = document.querySelector(".go-icon");
  var searchForm = document.querySelector(".search-form");

  searchInput.addEventListener("focus", function() {
    searchBox.classList.add("border-searching");
    searchIcon.classList.add("si-rotate");
  });

  searchInput.addEventListener("blur", function() {
    searchBox.classList.remove("border-searching");
    searchIcon.classList.remove("si-rotate");
  });

});
