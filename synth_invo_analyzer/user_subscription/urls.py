from django.urls import path
from . import views

urlpatterns = [
    path('create-subscription/', views.createSubscription, name='create-subscription'),
    path('subscription-data/', views.stripe_webhook, name='stripe-webhook'),
    
]