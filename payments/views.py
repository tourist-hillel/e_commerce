import logging
from decimal import Decimal
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from payments.models import Payment
from payments.stripe_service import StripePaymentService
from payments.serializers import PaymentSerializer, CreatePaymentSerializer
from shop.orders.models import Order
from payments.utils import send_reciept


logger = logging.getLogger(__name__)

STRIPE_P_KEY = settings.STRIPE_PUBLIC_KEY


def checkout_view(request, order_id=None):
    order = None
    if order_id:
        order = get_object_or_404(Order, id=order_id)
    return render(request, 'checkout.html', {
        'stripe_public_key': STRIPE_P_KEY,
        'order': order
    })


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).select_related('user')

    def get_serializer_class(self):
        if self.action == 'create_payment_intent':
            return CreatePaymentSerializer
        return PaymentSerializer

    @action(detail=False, methods=['post'])
    def create_payment_intent(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            payment, payment_intent = StripePaymentService.create_payment_intent(
                user=request.user,
                amount=Decimal(serializer.validated_data['amount']),
                currency=serializer.validated_data['currency'],
                description=serializer.validated_data['description'],
                metadata=serializer.validated_data.get('metadata', {})
            )

            return Response({
                'payment_id': str(payment.id),
                'client_secret': payment_intent.client_secret,
                'amount': str(payment.amount),
                'currency': payment.currency,
                'status': payment.status
            }, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f'Error on payment intent creation: {str(e)}')
            return Response(
                {'error': 'Failed to create payment intent'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        payment = self.get_object()
        order = get_object_or_404(Order, id=10)
        order.payment = payment
        order.save()

        try:
            payment = StripePaymentService.confirm_payment(
                payment_id=str(payment.id),
                stripe_payment_intent_id=payment.stripe_payment_intent_id
            )
            serializer = self.get_serializer(payment)
            send_reciept(order)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f'Error on payment intent confirmation: {str(e)}')
            return Response(
                {'error': 'Failed to confirm payment intent'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
