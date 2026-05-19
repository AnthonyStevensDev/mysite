from django.urls import path
from . import views

urlpatterns = [
    path('', views.summariser, name='summariser'),
    path('documentation/', views.documentation, name='documentation'),
]