from django.urls import path
from . import views
urlpatterns = [
    path('', views.news_list, name = 'news_list'),
    path('<int:pk>/details', views.news_detail, name= 'news_detail'),
    path('news/search/', views.news_search, name='news_search'),
    path('create_news/', views.news_create, name='create_news'),
    path('<int:news_id>/validate/', views.validate_and_impact_news, name='validate_and_impact_news'),
    path('<int:news_id>/comment/', views.add_comment, name='add_comment'),
    path('<int:news_id>/delete/', views.delete_news, name='delete_news'),
]
