from django.contrib import admin
from django.urls import path, include
from sfbot.views import MyPasswordChangeView


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include(("sfbot.urls", "sfbot"))),
    path('', include('allauth.urls')),
    path("password/change/", MyPasswordChangeView.as_view(),
         name="account_change_password"),
]
