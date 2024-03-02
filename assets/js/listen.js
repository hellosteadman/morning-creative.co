(
    () => {
        const getListenDOM = async () => {
            const response = await fetch('/listen/')
            const html = await response.text()
            const dom = document.createElement('html')

            dom.innerHTML = html
            return dom.querySelector('body')
        }

        let listenContainer

        if (document.body.clientWidth < 992) {
            return
        }

        document.addEventListener('click',
            async (e) => {
                const a = e.target.tagName === 'A' ? e.target : e.target.closest('a[href]')

                if (!a) {
                    return
                }

                if (a.getAttribute('href') === '/listen/') {
                    e.preventDefault()

                    if (!listenContainer) {
                        const listenDOM = await getListenDOM()
                        const closeBtn = document.createElement('button')
                        let addedCloseBtn = false

                        closeBtn.classList.add('btn')
                        closeBtn.classList.add('btn-lg')
                        closeBtn.style.position = 'absolute'
                        closeBtn.style.top = '-2rem'
                        closeBtn.style.right = 0
                        closeBtn.type = 'button'
                        closeBtn.innerHTML = '<i class="bi bi-x-circle-fill"></i>'

                        listenContainer = document.createElement('div')
                        listenDOM.childNodes.forEach(
                            (child) => {
                                if (child.tagName) {
                                    listenContainer.appendChild(child)
                                }
                            }
                        )

                        listenContainer.querySelectorAll('.container').forEach(
                            (subcontainer) => {
                                if (!addedCloseBtn) {
                                    subcontainer.style.position = 'relative'
                                    subcontainer.appendChild(closeBtn)
                                    addedCloseBtn = true
                                }
                            }
                        )

                        listenContainer.classList.add('background-body')
                        listenContainer.style.position = 'fixed'
                        listenContainer.style.bottom = '100%'
                        listenContainer.style.right = 0
                        listenContainer.style.left = 0
                        listenContainer.style.transition = '.3s bottom ease'

                        document.body.firstChild.before(listenContainer)
                        closeBtn.addEventListener('click',
                            (v) => {
                                listenContainer.style.bottom = '100%'
                                v.preventDefault()
                            }
                        )
                    }

                    window.requestAnimationFrame(
                        () => {
                            listenContainer.style.bottom = 0
                        }
                    )
                }
            }
        )
    }
)()
