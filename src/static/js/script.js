// adds host address box once add button is clicked in new_network.html and increments counter
var counter = 2;
var textBox = "";
function addBox()
{
        var addrss = document.getElementById("addrss")
        var div = document.createElement("div");
        div.setAttribute("class","form-group");
        div.setAttribute("id","box_"+counter);

        var textBox = "<input type='text' name='addresses[]' placeholder='Host Address "+counter+"' class='myinput form-control myinput' id='addresses_"+counter+"'><input class='mybox2' type='button' value='-'  onclick='removeBox(this)'>";

        div.innerHTML = textBox;
        addrss.appendChild(div);
        counter++;
}

// removes host address box once delete button is clicked in new_network.html
function removeBox(ele)
{
        counter--;
        ele.parentNode.remove();
}

// dropdown menu in docedit.html
function toggleDropdown() {
  var dropdownMenu = document.getElementById("dropdownMenu");
  dropdownMenu.classList.toggle("open");
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

function createNewFile() {
        var fileInput = document.getElementById('fileInput');
        var file = fileInput.files[0]; // Get the selected file

        if (file) {
                var reader = new FileReader();

                reader.onload = function(e) {
                var contents = e.target.result; // Binary contents of the file
                console.log(contents)
                console.log(e.target)
                var fileName = file.name;

                // For example, you can convert the binary data to a Uint8Array
                var binaryData = new Uint8Array(contents);
                putData(fileName, binaryData)
                };

                reader.readAsArrayBuffer(file);
        }
        location.reload()
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

// search box dynamically iterates through list
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

// search box animation
document.addEventListener("DOMContentLoaded", function() {
  var searchInput = document.getElementById("search");
  var searchBox = document.querySelector(".search-box");

  searchInput.addEventListener("focus", function() {
    searchBox.classList.add("border-searching");
  });

  searchInput.addEventListener("blur", function() {
    searchBox.classList.remove("border-searching");
  });

});
