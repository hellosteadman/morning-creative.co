from .forms import MiniCreateSubscriberForm


def newsletter(request):
    return {
        'mini_subscribe_form': MiniCreateSubscriberForm()
    }