from django.urls import path,include
from . import views
urlpatterns = [
    path('login/',views.login.as_view(),name='adminlogin'),
    path('details/',views.AdminDetails.as_view(),name='admindetails'),
    path('eventmanagement/',views.EventDetails.as_view(),name='eventdetails'),
    path('addmanager/',views.AddManager.as_view(),name='addmanager'),
    path('managermanagement',views.ManagerManagement.as_view(), name='usermanagement'),
    path('usermanagement',views.UserManagement.as_view(), name='usermanagement'),
    path('userdetails/',views.Users.as_view(),name='updateprofile'),
    path('managersdetails/', views.ManagersView.as_view(), name='managersdetails'),

    






]