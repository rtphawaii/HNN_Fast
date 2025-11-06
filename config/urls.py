from django.contrib import admin
from django.urls import path
from OutreachAuto.views import search_view, download_csv_view  # adjust app name if different

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", search_view, name="search"),
    path("download.csv", download_csv_view, name="download_csv"),
]