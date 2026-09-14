from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('transaction_uuid', 'student', 'course', 'total_amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('transaction_uuid', 'student__email', 'course__title', 'esewa_transaction_code')
    readonly_fields = [f.name for f in Order._meta.fields]  # prevent accidental manual edits

    def has_add_permission(self, request):
        # Orders should only ever be created through the payment flow itself,
        # never hand-typed in admin — same reasoning as editable=False on
        # transaction_uuid in the model.
        return False