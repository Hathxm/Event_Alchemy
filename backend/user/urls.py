from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('', views.landingpage.as_view(),name="landing-pg"),
    path('signup', views.Signup.as_view(),name="signup"),
    path('otp', views.OTP.as_view(),name="otp"),
    path('resendotp', views.resend_otp.as_view(),name="resendotp"),
    path('userlogin',views.Login.as_view(),name='login'),
    path('token/refresh',views.token_refresh.as_view(),name='token_refresh'),
    path('user/details/',views.UserDetailsView.as_view(), name='user-details'),
    path('updateprofile',views.UpdateProfile.as_view(), name='updatedetails'),
    path('venues',views.Venues.as_view(), name='venues'),
    path('venue_details',views.Venuedetail.as_view(), name='venuedetails'),
    path('venue_services',views.Venueservices.as_view(), name='venueservices'),
    path('selected_services',views.Selected_services.as_view(), name='selected_services'),
    path('userdetails/',views.UserDetails.as_view(), name='user-details'),




    


   

    



    

]
urlpatterns=urlpatterns+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)