from django.contrib import admin
from django.urls import path
from rsexamples import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.IndexView.as_view(), name='index'),
    path('map/<str:name_of_the_boat>/', views.map_show, name='map'),
]
