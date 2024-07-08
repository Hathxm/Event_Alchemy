from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
import json
from .models import ChatMessage, ChatRoom, Managers,Notification
from managers.models import AllUsers


class ChatConsumer(AsyncJsonWebsocketConsumer):
    active_users = set()

    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.manager_id = self.scope['url_route']['kwargs']['manager_id']

        print(f"WebSocket connection for user: {self.user_id}, manager: {self.manager_id}")

        self.user = await self.get_user_instance(self.user_id)
        self.manager = await self.get_manager_instance(self.manager_id)

        if self.user and self.manager:
            self.group_name = f'chat_{min(self.user_id, self.manager_id)}_{max(self.user_id, self.manager_id)}'
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            ChatConsumer.active_users.add(self.user_id)
            await self.accept()

            existing_messages = await self.get_existing_messages()
            for message in existing_messages:
                await self.send(text_data=json.dumps({
                    'message': message['message'],
                    'sendername': message['sendername'],
                    'is_read': message['is_read']
                }))
        else:
            await self.close()

    @database_sync_to_async
    def get_existing_messages(self):
        chatroom, created = ChatRoom.objects.get_or_create(user=self.user, manager=self.manager)
        messages = ChatMessage.objects.filter(room=chatroom).order_by('timestamp')
        return [{'message': message.message, 'sendername': message.sender.username, 'is_read': message.is_read} for message in messages]

    @database_sync_to_async
    def get_user_instance(self, user_id):
        try:
            return AllUsers.objects.get(id=user_id)
        except AllUsers.DoesNotExist:
            return None

    @database_sync_to_async
    def get_manager_instance(self, manager_id):
        try:
            return Managers.objects.get(id=manager_id)
        except Managers.DoesNotExist:
            return None

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        ChatConsumer.active_users.discard(self.user_id)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sendername = data.get('sendername')

        print(f"Received message from {sendername}: {message}")

        await self.save_message(sendername, message, is_read=False)
        
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'data': {
                    'message': message,
                    'sendername': sendername,
                    'is_read': False,
                }
            }
        )

    async def chat_message(self, event):
        print("Handling chat message event...")
        print(event)
        
        message = event['data']['message']
        sendername = event['data']['sendername']
        is_read = event['data']['is_read']

        print(f"Sending message: {message} from {sendername}")

        await self.send(text_data=json.dumps({
            'message': message,
            'sendername': sendername,
            'is_read': is_read
        }))

    @database_sync_to_async
    def save_message(self, sendername, message, is_read):
        chatroom, created = ChatRoom.objects.get_or_create(user=self.user, manager=self.manager)
        ChatMessage.objects.create(
            room=chatroom,
            sender=AllUsers.objects.get(username=sendername),
            message=message,
            is_read=is_read,
        )

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.manager_id = self.scope['url_route']['kwargs']['manager_id']
        self.manager_group_name = f'manager_{self.manager_id}'

        # Join manager group
        await self.channel_layer.group_add(
            self.manager_group_name,
            self.channel_name
        )

        await self.accept()
        notifications = await self.get_notifications()
        for notification in notifications:
            await self.send(text_data=json.dumps({
                'message': notification.message,
                # 'created_at': notification.created_at,
                'is_read': notification.is_read
            }))

    @database_sync_to_async
    def get_notifications(self):
        return list(Notification.objects.filter(user_id=self.manager_id).order_by('-created_at'))


    async def disconnect(self, close_code):
        # Leave manager group
        await self.channel_layer.group_discard(
            self.manager_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        # Send message to manager group
        await self.channel_layer.group_send(
            self.manager_group_name,
            {
                'type': 'send_notification',
                'message': message
            }
        )

    # Receive message from manager group
    async def send_notification(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

