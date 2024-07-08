from django.shortcuts import render,redirect
from .serializers import VenueSerializer,BookingSerializer
from managers.models import venues
from vendors.models import vendorservices
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from .models import Customusers,Booking
from django.utils import timezone
from datetime import datetime
from django.contrib.sessions.models import Session
from django.conf import settings
from django.db import IntegrityError,DatabaseError
from rest_framework.exceptions import AuthenticationFailed,ParseError
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomuserSerializer,ChatMessageSerializer,ChatRoomSerializer
from vendors.serializers import VendorserviceSerializer
from superadmin.models import Events
from managers.models import Managers,AllUsers
from vendors.models import vendorservices
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
import random
from chat.models import ChatRoom,ChatMessage,Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync




class landingpage(APIView):
    def get(self,request):
        data = Events.objects.all()
        serializer = VenueSerializer(data, many=True)
        return JsonResponse(serializer.data, safe=False)


class Signup(APIView):
    def post(self, request):
        try:
            # Get user data from request
            email = request.data.get('email')
            username = request.data.get('username')

            if not email or not username:
                return Response({'error': 'Email and Username are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if username already exists
            if AllUsers.objects.filter(username=username).exists():
                return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
            elif Customusers.objects.filter(email=email).exists():
                return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Generate OTP
            otp = get_random_string(length=6, allowed_chars='1234567890')

            # Send OTP to user's email
            send_otp_email(email, otp)
            
            return Response({'message': 'OTP sent to your email', 'otp': otp}, status=status.HTTP_200_OK)
        
        except Customusers.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        except ValueError as e:
            # Handle specific exceptions as needed
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # General exception handling
            return Response({'error': f'Something went wrong: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def send_otp_email(email, otp):
    # Construct email subject and message
    subject = 'Your OTP for account verification'
    message = f'Your OTP is: {otp}'
    
    # Send email
    send_mail(subject, message, "eventalchemy@gmail.com", [email], fail_silently=False)


class OTP(APIView):
    def post(self, request):
        try:
            # Get the data from the request
            username = request.data.get('username')
            password = request.data.get('password')
            email = request.data.get('email')
            name = request.data.get('name')

            # Print the name for debugging purposes
            print(name)

            # Hash the password before saving
            hashed_password = make_password(password)

            # Create the user
            Customusers.objects.create(
                username=username, 
                password=hashed_password, 
                email=email,
                first_name=name
            )

            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            # Handle database integrity errors, e.g., unique constraint violations
            print(f"IntegrityError: {e}")
            if 'username' in str(e):
                error_message = "Username already exists"
            elif 'email' in str(e):
                error_message = "Email already exists"
            else:
                error_message = "Data integrity error"
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

        except DatabaseError as e:
            # Handle general database errors
            print(f"DatabaseError: {e}")
            return Response({"error": "Database error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            # Handle unexpected errors
            print(f"Unexpected error: {e}")
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
            
class resend_otp(APIView):
    def post(self,request):
            email=request.data.get('email')
            otp=resend_otp_mail(email)
            return Response({'message':'new otp send','otp':otp},status=status.HTTP_200_OK)
    


def resend_otp_mail(mail):
        otp = get_random_string(length=6, allowed_chars='1234567890')
        email=mail

        subject = 'Your OTP for account verification'
        message = f'Your OTP is: {otp}'

        send_mail(subject, message, "eventalchemy@gmail.com", [email], fail_silently=False)
        return otp


class Login(APIView):
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
          
        except KeyError:
            return Response({"error": "Not sufficient data"})
        
        if not Customusers.objects.filter(username=username).exists():
            return Response({"error": "Username doesnt exists"})

        user = authenticate(request, username=username, password=password)
        print(user)
        
        if user is None:
           return Response({"error": "Invalid Password"})
        
        
        
        
        
        refresh = RefreshToken.for_user(user)
        refresh['username'] = str(user.username)

        content = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'isAuthenticated':user.is_active,
            'isAdmin': False,
            'isSuperAdmin': user.is_superuser,
            'username': user.username,
        }

        return Response(content, status=status.HTTP_200_OK)
    
class token_refresh(APIView):
      
      
      def post(self, request):
        user = request.user
        refresh_token = request.data.get('refresh')
   
        
        if not refresh_token:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
       
        try:
            
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            new_refresh_token = str(refresh)
            

            # Return the new access token
            return Response({'access': access_token,'refresh':new_refresh_token}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class UserDetailsView(APIView):
    def get(self, request):
        user = request.user  # Assuming user authentication is implemented
        if user.is_authenticated:
            user_details = Customusers.objects.get(username=user)
            serialized_data = CustomuserSerializer(user_details)
            return Response(serialized_data.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
         

class UpdateProfile(APIView):
    def patch(self, request):
        user = request.user
       
        if user.is_authenticated:
            user_details = Customusers.objects.get(username=user)
            serializer = CustomuserSerializer(user_details,data=request.data,partial=True)
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
        
    
class Venues(APIView):
    def get(self,request):
        id = request.query_params.get('id')
       
        event=Events.objects.get(id=id)
    
        venuess = venues.objects.filter(event_type=event)
      
        serializer=VenueSerializer(venuess,many=True)

        return Response({'data':serializer.data,'event_name':event.name})
        
class Venuedetail(APIView):
    def get(self,request):
        id = request.query_params.get('id')
        venue = venues.objects.get(id=id)
        serializer = VenueSerializer(venue) 
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class Venueservices(APIView):
    def get(self, request):
        venue_id = request.query_params.get('id')
        
        if not venue_id:
            return Response({'error': 'Venue ID is required'}, status=400)
        
        try:
            venue = venues.objects.get(id=venue_id)
        except venues.DoesNotExist:
            return Response({'error': 'Venue not found'}, status=404)
        
        # Get the related event and its services
        event = venue.event_type
        services = event.services.all()
        
        # Find all vendor services that match these services
        vendor_services = vendorservices.objects.filter(service_type__in=services,location=venue.location)
        
        # Serialize the vendor services
        vendor_services_serializer = VendorserviceSerializer(vendor_services, many=True)
        
        return Response(vendor_services_serializer.data)
    
class Selected_services(APIView):
    def get(self, request):
        venue_id = request.query_params.get('id')
        services_ids = request.query_params.get('ids', '').strip()  # Using default value of empty string and stripping whitespace

        if not venue_id:
            return Response({'error': 'Venue ID is missing.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            venue = venues.objects.get(id=venue_id)
        except venues.DoesNotExist:
            return Response({'error': 'Venue not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Initialize an empty list for services
        services_data = []

        if services_ids:  # Check if services_ids is not empty
            try:
                services_ids_list = services_ids.split(',')
                services = vendorservices.objects.filter(id__in=services_ids_list)
                services_serializer = VendorserviceSerializer(services, many=True)
                services_data = services_serializer.data
            except Exception as e:
                # Log the error for debugging
                print(f"Error fetching services: {e}")
                return Response({'error': 'Invalid service IDs provided.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            print("No services provided or services_ids is empty.")
        
        # Serialize venue data
        venue_serializer = VenueSerializer(venue)

        # Combine venue data with services data
        response_data = {
            'venue': venue_serializer.data,
            'services': services_data  # Use empty list if no services provided
        }

        return Response(response_data, status=status.HTTP_200_OK)
    

class UserDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_authenticated:
            try:
                User = Customusers.objects.get(username=user)
            except Customusers.DoesNotExist:
                return Response({'error': 'User details not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = CustomuserSerializer(User)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        
        
@api_view(['POST'])
def check_availability(request):
    venue_id = request.data.get('venue_id')
    date_str = request.data.get('date')
    start_time_str = request.data.get('start_time')
    end_time_str = request.data.get('end_time')

    if not all([venue_id, date_str, start_time_str, end_time_str]):
        return Response({'error': 'All fields are required'}, status=400)

    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    start_time = datetime.strptime(start_time_str, '%H:%M').time()
    end_time = datetime.strptime(end_time_str, '%H:%M').time()
  

    bookings = Booking.objects.filter(venue_id=venue_id, date=date)
 

    not_available_slots = []

    # Check if there are any overlapping bookings
    for booking in bookings:
        if not (end_time <= booking.start_time or start_time >= booking.end_time):
            # Collect all the times to find available slots
            not_available_slots.append({
                'start': booking.start_time,
                'end': booking.end_time,
            })

    if  not_available_slots:
        not_available_slots = sorted( not_available_slots, key=lambda x: x['start'])
        not_available_slots_formatted = [f"{slot['start']} - {slot['end']}" for slot in  not_available_slots]
        return Response({
            'available': False,
            'not_available_slots': not_available_slots_formatted
        }, status=200)

    # No overlaps found, the slot is available
    return Response({'available': True}, status=200)


class Confirm_Booking(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request.data)
        try:
            # Retrieve user from request context
            user = request.user
            
            # Extracting data from request
            venue_id = request.data.get('venueId')
            services_ids = request.data.get('services')
            booking_details = request.data.get('bookingDetails')

            # Validate and retrieve user and venue
            user = Customusers.objects.get(username=user.username)
            venue = venues.objects.get(id=venue_id)

            # Retrieve managers based on the event type of the venue
            managers = Managers.objects.filter(manager_type=venue.event_type)
            print(venue.event_type)
            print(managers)

            # Select a random manager from the list of available managers
            if not managers.exists():
                return Response({"error": "No managers available for this event type."}, status=404)
            manager = random.choice(managers)
            print(f"Selected Manager: {manager}")

            # Create the booking instance
            booking = Booking.objects.create(
                customer=user,
                venue=venue,
                date=booking_details.get('date'),
                start_time=booking_details.get('startTime'),
                end_time=booking_details.get('endTime'),
                Total=25000,  # Replace this with actual total calculation if needed
                manager=manager,
                event_type = venue.event_type,
            )

            # Add selected services to the booking
            for service_id in list(set(services_ids)):
                try:
                    service = vendorservices.objects.get(id=service_id)
                    booking.services.add(service)
                except vendorservices.DoesNotExist:
                    return Response({"error": f"Service with id {service_id} not found"},
                                    status=404)

            notification_message = f"A new booking has been made for the venue {venue.venue_name}."
            notification = Notification.objects.create(
                user=manager,
                message=notification_message,
                booking=booking
            )

            # Send notification via WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'manager_{manager.id}',
                {
                    'type': 'send_notification',
                    'message': notification_message
                }
            )

            return Response({"success": "Booking created successfully"}, status=201)
        except Exception as e:
            print(str(e))
            return Response({"error": str(e)}, status=400)
        

class Fetch_bookings(APIView):
    def post(self,request):
        user = request.user
        bookings = Booking.objects.filter(customer=user)
        serializer = BookingSerializer(bookings,many=True)
        return Response(serializer.data,status=200)
        
class Prev_msgs(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        chat_rooms = ChatRoom.objects.filter(user=user)
        print(chat_rooms)
        serializer = ChatRoomSerializer(chat_rooms, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        room_id = request.data.get('room_id')
        chat_room = ChatRoom.objects.get(id=room_id, user=user)
        messages = ChatMessage.objects.filter(room=chat_room)
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)
        









