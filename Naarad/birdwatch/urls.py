from django.urls import path
from . import views

urlpatterns = [
    path('train-model/', views.train_model, name='train_model'),
]
