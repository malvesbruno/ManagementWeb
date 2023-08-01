from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# Create your models here.


class CustomUser(AbstractUser):
    profiles = models.ManyToManyField('Profile', blank=True)
    enterprise = models.ManyToManyField('Enterprise', blank=True)


class Enterprise(models.Model):
    enterprise = models.CharField(max_length=14, null=True, unique=True)
    name = models.CharField(max_length=1000)
    picture = models.ImageField(null=True, upload_to='media')
    uuid = models.UUIDField(default=uuid.uuid4(), unique=True)

    def __str__(self):
        return self.name


class Area(models.Model):
    area_name = models.CharField(max_length=1000, null=False)
    id = models.IntegerField(primary_key=True, unique=True, db_index=True)
    enterprise = models.ForeignKey(
        Enterprise,
        related_name="area",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default='',
    )
    control_employee = models.BooleanField(default=True)
    area_add = models.BooleanField(default=True)
    add_employee = models.BooleanField(default=True)
    settings = models.BooleanField(default=True)
    control_sales = models.BooleanField(default=True)
    inventory_control = models.BooleanField(default=True)
    sales_analysis = models.BooleanField(default=True)
    add_product = models.BooleanField(default=True)
    add_sales = models.BooleanField(default=True)

    def __str__(self):
        return self.area_name


class Text_Message(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4(), unique=True, db_index=True)
    data = models.DateTimeField(null=True)
    title = models.CharField(max_length=100000, default='', null=True)
    text = models.CharField(max_length=100000, default='', null=True)
    enterprise = models.ForeignKey(
        Enterprise,
        related_name="Enterprise_Messages",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default='',
    )

    def __str__(self):
        return self.title

class Profile(models.Model):
    GENDER = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    name = models.CharField(max_length=1000)
    email = models.CharField(max_length=1000, default='')
    cpf = models.CharField(max_length=14, null=True, unique=True)
    picture = models.ImageField(null=True, upload_to='images/')
    gender = models.CharField(max_length=1000, null=True, choices=GENDER, default='')
    uuid = models.UUIDField(default=uuid.uuid4(), unique=True)
    enterprise = models.ForeignKey(
        Enterprise,
        related_name="employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=''
    )
    area = models.ForeignKey(
        Area,
        related_name="area",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=''
    )

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=1000, default='-----')
    picture = models.ImageField(null=True, upload_to='images/')
    inventory = models.IntegerField(null=True)
    inventory_minimal = models.IntegerField(null=True, default=0)
    price = models.FloatField(null=True, default=0)
    id = models.IntegerField(primary_key=True, unique=True, db_index=True)
    enterprise = models.ForeignKey(
        Enterprise,
        related_name="product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=''
    )

    def __str__(self):
        return self.name


class Sale(models.Model):
    data = models.DateTimeField()
    quantity = models.IntegerField(null=True)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4(), unique=True)
    product = models.ForeignKey(
        Product,
        related_name="product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=''
    )
    value = models.FloatField(null=True)
    enterprise = models.ForeignKey(
        Enterprise,
        related_name="sale",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=''
    )

    class Meta:
        verbose_name_plural = "Sales"

    def __str__(self):
        return str(self.uuid)


class ShoppingCar(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4(), unique=True)
    products = models.CharField(max_length=1000, default='-----------')
    data = models.DateTimeField(null=True)
    sales = models.ManyToManyField(Sale)
    enterprise = models.ForeignKey(
        Enterprise,
        related_name="marketconfirmenterprise",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default='',
    )
    profile = models.ForeignKey(
        Profile,
        related_name="profileconfirm",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default='',
    )

    def __str__(self):
        return str(f'{self.products}-{self.profile.name}')


class Sales_Made(models.Model):
    options = (
        ('Credit Cart', 'Credit Cart'),
        ('Debit Car', 'Debit Car'),
        ('Money', 'Money'),)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4(), unique=True, db_index=True)
    data = models.DateTimeField(null=True)
    product = models.ManyToManyField(Product)
    quantity = models.CharField(max_length=1000000, default='', null=True)
    total = models.FloatField(null=True, default=0)
    payment_method = models.CharField(choices=options, default='', null=True, max_length=1000)
    enterprise = models.ForeignKey(
        Enterprise,
        related_name="Sales_employees",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default='',
    )
    profile = models.ForeignKey(
        Profile,
        related_name="Sales",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default='',
    )


    def __str__(self):
        return str([self.profile.name, self.data])