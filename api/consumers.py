# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import firebase_admin
from firebase_admin import messaging
from asgiref.sync import sync_to_async

class DriverConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.driver_id = self.scope['url_route']['kwargs']['driver_id']
        self.room_group_name = f"driver_{self.driver_id}"

        # Join the driver-specific group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Join the live locations group
        await self.channel_layer.group_add("live_locations", self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the driver-specific group and live locations group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_discard("live_locations", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        # print("Dataaaa",data)
        # Handle location updates
        if 'location' in data:
            
            location = data['location']
            # print("received", location)
            await self.save_driver_location(self.driver_id, location)
            await self.channel_layer.group_send("live_locations", {
                'type': 'location_update',
                'driver_id': self.driver_id,
                'location': location
            })

        # Handle pickup notifications
        elif 'pickup' in data:
            pickup_details = data['pickup']
            fcm_token = data.get('fcm_token')
            # print("this is the fcm token")
            # print(fcm_token)

            if fcm_token:
                await self.send_fcm_notification(fcm_token, pickup_details)

    async def location_update(self, event):
        # Send location updates to the driver and others
        location = event['location']
        driver_id = event['driver_id']
        # print(location)
        await self.send(text_data=json.dumps({
            'type': 'location_update',
            'driver_id': driver_id,
            'location': location
        }))

    async def pickup_notification(self, event):
        # Send pickup notification to the driver
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'pickup_notification',
            'message': message
        }))

    async def send_fcm_notification(self, fcm_token, pickup_details):
        # Send a background notification using Firebase
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title="New Pickup Assigned",
                    body=pickup_details.get('details', "You have a new pickup.")
                ),
                token=fcm_token,
            )
            response = messaging.send(message)
            print(f"FCM Notification Sent: {response}")
        except Exception as e:
            print(f"Error sending FCM notification: {str(e)}")

    @sync_to_async
    def save_driver_location(self, driver_id, location):
        # Save the driver's location to the database
        pass
