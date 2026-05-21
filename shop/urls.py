from django.urls import path
from shop.views import (
    product_list,
    cart_add,
    cart_detail,
    cart_remove,
    order_create,
    upload_s3_files,
    s3_files_list
)

urlpatterns = [
    path('', product_list, name='product_list'),
    path('cart/', cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', cart_remove, name='cart_remove'),
    path('order/create/', order_create, name='order_create'),
    path('upload_s3_files/', upload_s3_files, name='upload_s3_files'),
    path('s3_files_list/', s3_files_list, name='s3_files_list'),
]