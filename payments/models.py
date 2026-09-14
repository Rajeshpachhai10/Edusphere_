import uuid
from django.db import models
from django.conf import settings
from courses.models import Course


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    # Our own reference, created the instant the student clicks "Pay to
    # Enroll" — sent to eSewa as transaction_uuid, and handed back to us
    # unchanged inside the callback payload. This is the ONE field we
    # dedupe on.
    transaction_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    amount = models.DecimalField(max_digits=8, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    # Only known once eSewa confirms payment — useful for support lookups,
    # never used for our own internal matching.
    esewa_transaction_code = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.transaction_uuid} — {self.student} — {self.course} ({self.status})"

    def mark_completed(self, esewa_transaction_code):
        self.status = self.Status.COMPLETED
        self.esewa_transaction_code = esewa_transaction_code
        self.save(update_fields=['status', 'esewa_transaction_code', 'updated_at'])

    def mark_failed(self):
        self.status = self.Status.FAILED
        self.save(update_fields=['status', 'updated_at'])