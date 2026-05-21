from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from shop.orders.models import Order
from shop.models import Product


User = get_user_model()


@shared_task
def test_task(user_id: int|None):
    user = None
    if user_id:
        user = User.objects.filter(id=user_id).first()
    requested_user = user or 'Not athenticated User'
    return f'Task executed succesfully! Requested by: {requested_user}'


@shared_task
def send_confirmation_order_email(order_id: int):
    try:
        order = Order.objects.prefetch_related('items__product').get(pk=order_id)
    except Order.DoesNotExist:
        return f'Order #{order_id} not found'
    
    items_text = '\n'.join(
        f' * {item.product.name} x {item.quantity} = {item.get_total()} UAH'
        for item in order.items.all()
    )

    subject = f'Order #{order_id} confirmed!'

    body = (
        f'Dear {order.first_name} \n\n'
        f'Thanks for order #{order_id} \n'
        f'Items: \n{items_text}\n'
        f'Total: {order.total_price}'
    )

    try:
        send_mail(
            subject=subject,
            message=body,
            recipient_list=[order.email],
            from_email=settings.DEFAULT_EMAIL_FROM
        )
    except Exception as e:
        return f'Email failed for order {order_id}'

    return f'Email sent to {order.email}'


@shared_task
def notify_low_stock_products():
    low_stock = list(
        Product.objects.filter(
            is_active=True,
            stock__lte=settings.LOW_STOCK_TRESHOLD
        ).values('id', 'name', 'stock')
    )

    if not low_stock:
        return {'notified': 0, 'products': []}
    
    staff_emails = list(
        User.objects.filter(is_staff=True, is_active=True)
        .values_list('email', flat=True)
    )

    if not staff_emails:
        return {'notified': 0, 'products': low_stock}
    
    lines = '\n'.join(
        f'* {p['name']} - stcok: {p['stock']}'
        for p in low_stock
    )

    send_mail(
        subject=f'Low stock for {len(low_stock)} products',
        message=lines,
        recipient_list=staff_emails,
        from_email=settings.DEFAULT_EMAIL_FROM
    )

    return {'notified': len(staff_emails), 'products': low_stock}
