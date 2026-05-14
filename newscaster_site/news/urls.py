from django.urls import path
from . import views

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('vote/<int:article_id>/<str:vote_type>/', views.vote, name='vote'),
    path('search/', views.search_results, name='search_results'),
    path('articles/<int:article_id>/', views.article_detail, name='article_detail'),
]
