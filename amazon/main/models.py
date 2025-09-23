from django.db import models
from userservice.models import User

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

    class Meta:
        db_table = "category"
        verbose_name = "Category"

class Product(models.Model):
    title = models.CharField(max_length=20)
    price = models.FloatField()
    product_image = models.CharField(max_length=255)
    description = models.CharField(max_length=500)
    count = models.IntegerField()
    status = models.CharField(max_length=10)
    isavaible = models.BooleanField()
    manufacturer_id = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)

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
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)