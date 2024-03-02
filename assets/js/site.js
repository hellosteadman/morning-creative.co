import '../scss/site.scss'
import adjust from './ratio'
import {} from './menu'
import imagesLoaded from 'imagesloaded'
import Masonry from 'masonry-layout'

document.querySelectorAll('.ratio-unknown').forEach(adjust)
document.querySelectorAll('.grid-masonry').forEach(
    (grid) => {
        const imgs = imagesLoaded(grid)
        let masonry

        imgs.on(
            'done',
            () => {
                masonry = new Masonry(
                    grid,
                    {
                        percentPosition: true
                    }
                )
            }
        )

        grid.addEventListener('masonry.append',
            (e) => {
                const ajaxImgs = imagesLoaded(e.detail.elements)

                ajaxImgs.on(
                    'done',
                    () => {
                        masonry.appended(e.detail.elements, true)
                        e.detail.done()
                    }
                )
            }
        )
    }
)

document.addEventListener(
    'ajax',
    (e) => {
        e.target.querySelectorAll('.ratio-unknown').forEach(adjust)
    },
    true
)

import {} from './pagination'
import {} from './confirmation-code'
import {} from 'bootstrap'
