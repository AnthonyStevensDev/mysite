from django.urls import path
from . import views

urlpatterns = [
    path('', views.docs_index, name='docs_index'),
    path('authentication/', views.docs_authentication, name='docs_authentication'),
    path('summariser/', views.docs_summariser, name='docs_summariser'),
]