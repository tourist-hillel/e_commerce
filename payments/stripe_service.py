import stripe
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from typing import Dict, Optional, Tuple
from payments.models import Payment

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = '2026-03-25.dahlia'


class StripePaymentService:
    @staticmethod
    @transaction.atomic
    def create_payment_intent(
        user,
        amount: Decimal,
        currency: str = 'usd',
        description: str = '',
        metadata: Optional[Dict] = None,
        idempotency_key: Optional[str] = None
    ) -> Tuple[Payment, stripe.PaymentIntent]:
        if amount < Decimal('0.50'):
            raise ValueError('Мінімальна сума платежу 0.50')
        
        stripe_amount = int(amount * 100)
        payment_metadata = metadata or {}
        payment_metadata['user_id'] = str(user.id)

        try:
            logger.info(
                f'Attempt to creaet paymnet intent for user {user.id}, amount {amount} {currency}'
            )
            payment_intent_params = {
                'amount': stripe_amount,
                'currency': currency.lower(),
                'description': description,
                'metadata': payment_metadata,
                'automatic_payment_methods': {
                    'enabled': True
                },
            }
            if idempotency_key:
                payment_intent = stripe.PaymentIntent.create(
                    **payment_intent_params,
                    idempotency_key=idempotency_key
                )
            else:
                payment_intent = stripe.PaymentIntent.create(
                    **payment_intent_params
                )
                payment = Payment.objects.create(
                    user=user,
                    amount=amount,
                    stripe_payment_intent_id=payment_intent.id,
                    currency=currency.upper(),
                    description=description,
                    metadata=payment_metadata,
                    status=Payment.Status.PENDING
                )
                logger.info(f'Payment {payment.id} created for user {user.id}')
                return payment, payment_intent
        except stripe.StripeError as e:
            logger.error(f'Stripe error while paymnet intent: {str(e)}')
            raise
        except Exception as e:
            logger.error(f'Unexpected error while paymnet intent: {str(e)}')
            raise
    
    @staticmethod
    @transaction.atomic
    def confirm_payment(
            payment_id: str,
            stripe_payment_intent_id: str,
    ) -> Payment:
        payment = Payment.objects.select_for_update().get(
            id=payment_id,
            stripe_payment_intent_id=stripe_payment_intent_id
        )

        if payment.is_successful:
            logger.warning(f'Payment {payment.id} already confirmed')
            return payment
        try:
            payment_intent = stripe.PaymentIntent.retrieve(stripe_payment_intent_id)
            if payment_intent.status == Payment.Status.SUCCEEDED:
                payment.status = Payment.Status.SUCCEEDED
                payment.stripe_charge_id = payment_intent.latest_charge
                payment.save(update_fields=['status', 'stripe_charge_id', 'updated_at'])
                logger.info(f'Payment {payment.id} confirmed')
            else:
                payment.status = Payment.Status.FAILED
                payment.error_message = f'Payment intent status: {payment_intent.status}'
                payment.save(update_fields=['status', 'error_message', 'updated_at'])
                logger.warning(f'Payment {payment.id} was not confirmed')
            return payment
        except stripe.StripeError as e:
            logger.error(f'Stripe error while payment confirmation: {str(e)}')
            payment.status = Payment.Status.FAILED
            payment.error_message = str(e)
            payment.save(update_fields=['status', 'error_message', 'updated_at'])
            raise
