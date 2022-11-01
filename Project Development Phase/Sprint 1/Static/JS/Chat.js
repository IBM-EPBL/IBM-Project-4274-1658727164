$(document).ready(function(){
    var server_user;
    const urlP = new URLSearchParams(window.location.search)
    const session = urlP.get("session")
    var socket = io.connect("http://localhost:5000")
    var private = io.connect("http://localhost:5000/private")
    let user = localStorage.getItem("username")
    var getUser = setInterval(function(){
        console.log("Still gettin")
        if(server_user != undefined){
            console.log("cleared",server_user)
            clearInterval(getUser)
            return
        }
        private.emit('username', {'session_id': session, 'email': user})
    },5000)
    socket.on('connect', function(){
        socket.send("User connected!")
    })
    document.querySelector("#sendBtn").addEventListener('click',function(){
        let message = document.querySelector("#message").value
        private.emit('private_message', {'session_id':session,'email':server_user, message})
    })
    private.on('recieve_private_message', function(data){
        let div = document.createElement("div")
        div.innerText = data
        document.querySelector("#messages").appendChild(div)
    })
    private.on('server_client', function(user){
        server_user = user
        console.log(server_user)
    })
})
document.cookie = 'Message="password Incorect";expires=Wed, 31 Oct 2012 08:50:17 GMT'