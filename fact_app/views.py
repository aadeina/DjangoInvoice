from django.shortcuts import render
from django.views import View
from .models import *
from django.contrib import messages

from django.http import HttpResponse

import pdfkit

import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.template.loader import get_template

from django.db import transaction

from .utils import pagination, get_invoice

from .decorators import *

from django.utils.translation import gettext as _
# Create your views here.

class HomeView(LoginRequiredSuperuserMixim, View):
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
                messages.error(request, _("Sorry, the following error has occurred: {}.").format(e))
        
        # Delete an invoice
        if request.POST.get('id_supprimer'):
            try:
                obj = Invoice.objects.get(pk=request.POST.get('id_supprimer'))
                obj.delete()
                messages.success(request, _("The deletion was successful."))
            except Exception as e:
                messages.error(request, _("Sorry, the following error has occurred: {}.").format(e))

        invoices = Invoice.objects.select_related('customer', 'save_by').all().order_by('-invoice_date_time')
        items = pagination(request, invoices)
        context = {'invoices': items}
        return render(request, self.template_name, context)


class AddCustomerView(LoginRequiredSuperuserMixim, View):
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
            'save_by': request.user if request.user.is_authenticated else None
        }
        image = request.FILES.get('image')
        if image:
            data['image'] = image

        try:
            Customer.objects.create(**data)
            messages.success(request, _("Customer registered successfully."))
        except Exception as e:
            messages.error(request, _("Sorry, our system detected the following issue: {}.").format(e))

        return render(request, self.template_name)


class AddInvoiceView(LoginRequiredSuperuserMixim, View):
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
                'save_by': request.user,
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
            messages.success(request, _("Data saved successfully."))
        except Exception as e:
            messages.error(request, _("Sorry, the following error has occurred: {}.").format(e))

        return render(request, self.template_name)


class InvoiceVisualizationView(LoginRequiredSuperuserMixim, View):
    """ This view helps to visualize the invoice """

    template_name = 'invoice.html'

    def get(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        context = get_invoice(pk)

        return render(request, self.template_name, context)


@superuser_required
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
        return HttpResponse(_("Error generating PDF: {}").format(e), status=500)
