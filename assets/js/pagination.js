import adjust from './ratio'

(
    () => {
        document.querySelectorAll('.pagination-context').forEach(
            (container) => {
                const btn = container.querySelector('.btn-pagination')
                const grid = container.querySelector('.grid')
                let href = btn ? btn.getAttribute('href') : null
                let oldBtn = btn

                const finish = (newBtn) => {
                    if (newBtn) {
                        newBtn.addEventListener('click', 
                            (e) => {
                                if (newBtn.disabled) {
                                    return
                                }

                                e.preventDefault()
                                go()
                            }
                        )
                    }

                    oldBtn.parentNode.removeChild(oldBtn)

                    if (newBtn) {
                        grid.after(newBtn)
                        oldBtn = newBtn
                        href = newBtn.getAttribute('href')
                    }
                }

                const go = () => {
                    btn.classList.add('disabled')
                    btn.disabled = true

                    fetch(href).then(
                        (response) => {
                            response.text().then(
                                (html) => {
                                    const fragment = document.createElement('html')

                                    fragment.innerHTML = html

                                    const newContainer = fragment.querySelector('.pagination-context')
                                    const items = newContainer.querySelectorAll('.pagination-item')
                                    const newBtn = newContainer.querySelector('.btn-pagination')
                                    const appended = []

                                    items.forEach(
                                        (item) => {
                                            appended.push(grid.appendChild(item))
                                        }
                                    )

                                    container.dispatchEvent(
                                        new Event('ajax')
                                    )

                                    if (grid.classList.contains('grid-masonry')) {
                                        grid.dispatchEvent(
                                            new CustomEvent(
                                                'masonry.append',
                                                {
                                                    detail: {
                                                        elements: appended,
                                                        done: () => {
                                                            finish(newBtn)
                                                        }
                                                    }
                                                }
                                            )
                                        )
                                    } else {
                                        finish(newBtn)
                                    }
                                }
                            )
                        }
                    ).catch(
                        (err) => {
                            console.error(err)
                        }
                    )
                }

                if (!btn) {
                    return
                }

                btn.addEventListener('click', 
                    (e) => {
                        if (btn.disabled) {
                            return
                        }

                        e.preventDefault()
                        go()
                    }
                )
            }
        )
    }
)()
