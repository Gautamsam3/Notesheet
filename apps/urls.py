# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.urls import path, re_path
from apps import views
from django.urls import path
from .views import login_view, register_user,create_notesheet
from django.contrib.auth.views import LogoutView

urlpatterns = [

    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('', views.index, name='home'),
    path('create/', create_notesheet, name='create_notesheet'),
    path('review/<int:notesheet_id>/', views.review_notesheet, name='review_notesheet'),
    path('pending/', views.pending_page, name='pending_page'),
    path('progress/', views.progress_page, name='progress_page'),
    path('no_notesheet/', views.no_notesheet, name='no_notesheet'),
    re_path(r'^.*\.*', views.pages, name='pages'),
    
]
