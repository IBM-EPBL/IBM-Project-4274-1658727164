var date = new Date()
document.forms.signup.onsubmit = function(event){
    document.forms.signup.style.pointerEvents = "none";
    document.forms.signup.style.opacity = .5;
    document.querySelector(".spin-ab").removeAttribute("hidden")
    
    setTimeout(function(){
        document.forms.signup.reset()
        document.forms.signup.style.removeProperty("pointer-events")
        document.forms.signup.style.removeProperty("opacity")
        document.querySelector(".spin-ab").setAttribute("hidden","")
    },5000)
}

function checkNumber(){
  let phoneNumber = document.forms.signup.number.value
  if(phoneNumber.length != 10){
    document.querySelector('.insertError').innerText = "Enter a valid Phone Number"
    changeError()
  }
}

function checkPassword(){
  let password = document.forms.signup.password.value
  let Cpassword = document.forms.signup.confirmPassword.value
  if(password != Cpassword){
    document.querySelector('.password-match').style.transform = 'scale(1)'
  }else{
    document.querySelector('.password-match').style.transform = 'scale(0)'
  }
}

function changeError(){
  document.querySelector('#Error-Message').setAttribute('class','enable')
  setTimeout(() => {
    document.querySelector('#Error-Message').setAttribute('class', 'goRight')
  }, 5000)
  setTimeout(() => {
    document.querySelector('#Error-Message').removeAttribute('class')
  }, 6000)
}

try {
  let cookie = document.cookie.split('=')[1]
  let message = cookie.split('"')[1]

  document.querySelector('.insertError').innerText = message
  changeError()
} catch (error) {}

document.querySelectorAll("img")[1].src = "/static/Images/signup-tran.gif?uploaded="+date.getTime();