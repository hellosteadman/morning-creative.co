from uuid import uuid4
import os
import random


def upload_image(self, filename):
    return 'uploads/%s%s' % (
        str(uuid4()),
        os.path.splitext(filename)[-1]
    )


def random_code():
    return '{:04d}'.format(random.randint(100, 9999))
