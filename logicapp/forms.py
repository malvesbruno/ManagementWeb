from django.forms import ModelForm
from .models import Profile, Enterprise, Area, Product, Sale
from django import forms
import  datetime
from pycpfcnpj import cpfcnpj


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        exclude = ['uuid', 'enterprise', 'picture', 'cpf']
    cpf = forms.CharField(max_length=14)

    def clean_cpf(self):
        cpf = self.cleaned_data['cpf']
        if cpfcnpj.validate(cpf):
            profiles = Profile.objects.filter(cpf=cpf)
            if profiles:
                raise forms.ValidationError('This CPF HAS ALREADY BEEN USED')
            else:
                return cpf
        else:
            raise forms.ValidationError('Invalid CPF!!')


class Employee(ModelForm):
    class Meta:
        model = Profile
        exclude = ['uuid', 'enterprise', 'picture', 'area', 'cpf']
    password = forms.CharField(widget=forms.PasswordInput())
    area = forms.ChoiceField()
    cpf = forms.CharField(max_length=14)

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 8:
            raise forms.ValidationError('Invalid Password!!')
        else:
            return password

    def clean_cpf(self):
        cpf = self.cleaned_data['cpf']
        if cpfcnpj.validate(cpf):
            profiles = Profile.objects.filter(cpf=cpf)
            if profiles:
                raise forms.ValidationError('This CPF HAS ALREADY BEEN USED')
            else:
                return cpf
        else:
            raise forms.ValidationError('Invalid CPF!!')




class PasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 8:
            raise forms.ValidationError('Invalid Password!!')
        else:
            return password

class EnterpriseForm(ModelForm):
    class Meta:
        model = Enterprise
        exclude = ['uuid', 'picture', 'enterprise']
    enterprise = forms.CharField(max_length=14)

    def clean_enterprise(self):
        cnpj = self.cleaned_data['enterprise']
        if cpfcnpj.validate(cnpj):
            cnpjs = Enterprise.objects.filter(enterprise=cnpj)
            if cnpjs:
                raise forms.ValidationError('This CNPJ HAS ALREADY BEEN USED!!')
            else:
                return cnpj
        else:
            raise forms.ValidationError('Invalid CNPJ!!')


class AreaForm(ModelForm):
    class Meta:
        model = Area
        exclude = ['id', ]


class ProductForm(ModelForm):
    class Meta:
        model = Product
        exclude = ['id', 'picture', 'inventory_minimal', 'price', ]
    price = forms.FloatField()
    name = forms.CharField(max_length=1000)

    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) > 0:
            return name
        else:
            raise forms.ValidationError('Name Invalid!!')

    def clean_price(self):
        price = self.cleaned_data['price']
        if price < 0:
            raise forms.ValidationError('Price must be a positive number or Zero')
        else:
            return price

class EditAreaForm(ModelForm):
    class Meta:
        model = Area
        exclude = ['id', 'enterprise', ]

class PictureProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('picture', )

class PictureProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ('picture', )


class ProductEditForm(ModelForm):
    class Meta:
        model = Product
        fields = ('name', 'inventory', 'price')


class AddProductInventory(forms.Form):
    quantity = forms.IntegerField()


class SaleDate(forms.Form):
    data_initial = forms.DateField()
    data_final = forms.DateField()


class SalesForm(ModelForm):
    class Meta:
        model = Sale
        fields = ('quantity', 'product', 'enterprise', 'data')


class ShoppingCartForm(forms.Form):
    options = (
        ('Credit Cart', 'Credit Cart'),
        ('Debit Car', 'Debit Car'),
        ('Money', 'Money'),)
    payment_method = forms.ChoiceField(choices=options)


class EditProfileForm(ModelForm):
    class Meta:
        model = Profile
        exclude = ['uuid', 'picture', 'cpf']


class PictureEnterpriseForm(ModelForm):
    class Meta:
        model = Enterprise
        fields = ('picture', )


class EditEnterpriseForm(ModelForm):
    class Meta:
        model = Enterprise
        exclude = ['uuid', 'picture', 'enterprise']


