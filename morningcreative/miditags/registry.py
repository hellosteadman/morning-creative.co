from .helpers import handle_args
import re


class Library(object):
    def __init__(self):
        self.__registry = {}

    def register(self, tag, handler):
        if tag in self.__registry:
            raise Exception('Already registered', tag)

        self.__registry[tag] = handler

    def __parse_line(self, line, format, context):
        def replacer(match, Handler):
            groups = match.groups()
            handler = Handler(format, context)

            if len(groups) == 1 and groups[0]:
                args, kwargs = handle_args(groups[0].strip())
            else:
                args, kwargs = (), {}

            return handler.handle(*args, **kwargs)

        for tag, Handler in self.__registry.items():
            if not Handler.self_closing:
                continue

            regex = r'^\[' + tag + r'([^\]]*)\]$'
            line = re.sub(regex, lambda m: replacer(m, Handler), line)

        return line

    def parse(self, text, format='full', base_context={}):
        split = text.splitlines()
        lines = []
        number = 0
        context = {
            **base_context
        }

        while number < len(split):
            line = split[number]
            number += 1

            match = re.search(r'^ *\[([a-z0-9]+)(?: (.+))?\]\s*\S?$', line)
            if match is None:
                lines.append(
                    self.__parse_line(line, format, context)
                )

                continue

            groups = match.groups()
            tag = groups[0]

            if len(groups) == 2 and groups[1]:
                args, kwargs = handle_args(groups[1])
            else:
                args, kwargs = (), {}

            try:
                Handler = self.__registry[tag]
            except KeyError:
                lines.append(line)
                continue

            handler = Handler(format, context)
            if handler.self_closing:
                lines.append(
                    handler.handle(
                        *args,
                        **kwargs
                    )
                )

                continue

            middle_lines = []
            next_number = number
            middle_parsed = False

            while next_number < len(split):
                next_line = split[next_number]
                next_number += 1

                closing_match = re.search(r'^ *\[/' + tag + '] *$', next_line)
                if closing_match is None:
                    middle_lines.append(
                        self.__parse_line(next_line, format, context)
                    )

                    continue

                lines.append(
                    handler.handle(
                        self.parse(
                            '\n'.join(middle_lines),
                            format,
                            context
                        ),
                        *args,
                        **kwargs
                    )
                )

                number = next_number + 1
                middle_parsed = True
                break

            if not middle_parsed:
                raise Exception('Tag not closed', tag)

        return '\n'.join(lines)
