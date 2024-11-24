# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    
    # Product URLs
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-detail'),
    path('products/bulk_upload/', bulk_upload_products, name='bulk_upload_products'),
    path('products/download_template/', download_template, name='download_template'),

    # Warehouse URLs
    path('warehouses/', WarehouseListCreateView.as_view(), name='warehouse-list-create'),
    path('warehouses/<int:pk>/', WarehouseRetrieveUpdateDestroyView.as_view(), name='warehouse-detail'),

    # Store URLs
    path('stores/', StoreListCreateView.as_view(), name='store-list-create'),
    path('stores/<int:pk>/', StoreRetrieveUpdateDestroyView.as_view(), name='store-detail'),
    path('download-qr-code/<int:store_id>/', download_qr_code, name='download_qr_code'),

    # Driver URLs
    path('drivers/', DriverListCreateView.as_view(), name='driver-list-create'),
    path('drivers/<int:pk>/', DriverRetrieveUpdateDestroyView.as_view(), name='driver-detail'),

    # Pickup URLs
    path('pickups/', PickupListCreateView.as_view(), name='pickup-list-create'),
    path('pickups/<int:pk>/', PickupRetrieveUpdateDestroyView.as_view(), name='pickup-detail'),

    # Return URLs
    path('returns/', ReturnListCreateView.as_view(), name='return-list-create'),
    path('returns/<int:pk>/', ReturnRetrieveUpdateDestroyView.as_view(), name='return-detail'),


    # Return URLs
    path('dropoffs/', DropoffListCreateView.as_view(), name='dropoff-list-create'),
    path('dropoffs/<int:pk>/', DropoffRetrieveUpdateDestroyView.as_view(), name='dropoff-detail'),

    #Specific task urls
    path('create-pickup/', create_pickup, name='create_pickup'),
    path('create-dropoff/', create_dropoff, name='create_dropoff'),
    path('take-inventory/', take_inventory, name='take_inventory'),
    path('initiate-return/', initiate_return, name='initiate_return'),
    path('receive-return/', receive_return, name='receive_return'),
    path("get-cashflow-data/",get_cashflow_data,name="get_cashflow_data"),
    #product activity log
    path('product-activity-logs/', ProductActivityLogListCreateAPIView.as_view(), name='activity-log-list-create'),
    path('product-activity-logs/<int:pk>/', ProductActivityLogRetrieveUpdateDestroyAPIView.as_view(), name='activity-log-detail'),

    # Push Notifications and location receive
    path('driver/update-location/', update_driver_location, name='update-driver-location'),
    path('driver/set-fcm-token/', SetFCMTokenView.as_view(), name='set-fcm-token'),

]
