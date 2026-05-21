from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid

User = get_user_model()


class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Payment(TimeStampModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Очікує'
        PROCESSING = 'processing', 'Оброблюється'
        SUCCEEDED = 'succeeded', 'Успішно'
        FAILED = 'failed', 'Невдало'
        CANCELED = 'canceled', 'Скасовано'
        REFUNDED = 'refunded', 'Повернуто'
        PARTIALLY_REFUNDED = 'partially_refunded', 'Частково повернуто'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='payments'
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True
    )
    stripe_charge_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.50'))]
    )
    currency = models.CharField(
        max_length=5,
        default='USD'
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING
    )
    description = models.TextField(
        blank=True
    )
    metadata = models.JSONField(
        default=dict,
        blank=True
    )
    error_message = models.TextField(
        blank=True,
        null=True
    )
    refund_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    class Meta:
        db_table = 'stripe_paymnets'
        verbose_name = 'Платіж'
        verbose_name_plural = 'Платежі'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'Payment {self.id} - {self.amount} {self.currency} ({self.status})'

    @property
    def is_successful(self):
        return self.status == self.Status.SUCCEEDED

    @property
    def can_be_refunded(self):
        return (
            self.is_successful and
            self.refund_amount <= self.amount
        )
