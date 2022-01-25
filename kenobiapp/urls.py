from django.urls import path

from kenobiapp.views import home

urlpatterns = [
    path('', home, name='home')
]
