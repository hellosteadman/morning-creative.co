from uuid import uuid4
import json
import os
import random


ADJECTIVES = json.load(
    open(
        os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'adjectives.json'
        ),
        'rb'
    )
)

COLOURS = json.load(
    open(
        os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'colours.json'
        ),
        'rb'
    )
)

ANIMALS = json.load(
    open(
        os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'animals.json'
        ),
        'rb'
    )
)


def upload_image(self, filename):
    return 'uploads/%s%s' % (
        str(uuid4()),
        os.path.splitext(filename)[-1]
    )


def random_phrase():
    def random_word(pile):
        return random.choice(pile)

    groups = [ADJECTIVES, COLOURS, ANIMALS]
    words = []
    random.seed()

    while any(groups):
        words.append(
            random_word(groups.pop(0))
        )

    return ' '.join(words)
