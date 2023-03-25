function reset() {
    document.getElementById("accountCreateForm").reset();
    }



function validateForm() {  
    //collect form data in JavaScript variables  
    var pw1 = document.getElementById("pwd1").value;  
    var pw2 = document.getElementById("pwd2").value;  
    console.log(pw1, pw2)
    if (pw1 != pw2) {  
        document.getElementById("message2").innerHTML = "**Passwords are not same";  
        return false;  
    } else {  
        return true;
    }  
}  


