from django.urls import path
from .views import (
    CreateSubscriberView,
    ConfirmSubscriptionView,
    SubscriptionPendingView,
    SubscriptionCreatedView,
    DeliveryOpenTrackingView,
    UnsubscribeView,
    UnsubscriberCreatedView
)


urlpatterns = (
    path(
        'subscribe/',
        CreateSubscriberView.as_view(),
        name='create_subscriber'
    ),
    path(
        'c/<path:token>/',
        ConfirmSubscriptionView.as_view(),
        name='confirm_subscription'
    ),
    path(
        't/<pk>.png',
        DeliveryOpenTrackingView.as_view(),
        name='track_delivery_open'
    ),
    path(
        'subscribing/',
        SubscriptionPendingView.as_view(),
        name='subscriber_pending'
    ),
    path(
        'subscribed/',
        SubscriptionCreatedView.as_view(),
        name='subscriber_created'
    ),
    path(
        'unsubscribe/',
        UnsubscribeView.as_view(),
        name='unsubscribe'
    ),
    path(
        'unsubscribed/',
        UnsubscriberCreatedView.as_view(),
        name='unsubscriber_created'
    )
)
