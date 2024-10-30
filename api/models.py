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
    STATUS_CHOICES = [
        ('in_warehouse', 'In Warehouse'),
        ('in_transit', 'In Transit'),
        ('in_store', 'In Store'),
        ('sold', 'Sold'),
    ]

    name = models.CharField(max_length=255)
    box_code = models.CharField(max_length=100)
    item_code = models.CharField(max_length=100)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    warehouse = models.ForeignKey('Warehouse', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_warehouse')

    def __str__(self):
        return self.name

    
class Warehouse(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    vat_no = models.CharField(max_length=100)
    cr_no = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Store(models.Model):
    name = models.CharField(max_length=255)
    vat_no = models.CharField(max_length=100)
    cr_no = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    point_of_contact = models.CharField(max_length=255)
    whatsapp_number = models.CharField(max_length=20)
    email = models.EmailField()
    qr_code_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True, editable=False)


    def __str__(self):
        return self.name

    def generate_qr_code(self):
        # Serialize the instance data to JSON
        store_data = {
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
        # Generate the QR code before saving
        if not self.qr_code_image:
            self.generate_qr_code()
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name

class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
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
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)  # Pickup location
    store = models.ForeignKey(Store, on_delete=models.CASCADE)          # Drop-off location
    pickup_time = models.DateTimeField(default=timezone.now)
    dropoff_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('In Transit', 'In Transit'), ('Completed', 'Completed')], default='Pending')

    def __str__(self):
        return f"Pickup {self.id} - {self.product.name} from {self.warehouse.name} to {self.store.name}"

class Return(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)          # Pickup location
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)  # Return location
    pickup_time = models.DateTimeField(default=timezone.now)
    return_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('In Transit', 'In Transit'), ('Returned', 'Returned')], default='Pending')

    def __str__(self):
        return f"Return {self.id} - {self.product.name} from {self.store.name} to {self.warehouse.name}"
    
