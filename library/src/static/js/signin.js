signin = document.getElementsByClassName("signinbody")[0]
signin.addEventListener("keyup" , function(event){
    if(event.key === "Enter"){
        match();
    }
})


function match(){

    var pwd = document.getElementById("signinpwd").value;
    var conpwd = document.getElementById("signinconpwd").value;

    if(pwd!==conpwd){

        alert("Password and Confirm Password must Match!");
        return;

    }

    document.forms[1].submit();

}
