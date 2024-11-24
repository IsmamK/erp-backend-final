from rest_framework import generics
from rest_framework.permissions import AllowAny  # Import AllowAny
from .serializers import *
from .models import *
from django.http import HttpResponse
import pandas as pd
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework import filters
from django.http import JsonResponse
from rest_framework.decorators import api_view
import requests
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.views.decorators.csrf import csrf_exempt
import firebase_admin
from firebase_admin import messaging
import json

apiUrl =  "http://localhost:8000/api"



class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]  # Allow access to all users
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = "__all__"
    search_fields = ['box_code'] 

class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]  # Allow access to all users


class ProductActivityLogListCreateAPIView(generics.ListCreateAPIView):
    """
    API endpoint to view and create product activity logs.
    """
    queryset = ProductActivityLog.objects.all()
    serializer_class = ProductActivityLogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = "__all__"
    search_fields = "__all__"

class ProductActivityLogRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, or delete a specific product activity log.
    """
    queryset = ProductActivityLog.objects.all()
    serializer_class = ProductActivityLogSerializer


class WarehouseListCreateView(generics.ListCreateAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [AllowAny]  # Allow access to all users
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = "__all__"

class WarehouseRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [AllowAny]  # Allow access to all users

class StoreListCreateView(generics.ListCreateAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [AllowAny]  # Allow access to all users
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['id', 'created_at', 'name', 'vat_no', 'cr_no', 'location', 'latitude', 'longitude', 'point_of_contact', 'whatsapp_number', 'email']  # Excludes qr_code_image

class StoreRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [AllowAny]  # Allow access to all users
    filterset_fields = '__all__'  # Allow filtering on all fields

class DriverListCreateView(generics.ListCreateAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [AllowAny]  # Allow access to all users
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ["user","driving_license_expiry_date","iqama_expiry_date","nationality","iqama_number","contact_number","last_name","first_name","created_at","id"]
    
 

class DriverRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [AllowAny]  # Allow access to all users


class PickupListCreateView(generics.ListCreateAPIView):
    queryset = Pickup.objects.all()
    serializer_class = PickupSerializer
    permission_classes = [AllowAny]  # Allow access to all users
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = "__all__"

class PickupRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pickup.objects.all()
    serializer_class = PickupSerializer
    permission_classes = [AllowAny]  # Allow access to all users

class DropoffListCreateView(generics.ListCreateAPIView):
    queryset = DropOff.objects.all()
    serializer_class = DropOffSerializer
    permission_classes = [AllowAny]  # Allow access to all users
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = "__all__"

class DropoffRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DropOff.objects.all()
    serializer_class = DropOffSerializer
    permission_classes = [AllowAny]  # Allow access to all users


class ReturnListCreateView(generics.ListCreateAPIView):
    queryset = Return.objects.all()
    serializer_class = ReturnSerializer
    permission_classes = [AllowAny]  # Allow access to all users
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = "__all__"

class ReturnRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Return.objects.all()
    serializer_class = ReturnSerializer
    permission_classes = [AllowAny]  # Allow access to all users


# ------------------------------------------ SPECIFIC TASK URLS ------------------------------------------ 

# ------------------------------------------ STORE QR DOWNLOAD ------------------------------------------ 

def download_qr_code(request, store_id):
    try:
        store = Store.objects.get(id=store_id)
        response = HttpResponse(store.qr_code_image, content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{store.name}_qr_code.png"'
        return response
    except Store.DoesNotExist:
        return HttpResponse(status=404)
    

# ------------------------------------------ PRODUCT BUL UPLOAD & TEMPLATE ------------------------------------------ 


@api_view(['POST'])
@permission_classes([AllowAny])
def bulk_upload_products(request):
    if 'file' not in request.FILES:
        return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

    file = request.FILES['file']
    created_by = request.POST.get('created_by')
    try:
        df = pd.read_excel(file)
        required_columns = {'name', 'box_code', 'item_code', 'buying_price', 'selling_price', 'warehouse_id'}
        if not required_columns.issubset(df.columns):
            return Response(
                {"error": "Invalid file format. Ensure it has columns: name, box_code, item_code, buying_price, selling_price, warehouse_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        products = []
        for _, row in df.iterrows():
            product_data = {
                "created_by":created_by,
                'name': row['name'],
                'box_code': row['box_code'],
                'item_code': row['item_code'],
                'buying_price': row['buying_price'],
                'selling_price': row['selling_price'],
                'warehouse': row['warehouse_id']
            }
            serializer = ProductSerializer(data=product_data)
            if serializer.is_valid():
                serializer.save()
                products.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"success": "Products uploaded successfully!", "products": products}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": f"Error processing file: {e}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def download_template(request):
    df = pd.DataFrame(columns=['name', 'box_code', 'item_code', 'buying_price', 'selling_price', 'warehouse_id'])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="product_upload_template.xlsx"'
    permission_classes = [AllowAny]
    df.to_excel(response, index=False, engine='openpyxl')
    return response

# ------------------------------------------ ASSIGN PICKUP  ------------------------------------------ 

@api_view(['POST'])
@permission_classes([AllowAny])
def create_pickup(request):
    driver_id = request.data.get('driver_id')
    items = request.data.get('items')  # This should be a list of strings
    item_type = request.data.get('item_type')  # 'product' or 'box'
    warehouse_id = request.data.get('warehouse_id')
    created_by = Profile.objects.get(pk=request.data.get('created_by'))

    if not driver_id:
        return JsonResponse({'error': 'Driver ID is required.'}, status=400)

    if not items:
        return JsonResponse({'error': 'Items are required.'}, status=400)

    if not item_type:
        return JsonResponse({'error': 'Item type is required.'}, status=400)

    if not warehouse_id:
        return JsonResponse({'error': 'Warehouse ID is required.'}, status=400)

    items_list = items  # Use the provided items list directly
    pickup = Pickup.objects.create(driver_id=driver_id, warehouse_id=warehouse_id,created_by=created_by)  # Create a new pickup instance

    successfully_added = []
    errors = []

    if item_type == 'product':
        for code in items_list:
            try:
                product = Product.objects.get(item_code=code.strip())
                if product.status == "in_warehouse":
                    # Update product details
                    product.warehouse_id = None  # Remove warehouse ID
                    product.driver_id = driver_id  # Assign the driver ID
                    product.status = "in_transit"  # Change status to in_transit
                    product.save()  # Save the updated product instance
                    pickup.products.add(product)  # Add the product to the pickup
                    successfully_added.append(product.item_code)
                else:
                    errors.append({
                        'item_code': code.strip(),
                        'error': 'Product is not in warehouse'
                    })
            except Product.DoesNotExist:
                errors.append({
                    'item_code': code.strip(),
                    'error': 'Product does not exist'
                })

    elif item_type == 'box':
        for box_code in items_list:
            box_code = box_code.strip()
            # Fetch products associated with the box code from the products API
            response = requests.get(f'{apiUrl}/products?box_code={box_code}')

            if response.status_code == 200:
                products = response.json()

                for product in products:
                    try:
                        product_instance = Product.objects.get(id=product['id'])
                        if product_instance.status == "in_warehouse":
                            # Update product details
                            product_instance.warehouse_id = None  # Remove warehouse ID
                            product_instance.driver_id = driver_id  # Assign the driver ID
                            product_instance.status = "in_transit"  # Change status to in_transit
                            product_instance.save()  # Save the updated product instance
                            pickup.products.add(product_instance)  # Add the product to the pickup
                            successfully_added.append(product_instance.item_code)
                        else:
                            errors.append({
                                'item_code': product['item_code'],
                                'error': 'Product is not in warehouse'
                            })
                    except Product.DoesNotExist:
                        errors.append({
                            'item_code': product['item_code'],
                            'error': 'Product does not exist'
                        })
            else:
                errors.append({
                    'box_code': box_code,
                    'error': f'Failed to fetch products for box code {box_code}.'
                })

    else:
        return JsonResponse({'error': 'Invalid item type. Must be "product" or "box".'}, status=400)

    pickup.save()  # Save the pickup instance

    driver = Driver.objects.get(pk=driver_id)
    send_fcm_notification(driver)
    
    if len(successfully_added) != 0:
        # WebSocket notification - send to the driver after all operations are done
        channel_layer = get_channel_layer()
        message = f"New pickup created with ID: {pickup.id}. Products added: {len(successfully_added)}"

        # Send the message to the driver’s WebSocket group
        async_to_sync(channel_layer.group_send)(
            f"driver_{driver_id}",  # The group name for the driver
            {
                'type': 'pickup_notification',  # This matches the method in the consumer
                'message': message,
            }
        )

    return JsonResponse({
        'pickup_id': pickup.id,
        'driver_id': pickup.driver_id,
        'successfully_added': successfully_added,
        'errors': errors,
        'total_products_added': len(successfully_added),
        'total_errors': len(errors),
    }, status=201)

# ------------------------------------------ FCM ENDPOINTS  ------------------------------------------ 
def send_fcm_notification(driver):
    # Assuming that the driver has an FCM token stored in the 'fcm_token' field
    fcm_token = driver.fcm_token

    # Create the message to send
    message = messaging.Message(
        notification=messaging.Notification(
            title="New Pickup Assigned",
            body=f"You have been assigned a new pickup with {driver.first_name} {driver.last_name}.",
        ),
        token=fcm_token,
    )

    # Send the notification
    try:
        response = messaging.send(message)
        print('Successfully sent message:', response)
    except Exception as e:
        print(f"Error sending message: {e}")

# Example endpoint to update driver's location
@api_view(['POST'])
@permission_classes([AllowAny])
def update_driver_location(request):
    driver = Driver.objects.get(request.data.get("driver_id"))
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')

    # Update the driver's location
    driver.current_latitude = latitude
    driver.current_longitude = longitude
    driver.save()

    return JsonResponse({'message': 'Location updated successfully'}, status=200)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class SetFCMTokenView(APIView):
    def post(self, request):
        driver = Driver.objects.ge(request.data.get("driver_id"))
        fcm_token = request.data.get('fcm_token')

        if not fcm_token:
            return Response({"error": "FCM token is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Save the token to the user's profile or database
        driver.fcm_token = fcm_token
        driver.save()

        return Response({"message": "FCM token saved successfully"}, status=status.HTTP_200_OK)



# ------------------------------------------ CREATE DROPOFF (FOR APP)  ------------------------------------------ 

@api_view(['POST'])
@permission_classes([AllowAny])
def create_dropoff(request):
    driver_id = request.data.get('driver_id')
    items = request.data.get('items')  # This should be a list of strings
    item_type = request.data.get('item_type')  # 'product' or 'box'
    store_id = request.data.get('store_id')
    method_of_collection = request.data.get('method_of_collection') or "Cash"

    if not driver_id:
     return JsonResponse({'error': 'Driver ID is required.'}, status=400)

    if not items:
        return JsonResponse({'error': 'Items are required.'}, status=400)

    if not item_type:
        return JsonResponse({'error': 'Item type is required.'}, status=400)

    if not store_id:
        return JsonResponse({'error': 'Store ID is required.'}, status=400)

    items_list = items  # Use the provided items list directly
    dropoff = DropOff.objects.create(driver_id=driver_id, store_id=store_id,method_of_collection=method_of_collection)  # Create a new pickup instance

    successfully_added = []
    errors = []
    total_amount = 0
    if item_type == 'product':
        for code in items_list:
            try:
                product = Product.objects.get(item_code=code.strip())
                total_amount += float(product.buying_price)
                if product.status == "in_transit":
                    # Update product details
                    product.driver_id = None  # Remove Store ID
                    product.store_id = store_id  # Assign the driver ID
                    product.status = "in_store"  # Change status to in_transit
                    product.save()  # Save the updated product instance
                    dropoff.products.add(product)  # Add the product to the pickup
                    successfully_added.append(product.item_code)
                else:
                    errors.append({
                        'item_code': code.strip(),
                        'error': 'Product is not in available in pickup list'
                    })
            except Product.DoesNotExist:
                errors.append({
                    'item_code': code.strip(),
                    'error': 'Product does not exist'
                })

    elif item_type == 'box':
        for box_code in items_list:
            box_code = box_code.strip()
            # Fetch products associated with the box code from the products API
            response = requests.get(f'{apiUrl}/products?box_code={box_code}')

            if response.status_code == 200:
                products = response.json()

                for product in products:
                    total_amount += float(product["buying_price"])
                    try:
                        product_instance = Product.objects.get(id=product['id'])
                        if product_instance.status == "in_transit":
                            # Update product details
                            product_instance.driver_id = None  # Remove warehouse ID
                            product_instance.store_id = store_id  # Assign the driver ID
                            product_instance.status = "in_store"  # Change status to in_transit
                            product_instance.save()  # Save the updated product instance
                            dropoff.products.add(product_instance)  # Add the product to the pickup
                            successfully_added.append(product_instance.item_code)
                        else:
                            errors.append({
                                'item_code': product['item_code'],
                                'error': 'Product is not in pickup list'
                            })
                    except Product.DoesNotExist:
                        errors.append({
                            'item_code': product['item_code'],
                            'error': 'Product does not exist'
                        })
            else:
                errors.append({
                    'box_code': box_code,
                    'error': f'Failed to fetch products for box code {box_code}.'
                })

    
    else:
        return JsonResponse({'error': 'Invalid item type. Must be "product" or "box".'}, status=400)

    dropoff.total_value = total_amount
    dropoff.save()  # Save the pickup instance

    return JsonResponse({
        'dropoff_id': dropoff.id,
        'driver_id': dropoff.driver_id,
        'status':dropoff.status,
        'store_id':dropoff.store_id,
        "method_of_collection":dropoff.method_of_collection,
        'total_value':dropoff.total_value,
        'successfully_added': successfully_added,
        'errors': errors,
        'total_products_added': len(successfully_added),
        'total_errors': len(errors),
    }, status=201)

# ------------------------------------------ TAKE INVENTORY (FOR APP)  ------------------------------------------ 

@api_view(['POST'])
@permission_classes([AllowAny])
def take_inventory(request):
    store_id = request.data.get('store_id')
    items = request.data.get('items')  # This should be a list of strings
    item_type = request.data.get('item_type')  # 'product' or 'box'
    driver_id = request.data.get('driver_id')

    if not store_id:
     return JsonResponse({'error': 'Store ID is required.'}, status=400)

    if not items:
        return JsonResponse({'error': 'Items are required.'}, status=400)

    if not item_type:
        return JsonResponse({'error': 'Item type is required.'}, status=400)

    items_list = items  # Use the provided items list directly

    successfully_matched = []
    errors = []
    missing_products = []

    # Fetch all products associated with the store_id
    current_products = Product.objects.filter(store_id=store_id)
    current_product_codes = set(current_products.values_list('item_code', flat=True))

    if item_type == 'product':
        # Convert incoming product codes into a set
        new_product_codes = set(code.strip() for code in items_list)

        # Identify products that are no longer present in the new product list
        missing_product_codes = current_product_codes - new_product_codes

        # Update the status of missing products to 'sold' and remove store_id and box_code
        Product.objects.filter(item_code__in=missing_product_codes, store_id=store_id).update(
            status='sold', store_id=None, box_code=None
        )
        for product in (Product.objects.filter(item_code__in=missing_product_codes)):
            ProductActivityLog.objects.create(
                    product=product,
                    details=f"Product {product.name} marked as sold at {timezone.now().strftime('%Y-%m-%d %H:%M')} by {Driver.objects.get(pk=driver_id)} at store {Store.objects.get(pk=store_id)}"
                )
            
            


        # Check which items are successfully matched
        for code in new_product_codes:
            if code in current_product_codes:
                successfully_matched.append(code)
                product = Product.objects.get(item_code=code)
                ProductActivityLog.objects.create(
                    product=Product.objects.get(item_code = code),
                    details=f"Inventory taken at {timezone.now().strftime('%Y-%m-%d %H:%M')} for Product {product.name} by {Driver.objects.get(pk=driver_id)} at store {Store.objects.get(pk=store_id)}"
                )
            else:
                errors.append({
                    'item_code': code,
                    'error': 'Product does not exist in store inventory'
                })

        # Collect missing products for response
        missing_products = list(missing_product_codes)

    elif item_type == 'box':
        for box_code in items_list:
            box_code = box_code.strip()
            # Fetch products associated with the box code from the products API
            response = requests.get(f'{apiUrl}/products?box_code={box_code}')

            if response.status_code == 200:
                products = response.json()
                box_product_codes = set(product['item_code'] for product in products)

                # Identify products that are no longer present in the box
                missing_box_products = current_product_codes - box_product_codes

                # Update the status of missing products to 'sold' and remove store_id and box_code
                Product.objects.filter(item_code__in=missing_box_products, store_id=store_id).update(
                    status='sold', store_id=None, box_code=None
                ) 
                for product in (Product.objects.filter(item_code__in=missing_box_products, store_id=store_id)):
                        ProductActivityLog.objects.create(
                            f"Product {product.name} marked as sold at {timezone.now().strftime('%Y-%m-%d %H:%M')} "
                            f"by {Driver.objects.get(pk=driver_id)} at store {Store.objects.get(pk=store_id)}"
                    )
                            

                # Check which items are successfully matched
                for product in products:
                    if product['item_code'] in current_product_codes:
                        successfully_matched.append(product['item_code'])

                        try:
                            # Fetch the Product instance
                            product_instance = Product.objects.get(item_code=product['item_code'], store_id=store_id)
                            ProductActivityLog.objects.create(
                                product=product_instance,
                                details=(
                                    f"Inventory taken at {timezone.now().strftime('%Y-%m-%d %H:%M')} "
                                    f"for Product {product['name']} by "
                                    f"{Driver.objects.get(pk=driver_id)} at store {Store.objects.get(pk=store_id)}"
                                )
                            )
                        except Product.DoesNotExist:
                            errors.append({
                                'item_code': product['item_code'],
                                'error': 'Product does not exist in store inventory'
                            })
                    else:
                        errors.append({
                            'item_code': product['item_code'],
                            'error': 'Product does not exist in store inventory'
                        })


                # Collect missing products for response
                missing_products.extend(list(missing_box_products))
            else:
                errors.append({
                    'box_code': box_code,
                    'error': f'Failed to fetch products for box code {box_code}.'
                })
    else:
        return JsonResponse({'error': 'Invalid item type. Must be "product" or "box".'}, status=400)

    return JsonResponse({
        'store_id': store_id,
        'successfully_matched': successfully_matched,
        'errors': errors,
        'missing_products_marked_as_sold': missing_products,
        'total_products_matched': len(successfully_matched),
        'total_missing_products': len(missing_products),
        'total_errors': len(errors),
    }, status=200)



# ------------------------------------------ INITATE RETURN  (FOR APP)  ------------------------------------------ 


@api_view(['POST'])
@permission_classes([AllowAny])
def initiate_return(request):
    driver_id = request.data.get('driver_id')
    items = request.data.get('items')  # This should be a list of strings
    item_type = request.data.get('item_type')  # 'product' or 'box'
    store_id = request.data.get('store_id')

    if not driver_id:
        return JsonResponse({'error': 'Driver ID is required.'}, status=400)

    if not items:
        return JsonResponse({'error': 'Items are required.'}, status=400)

    if not item_type:
        return JsonResponse({'error': 'Item type is required.'}, status=400)

    if not store_id:
        return JsonResponse({'error': 'Store ID is required.'}, status=400)

    items_list = items  # Use the provided items list directly
    successfully_updated = []
    errors = []

    # Create a Return object
    return_instance = Return.objects.create(driver_id=driver_id, store_id=store_id)

    if item_type == 'product':
        for code in items_list:
            try:
                product = Product.objects.get(item_code=code.strip())
                
                if product.status == "in_store" and int(product.store_id) == int(store_id):
                    # Update product details
                    product.store_id = None  # Remove store ID
                    product.driver_id = driver_id  # Assign the driver ID
                    product.status = "in_return_transit"  # Change status to in_return_transit
                    product.save()  # Save the updated product instance
                    successfully_updated.append(product.item_code)

                    # Associate product with the return instance
                    return_instance.products.add(product)
                else:
                    errors.append({
                        'item_code': code.strip(),
                        'error': 'Product is not in store or store mismatch'
                    })
            except Product.DoesNotExist:
                errors.append({
                    'item_code': code.strip(),
                    'error': 'Product does not exist'
                })

    elif item_type == 'box':
        for box_code in items_list:
            box_code = box_code.strip()
            # Fetch products associated with the box code from the products API
            response = requests.get(f'{apiUrl}/products?box_code={box_code}')

            if response.status_code == 200:
                products = response.json()

                for product in products:
                    try:
                        product_instance = Product.objects.get(id=product['id'])
                        if product_instance.status == "in_store" and str(product_instance.store_id) == str(store_id):
                            # Update product details
                            product_instance.store_id = None  # Remove store ID
                            product_instance.driver_id = driver_id  # Assign the driver ID
                            product_instance.status = "in_return_transit"  # Change status to in_return_transit
                            product_instance.save()  # Save the updated product instance
                            successfully_updated.append(product_instance.item_code)

                            # Associate product with the return instance
                            return_instance.products.add(product_instance)
                        else:
                            print(f"Product Status: {product_instance.status}, Product Store ID: {type(product_instance.store_id)}, Incoming Store ID: {type(store_id)}")
                            errors.append({
                                'item_code': product['item_code'],
                                'error': 'Product is not in store or store mismatch'
                            })
                    except Product.DoesNotExist:
                        errors.append({
                            'item_code': product['item_code'],
                            'error': 'Product does not exist'
                        })
            else:
                errors.append({
                    'box_code': box_code,
                    'error': f'Failed to fetch products for box code {box_code}.'
                })
    else:
        return JsonResponse({'error': 'Invalid item type. Must be "product" or "box".'}, status=400)
    
        # Create logs after adding products
    return_instance.save()

    for product in return_instance.products.all():
            ProductActivityLog.objects.create(
                product=product,
                details=f"Return initiated at {timezone.now().strftime('%Y-%m-%d %H:%M')} for Product {product.name} by {return_instance.driver.first_name}."
            )

    return JsonResponse({
        'return_id': return_instance.id,  # Return the ID of the newly created return instance
        'driver_id': driver_id,
        'successfully_updated': successfully_updated,
        'errors': errors,
        'total_products_updated': len(successfully_updated),
        'total_errors': len(errors),
    }, status=200)


# ------------------------------------------ RECEIVE RETURN  ------------------------------------------ 

@api_view(['POST'])
@permission_classes([AllowAny])
def receive_return(request):
    product_codes = request.data.get('product_codes', [])  # List of product or box codes
    warehouse_id = request.data.get('warehouse_id')
    profile_id = request.data.get('profile_id')
    item_type = request.data.get('item_type')  # 'product' or 'box'

    if not product_codes or not warehouse_id or not profile_id or not item_type:
        return JsonResponse(
            {'error': 'Product/Box codes, warehouse ID, profile ID, and item type are required.'},
            status=400
        )

    profile = Profile.objects.get(pk=profile_id)
    successfully_processed = []
    errors = []

    if item_type == "product":
        for product_code in product_codes:
            try:
                product = Product.objects.get(item_code=product_code.strip())

                # Find the return instance associated with the product
                return_instance = Return.objects.filter(products=product).first()
                if not return_instance:
                    errors.append({'product_code': product_code, 'error': 'Product is not part of any return.'})
                    continue

                # Check if the return has already been processed
                if return_instance.status == "processed":
                    errors.append({'product_code': product_code, 'error': 'Return has already been processed.'})
                    continue

                # Update product details
                product.warehouse_id = warehouse_id
                product.status = "in_warehouse"
                product.driver_id = None
                product.save()

                # Remove product from the return instance
                return_instance.products.remove(product)
                successfully_processed.append(product_code)

                # Log the activity
                ProductActivityLog.objects.create(
                    product=product,
                    details=(
                        f"Product {product.name} received at {timezone.now().strftime('%Y-%m-%d %H:%M')} "
                        f"by {profile.first_name} at warehouse {warehouse_id}."
                    )
                )

                # Mark the return as processed if all products are removed
                if not return_instance.products.exists():
                    return_instance.status = "processed"
                    return_instance.save()

            except Product.DoesNotExist:
                errors.append({'product_code': product_code, 'error': 'Product does not exist.'})
            except Profile.DoesNotExist:
                errors.append({'product_code': product_code, 'error': 'Profile does not exist.'})

    elif item_type == "box":
        for box_code in product_codes:
            box_code = box_code.strip()
            # Fetch products associated with the box code from the products API
            response = requests.get(f'{apiUrl}/products?box_code={box_code}')

            if response.status_code == 200:
                products = response.json()

                for product in products:
                    try:
                        product_instance = Product.objects.get(id=product['id'])
                        
                        # Find the return instance associated with the product
                        return_instance = Return.objects.filter(products=product_instance).first()
                        if not return_instance:
                            errors.append({'box_code': box_code, 'error': 'Product is not part of any return.'})
                            continue

                        # Check if the return has already been processed
                        if return_instance.status == "processed":
                            errors.append({'box_code': box_code, 'error': 'Return has already been processed.'})
                            continue

                        # Update product details
                        product_instance.warehouse_id = warehouse_id
                        product_instance.status = "in_warehouse"
                        product_instance.driver_id = None
                        product_instance.save()

                        # Remove product from the return instance
                        return_instance.products.remove(product_instance)
                        successfully_processed.append(product_instance.item_code)

                        # Log the activity
                        ProductActivityLog.objects.create(
                            product=product_instance,
                            details=(
                                f"Product {product_instance.name} received at {timezone.now().strftime('%Y-%m-%d %H:%M')} "
                                f"by {profile.first_name} at warehouse {warehouse_id}."
                            )
                        )

                        # Mark the return as processed if all products are removed
                        if not return_instance.products.exists():
                            return_instance.status = "processed"
                            return_instance.save()

                    except Product.DoesNotExist:
                        errors.append({'box_code': box_code, 'error': 'Product does not exist.'})
                    except Profile.DoesNotExist:
                        errors.append({'box_code': box_code, 'error': 'Profile does not exist.'})

            else:
                errors.append({
                    'box_code': box_code,
                    'error': f'Failed to fetch products for box code {box_code}.'
                })

    else:
        return JsonResponse({'error': 'Invalid item type. Must be "product" or "box".'}, status=400)

    return JsonResponse({
        'message': 'Return processing completed.',
        'successfully_processed': successfully_processed,
        'errors': errors,
        'total_processed': len(successfully_processed),
        'total_errors': len(errors),
    }, status=200)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_cashflow_data(request):
    return JsonResponse({
        "cash":"25000",
        "pos":"30000",
        "returned-parcel":"33",
        "delivered-parcel":"140",

    })

# # views.py
# import requests
# from django.http import JsonResponse
# from .models import Invoice
# from .util import generate_invoice_xml, generate_qr_code, sign_invoice_xml

# def send_invoice_to_zatca(invoice_id):
#     # Get the invoice data
#     invoice = Invoice.objects.get(id=invoice_id)

#     # Generate XML and sign it
#     xml_data = generate_invoice_xml(invoice)
#     signature = sign_invoice_xml(xml_data)
    
#     # Generate the QR code
#     qr_path = generate_qr_code(invoice)
    
#     # API details
#     zatca_url = "https://api.zatca.gov.sa/your-endpoint"
#     headers = {
#         "Authorization": "Bearer YOUR_API_TOKEN",
#         "Content-Type": "application/xml",
#     }

#     # Constructing payload
#     payload = {
#         "invoice_xml": xml_data,
#         "signature": signature,
#         "qr_code": qr_path
#     }

#     # Send POST request to ZATCA API
#     response = requests.post(zatca_url, headers=headers, data=payload)
    
#     if response.status_code == 200:
#         return JsonResponse({"status": "success", "message": "Invoice sent successfully"})
#     else:
#         return JsonResponse({"status": "error", "message": response.text})
