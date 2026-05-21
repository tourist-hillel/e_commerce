from django import forms
from shop.orders.models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'address'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3})
        }
