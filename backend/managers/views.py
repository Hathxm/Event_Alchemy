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
from superadmin.models import location,Events,services
from user.serializers import VenueSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from user.serializers import CustomuserSerializer,ChatMessageSerializer,ChatRoomSerializer
from django.http import Http404
from superadmin.serializers import ServiceSerializer
from chat.models import ChatRoom,ChatMessage
from vendors.serializers import VendorserviceSerializer
from vendors.models import vendorservices


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
        refresh['username'] = str(user.username)
        

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
        
class EventServices(APIView):
    def post(self, request):
        event_type = request.data.get('manager_type')
       
        
        try:
            event = Events.objects.get(name=event_type)
            services = event.services.all()  # Ensure `services` is a related name or a foreign key relationship
            
            serialized = ServiceSerializer(services, many=True)
            print(serialized.data)
            return Response(serialized.data, status=200)
        except Events.DoesNotExist:
            return Response({"error": "Event not found"}, status=404)
        except Exception as e:
            print(e)
            return Response({"error": "Something went wrong"}, status=500)
        
class AddService(APIView):
   parser_classes = (MultiPartParser, FormParser)
   def post(self, request):
        print(request.data)
        event_type = request.data.get('manager_type')
        service_name = request.data.get('name')
        

        print(event_type)
        
        try:
            event = Events.objects.get(name=event_type)
            new_service = services.objects.create(service_name=service_name)
            event.services.add(new_service)
              # Ensure `services` is a related name or a foreign key relationship
            service = event.services.all()
            serialized = ServiceSerializer(service, many=True)
            print(serialized.data)
            return Response(serialized.data, status=200)
        except Events.DoesNotExist:
            return Response({"error": "Event not found"}, status=404)
        except Exception as e:
            print(e)
            return Response({"error": "Something went wrong"}, status=500)
        

        
class Prev_msgs(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        chat_rooms = ChatRoom.objects.filter(manager=user)
        print(chat_rooms)
        serializer = ChatRoomSerializer(chat_rooms, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        room_id = request.data.get('room_id')
        chat_room = ChatRoom.objects.get(id=room_id, manager=user)
        messages = ChatMessage.objects.filter(room=chat_room)
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)
    

class Vendors(APIView):
    def post(self, request):
     
        manager_name = request.data.get('manager_name')
        print(manager_name)
        
        
        try:
            # Get the event based on manager_type
            manager = Managers.objects.get(username=manager_name)
            event = Events.objects.get(name=manager.manager_type)
            
            # Get all services associated with the event
            services = event.services.all()
            
            # Filter VendorServices where service is in the event's services
            vendor_services = vendorservices.objects.filter(service_type__in=services)
            
            # Serialize the filtered vendor services
            serializer = VendorserviceSerializer(vendor_services, many=True)
            
            return Response({'data':serializer.data,'manager_id':manager.id}, status=status.HTTP_200_OK)
        
        except Events.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)