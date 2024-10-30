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
]