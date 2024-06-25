from django.shortcuts import render
from rest_framework.views import APIView
from managers.models import AllUsers,Managers
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .models import Events
from .serializers import EventSerializer,AdminSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from user.models import Customusers
from user.serializers import CustomuserSerializer
from managers.serializers import ManagerSerializer
from django.contrib.auth import authenticate
from django.utils.crypto import get_random_string
from rest_framework.permissions import IsAuthenticated




# Create your views here.

class login(APIView):
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            
        except KeyError:
            return Response({"error": "Not sufficient data"})

        if not AllUsers.objects.filter(username=username).exists():
            return Response({"error": "Email doesn't exist"})

        user = authenticate(username=username,password=password)
        
       

     
        if user is None:
            return Response({"error": "Invalid Password"})

        refresh = RefreshToken.for_user(user)
        refresh['email'] = str(user.email)
        

        content = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'isAuthenticated': user.is_active,
            'isAdmin':False,
            'isSuperUser':user.is_superuser,
            'username': user.username,
        }

        return Response(content, status=status.HTTP_200_OK)
    
class EventDetails(APIView):
    def get(self,request):
        events = Events.objects.all()
        serializer = EventSerializer(events,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        # Manually create an Event instance
        event_name = request.data.get('eventname')
        description = request.data.get('description')
        image = request.FILES.get('image')

        if event_name and description:
            event = Events.objects.create(
                name=event_name,
                description=description,
                image=image
            )
            event.save()

            # Serialize the created event
            serializer = EventSerializer(event)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
    
class AddManager(APIView):
    def post(self, request):
        username = request.data.get('username')
        name = request.data.get('name')
        email = request.data.get('email')
        password = get_random_string(length=6, allowed_chars='1234567890')
        event_type_name = request.data.get('eventType')
        hashed_password = make_password(password)

        try:
            manager_type = Events.objects.get(name=event_type_name)
        except ObjectDoesNotExist:
            return Response(
                {'error': 'Event type does not exist.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Managers.objects.create(
            username=username,
            first_name=name,
            email=email,
            password=hashed_password,
            manager_type=manager_type,
            is_Manager=True
        )
        send_manager_details(email,username,password)
        return Response(status=status.HTTP_200_OK)

def send_manager_details(email,username,password):
    # Construct email subject and message
    subject = 'You Manager Account Details At EventAlchemy.com'
    message = f' Use Your Username And Password to Log In \nUsername:{username}\npassword:{password}'
    
    # Send email
    send_mail(subject, message, "eventalchemy@gmail.com", [email], fail_silently=False)

class ManagerManagement(APIView):
    def patch(self,request):
        id=request.data.get('userId')
        print(id)
        user=Managers.objects.get(id=id)
        if user.is_active==True:
             user.is_active=False
        else:
             user.is_active=True
        user.save()
        return Response({'success':'user updated successfully'},status=status.HTTP_200_OK)
    
class ManagersView(APIView):
    def get(self,request):
        managers = Managers.objects.filter(is_Manager=True)
        serializer = ManagerSerializer(managers,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
        
class Users(APIView):
    def get(self,request):
        users = Customusers.objects.all()
        serializer = CustomuserSerializer(users,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UserManagement(APIView):
    def patch(self,request):
        id=request.data.get('userId')
        print(id)
        user=Customusers.objects.get(id=id)
        if user.is_active==True:
             user.is_active=False
        else:
             user.is_active=True
        user.save()
        return Response({'success':'user updated successfully'},status=status.HTTP_200_OK)
    

class AdminDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_authenticated:
            try:
                Admin = AllUsers.objects.get(username=user)
            except AllUsers.DoesNotExist:
                return Response({'error': 'Manager details not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = AdminSerializer(Admin)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        
class AddManager(APIView):
    def post(self, request):
        username = request.data.get('username')
        name = request.data.get('name')
        email = request.data.get('email')
        password = get_random_string(length=6, allowed_chars='1234567890')
        event_type_name = request.data.get('eventType')
        hashed_password = make_password(password)

        try:
            manager_type = Events.objects.get(name=event_type_name)
        except ObjectDoesNotExist:
            return Response(
                {'error': 'Event type does not exist.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Managers.objects.create(
            username=username,
            first_name=name,
            email=email,
            password=hashed_password,
            manager_type=manager_type,
            is_Manager=True
        )
        send_manager_details(email,username,password)
        return Response(status=status.HTTP_200_OK)

def send_manager_details(email,username,password):
    # Construct email subject and message
    subject = 'You Manager Account Details At EventAlchemy.com'
    message = f' Use Your Username And Password to Log In \nUsername:{username}\npassword:{password}'
    
    # Send email
    send_mail(subject, message, "eventalchemy@gmail.com", [email], fail_silently=False)



