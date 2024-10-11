from django.contrib import admin
from .models import Contact,Product,Order
from django.utils.html import format_html

# Register your models here.

admin.site.register(Contact)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'image')
    search_fields = ('title', 'description')
    
    def image_tag(self, obj):
        return format_html('<img src="{}" width="60" height="50" />'.format(obj.image.url))
    image_tag.short_description = 'Image'

    # If you want to display the image thumbnail instead of the full image path in the list view:
    list_display = ('title', 'price', 'image_tag')


## DELIVERY PANEL

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'order_date', 'total_price', 'status', 'delivery_status')
    list_filter = ('status', 'delivery_status')
    actions = ['mark_as_delivered', 'mark_as_processing']

    def mark_as_delivered(self, request, queryset):
        queryset.update(delivery_status='Delivered')
        self.message_user(request, "Selected orders have been marked as delivered.")

    def mark_as_processing(self, request, queryset):
        queryset.update(delivery_status='Processing')
        self.message_user(request, "Selected orders have been marked as processing.")

    mark_as_delivered.short_description = "Mark selected orders as Delivered"
    mark_as_processing.short_description = "Mark selected orders as Processing"