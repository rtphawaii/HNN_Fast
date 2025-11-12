from django.contrib import admin
from django.urls import path
from HNN_Fast.views import search_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", search_view, name="search"),
]