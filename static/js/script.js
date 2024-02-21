btn = document.querySelector('#btn')

function reloadPage() {
    location.reload();
}

//setTimeout(reloadPage, 30000)
btn.addEventListener('click', reloadPage)