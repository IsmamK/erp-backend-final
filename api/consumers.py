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

        # Handle location updates
        if 'location' in data:
            location = data['location']  # e.g., {'latitude': 12.34, 'longitude': 56.78}
            
            # Broadcast the location update to the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'location_update',
                    'location': location
                }
            )

        # Handle other messages
        elif 'message' in data:
            message = data['message']
            await self.send(text_data=json.dumps({
                'message': message
            }))

    # Receive location updates from the group
    async def location_update(self, event):
        location = event['location']

        # Send the location update to the WebSocket
        await self.send(text_data=json.dumps({
            'location': location
        }))

    # Receive other notifications from the group
    async def pickup_notification(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
