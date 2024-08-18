from django.contrib import admin
from .models import * 
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

class AdminCustomer(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'address', 'sex', 'age', 'city', 'zip_code', 'display_image')

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return 'No Image'
    display_image.short_description = 'Image'

admin.site.register(Customer, AdminCustomer)

class AdminInvoice(admin.ModelAdmin):
    list_display = ('customer', 'save_by', 'invoice_date_time', 'total', 'last_updated_date', 'paid', 'invoice_type')    

admin.site.register(Customer, AdminCustomer)
admin.site.register(Invoice, AdminInvoice)
admin.site.register(Article)

admin.site.site_title = _("Amar INVOICE SYSTEM")
admin.site.site_header = _("Amar INVOICE SYSTEM")
admin.site.index_title = _("Amar INVOICE SYSTEM")
