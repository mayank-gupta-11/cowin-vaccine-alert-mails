
function myFunction(){
var areapin = document.getElementById("areapin").value;
var emailid = document.getElementById("emailid").value;
var data = JSON.stringify({"pin":areapin,"email":emailid});
var res = document.getElementById('response');

var xhr = new XMLHttpRequest();

	xhr.addEventListener("readystatechange", function() {
	  if(this.readyState === 4) {
		console.log(this.responseText);
		//window.alert(this.responseText)
		//alert(this.responseText);
		var msg = this.responseText;
		//alert(typeof msg);
		
		try{
			var obj = JSON.parse(msg);
			res.innerHTML = obj.body;
		}
		catch(err)
		{
			res.innerHTML = 'You Have Exceeded the maximum Number of trials, Your IP has been Blocked.';
		}
		
		
	  }
	  else{
		res.innerHTML = "<img src='roll.gif'>";
	  }
	});
	// https://pkimtpogp0.execute-api.ap-south-1.amazonaws.com/main-lambdattac
	// https://8i7br2mmt7.execute-api.ap-south-1.amazonaws.com/dev
	// https://pkimtpogp0.execute-api.ap-south-1.amazonaws.com/html-res/
	xhr.open("POST", "https://pt5u9bxa5g.execute-api.ap-south-1.amazonaws.com/dev");
	//xhr.setRequestHeader("Authorization", "testmyk");
	xhr.setRequestHeader("Content-Type", "application/json");

	xhr.send(data);

	return false;

}

