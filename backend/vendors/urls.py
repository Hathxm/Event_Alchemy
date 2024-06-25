from django.urls import path
from .import views

urlpatterns = [
    path('signup',views.Signup.as_view(),name="signup" ),
    path('otp',views.OTP.as_view(),name="otp" ),
    path('login',views.login.as_view(),name="login" ),
    path('vendor_services',views.Vendor_services.as_view(),name="vendorservices" ),
    path('details',views.Vendor_Details.as_view(),name="vendor_details" ),
    path('services',views.Services.as_view(),name="services" ),
    path('addservice',views.AddService.as_view(),name="addservices" ),








]