from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.myHome, name="myHome"),
    path('about/', views.about, name="about"),
    path('createSlider/', views.createSlider, name="createSlider"),
    # path('property_list/', views.property_list_view, name="property_list"),
    path('Dashboard/', views.Dashboard, name="Dashboard"),
    path('Dashboard/FormProperty', views.FormProperty, name="FormProperty"),
    path('Dashboard/propertyType', views.FormPropertyType, name='FormPropertyType'),
    path('Dashboard/propertyLocation', views.FormPropertyLocation, name='FormPropertyLocation'),
    path('Dashboard/add_agent', views.add_agent, name='add_agent'),
    path('Dashboard/client_testimony', views.clientTestimony, name='clientTestimony'),
    path('viewProperty/<int:id>', views.viewProperty, name="viewProperty"),
    path('login/', views.LoginUser, name="LoginUser"),
    path('add_to_cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<str:id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    # path('payment/success/', views.payment_success, name='payment_success'),
   # 1. Probably meant for backend/API verification (e.g., called after payment)
    path('Dashboard/payementVerification', views.verify_payment, name='verify_payment'),
    path('register/', views.register_client, name='register_client'),
    # 2. Used to display the result of the verification (success/failure)
    path('Dashboard/verify/<str:reference>/', views.paymentVerification, name='paymentVerification'),
    path('Dashboard/my-orders/', views.my_orders, name='my_orders'),
    path('Dashboard/add_plan/<int:property_id>/', views.add_subscription_plan, name='add_subscription_plan'),
    path('Dashboard/property_list/', views.propertyList, name='propertyList'),
    path('logout/', views.custom_logout_view, name='LogoutUser'),
    path('Dashboard/payment-history/', views.payment_history, name='payment_history'),
    path('Dashboard/wallet/', views.initiate_wallet_payment, name='initiate_wallet_payment'),
    path('Dashboard/walletsuccess/', views.verify_wallet_payment, name='verify_wallet_payment'),



    # path("api/slider/upload/", views.create_slider_api, name="slider_upload"),
]
