import qrcode
from django.db import models
# from django.core.files import File
from io import BytesIO
# from django.conf import settings
from django.utils import timezone
import json
# Create your models here.
from django.core.files.base import ContentFile
from io import BytesIO
from django.contrib.auth.models import User

from django.db import models

class Product(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ('in_warehouse', 'In Warehouse'),
        ('in_transit', 'In Transit'),
        ('in_return_transit', 'In Return Transit'),
        ('in_store', 'In Store'),
        ('sold', 'Sold'),
    ]

    name = models.CharField(max_length=255)
    box_code = models.CharField(max_length=100,null=True,blank=True)
    item_code = models.CharField(max_length=100,null=True,blank=True)  # Make item_code unique
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    warehouse = models.ForeignKey('Warehouse', on_delete=models.CASCADE, null=True, blank=True)
    store = models.ForeignKey('Store', on_delete=models.CASCADE, null=True, blank=True)  # New field
    driver = models.ForeignKey('Driver', on_delete=models.CASCADE, null=True, blank=True)  # New field
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_warehouse')

    def __str__(self):
        return self.name


    
class Warehouse(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    vat_no = models.CharField(max_length=100)
    cr_no = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Store(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    vat_no = models.CharField(max_length=100)
    cr_no = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    point_of_contact = models.CharField(max_length=256)
    whatsapp_number = models.CharField(max_length=20)
    email = models.EmailField()
    qr_code_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True, editable=False)


    def __str__(self):
        return self.name

    def generate_qr_code(self):
        # Serialize the instance data to JSON
        store_data = {
            'id':self.id,
            'name': self.name,
            'vat_no': self.vat_no,
            'cr_no': self.cr_no,
            'location': self.location,
            'point_of_contact': self.point_of_contact,
            'whatsapp_number': self.whatsapp_number,
            'email': self.email,
        }
        json_data = json.dumps(store_data)

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(json_data)
        qr.make(fit=True)

        # Create an image from the QR code
        img = qr.make_image(fill_color="black", back_color="white")

        # Save the image to a BytesIO object
        img_io = BytesIO()
        img.save(img_io, format='PNG')
        img_file = ContentFile(img_io.getvalue(), f'qr_code_{self.pk}.png')

        # Save the image to the model
        self.qr_code_image.save(f'qr_code_{self.name}.png', img_file)

    def save(self, *args, **kwargs):
            # Save the instance first to get the id if it doesn't exist
            if not self.id:
                super(Store, self).save(*args, **kwargs)
        
            # Generate and save the QR code if not already created
            if not self.qr_code_image:
                self.generate_qr_code()
        
            # Call super().save() again to ensure the QR code is saved in the instance
            super(Store, self).save(*args, **kwargs)



 


    def __str__(self):
        return self.name

class Driver(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True,related_name = "drivers")
    profile_picture = models.ImageField(upload_to='media/', blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    iqama_number = models.CharField(max_length=100)
    nationality = models.CharField(max_length=100)
    iqama_expiry_date = models.DateField()
    driving_license_expiry_date = models.DateField()
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Pickup(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)  # Use ManyToManyField for products
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Pickup {self.id} - {self.products.count()} Products"

class DropOff(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='dropoffs')  # Link to Pickup
    store = models.ForeignKey(Store, on_delete=models.CASCADE)  # The store where products are dropped off
    products = models.ManyToManyField(Product)  # The products being dropped off
    dropoff_time = models.DateTimeField(default=timezone.now)  # Time of the drop-off

    def __str__(self):
        product_names = ', '.join([product.name for product in self.products.all()])
        return f"DropOff {self.id} - {product_names} to {self.store.name}"

class Return(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product,related_name="returns")  # Change from ForeignKey to ManyToManyField
    store = models.ForeignKey(Store, on_delete=models.CASCADE)          
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE,null=True,blank=True)  

    def __str__(self):
        product_names = ', '.join([product.name for product in self.products.all()])
        return f"Return {self.id} - {product_names} from {self.store.name} to {self.warehouse.name}"

    def update_product_status(self, warehouse_id):
        for product in self.products.all():
            if product.status == 'in_return_transit':
                product.status = 'in_warehouse'
                product.warehouse_id = warehouse_id  # Set the warehouse ID
                product.driver = None  # Optionally remove the driver
                product.save()