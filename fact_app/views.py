from django.shortcuts import render
from django.views import View
from .models import *

# Create your views here.

class HomeView(View):
    """Main view"""

    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        invoices = Invoice.objects.select_related('customer', 'save_by').all().order_by('-invoice_date_time')
        context = {
            'invoices': invoices
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        invoices = Invoice.objects.select_related('customer', 'save_by').all().order_by('-invoice_date_time')
        context = {
            'invoices': invoices
        }
        return render(request, self.template_name, context)


class AddCustomerView(View):
    """Add new customer"""

    template_name = 'add_customer.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name)
