# your_app/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class DriverConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the driver ID from the URL
        self.driver_id = self.scope['url_route']['kwargs']['driver_id']
        self.room_group_name = f"driver_{self.driver_id}"

        # Join the driver group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the driver group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive messages from the WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    # Receive message from the group
    async def pickup_notification(self, event):
        # Send the message to WebSocket
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
