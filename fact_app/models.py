from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

class Customer(models.Model):
    """
    Customer model definition
    """
    SEX_TYPES = (
        ('M', _('Male')),
        ('F', _('Female')),  # Changed 'Feminine' to 'Female' for consistency
    )

    # Define the regex validator for the phone number
    phone_regex = RegexValidator(
        regex=r'^[234]\d{7}$',
        message=_("Phone number must be exactly 8 digits long and start with '2', '3', or '4'.")
    )

    name = models.CharField(max_length=132)
    email = models.EmailField()
    phone = models.CharField(max_length=8, validators=[phone_regex])
    address = models.CharField(max_length=64)
    sex = models.CharField(max_length=1, choices=SEX_TYPES)
    age = models.CharField(max_length=12)
    city = models.CharField(max_length=32)
    zip_code = models.CharField(max_length=16)
    created_date = models.DateTimeField(auto_now_add=True)
    save_by = models.ForeignKey(User, on_delete=models.PROTECT)
    image = models.ImageField(upload_to='customer_images/', blank=True, null=True)

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return self.name
    
    @property
    def phone_label(self):
        """
        Return the label based on the starting digit of the phone number.
        """
        if self.phone.startswith('2'):
            return 'Chinguittel'
        elif self.phone.startswith('4'):
            return 'Mauritel'
        elif self.phone.startswith('3'):
            return 'Mattel'
        return 'Unknown'


class Invoice(models.Model):
    """
    Invoice model definition
    """
    INVOICE_TYPE = (
        ('R', _('RECEIPT')),
        ('P', _('PROFORMA INVOICE')),
        ('I', _('INVOICE'))
    )

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    save_by = models.ForeignKey(User, on_delete=models.PROTECT)
    invoice_date_time = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated_date = models.DateTimeField(null=True, blank=True)
    paid = models.BooleanField(default=False)
    invoice_type = models.CharField(max_length=1, choices=INVOICE_TYPE)
    comments = models.TextField(null=True, max_length=1000, blank=True)
    image = models.ImageField(upload_to='invoice_images/', blank=True, null=True)

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"

    def __str__(self):
        return f"{self.customer.name}_{self.invoice_date_time}"

    @property
    def get_total(self):
        articles = self.article_set.all()
        total = sum(article.get_total for article in articles)
        return total


class Article(models.Model):
    """
    Article model definition
    """
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

    @property
    def get_total(self):
        # Ensure total is computed correctly if it's not set manually
        return self.quantity * self.unit_price
