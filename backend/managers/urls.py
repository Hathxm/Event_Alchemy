from django.urls import path
from . import views

urlpatterns = [
    path('login',views.login.as_view()),
    path('details/',views.ManagerDetails.as_view(),name='managerdetails'),
    path('venues/',views.ManageVenues.as_view(),name='managevenues'),
    path('add-venue/', views.AddVenue.as_view(), name='add-venue'),
    path('edit-venue/', views.EditVenue.as_view(), name='edit-venue'),
    path('locations/',views.Locations.as_view(),name='locations'),
    path('updateprofile',views.UpdateProfile.as_view(),name='updateprofile'),
    path('event_services',views.EventServices.as_view(),name='Event_services'),
    path('add_service',views.AddService.as_view(),name='add_services'),
    path('chats/prev_msgs',views.Prev_msgs.as_view(), name='previousmessages'),
    path('vendor_details',views.Vendors.as_view(), name='vendors'),




     


    




   

]
