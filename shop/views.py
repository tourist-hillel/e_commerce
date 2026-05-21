from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from botocore.exceptions import ClientError
from shop.models import Product, Customer
from shop.orders.models import Order, OrderItem
from shop.cart.cart import Cart
from shop.cache import get_cached_api_response, set_cached_api_response
from django.contrib import messages
from shop.forms import OrderCreateForm
from shop.tasks import test_task, send_confirmation_order_email
import logging
from shop.boto_client import get_s3_client, FILE_BUCKET_NAME
# import tthis

logger = logging.getLogger(__name__)

def product_list(request):
    request_id = getattr(request,'request_id', '-')
    CACHE_PATH = '/products/'
    cached = get_cached_api_response(CACHE_PATH)
    if cached is not None:
        logger.debug('product_list: L3 cahce HIT', extra={'request_id': request_id})
        return render(request, 'products/list.html', {'products': cached})
    products = list(Product.active.all())
    set_cached_api_response(CACHE_PATH, products)

    user_id = None
    if request.user.is_authenticated:
        user_id = request.user.id

    test_task.delay(user_id)
    return render(request, 'products/list.html', {'products': products})


def cart_detail(request):
    cart = Cart(request)

    context = {
        'cart': cart,
        'total_price': cart.get_total_price()
    }
    return render(request, 'cart/detail.html', context)


def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart.add(product=product, quantity=quantity, override_quantity=False)
        messages.success(request, f'{product.name} додано до кошику')
    return redirect('cart_detail')


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart.remove(product)
    messages.info(request, f'{product.name} видалено з кошика')
    return redirect('cart_detail')


def order_create(request):
    cart = Cart(request)

    if not cart.cart:
        messages.warning(request, 'Ваш кошик пустий!!')
        return redirect('cart_detail')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.total_price = cart.get_total_price()

            if request.user.is_authenticated:
                try:
                    order.customer = request.user.customer
                except:
                    customer, created = Customer.objects.get_or_create(user=request.user)
                    order.customer = customer
            order.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            cart.clear()

            messages.success(request, f'Замовлення #{order.id} було успішно оформлене')
            send_confirmation_order_email.delay(order.id)
            return render(request, 'order/success_order.html', {'order': order})
    else:
        initial = {}
        if request.user.is_authenticated:
            customer = None
            user = request.user
            
            initial = {
                'first_name':  user.first_name,
                'last_name': user.last_name,
                'email': user.email,
            }
            if hasattr(user, 'customer'):
                customer = user.customer
            if customer:
                initial.update({
                    'phone': getattr(customer, 'phone', ''),
                    'address': getattr(customer, 'adress', '')
                })

        form = OrderCreateForm(initial=initial)

    context = {
        'form': form,
        'cart': cart,
        'total_price': cart.get_total_price()
    }

    return render(request, 'order/create_order.html', context)


def upload_s3_files(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        logger.info(f'File: {file.name}')
        try:
            default_storage.save(file.name, ContentFile(file.read()))
        except Exception as e:
            logger.error(str(e))
    return redirect('s3_files_list')

def s3_files_list(request):
    s3_client = get_s3_client()
    files = []
    errors = []
    continuation_token = None

    try:
        logger.info('Test \'Shop\' logger')
        while True:
            params  = {'Bucket': FILE_BUCKET_NAME}
            if continuation_token:
                params['ContinuationToken'] = continuation_token
            response = s3_client.list_objects_v2(**params)
            for file in response.get('Contents', []):
                file_name = file['Key']
                try:
                    file_params = params.copy()
                    file_params['Key'] = file_name
                    presigned_file_url = s3_client.generate_presigned_url(
                        'get_object',
                        Params=file_params,
                        ExpiresIn=30
                    )
                    files.append({
                        'file_name': file_name,
                        'file_url': presigned_file_url,
                        'size': file['Size'],
                        'last_modified': file['LastModified']
                    })
                except ClientError as err:
                    errors.append(err)
                    logger.error(f'Client Error: {err}')
            if response.get('isTruncated'):
                continuation_token = response.get('NextContinuationToken')
            else:
                break
    except ClientError as err:
        errors.append(err)
        logger.error(f'Client Error: {err}')

    return render(request, 's3_bucket/s3_files_list.html', {'files': files, 'errors': errors})