from markdown import markdown


class HandlerBase(object):
    self_closing = True

    def __init__(self, format='full', context={}):
        self.format = format
        self.context = context

    def handle(self, value):
        raise NotImplementedError('Method not implemented')

    def markdown(self, value):
        return markdown(value)

    def parse_contents(self, value, to_markdown=False):
        from . import tags

        parsed = tags.parse(value, self.format)
        if to_markdown:
            parsed = self.markdown(parsed)

        return parsed
