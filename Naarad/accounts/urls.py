from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('register/', views.register, name='register'),  # Ensure this is correct
    path('login/', views.login, name = 'login' ),
    path('logout/', LogoutView.as_view(), name = 'logout'),
    path('profile/', views.profile, name= 'profile'),
    path('profile/<int:pk>/', views.profile, name='profile_with_pk'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
]
