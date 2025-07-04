from django.urls import path
from . import views


urlpatterns = [
    path('', views.myHome, name="myHome"),
    path('about/', views.about, name="about"),
    path('createSlider/', views.createSlider, name="createSlider"),
    path('property_list/', views.property_list_view, name="property_list"),
    path('Dashboard/', views.Dashboard, name="Dashboard"),
    path('Dashboard/FormProperty', views.FormProperty, name="FormProperty"),
    path('Dashboard/propertyType', views.FormPropertyType, name='FormPropertyType'),
    path('Dashboard/propertyLocation', views.FormPropertyLocation, name='FormPropertyLocation'),
    path('Dashboard/add_agent', views.add_agent, name='add_agent'),
    path('Dashboard/client_testimony', views.clientTestimony, name='clientTestimony')

    # path("api/slider/upload/", views.create_slider_api, name="slider_upload"),
]
