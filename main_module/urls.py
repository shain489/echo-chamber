
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.search_view, name='search'),
    path('search/', views.search_results, name='search_results'),
    path('fetch_analysis/', views.fetch_analysis, name='fetch_analysis'),
    path('fetch_articles/', views.fetch_articles, name='fetch_articles'),

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
