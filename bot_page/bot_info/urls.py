from django.urls import path

from . import views

app_name = "bot_info"

urlpatterns = [
    path('', views.index, name='index'),
]
