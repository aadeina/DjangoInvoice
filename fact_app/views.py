from django.shortcuts import render
from django.views import View
from .models import Customer, Invoice
from django.contrib import messages

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
        data = {
            'name': request.POST.get('name'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'address': request.POST.get('address'),
            'sex': request.POST.get('sex'),
            'age': request.POST.get('age'),
            'city': request.POST.get('city'),
            'zip_code': request.POST.get('zip'),
            'save_by': request.user
        }
        # Include the image file in the data dictionary
        image = request.FILES.get('image')
        if image:
            data['image'] = image

        try:
            created = Customer.objects.create(**data)

            if created:
                messages.success(request, "Customer registered successfully.")
            else:
                messages.error(request, "Sorry, please try again. The sent data is corrupt.")
        
        except Exception as e:    
            messages.error(request, f"Sorry, our system detected the following issue: {e}.")

        return render(request, self.template_name)
