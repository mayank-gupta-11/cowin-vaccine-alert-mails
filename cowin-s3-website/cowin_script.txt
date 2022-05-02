function myFunction(){
var areapin = document.getElementById("areapin").value;
var emailid = document.getElementById("emailid").value;
var data = JSON.stringify({"pin":areapin,"email":emailid});
var res = document.getElementById('response');

var xhr = new XMLHttpRequest();

xhr.addEventListener("readystatechange", function() {
  if(this.readyState === 4) {
    console.log(this.responseText);
	//alert(this.responseText);
	var msg = this.responseText;
	//alert(msg);
	var obj = JSON.parse(msg);
	res.innerHTML = obj.body;
  }
});
// https://pkimtpogp0.execute-api.ap-south-1.amazonaws.com/html-res/
xhr.open("POST", "https://pkimtpogp0.execute-api.ap-south-1.amazonaws.com/dev");
xhr.setRequestHeader("Authorization", "testmyk");
xhr.setRequestHeader("Content-Type", "application/json");

xhr.send(data);

return false;
}