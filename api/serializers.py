# serializers.py
from rest_framework import serializers
from .models import *
from djoser.serializers import UserSerializer as DjoserUserSerializer
from djoser.serializers import TokenSerializer

class CustomTokenSerializer(TokenSerializer):
    user = serializers.SerializerMethodField()

    class Meta(TokenSerializer.Meta):
        fields = ['auth_token', 'user']

    def get_user(self, obj):
        user = obj.user
        user_data = {
            "u_id": user.id,
            "username": user.username,
            "email": user.email,
        }

        # Check if the user has a Profile or Driver model and include relevant data
        if hasattr(user, 'profile'):
            user_data.update({
                "profile_id":user.profile.id,
                "role": user.profile.role,
                "contact_number": user.profile.contact_number,
                "address": user.profile.address,
                "profile_picture": user.profile.profile_picture.url if user.profile.profile_picture else None,
            })
        elif hasattr(user, 'drivers'):
            driver = user.drivers
            user_data.update({
                "driver_id":driver.id,
                "role": "driver",
                "first_name": driver.first_name,
                "last_name": driver.last_name,
                "contact_number": driver.contact_number,
                "iqama_number": driver.iqama_number,
                "nationality": driver.nationality,
                "iqama_expiry_date": driver.iqama_expiry_date,
                "profile_picture": driver.profile_picture.url if driver.profile_picture else None,
                "driving_license_expiry_date": driver.driving_license_expiry_date,
                "current_location": {
                    "latitude": driver.current_latitude,
                    "longitude": driver.current_longitude
                }
            })

        return user_data


class ProductActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductActivityLog
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    activity_logs = serializers.StringRelatedField(many=True,read_only=True)
    class Meta:
        model = Product
        fields = '__all__'

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = '__all__'

class PickupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pickup
        fields = '__all__'

class DropOffSerializer(serializers.ModelSerializer):
    class Meta:
        model = DropOff
        fields = '__all__'

class ReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Return
        fields = '__all__'
