from django.core.mail import send_mail, EmailMultiAlternatives  # noqa: F401
from django.template.loader import render_to_string


def send_reciept(order):
    # send_mail(
    #     subject='Order reciept',
    #     message='Test message',
    #     from_email=None,
    #     recipient_list=[email]
    # )

    # html_content = render_to_string('email/order_receipt.html', {'order': order})
    text_content = render_to_string('email/order_receipt.txt', {'order': order})
    email = EmailMultiAlternatives(
        subject=f'Замовлення №{order.id}',
        body=text_content,
        from_email=None,
        to=[order.email]
    )
    # email.attach_alternative(html_content, mimetype='text/html')
    email.send()
