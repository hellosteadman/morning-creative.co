document.querySelectorAll('[data-toggle="menu"]').forEach(
    (btn) => {
        btn.addEventListener('click',
            (e) => {
                const menu = btn.closest('header').querySelector('.nav')

                e.preventDefault()
                menu.classList.toggle('show-none')
            }
        )
    }
)