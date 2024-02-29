from django.utils.text import smart_split
import re
import shlex


KEY_REGEX = re.compile(r'^\w+$')


def split_contents(value):
    split = []
    bits = smart_split(value)

    for bit in bits:
        if bit.startswith(('_("', "_('")):
            sentinel = bit[2] + ')'
            trans_bit = [bit]

            while not bit.endswith(sentinel):
                bit = next(bits)
                trans_bit.append(bit)
            bit = ' '.join(trans_bit)

        split.append(bit)

    return split


def handle_args(value):
    args = []
    kwargs = {}

    for bit in split_contents(value):
        q = bit.find("'")
        if q > -1:
            e = bit.find('=')
            if e < q and e > -1:
                value = shlex.split(bit[e + 1:])[0]
                key = bit[:e]
                kwargs[key] = value
            else:
                value = shlex.split(bit[q:])[0]
                args.append(value)

            continue

        q = bit.find('"')
        if q > -1:
            e = bit.find('=')
            if e < q and e > -1:
                value = shlex.split(bit[e + 1:])[0]
                key = bit[:e]
                kwargs[key] = value
            else:
                value = shlex.split(bit[q:])[0]
                args.append(value)

            continue

        e = bit.find('=')
        if e > -1:
            value = shlex.split(bit[e + 1:])[0]
            key = bit[:e]
            match = KEY_REGEX.match(key)

            if match is not None:
                kwargs[key] = value
                continue

        args.append(bit)

    return tuple(args), kwargs
