from django.db.models.signals import post_save
from django.dispatch import receiver
from shop.orders.models import OrderItem, Order


@receiver(post_save, sender=OrderItem)
def change_stock_on_order(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        if product.stock >= instance.quantity:
            product.stock -= instance.quantity
            product.save(update_fields=['stock'])
        else:
            order = instance.order
            order.status = Order.OrderStatus.CANCELED
            order.save(update_fields=['status'])
