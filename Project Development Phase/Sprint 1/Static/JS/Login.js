history.pushState('login','login','/login')

try {
    let cookie = document.cookie.split('=')[1]
    let message = cookie.split('"')[1]

    document.querySelector('.insertError').innerText = message
    document.querySelector('#Error-Message').setAttribute('class','enable')

    setTimeout(() => {
        document.querySelector('#Error-Message').setAttribute('class', 'goRight')
    }, 5000)
    setTimeout(() => {
        document.querySelector('#Error-Message').removeAttribute('class')
    }, 6000)
} catch (error) {}