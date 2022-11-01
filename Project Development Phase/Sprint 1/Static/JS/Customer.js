window.history.pushState({page: 1}, "", "");

window.onpopstate = function(event) {
    if(event){
        window.location.href = 'http://localhost:5000/customer';
        // Code to handle back button or prevent from navigation
    }
}
document.querySelector("button[role='signup']").addEventListener('click', function(){
    location.href = "../signup"
})