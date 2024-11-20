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


    if not driver_id:
        return JsonResponse({'error': 'Driver ID is required.'}, status=400)

    if not items:
        return JsonResponse({'error': 'Items are required.'}, status=400)

    if not item_type:
        return JsonResponse({'error': 'Item type is required.'}, status=400)

    if not warehouse_id:
        return JsonResponse({'error': 'Warehouse ID is required.'}, status=400)

    items_list = items  # Use the provided items list directly
    pickup = Pickup.objects.create(driver_id=driver_id, warehouse_id=warehouse_id)  # Create a new pickup instance

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


# ------------------------------------------ CREATE DROPOFF (FOR APP)  ------------------------------------------ 

@api_view(['POST'])
@permission_classes([AllowAny])
def create_dropoff(request):
    driver_id = request.data.get('driver_id')
    items = request.data.get('items')  # This should be a list of strings
    item_type = request.data.get('item_type')  # 'product' or 'box'
    store_id = request.data.get('store_id')
    method_of_collection = request.data.get('method_of_collection')

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
                total_amount += product.buying_price
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
                    total_amount += product.buying_price
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

        # Check which items are successfully matched
        for code in new_product_codes:
            if code in current_product_codes:
                successfully_matched.append(code)
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

                # Check which items are successfully matched
                for product in products:
                    if product['item_code'] in current_product_codes:
                        successfully_matched.append(product['item_code'])
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
                print(type(store_id))
                print(type(product.store_id))
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
    return_id = request.data.get('return_id')
    warehouse_id = request.data.get('warehouse_id')

    if not return_id or not warehouse_id:
        return JsonResponse({'error': 'Return ID and warehouse ID are required.'}, status=400)

    try:
        return_instance = Return.objects.get(id=return_id)
    except Return.DoesNotExist:
        return JsonResponse({'error': 'Return does not exist.'}, status=404)

    # Update product statuses and get the list of successfully returned products
    successfully_returned_products = return_instance.update_product_status(warehouse_id)

    return JsonResponse({
        'message': 'Return processed successfully.',
        'successfully_returned_products': successfully_returned_products
    }, status=200)

#

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
