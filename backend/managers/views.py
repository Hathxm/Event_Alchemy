from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework import status
from .serializers import LocationSerializer,ManagerSerializer
from user.models import Customusers
from rest_framework.permissions import IsAuthenticated
from .models import venues, Managers
from superadmin.models import location,Events
from user.serializers import VenueSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from user.serializers import CustomuserSerializer 
from django.http import Http404
# Create your views here.

class login(APIView):
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
        except KeyError:
            return Response({"error": "Not sufficient data"})

        if not Managers.objects.filter(username=username).exists():
            return Response({"error": "Email doesn't exist"})

        user = authenticate(username=username,password=password)
        
        print(user)

     
        if user is None:
            return Response({"error": "Invalid Password"})
        
        serializer=ManagerSerializer(user)

        refresh = RefreshToken.for_user(user)
        refresh['email'] = str(user.email)
        

        content = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'manager_details':serializer.data
        }

        return Response(content, status=status.HTTP_200_OK)
    
class ManagerDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_authenticated:
            try:
                manager = Managers.objects.get(username=user)
            except Managers.DoesNotExist:
                return Response({'error': 'Manager details not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = ManagerSerializer(manager)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        


class ManageVenues(APIView):
    def post(self,request):
        event_type=request.data.get('manager_type')
        event = Events.objects.get(name=event_type)
        venue = venues.objects.filter(event_type=event)
        serialized = VenueSerializer(venue,many=True)
        return Response(serialized.data)
    
class AddVenue(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        manager_type = request.data.get('manager_type')
        location_name = request.data.get('location')
        print("Received location:", location_name)
        
        if not manager_type:
            return Response({"error": "Manager type is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Attempt to fetch event type
            event_type = Events.objects.get(name=manager_type)
        except Events.DoesNotExist:
            return Response({"error": "Event type for the given manager type does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Attempt to fetch location
            venue_location = location.objects.get(name=location_name)
            print(venue_location.id)
            request.data['location'] = venue_location.id
        except location.DoesNotExist:
            return Response({"error": "Location not found"}, status=status.HTTP_400_BAD_REQUEST)

        request.data['event_type'] = event_type.id

        serializer = VenueSerializer(data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


    
class Locations(APIView):
    def get(self,request):
        locations = location.objects.all()
        serializer = LocationSerializer(locations,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    



class EditVenue(APIView):
    def patch(self, request):
        venue_id = request.data.get('venue_id')
        location_name = request.data.get('location')

        if not venue_id:
            return Response({'error': 'Venue ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            venue = venues.objects.get(id=venue_id)
        except venues.DoesNotExist:
            raise Http404
        
        # Update venue attributes based on request data, excluding image1 and location
        for key, value in request.data.items():
            if key not in ['image1', 'location']:
                setattr(venue, key, value[0] if isinstance(value, list) else value)
        
        # Update location if it's provided
        if location_name:
            try:
                location_instance = location.objects.get(name=location_name)
                venue.location = location_instance
            except location.DoesNotExist:
                return Response({'error': f'Location "{location_name}" does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Conditionally update image
        if 'image1' in request.FILES:
            venue.image1 = request.FILES['image1']
        
        # Save the venue
        venue.save()
        
        return Response({'message': 'Venue updated successfully'}, status=status.HTTP_200_OK)
    
class UpdateProfile(APIView):
    def patch(self, request):
        user = request.user
        print(user)
        if user.is_authenticated:
            Manager_details = Managers.objects.get(username=user)
            serializer = ManagerSerializer(Manager_details,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                print("User details updated successfully:", serializer.data)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                print("Validation errors:", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            print("User is not authenticated")
            return Response({'error': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
