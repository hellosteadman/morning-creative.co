$('form.sponsorship-form').each(
    function (e) {
        var self = $(this)
        var textarea = self.find(':input[name="message"]')
        var message = $('<p>').html(textarea.val() || textarea.attr('placeholder')).text()
        var linkEx = new RegExp(/\[([^\[]+)\]/)
        var sample = self.find('.message-sample')
        var html = message.replace(
            linkEx,
            '<a href="javascript:;">$1</a>'
        )

        sample.html(html)
    }
)

$('body').on('input', '.sponsorship-form :input[name="message"]',
    function (e) {
        var self = $(this)
        var message = $('<p>').html(self.val() || self.attr('placeholder')).text()
        var form = self.closest('form')
        var linkEx = new RegExp(/\[([^\[]+)\]/)
        var sample = form.find('.message-sample')

        if (message.length >= 149) {
            message = message.substr(0, 150)
            self.val(message)
        }

        var html = message.replace(
            linkEx,
            '<a href="javascript:;">$1</a>'
        )

        sample.html(html)
    }
)
