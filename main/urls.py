from django.urls import path
from . import views

urlpatterns=[
    path('',views.index, name="index"),
    path('post/ajax/process', views.process_backend, name = "process_backend"),
    path('demo',views.demo, name="demo"),
]