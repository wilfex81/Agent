from django.urls import path
from django.shortcuts import render
from .views import chat_view

urlpatterns = [
    path("chat/", chat_view, name="chat"),
]
