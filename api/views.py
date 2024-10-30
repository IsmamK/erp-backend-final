from rest_framework import generics
from rest_framework.permissions import AllowAny  # Import AllowAny
from .serializers import *
from .models import *
from django.http import HttpResponse
import pandas as pd
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]  # Allow access to all users

class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]  # Allow access to all users

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


class WarehouseListCreateView(generics.ListCreateAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [AllowAny]  # Allow access to all users

class WarehouseRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [AllowAny]  # Allow access to all users

class StoreListCreateView(generics.ListCreateAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [AllowAny]  # Allow access to all users

class StoreRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [AllowAny]  # Allow access to all users

class DriverListCreateView(generics.ListCreateAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [AllowAny]  # Allow access to all users

class DriverRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [AllowAny]  # Allow access to all users

class PickupListCreateView(generics.ListCreateAPIView):
    queryset = Pickup.objects.all()
    serializer_class = PickupSerializer
    permission_classes = [AllowAny]  # Allow access to all users

class PickupRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pickup.objects.all()
    serializer_class = PickupSerializer
    permission_classes = [AllowAny]  # Allow access to all users

class ReturnListCreateView(generics.ListCreateAPIView):
    queryset = Return.objects.all()
    serializer_class = ReturnSerializer
    permission_classes = [AllowAny]  # Allow access to all users

class ReturnRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Return.objects.all()
    serializer_class = ReturnSerializer
    permission_classes = [AllowAny]  # Allow access to all users

def download_qr_code(request, store_id):
    try:
        store = Store.objects.get(id=store_id)
        response = HttpResponse(store.qr_code_image, content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{store.name}_qr_code.png"'
        return response
    except Store.DoesNotExist:
        return HttpResponse(status=404)