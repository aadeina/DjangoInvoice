from django.shortcuts import render
from django.views import View
from .models import Article, Customer, Invoice
from django.contrib import messages
from django.db import transaction
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



class AddInvoiceView( View):
    """ add a new invoice view """

    template_name = 'add_invoice.html'

    customers = Customer.objects.select_related('save_by').all()

    context = {
        'customers': customers
    }

    def get(self, request, *args, **kwargs):
        return  render(request, self.template_name, self.context)

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        
        items = []

        try: 

            customer = request.POST.get('customer')

            type = request.POST.get('invoice_type')

            articles = request.POST.getlist('article')

            qties = request.POST.getlist('qty')

            units = request.POST.getlist('unit')

            total_a = request.POST.getlist('total-a')

            total = request.POST.get('total')

            comment = request.POST.get('commment')

            invoice_object = {
                'customer_id': customer,
                'save_by': request.user,
                'total': total,
                'invoice_type': type,
                'comments': comment
            }

            invoice = Invoice.objects.create(**invoice_object)

            for index, article in enumerate(articles):

                data = Article(
                    invoice_id = invoice.id,
                    name = article,
                    quantity=qties[index],
                    unit_price = units[index],
                    total = total_a[index],
                )

                items.append(data)

            created = Article.objects.bulk_create(items)   

            if created:
                messages.success(request, "Data saved successfully.") 
            else:
                messages.error(request, "Sorry, please try again the sent data is corrupt.")    

        except Exception as e:
            messages.error(request, f"Sorry the following error has occured {e}.")   

        return  render(request, self.template_name, self.context)

