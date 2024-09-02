from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from .models import Article, Customer, Invoice
from django.contrib import messages
from django.db import transaction
from django.utils.translation import gettext as _
from .utils import get_invoice, pagination
import pdfkit
import datetime
from django.template.loader import get_template
# Create your views here.

class HomeView(View):
    """Main view"""
    
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        invoices = Invoice.objects.select_related('customer', 'save_by').all().order_by('-invoice_date_time')
        items = pagination(request, invoices)
        context = {'invoices': items}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Modify an invoice
        if request.POST.get('id_modified'):
            paid = request.POST.get('modified')
            try:
                obj = Invoice.objects.get(id=request.POST.get('id_modified'))
                obj.paid = (paid == 'True')
                obj.save()
                messages.success(request, _("Change made successfully."))
            except Exception as e:
                messages.error(request, f"Sorry, the following error has occurred: {e}.")
        
        # Delete an invoice
        if request.POST.get('id_supprimer'):
            try:
                obj = Invoice.objects.get(pk=request.POST.get('id_supprimer'))
                obj.delete()
                messages.success(request, _("The deletion was successful."))
            except Exception as e:
                messages.error(request, f"Sorry, the following error has occurred: {e}.")

        invoices = Invoice.objects.select_related('customer', 'save_by').all().order_by('-invoice_date_time')
        items = pagination(request, invoices)
        context = {'invoices': items}
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
             # Ensure this is a User instance if applicable to your design
            'save_by': request.user if request.user.is_authenticated else None
            #'save_by': request.user  # Ensure this is a User instance
        }
        # Include the image file in the data dictionary
        image = request.FILES.get('image')
        if image:
            data['image'] = image

        try:
            Customer.objects.create(**data)
            messages.success(request, "Customer registered successfully.")
        except Exception as e:
            messages.error(request, f"Sorry, our system detected the following issue: {e}.")

        return render(request, self.template_name)


class AddInvoiceView(View):
    """Add a new invoice view"""

    template_name = 'add_invoice.html'

    def get(self, request, *args, **kwargs):
        customers = Customer.objects.all()  # Get all customers
        context = {'customers': customers}
        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        items = []
        try:
            customer_id = request.POST.get('customer')
            invoice_type = request.POST.get('invoice_type')
            articles = request.POST.getlist('article')
            quantities = request.POST.getlist('qty')
            units = request.POST.getlist('unit')
            total_arts = request.POST.getlist('total-a')
            total = request.POST.get('total')
            comment = request.POST.get('comment')

            invoice_object = {
                'customer_id': customer_id,
                'save_by': request.user,  # Ensure request.user is a User instance
                'total': total,
                'invoice_type': invoice_type,
                'comments': comment
            }

            invoice = Invoice.objects.create(**invoice_object)

            for index, article in enumerate(articles):
                data = Article(
                    invoice=invoice,
                    name=article,
                    quantity=quantities[index],
                    unit_price=units[index],
                    total=total_arts[index],
                )
                items.append(data)

            Article.objects.bulk_create(items)
            messages.success(request, "Data saved successfully.")
        except Exception as e:
            messages.error(request, f"Sorry, the following error has occurred: {e}.")

        return render(request, self.template_name)


class InvoiceVisualizationView(View):
    """ This view helps to visualize the invoice """

    template_name = 'invoice.html'

    def get(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        context = get_invoice(pk)

        return render(request, self.template_name, context)



def get_invoice_pdf(request, *args, **kwargs):
    """Generate PDF file from HTML file."""

    pk = kwargs.get('pk')
    context = get_invoice(pk)
    context['date'] = datetime.datetime.today()

    # Get the HTML file
    template = get_template('invoice-pdf.html')
    html = template.render(context)

    # Specify the path to wkhtmltopdf
    path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

    # Options for PDF format
    options = {
        'page-size': 'Letter',
        'encoding': 'UTF-8',
        'enable-local-file-access': True  # This should be set to True to enable local file access
    }

    # Generate PDF
    try:
        pdf = pdfkit.from_string(html, False, configuration=config, options=options)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
        return response
    except IOError as e:
        return HttpResponse(f"Error generating PDF: {e}", status=500)
