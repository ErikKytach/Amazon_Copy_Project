from django.db import models
from userservice.models import User
from django.utils import timezone
from django.utils.translation import gettext as _
import os


class Manufacturer(models.Model):
    name = models.CharField(max_length=20)
    country = models.CharField(max_length=20)
    buisness_stream = models.CharField(max_length=15)
    description = models.CharField(max_length=500)

    class Meta:
        db_table = "manufacturer"
        verbose_name = "Manufacturer"

class Category(models.Model):
    name = models.CharField(max_length=20)

    @property
    def translated_name(self):
        return _(self.name)

    class Meta:
        db_table = "category"
        verbose_name = "Category"

class Product(models.Model):
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_image = models.CharField(max_length=255)
    description = models.CharField(max_length=500)
    count = models.IntegerField()
    status = models.CharField(max_length=10)
    isavaible = models.BooleanField()
    manufacturer_id = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    view_count = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    out_of_stock_since = models.DateTimeField(null=True, blank=True)
    sold_count = models.IntegerField(default=0)

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def save(self, *args, **kwargs):
        try:
            self.count = int(self.count) if self.count is not None and str(self.count).strip() != '' else 0
        except (ValueError, TypeError):
            self.count = 0

        if self.count <= 0 and self.out_of_stock_since is None:
            self.out_of_stock_since = timezone.now()
        elif self.count > 0 and self.out_of_stock_since is not None:
            self.out_of_stock_since = None

        need_trans = False
        if self.title and (not getattr(self, 'title_en', None) or not getattr(self, 'title_uk', None) or not getattr(self, 'title_de', None)):
            need_trans = True
        if self.description and (not getattr(self, 'description_en', None) or not getattr(self, 'description_uk', None) or not getattr(self, 'description_de', None)):
            need_trans = True

        super().save(*args, **kwargs)

    class Meta:
        db_table = "product"
        verbose_name = "Product"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)


class PaymentMethod(models.Model):
    card_number = models.CharField(max_length=20, null=True)
    card_expiry = models.CharField(max_length=5, null=True)
    card_cvc = models.IntegerField(null=True)
    card_name = models.CharField(max_length=20, null=True)
    email = models.EmailField(null=True)
    type = models.CharField(max_length=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "paymentmethod"
        verbose_name = "PaymentMethod"

class Order(models.Model):
    paymentmethod = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    status = models.CharField(max_length=10)
    date_of_create = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    count = models.IntegerField(default=1)
    product_title = models.CharField(max_length=255)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image_url = models.CharField(max_length=255)

    def __str__(self):
        return f"Product image: {self.product.title}"


class ProductView(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ip_views')
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # indexes for easier work
        indexes = [
            models.Index(fields=['product', 'ip_address', 'created_at']),
        ]