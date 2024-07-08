from django.shortcuts import render
from rest_framework.views import APIView
from .models import Vendors,vendorservices
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError,DatabaseError
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .serializers import VendorserviceSerializer,VendorSerializer
from managers.models import AllUsers 
from superadmin.serializers import LocationSerializer,ServiceSerializer
from superadmin.models import location,services
from chat.models import ChatMessage,ChatRoom
from user.serializers import ChatMessageSerializer,ChatRoomSerializer
from .tasks import notify_vendors



# Create your views here.

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
            elif Vendors.objects.filter(email=email).exists():
                return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Generate OTP
            otp = get_random_string(length=6, allowed_chars='1234567890')

            # Send OTP to user's email
            send_otp_email(email, otp)
            
            return Response({'message': 'OTP sent to your email', 'otp': otp}, status=status.HTTP_200_OK)
        
        except Vendors.DoesNotExist:
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
            phone_number = request.data.get('phone_number')


            # Print the name for debugging purposes
            print(name)

            # Hash the password before saving
            hashed_password = make_password(password)

            # Create the user
            Vendors.objects.create(
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


class login(APIView):
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            
        except KeyError:
            return Response({"error": "Not sufficient data"})

        if not Vendors.objects.filter(username=username).exists():
            return Response({"error": "username doesn't exist"})

        user = authenticate(username=username,password=password)
        
       

     
        if user is None:
            return Response({"error": "Invalid Password"})
        
        serializer=VendorSerializer(user)
        refresh = RefreshToken.for_user(user)
        refresh['username'] = str(user.username)

        

        content = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'vendor_details':serializer.data,
        }

        return Response(content, status=status.HTTP_200_OK)
    
class Vendor_services(APIView):
    def get(self,request):
        user=request.user
        user=Vendors.objects.get(username=user)
        data = vendorservices.objects.filter(vendor=user)
        serializer = VendorserviceSerializer(data,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class Vendor_Details(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_authenticated:
            try:
                User = Vendors.objects.get(username=user)
            except Vendors.DoesNotExist:
                return Response({'error': 'User details not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = VendorSerializer(User)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        
class Services(APIView):
    def get(self, request):
        locations = location.objects.all()
        service = services.objects.all()
        
        locations_serializer = LocationSerializer(locations, many=True)
        services_serializer = ServiceSerializer(service, many=True)
        
        return Response({
            'locations': locations_serializer.data,
            'services': services_serializer.data
        }, status=status.HTTP_200_OK) 
    

class AddService(APIView):
    def post(self, request):
        try:
            user = request.user
            print(user)

            if not user.is_authenticated:
                return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
            
            try:
                vendor = Vendors.objects.get(username=user.username)
            except Vendors.DoesNotExist:
                return Response({'error': 'Vendor not found'}, status=status.HTTP_404_NOT_FOUND)
            
            location_id = request.data.get('location')
            price = request.data.get('price')
            description = request.data.get('description')
            service_type_id = request.data.get('serviceType')

            if not all([location_id, price, description, service_type_id]):
                return Response({'error': 'Missing one or more required fields'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                service_type = services.objects.get(id=service_type_id)
            except services.DoesNotExist:
                return Response({'error': 'Service type not found'}, status=status.HTTP_404_NOT_FOUND)
            
            try:
                service_location = location.objects.get(id=location_id)
            except location.DoesNotExist:
                return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)

            vendorservice = vendorservices.objects.create(
                vendor=vendor,
                service_type=service_type,
                location=service_location,
                description=description,
                price=price,
                is_active=True
            )

            updated_data = vendorservices.objects.filter(vendor=vendor)
            serializer = VendorserviceSerializer(updated_data, many=True)  # Serializing a queryset, so use `many=True`

            return Response({'success': 'Service added successfully', 'updated_data': serializer.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class Prev_msgs(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        print(user)
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


def test(request):
    notify_vendors.delay()
    return Response("heyyy",status=200)