import base64
import json
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect

from courses.models import Course
from enrollments.models import Enrollment
from .models import Order
from .utils import generate_signature, verify_signature


@login_required
def initiate_payment_view(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, is_published=True)

    if course.price == 0:
        messages.info(request, "This course is free — enroll directly.")
        return redirect('courses:course_detail', slug=course.slug)

    if course.enrollments.filter(student=request.user).exists():
        messages.info(request, "You're already enrolled in this course.")
        return redirect('courses:course_detail', slug=course.slug)

    amount = course.price
    tax_amount = Decimal('0')
    total_amount = amount + tax_amount

    order = Order.objects.create(
        student=request.user,
        course=course,
        amount=amount,
        tax_amount=tax_amount,
        total_amount=total_amount,
    )

    payment_data = {
        "amount": str(amount),
        "tax_amount": str(tax_amount),
        "total_amount": str(total_amount),
        "transaction_uuid": str(order.transaction_uuid),
        "product_code": settings.ESEWA_PRODUCT_CODE,
        "product_service_charge": "0",
        "product_delivery_charge": "0",
        "success_url": request.build_absolute_uri('/payments/success/'),
        "failure_url": request.build_absolute_uri('/payments/failure/'),
        "signed_field_names": "total_amount,transaction_uuid,product_code",
    }
    payment_data["signature"] = generate_signature(payment_data, settings.ESEWA_SECRET_KEY)

    return render(request, 'payments/redirect_to_esewa.html', {
        'payment_data': payment_data,
        'esewa_form_url': settings.ESEWA_FORM_URL,
    })


def payment_success_view(request):
    encoded_data = request.GET.get('data')
    if not encoded_data:
        return HttpResponseBadRequest("Missing payment data.")

    try:
        decoded_json = base64.b64decode(encoded_data).decode('utf-8')
        payload = json.loads(decoded_json)
    except Exception:
        return HttpResponseBadRequest("Malformed payment data.")

    if not verify_signature(payload, settings.ESEWA_SECRET_KEY):
        return HttpResponseBadRequest("Signature verification failed.")

    order = get_object_or_404(Order, transaction_uuid=payload.get('transaction_uuid'))

    if order.student != request.user:
        return HttpResponseBadRequest("Order does not belong to this user.")

    if order.status == Order.Status.COMPLETED:
        return render(request, 'payments/payment_success.html', {'order': order})

    # Compare amounts numerically, not as strings — eSewa's callback format
    # ("101.0") doesn't always match Decimal's own string form ("101.00"),
    # even when the value is identical.
    try:
        returned_amount = Decimal(str(payload.get('total_amount')).replace(',', ''))
    except (InvalidOperation, TypeError):
        order.mark_failed()
        return HttpResponseBadRequest("Invalid amount format.")

    if returned_amount != order.total_amount:
        order.mark_failed()
        return HttpResponseBadRequest("Amount mismatch.")

    with transaction.atomic():
        order.mark_completed(esewa_transaction_code=payload.get('transaction_code', ''))
        Enrollment.objects.get_or_create(student=order.student, course=order.course)

    return render(request, 'payments/payment_success.html', {'order': order})


def payment_failure_view(request):
    return render(request, 'payments/payment_failure.html')