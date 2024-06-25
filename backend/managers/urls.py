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
     


    




   

]
