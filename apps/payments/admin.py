from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'size', 'price', 'quantity', 'get_cost']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['id', 'email', 'first_name', 'last_name', 'stripe_payment_intent_id']
    readonly_fields = [
        'created_at', 'updated_at', 'stripe_payment_intent_id',
        'stripe_charge_id', 'get_total_cost'
    ]
    inlines = [OrderItemInline]

    fieldsets = (
        ('Order Information', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
        ('Customer Information', {
            'fields': ('user', 'email', 'first_name', 'last_name', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'postal_code', 'country')
        }),
        ('Order Amounts', {
            'fields': ('total_amount', 'shipping_cost', 'tax_amount', 'get_total_cost')
        }),
        ('Payment Information', {
            'fields': ('stripe_payment_intent_id', 'stripe_charge_id')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes'),
            'classes': ('collapse',)
        }),
    )

    def get_total_cost(self, obj):
        return f'${obj.get_total_cost()}'

    get_total_cost.short_description = 'Total Cost'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'size', 'quantity', 'price', 'get_cost']
    list_filter = ['order__created_at']
    search_fields = ['order__id', 'product__name']
    readonly_fields = ['get_cost']