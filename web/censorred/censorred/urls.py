from django.contrib import admin
from django.urls import path
from validator_bars import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("valbars/", views.index, name='bars')
]
