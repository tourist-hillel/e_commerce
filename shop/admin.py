from django.contrib import admin
from shop.models import Product, Customer, Category
from shop.orders.models import Order, OrderItem


admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Category)