from django.urls import path
from . import views

urlpatterns = [
    path('create_subscription/', views.createSubscriptionModel, name='create_subscription'),
    path('modify_product/', views.modifyProduct, name='modify_product'),
    path('archive_product/', views.archiveProduct, name='archive_product'),
    path('get_subscription_models/', views.getSubscriptionModels, name='get_subscription_models'),
    path('create-feature/', views.create_feature, name='create-feature'),
    path('modify-feature/<int:pk>/', views.modify_feature, name='modify-feature'),
    path('remove-feature/<int:pk>/', views.remove_feature, name='remove-feature'),
    path('get-features/<int:model_id>/',views.get_features ,name = 'get_features'),
]
