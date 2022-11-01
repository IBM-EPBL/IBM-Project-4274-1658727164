setTimeout(function(){
    if(document.cookie.startsWith("_ID:") === true) return
    document.querySelector(".cookies").style.display = "flex"
},5000)
// $('button').on('click',function(){
//     document.cookie =  '_ID:' + Math.random().toString(36).substr(2, 9) + ";SESSIONID=123";
//     document.querySelector(".cookies").style.display = "none"
// })
document.querySelector('span.cancelCookie').addEventListener('click',()=>{
    document.querySelector(".cookies").style.display = "none"
})
document.querySelector("button[role='login']").addEventListener('click', function(event){
    location.href = "../login"
})
document.querySelector("button[role='signup']").addEventListener('click', function(){
    location.href = "../signup"
})