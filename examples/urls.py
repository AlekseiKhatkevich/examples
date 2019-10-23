from django.contrib import admin
from django.urls import path
from rsexamples import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.IndexView.as_view(), name='index'),

    path('boats/detail/<int:pk>/', views.boat_detail_view, name='boat_detail'),
    path('boats/version2/', views.BoatListView_2.as_view(), name='boats_version_2'),
    path('boats/', views.BoatListView.as_view(), name='boats'),

    path('map/<str:name_of_the_boat>/', views.map_show, name='map'),
]
