from django.db import models
from django.utils.translation import gettext_lazy as _
from shop.models import Product, Customer


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = 'pending', _('Очікує')
        PAID = 'paid', _('Оплачено')
        CREATED = 'created', _('Створено')
        DELIVERED = 'delivered', _('Доставлено')
        CANCELED = 'canceled', _('Скасовано')

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=30,
        choices=OrderStatus.choices,
        default=OrderStatus.CREATED
    )
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    payment = models.OneToOneField(
        'payments.Payment',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def get_total(self):
        return self.price * self.quantity
