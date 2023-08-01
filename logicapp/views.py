from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import ProfileForm, EnterpriseForm, PictureProfileForm, EditProfileForm,\
    EditEnterpriseForm, PictureEnterpriseForm, AreaForm, EditAreaForm, Employee, PasswordForm, ProductForm, PictureProductForm,\
    ProductEditForm, SalesForm, ShoppingCartForm, AddProductInventory, SaleDate
from django.core.exceptions import ValidationError
from .models import Profile, Enterprise, Area, CustomUser, Product, Sale, ShoppingCar, Sales_Made, Text_Message
from django.contrib.auth import login, logout
import datetime
import uuid
from django import forms
from pycpfcnpj import cpfcnpj
import json


class Home(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('logicapp:CreateProfile')
        return render(request, 'home.html')


method_decorator(login_required, name='dispatch')


class CreateProfile(View):
    def get(self, request, *args, **kwargs):
        profiles = request.user.profiles.all()
        context = {
            'profiles': profiles,

        }
        return render(request, 'createprofile.html', context)


method_decorator(login_required, name='dispatch')


class ListEnterprise(View):
    def get(self, request, profile_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprises = request.user.enterprise.all()
        context = {
            'profile': profile,
            'enterprises': enterprises

        }
        return render(request, 'listenterprise.html', context)



method_decorator(login_required, name='dispatch')


class ProfileCreate(View):
    def get(self, request, *args, **kwargs):
        area = Area.objects.filter(area_name='admin')
        if area:
            area = Area.objects.get(area_name='admin')
            preview_data = {
                'area': area,
            }
        else:
            area = Area(area_name='admin')
            area.save()

        preview_data = {
            'area': area,
        }
        form = ProfileForm(initial=preview_data)
        profiles = request.user.profiles.all()
        context = {
            'form': form,
            'profiles': profiles,

        }
        return render(request, 'profilecreate.html', context)

    def post(self, request, *args, **kwargs):
        area = Area.objects.get(area_name='admin')
        preview_data = {
            'area': area,
        }

        form = ProfileForm(request.POST or None, initial=preview_data)
        if form.is_valid():
            cpf = form.cleaned_data['cpf']
            if cpfcnpj.validate(cpf):
                profile = Profile.objects.create(**form.cleaned_data)
                if profile:
                    request.user.profiles.add(profile)
                    profile_id = profile.uuid
                    return redirect('logicapp:EnterpriseCreate', profile_id=profile_id)
            else:
                return redirect('logicapp:ProfileCreate')
        context = {
            'form': form,

        }
        return render(request, 'profilecreate.html', context)


method_decorator(login_required, name='dispatch')

class EnterpriseCreate(View):
    def get(self, request, profile_id, *args, **kwargs):
        try:
            profile = Profile.objects.get(uuid=profile_id)
            if profile in request.user.profiles.all():
                form = EnterpriseForm()
                context = {
                    'form': form,
                    'profile': profile,

                }
                return render(request, 'enterprisecreate.html', context)
        except Profile.DoesNotExist:
            return redirect('logicapp:ProfileCreate')

    def post(self, request, profile_id,  *args, **kwargs):
        form = EnterpriseForm(request.POST or None)
        profile = Profile.objects.get(uuid=profile_id)
        if form.is_valid():
            if cpfcnpj.validate(form.cleaned_data['enterprise']):
                enterprise = Enterprise.objects.create(**form.cleaned_data)
                if enterprise:
                    request.user.enterprise.add(enterprise)
                    profile.enterprise = enterprise
                    profile.save()
                    message = Text_Message(title=f'{enterprise.name} Created', data=datetime.datetime.now(), text=f'The enterprise {enterprise.name} was created', enterprise=enterprise)
                    message.save()
                    return redirect('logicapp:Home_Page', profile_id=profile_id, enterprise_id=enterprise.uuid)
                else:
                    return redirect('logicapp:EnterpriseCreate', profile_id=profile_id)
        context = {
            'form': form,
            'profile': profile,

        }
        return render(request, 'enterprisecreate.html', context)


method_decorator(login_required, name='dispatch')


class HomePage(View):
    def get(self, request, profile_id, enterprise_id, *args, **kwargs):
        try:
            profile = Profile.objects.get(uuid=profile_id)
            enterprise = Enterprise.objects.get(uuid=enterprise_id)
            try:
                data_list = []
                post_list = []
                shopping_cart = ShoppingCar.objects.get(profile=profile)
                posts = Text_Message.objects.filter(enterprise=enterprise)
                for post in posts:
                    data = str(post.data)
                    data = data[0:19]
                    data = data.replace('-', '')
                    data = data.replace(':', '')
                    data = data.replace(' ', '')
                    data = data.strip()
                    data_list.append(data)

                data_list = sorted(data_list, reverse=True)

                for data_l in data_list:
                    for post in posts:
                        data = str(post.data)
                        data = data[0:19]
                        data = data.replace('-', '')
                        data = data.replace(':', '')
                        data = data.replace(' ', '')
                        data = data.strip()
                        if data == data_l:
                            post_list.append(post)

                if profile.area.sales_analysis or profile.area.control_sales or profile.area.inventory_control or profile.area.add_product or profile.area.add_sales:
                    sale_ver = True
                else:
                    sale_ver = False
                if profile.area.add_employee or profile.area.control_employee or profile.area.area_add or profile.area.settings:
                    enterprise_ver = True
                else:
                    enterprise_ver = False

                if profile in request.user.profiles.all():
                    context = {
                        'profile': profile,
                        'enterprise': enterprise,
                        'shopping_cart': shopping_cart,
                        'posts': post_list,
                        'e_v': enterprise_ver,
                        's_v': sale_ver
                    }
                    return render(request, 'home.html', context)

            except ShoppingCar.DoesNotExist:
                shopping_cart = ShoppingCar(uuid=uuid.uuid4(), enterprise=enterprise, profile=profile, data=datetime.datetime.now(), products=f'{enterprise.name}')
                shopping_cart.save()
                if profile in request.user.profiles.all():
                    context = {
                        'profile': profile,
                        'enterprise': enterprise,
                        'shopping_cart': shopping_cart
                    }
                    return render(request, 'home.html', context)

        except Profile.DoesNotExist:
            return redirect('logicapp:EnterpriseCreate')


method_decorator(login_required, name='dispatch')


class EditProfile(View):
    def get(self, request, profile_id, enterprise_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        profile_picture = PictureProfileForm(instance=profile)
        edit_form = EditProfileForm(request.POST or None, instance=profile)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)

        context = {
            'profile': profile,
            'enterprise': enterprise,
            'profile_picture': profile_picture,
            'edit_form': edit_form,

        }
        return render(request, 'edit_profile.html', context)

    def post(self, request, profile_id, enterprise_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        profile_picture = PictureProfileForm(request.POST or None, request.FILES or None, instance=profile)
        edit_form = EditProfileForm(request.POST or None, request.FILES or None, instance=profile)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        if edit_form.is_valid() and profile_picture.is_valid():
            edit_form.save()
            profile_picture.save()
            return redirect('logicapp:Home_Page', profile_id=profile_id, enterprise_id=enterprise.uuid)
        context = {
            'profile': profile,
            'enterprise': enterprise,
            'profile_picture': profile_picture,
            'edit_form': edit_form,
        }
        return render(request, 'profilecreate.html', context)



method_decorator(login_required, name='dispatch')


class EditEnterprise(View):
    def get(self, request, profile_id, enterprise_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        enterprise_picture = PictureEnterpriseForm()
        edit_form = EditEnterpriseForm(request.POST or None, instance=enterprise)


        context = {
            'profile': profile,
            'enterprise': enterprise,
            'enterprise_picture': enterprise_picture,
            'edit_form': edit_form,

        }
        return render(request, 'edit_enterprise.html', context)

    def post(self, request, profile_id, enterprise_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        enterprise_picture = PictureEnterpriseForm(request.POST or None, request.FILES or None, instance=enterprise)
        edit_form = EditEnterpriseForm(request.POST or None, request.FILES or None, instance=enterprise)
        if edit_form.is_valid() and enterprise_picture.is_valid():
            edit_form.save()
            enterprise_picture.save()
            message = Text_Message(title=f'{enterprise.name} Edited', data=datetime.datetime.now(),
                                   text=f'The enterprise {enterprise.name} was edited', enterprise=enterprise, uuid=uuid.uuid4())
            message.save()
            return redirect('logicapp:Home_Page', profile_id=profile_id, enterprise_id=enterprise.uuid)
        context = {
            'profile': profile,
            'enterprise': enterprise,
            'profile_picture': enterprise_picture,
            'edit_form': edit_form,
        }
        return render(request, 'enterprisecreate.html', context)


method_decorator(login_required, name='dispatch')


class AddArea(View):
    def get(self, request, profile_id, enterprise_id,  *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        area_form = AreaForm(initial={'enterprise': enterprise})

        areas = Area.objects.all()
        context = {
            'profile': profile,
            'enterprise': enterprise,
            'area_form': area_form,
            'area_list': areas

        }
        return render(request, 'area_create.html', context)

    def post(self, request, profile_id, enterprise_id, *args, **kwargs):

        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)

        data_preview = {
            'enterprise': enterprise,
        }
        area_form = AreaForm(request.POST or None, initial={'enterprise': enterprise})
        if area_form.is_valid():
            message = Text_Message(title=f'{area_form.cleaned_data["area_name"]} Created', data=datetime.datetime.now(),
                                   text=f'The area {area_form.cleaned_data["area_name"]} was created', uuid=uuid.uuid4(),
                                   enterprise=enterprise)
            message.save()
            area_form.save()
            return redirect('logicapp:AreaCreate', profile_id=profile_id, enterprise_id=enterprise.uuid)
        context = {
            'profile': profile,
            'enterprise': enterprise,
            'area_form': area_form,
        }
        return render(request, 'area_create.html', context)


method_decorator(login_required, name='dispatch')


class EditArea(View):
    def get(self, request, profile_id, enterprise_id, area_id,  *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        area = Area.objects.get(id=area_id)
        area_form_edit = EditAreaForm(request.POST or None, instance=area)
        context = {
            'profile': profile,
            'enterprise': enterprise,
            'area_form': area_form_edit,
            'area': area

        }
        return render(request, 'edit_area.html', context)

    def post(self, request, profile_id, enterprise_id, area_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        area = Area.objects.get(id=area_id)
        area_form_edit = EditAreaForm(request.POST or None, instance=area)
        if area_form_edit.is_valid():
            message = Text_Message(title=f'{area_form_edit.cleaned_data["area_name"]} Edited',
                                   data=datetime.datetime.now(),
                                   text=f'The area {area_form_edit.cleaned_data["area_name"]} was Edited',
                                   enterprise=enterprise, uuid=uuid.uuid4())
            message.save()
            area_form_edit.save()
            return redirect('logicapp:AreaCreate', profile_id=profile_id, enterprise_id=enterprise.uuid)
        context = {
            'profile': profile,
            'enterprise': enterprise,
            'area_form': area_form_edit,
            'area': area
        }
        return render(request, 'edit_area.html', context)


method_decorator(login_required, name='dispatch')


class DeleteArea(View):
    def get(self, request, profile_id, enterprise_id, area_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        area = Area.objects.get(id=area_id)

        context = {
            'profile': profile,
            'enterprise': enterprise,
            'area': area
        }

        return render(request, 'delete_area.html', context)

    def post(self, request, profile_id, enterprise_id, area_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        area = Area.objects.get(id=area_id)
        context = {
            'profile': profile,
            'enterprise': enterprise,
            'area': area
        }
        message = Text_Message(title=f'{area.area_name} was Deleted', data=datetime.datetime.now(),
                               text=f'The area {area.area_name} was Deleted',
                               enterprise=enterprise, uuid=uuid.uuid4())
        message.save()
        area.delete()
        return redirect('logicapp:AreaCreate', profile_id=profile_id, enterprise_id=enterprise.uuid)


method_decorator(login_required, name='dispatch')


class AddEmployee(View):
    def get(self, request,  profile_id, enterprise_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        area = Area.objects.get(area_name='admin')
        preview_data = {
            'area': area,
        }
        area = Area.objects.all()
        form = Employee()
        profiles = request.user.profiles.all()
        context = {
            'form': form,
            'profile': profile,
            'profiles': profiles,
            'enterprise': enterprise,
            'area': area

        }
        return render(request, 'employeecreate.html', context)

    def post(self, request, profile_id, enterprise_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        area = Area.objects.get(area_name='admin')
        adm = request.user
        preview_data = {
            'area': area,
        }
        area = Area.objects.all()
        profiles = request.user.profiles.all()
        form = Employee(request.POST or None, initial=preview_data)
        context = {
            'form': form,
            'profile': profile,
            'profiles': profiles,
            'enterprise': enterprise,
            'area': area
        }
        try:
            if form.is_valid():
                user = CustomUser.objects.create_user(form['name'].value(), form['email'].value(), form['password'].value())
                user.save()
                logout(request)
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                profile = Profile.objects.create(name=form['name'].value(), email=form['email'].value(), cpf=form['cpf'].value(), area=Area.objects.get(id=form['area'].value()), enterprise=Enterprise.objects.get(uuid=enterprise_id), uuid=uuid.uuid4())
                message = Text_Message(title=f'{form["name"].value()} was hired', data=datetime.datetime.now(),
                                       text=f'The employee {form["name"].value()} was hired',
                                       enterprise=Enterprise.objects.get(uuid=enterprise_id), uuid=uuid.uuid4())
                message.save()
                request.user.profiles.add(profile)
                logout(request)
                login(request, adm, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('logicapp:Home_Page', profile_id=profile_id, enterprise_id=enterprise_id)
        except KeyError:
            return redirect('logicapp:Home_Page', profile_id=profile_id, enterprise_id=enterprise_id)
        return render(request, 'employeecreate.html', context)


method_decorator(login_required, name='dispatch')


class Employee_Control(View):
    def get(self, request, profile_id, enterprise_id,  *args, **kwargs):
        profiles = Profile.objects.all()
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        areas = Area.objects.all()

        area_list = []
        for c, area in enumerate(areas.values()):
            if area['area_name'] == 'admin':
                area_list.append({'area_name': area['area_name'], 'id': area['id'], 'enterprise_id': area['enterprise_id'], 'level': 9})
            else:
                cont = 0
                if area['control_employee']:
                    cont += 1
                if area['area_add']:
                    cont += 1
                if area['add_employee']:
                    cont += 1
                if area['settings']:
                    cont += 1
                if area['control_sales']:
                    cont += 1
                if area['inventory_control']:
                    cont += 1
                if area['sales_analysis']:
                    cont += 1
                if area['add_product']:
                    cont += 1
                if area['add_sales']:
                    cont += 1
                area_list.append({'area_name': area['area_name'], 'id': area['id'], 'enterprise_id': area['enterprise_id'], 'level': cont})


        area_list = sorted(area_list, key=lambda x: x['level'], reverse=True)


        context = {
            'current_profile': profile,
            'enterprise': enterprise,
            'profile_list': profiles,
            'area_list': area_list,
        }
        return render(request, 'employee_control.html', context)


method_decorator(login_required, name='dispatch')


class Employee_Edit(View):
    def get(self, request, profile_id, enterprise_id, employee_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        employee = Profile.objects.get(uuid=employee_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        area = Area.objects.all()

        edit_form = EditProfileForm(request.POST or None, instance=employee)

        context = {
            'profile': profile,
            'enterprise': enterprise,
            'employee': employee,
            'form': edit_form,
            'area': area

        }
        return render(request, 'employeeedit.html', context)

    def post(self, request, profile_id, enterprise_id, employee_id, *args, **kwargs):
        adm = request.user
        profile = Profile.objects.get(uuid=profile_id)
        employee = Profile.objects.get(uuid=employee_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        edit_form = EditProfileForm(request.POST or None, instance=employee)
        if edit_form.is_valid():
            employee.name = edit_form['name'].value()
            employee.email = edit_form['email'].value()
            employee.gender = edit_form['gender'].value()
            employee.area = Area.objects.get(id=edit_form['area'].value())
            message = Text_Message(title=f'{edit_form["name"].value()} was edited', data=datetime.datetime.now(),
                                   text=f'The area {edit_form["name"].value()} was edited',
                                   enterprise=enterprise, uuid=uuid.uuid4())
            message.save()
            employee.save()

            return redirect('logicapp:EmployeeControl', profile_id=profile.uuid, enterprise_id=enterprise.uuid)
        context = {
            'profile': profile,
            'enterprise': enterprise,
            'edit_form': edit_form,
            'employee': employee
        }
        return render(request, 'profilecreate.html', context)


method_decorator(login_required, name='dispatch')


class DeleteEmployee(View):
    def get(self, request, profile_id, enterprise_id,  employee_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        employee = Profile.objects.get(uuid=employee_id)

        context = {
            'profile': profile,
            'enterprise': enterprise,
            'employee': employee
        }

        employee_user = CustomUser.objects.get(profiles=employee)


        return render(request, 'delete_employee.html', context)

    def post(self, request, profile_id, enterprise_id, employee_id,  *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        employee = Profile.objects.get(uuid=employee_id)

        context = {
            'profile': profile,
            'enterprise': enterprise,
            'employee': employee
        }
        employee_user = CustomUser.objects.get(profiles=employee)

        message = Text_Message(title=f'{employee.name} has been fired', data=datetime.datetime.now(),
                               text=f'The employee {employee.name} has been fired',
                               enterprise=enterprise, uuid=uuid.uuid4())
        message.save()
        try:
            shopping_car = ShoppingCar.objects.get(profile=employee)
            shopping_car.delete()
        except ShoppingCar.DoesNotExist:
            pass

        employee.delete()
        employee_user.delete()
        return redirect('logicapp:Home_Page', profile_id=profile_id, enterprise_id=enterprise.uuid)


method_decorator(login_required, name='dispatch')


class AddProduct(View):
    def get(self, request, profile_id, enterprise_id,  *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        product_form = ProductForm(initial={'enterprise': enterprise})

        context = {
            'profile': profile,
            'enterprise': enterprise,
            'form': product_form

        }
        return render(request, 'product_create.html', context)

    def post(self, request, profile_id, enterprise_id, *args, **kwargs):

        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)

        data_preview = {
            'enterprise': enterprise,
        }
        product_form = ProductForm(request.POST or None, initial={'enterprise': enterprise})
        if product_form.is_valid():
            product = Product.objects.create(name=product_form.cleaned_data['name'], inventory=product_form.cleaned_data['inventory'],
                                             price=product_form.cleaned_data['price'], enterprise=enterprise, inventory_minimal=0)
            message = Text_Message(title=f'{product_form.cleaned_data["name"]} has been created', data=datetime.datetime.now(),
                                   text=f'The Product {product_form.cleaned_data["name"]} has been created',
                                   enterprise=enterprise, uuid=uuid.uuid4())
            message.save()
            return redirect('logicapp:InventoryControl', profile_id=profile_id, enterprise_id=enterprise.uuid)
        context = {
            'profile': profile,
            'enterprise': enterprise,
            'form': product_form,
        }
        return render(request, 'product_create.html', context)


method_decorator(login_required, name='dispatch')


class Inventory_Control(View):
    def get(self, request, profile_id, enterprise_id,  *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        prducts = Product.objects.all()

        context = {
            'profile': profile,
            'enterprise': enterprise,
            'product_list': prducts,
        }
        return render(request, 'inventory_control.html', context)


method_decorator(login_required, name='dispatch')


class Product_Picture(View):
    def get(self, request, profile_id, enterprise_id, product_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        product = Product.objects.get(id=product_id)
        form = PictureProductForm(instance=product)
        context = {
            'profile': profile,
            'enterprise': enterprise,
            'form': form,
            'product': product

        }
        return render(request, 'productpicture.html', context)

    def post(self, request, profile_id, enterprise_id, product_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        product = Product.objects.get(id=product_id)
        form = PictureProductForm(request.POST or None, request.FILES or None, instance=product)
        if form.is_valid():
            form.save()
            return redirect('logicapp:InventoryControl', profile_id=profile_id, enterprise_id=enterprise.uuid)

        context = {
            'profile': profile,
            'enterprise': enterprise,
            'form': form,
            'product': product

        }

        return render(request, 'productpicture.html', context)


method_decorator(login_required, name='dispatch')


class EditProduct(View):
    def get(self, request, profile_id, enterprise_id, product_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        product = Product.objects.get(id=product_id)
        form = ProductEditForm(instance=product)
        context = {
            'profile': profile,
            'enterprise': enterprise,
            'form': form,
            'product': product

        }
        return render(request, 'edit_product.html', context)

    def post(self, request, profile_id, enterprise_id, product_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        product = Product.objects.get(id=product_id)
        form = ProductEditForm(request.POST or None, instance=product)
        if form.is_valid():
            message = Text_Message(title=f'{form.cleaned_data["name"]} was edited',
                                   data=datetime.datetime.now(),
                                   text=f'The Product {form.cleaned_data["name"]} was edited',
                                   enterprise=enterprise, uuid= uuid.uuid4())
            message.save()
            form.save()
            return redirect('logicapp:InventoryControl', profile_id=profile_id, enterprise_id=enterprise.uuid)
        context = {
            'profile': profile,
            'enterprise': enterprise,
            'form': form,
            'product': product

        }
        return render(request, 'edit_product.html', context)


method_decorator(login_required, name='dispatch')


class AddInventory(View):
    def get(self, request, profile_id, enterprise_id, product_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        product = Product.objects.get(id=product_id)
        form = AddProductInventory()
        context = {
            'profile': profile,
            'enterprise': enterprise,
            'product': product,
            'form': form
        }

        return render(request, 'add_inventory.html', context)

    def post(self, request, profile_id, enterprise_id, product_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        product = Product.objects.get(id=product_id)
        form = AddProductInventory(request.POST or None)
        if form.is_valid() and form.cleaned_data['quantity'] > 0:
            product.inventory += form.cleaned_data['quantity']
            message = Text_Message(title=f'{product.name} Inventory',
                                   data=datetime.datetime.now(),
                                   text=f'The inventory of {product.name} was edited',
                                   enterprise=enterprise, uuid=uuid.uuid4())
            message.save()
            product.save()
        context = {
            'profile': profile,
            'enterprise': enterprise,
            'product': product,
            'form': form
        }
        return redirect('logicapp:InventoryControl', profile_id=profile_id, enterprise_id=enterprise.uuid)


method_decorator(login_required, name='dispatch')


class AddInventory_Minimal(View):
    def get(self, request, profile_id, enterprise_id, product_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        product = Product.objects.get(id=product_id)
        form = AddProductInventory()
        context = {
            'profile': profile,
            'enterprise': enterprise,
            'product': product,
            'form': form
        }

        return render(request, 'inventory_minimal.html', context)

    def post(self, request, profile_id, enterprise_id, product_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        product = Product.objects.get(id=product_id)
        form = AddProductInventory(request.POST or None)
        if form.is_valid() and form.cleaned_data['quantity'] > 0:
            product.inventory_minimal = form.cleaned_data['quantity']
            product.save()
        context = {
            'profile': profile,
            'enterprise': enterprise,
            'product': product,
            'form': form
        }
        return redirect('logicapp:InventoryControl', profile_id=profile_id, enterprise_id=enterprise.uuid)


method_decorator(login_required, name='dispatch')


class DeleteProduct(View):
    def get(self, request, profile_id, enterprise_id, product_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        product = Product.objects.get(id=product_id)

        context = {
            'profile': profile,
            'enterprise': enterprise,
            'product': product,
        }

        return render(request, 'delete_product.html', context)

    def post(self, request, profile_id, enterprise_id, product_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        product = Product.objects.get(id=product_id)
        context = {
            'profile': profile,
            'enterprise': enterprise,
            'product': product
        }
        message = Text_Message(title=f'{product.name} Deleted',
                               data=datetime.datetime.now(),
                               text=f'{product.name} was deleted',
                               enterprise=enterprise, uuid=uuid.uuid4())
        message.save()

        sales = Sales_Made.objects.filter(enterprise=enterprise)
        for sale in sales:
            for p in sale.product.all():
                if p.name == product.name:
                    sale.delete()

        product.delete()
        return redirect('logicapp:InventoryControl', profile_id=profile_id, enterprise_id=enterprise.uuid)


method_decorator(login_required, name='dispatch')


class AddSale(View):
    def get(self, request, profile_id, enterprise_id,  *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)

        preview = {
            'enterprise': enterprise,
            'data': datetime.datetime.now()
        }

        form = SalesForm(initial=preview)

        shoppingcar = ShoppingCar.objects.get(profile=profile)
        product = Product.objects.filter(enterprise=enterprise)

        context = {
            'profile': profile,
            'enterprise': enterprise,
            'form': form,
            'product_list': product,
            'shoppincar': shoppingcar
        }
        return render(request, 'salesadd.html', context)

    def post(self, request, profile_id, enterprise_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)

        preview = {
            'enterprise': enterprise,
            'data': datetime.datetime.now()
        }

        form = SalesForm(request.POST or None, initial=preview)
        product = Product.objects.all()
        if form.is_valid():
            product = Product.objects.get(id=form['product'].value())
            quantity = form.cleaned_data['quantity']
            if quantity > product.inventory or quantity <= 0:
                return redirect('logicapp:InventoryControl', profile_id=profile_id, enterprise_id=enterprise.uuid)
            else:
                sale = Sale.objects.create(data=form.cleaned_data['data'], quantity=form.cleaned_data['quantity'], enterprise=Enterprise.objects.get(uuid=enterprise_id), product=product, value=int(form.cleaned_data['quantity']) * product.price, uuid=uuid.uuid4())
                sale.save()
                shoppingcar = ShoppingCar.objects.get(profile=profile)
                shoppingcar.sales.add(sale)
                shoppingcar.save()
                return redirect('logicapp:ShoppingCart', profile_id=profile_id, enterprise_id=enterprise.uuid, shoppingcart_id=shoppingcar.uuid)

        context = {
            'profile': profile,
            'enterprise': enterprise,
            'form': form,
            'product_list': product,

        }
        return render(request, 'salesadd.html', context)


method_decorator(login_required, name='dispatch')


class DeleteSale(View):
    def get(self, request, profile_id, enterprise_id, sale_id,  *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        sale = Sale.objects.get(uuid=sale_id)
        sale.delete()
        shoppingcar = ShoppingCar.objects.get(profile=profile)
        return redirect('logicapp:ShoppingCart', profile_id=profile_id, enterprise_id=enterprise.uuid,
                        shoppingcart_id=shoppingcar.uuid)



method_decorator(login_required, name='dispatch')


class EditSale(View):
    def get(self, request, profile_id, enterprise_id, sale_id,  *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        sale = Sale.objects.get(uuid=sale_id)

        preview = {
            'enterprise': enterprise,
            'data': datetime.datetime.now()
        }

        form = SalesForm(initial=preview, instance=sale)

        shoppingcar = ShoppingCar.objects.get(profile=profile)
        product = Product.objects.filter(enterprise=enterprise)

        context = {
            'profile': profile,
            'enterprise': enterprise,
            'form': form,
            'product_list': product,
            'shoppincar': shoppingcar
        }
        return render(request, 'salesadd.html', context)

    def post(self, request, profile_id, enterprise_id, sale_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        sale = Sale.objects.get(uuid=sale_id)

        preview = {
            'enterprise': enterprise,
            'data': datetime.datetime.now()
        }

        form = SalesForm(request.POST or None, initial=preview)
        product = Product.objects.all()
        if form.is_valid():
            product = Product.objects.get(id=form['product'].value())
            quantity = form.cleaned_data['quantity']
            if quantity > product.inventory or quantity <= 0:
                return redirect('logicapp:InventoryControl', profile_id=profile_id, enterprise_id=enterprise.uuid)
            else:
                sale.product = form.cleaned_data['product']
                sale.quantity = form.cleaned_data['quantity']
                sale.save()
                shoppingcar = ShoppingCar.objects.get(products=enterprise.name)

                return redirect('logicapp:ShoppingCart', profile_id=profile_id, enterprise_id=enterprise.uuid, shoppingcart_id=shoppingcar.uuid)

        context = {
            'profile': profile,
            'enterprise': enterprise,
            'form': form,
            'product_list': product,

        }
        return render(request, 'salesadd.html', context)


method_decorator(login_required, name='dispatch')


class ShoppingCarConfirm(View):
    def get(self, request, profile_id, enterprise_id, shoppingcart_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        shopping_cart = ShoppingCar.objects.get(uuid=shoppingcart_id)
        form = ShoppingCartForm()
        product_list = []
        total_value = 0
        for sale in shopping_cart.sales.all():
            total = sale.product.price * sale.quantity
            product_list.append([sale.product, sale.quantity, total, sale.uuid])
        for product, quantity, total, sale_id in product_list:
            total_value += total
        context = {
            'form': form,
            'profile': profile,
            'enterprise': enterprise,
            'product_list': product_list,
            'total_value': total_value
        }
        return render(request, 'shopping_car.html', context)

    def post(self, request, profile_id, enterprise_id, shoppingcart_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        shopping_cart = ShoppingCar.objects.get(uuid=shoppingcart_id)
        form = ShoppingCartForm(request.POST or None)

        product_list = []
        produtos = list()

        total_value = 0
        for sale in shopping_cart.sales.all():
            total = sale.product.price * sale.quantity
            product_list.append([sale.product, sale.quantity, total])
            produtos.append(sale.product)
        for product, quantity, total in product_list:
            total_value += total

        final_list = []
        for c in product_list:
            final_list.append([c[0], c[1]])
        product_quantity = {}



        context = {
            'form': form,
            'profile': profile,
            'enterprise': enterprise,
            'product_list': product_list,
            'total_value': total_value
        }
        if form.is_valid():
            inventory_minimal = [[], False]
            for i in final_list:
                product_quantity[f'{i[0].id}'] = i[1]
            sale_made = Sales_Made(uuid=uuid.uuid4(), data=datetime.datetime.now(), quantity=str(product_quantity), total=total_value ,payment_method=form.cleaned_data['payment_method'],
                                   enterprise=Enterprise.objects.get(uuid=enterprise.uuid), profile=Profile.objects.get(uuid=profile_id))
            sale_made.save()
            for i in final_list:
                sale_made.product.add(i[0])
                i[0].inventory -= i[1]
                i[0].save()
                if i[0].inventory <= i[0].inventory_minimal:
                    inventory_minimal[1] = False
                    inventory_minimal[0].append(i[0])
            message = Text_Message(title=f'Sale Made',
                                   data=datetime.datetime.now(),
                                   text=f'{Profile.objects.get(uuid=profile_id)} sold R${"{:.2f}".format(total_value)}',
                                   enterprise=enterprise, uuid=uuid.uuid4())
            message.save()
            if inventory_minimal[1] == False:
                for product in inventory_minimal[0]:
                    message_inventory = Text_Message(title=f'Sale Inventory',
                                           data=datetime.datetime.now() + datetime.timedelta(minutes=5),
                                           text=f'{product} inventory is running out',
                                           enterprise=enterprise, uuid=uuid.uuid4())
                    message_inventory.save()
            sale_made.save()
            for sale in shopping_cart.sales.all():
                sale.delete()
            return redirect('logicapp:Home_Page', profile_id=profile_id, enterprise_id=enterprise.uuid)
        return render(request, 'shopping_car.html', context)




method_decorator(login_required, name='dispatch')


class Sales_Analysis_Month(View):
    def get(self, request, profile_id, enterprise_id, data_initial, data_final, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        products = Product.objects.filter(enterprise=enterprise)
        sales = Sales_Made.objects.filter(enterprise=enterprise)
        employees = Profile.objects.filter(enterprise=enterprise)

        sales_month = []
        sales_month_p = []

        for sale in sales:
            data = str(datetime.datetime.date(sale.data))
            if int(data_final.replace('-', '')) >= int(data.replace('-', '')) >= int(data_initial.replace('-', '')):
                sales_month.append(sale)
                sales_month_p.append(sale)

        list_quantity = []
        for sale in sales_month_p:

            list_sale = []
            sale.quantity = str(sale.quantity)
            sale.quantity = sale.quantity.replace("'", '')

            sale.quantity = sale.quantity.replace('{', '')

            sale.quantity = sale.quantity.replace('}', '')

            sale.quantity = sale.quantity.replace(' ', '')
            sale.quantity = sale.quantity.strip()
            sale.quantity = sale.quantity.split(',')
            for c, i in enumerate(sale.quantity):
                sale.quantity[c] = i.split(':')

            for id, quantity in sale.quantity:
                product_quantity = {}
                id = int(float(id))
                quantity = int(float(quantity))
                product_quantity['sale'] = sale
                product_quantity['product'] = Product.objects.get(id=id)
                product_quantity['quantity'] = quantity
                list_sale.append(product_quantity.copy())
            list_quantity.append(list_sale.copy())
            list_sale.clear()

        print(list_quantity)

        product_sales = {}
        employee_sales = {}
        product_quantity_test = []

        for product in products:
            product_sales[f'{product.name}'] = 0

        for employee in employees:
            if employee.area.add_sales:
                employee_sales[f'{employee.name}'] = 0

        for sale in sales_month:
            for employee in employees:
                if employee.name == sale.profile.name and employee.area.add_sales:
                    employee_sales[f'{employee.name}'] += 1

        for sale in sales_month:
            for c in list_quantity:
                for i in c:
                    if i['sale'] == sale:
                        for product in products:
                            if i['product'] == product:
                                product_sales[f'{product.name}'] += i['quantity']
        employee_sales = sorted(employee_sales.items(), key=lambda x:x[1], reverse=True)
        employee_sales = dict(employee_sales)

        product_sales = sorted(product_sales.items(),  key=lambda x:x[1], reverse=True)
        product_sales = dict(product_sales)

        products_total = {}
        employee_total = {}

        for p, c in product_sales.items():
            for product in products:
                if p == product.name:
                    products_total[f'{product.name}'] = c * float(product.price)

        for p, c in employee_sales.items():
            employee_total[f'{p}'] = 0

        for p, c in employee_sales.items():
            for sale in sales_month:
                if p == sale.profile.name:
                    employee_total[f'{sale.profile.name}'] += sale.total


        product_list = list(product_sales.keys())

        employee_list = list(employee_sales.keys())

        employee_more_sale = employee_list[0]
        employee_less_sale = employee_list[-1]
        product_less_sold = product_list[-1]
        product_most_sold = product_list[0]

        form = SaleDate(initial={'data_initial': data_initial, 'data_final': data_final})

        context = {
            'profile': profile,
            'enterprise': enterprise,
            'sales': sales_month,
            'products': products,
            'product_sales': product_sales,
            'employee_sales': employee_sales,
            'most_sold': product_most_sold,
            'less_sold': product_less_sold,
            'more_sales': employee_more_sale,
            'less_sales': employee_less_sale,
            'employee_total': employee_total,
            'products_total': products_total,
            'form': form,
            'list_quantity': list_quantity,
            'data_initial': data_initial,
            'data_final': data_final
        }
        return render(request, 'Sales_Analysis.html', context)

    def post(self, request, profile_id, enterprise_id, data_initial, data_final, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        products = Product.objects.filter(enterprise=enterprise)
        sales = Sales_Made.objects.filter(enterprise=enterprise)
        employees = Profile.objects.filter(enterprise=enterprise)




        sales_month = []
        sales_month_p = []

        for sale in sales:
            data = str(datetime.datetime.date(sale.data))
            if int(data_final.replace('-', '')) >= int(data.replace('-', '')) >= int(data_initial.replace('-', '')):
                sales_month.append(sale)
                sales_month_p.append(sale)


        product_sales = {}
        employee_sales = {}
        list_quantity = []



        for sale in sales_month_p:

            list_sale = []
            sale.quantity = str(sale.quantity)
            sale.quantity = sale.quantity.replace("'", '')

            sale.quantity = sale.quantity.replace('{', '')

            sale.quantity = sale.quantity.replace('}', '')

            sale.quantity = sale.quantity.replace(' ', '')
            sale.quantity = sale.quantity.strip()
            sale.quantity = sale.quantity.split(',')
            for c, i in enumerate(sale.quantity):
                sale.quantity[c] = i.split(':')

            for id, quantity in sale.quantity:
                product_quantity = {}
                id = int(float(id))
                quantity = int(float(quantity))
                product_quantity['sale'] = sale
                product_quantity['product'] = Product.objects.get(id=id)
                product_quantity['quantity'] = quantity
                list_sale.append(product_quantity.copy())
            list_quantity.append(list_sale.copy())
            list_sale.clear()

        for product in products:
            product_sales[f'{product.name}'] = 0

        for employee in employees:
            if employee.area.add_sales:
                employee_sales[f'{employee.name}'] = 0

        for sale in sales:
            for employee in employees:
                if employee.name == sale.profile.name and employee.area.add_sales:
                    employee_sales[f'{employee.name}'] += 1

        for sale in sales:
            for c in list_quantity:
                for i in c:
                    if i['sale'] == sale:
                        for product in products:
                            if i['product'] == product:
                                product_sales[f'{product.name}'] += i['quantity']

        employee_sales = sorted(employee_sales.items(), key=lambda x:x[1], reverse=True)
        employee_sales = dict(employee_sales)

        product_sales = sorted(product_sales.items(),  key=lambda x:x[1], reverse=True)
        product_sales = dict(product_sales)

        products_total = {}
        employee_total = {}

        for p, c in product_sales.items():
            for product in products:
                if p == product.name:
                    products_total[f'{product.name}'] = c * float(product.price)

        for p, c in employee_sales.items():
            employee_total[f'{p}'] = 0

        for p, c in employee_sales.items():
            for sale in sales:
                if p == sale.profile.name:
                    employee_total[f'{sale.profile.name}'] += sale.total


        product_list = list(product_sales.keys())

        employee_list = list(employee_sales.keys())

        employee_more_sale = employee_list[0]
        employee_less_sale = employee_list[-1]
        product_less_sold = product_list[-1]
        product_most_sold = product_list[0]

        form = SaleDate(request.POST or None)
        if form.is_valid():
            if form.cleaned_data['data_initial'] and form.cleaned_data['data_final']:
                data_initial = str(form.cleaned_data['data_initial'])
                data_final = str(form.cleaned_data['data_final'])
                return redirect('logicapp:SalesAnalysisMonth', profile_id=profile_id, enterprise_id=enterprise.uuid,
                                data_initial=data_initial, data_final=data_final)

        context = {
            'profile': profile,
            'enterprise': enterprise,
            'sales': sales,
            'products': products,
            'product_sales': product_sales,
            'employee_sales': employee_sales,
            'most_sold': product_most_sold,
            'less_sold': product_less_sold,
            'more_sales': employee_more_sale,
            'less_sales': employee_less_sale,
            'employee_total': employee_total,
            'products_total': products_total,
            'form': form,
            'list_quantity': list_quantity,
        }
        return render(request, 'Sales_Analysis.html', context)





method_decorator(login_required, name='dispatch')


class Sales_Analysis(View):
    def get(self, request, profile_id, enterprise_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        products = Product.objects.filter(enterprise=enterprise)
        sales = Sales_Made.objects.filter(enterprise=enterprise)
        sales_p = Sales_Made.objects.filter(enterprise=enterprise)
        employees = Profile.objects.filter(enterprise=enterprise)

        list_quantity = []
        for sale in sales_p:
            print(sale.quantity)
            list_sale = []
            sale.quantity = str(sale.quantity)
            sale.quantity = sale.quantity.replace('{', '')
            sale.quantity = sale.quantity.replace('}', '')
            sale.quantity = sale.quantity.replace("'", '')
            sale.quantity = sale.quantity.replace(' ', '')
            sale.quantity = sale.quantity.strip()
            sale.quantity = sale.quantity.split(',')
            print(sale.quantity)
            for c, i in enumerate(sale.quantity):
                sale.quantity[c] = i.split(':')
            print(sale.quantity)
            for id, quantity in sale.quantity:
                print(id, '-----', quantity)
                product_quantity = {}
                id = int(float(id))
                quantity = int(quantity)
                product_quantity['sale'] = sale
                product_quantity['product'] = Product.objects.get(id=id)
                product_quantity['quantity'] = quantity
                list_sale.append(product_quantity.copy())
            list_quantity.append(list_sale.copy())
            list_sale.clear()


        product_sales = {}
        employee_sales = {}
        for product in products:
            product_sales[f'{product.name}'] = 0

        for employee in employees:
            if employee.area.add_sales:
                employee_sales[f'{employee.name}'] = 0

        for sale in sales:
            for employee in employees:
                if employee.name == sale.profile.name and employee.area.add_sales:
                    employee_sales[f'{employee.name}'] += 1

        for sale in sales:
            for c in list_quantity:
                for i in c:
                    if i['sale'] == sale:
                        for product in products:
                            if i['product'] == product:
                                product_sales[f'{product.name}'] += i['quantity']
        employee_sales = sorted(employee_sales.items(), key=lambda x:x[1], reverse=True)
        employee_sales = dict(employee_sales)

        product_sales = sorted(product_sales.items(),  key=lambda x:x[1], reverse=True)
        product_sales = dict(product_sales)

        products_total = {}
        employee_total = {}

        for p, c in product_sales.items():
            for product in products:
                if p == product.name:
                    products_total[f'{product.name}'] = c * float(product.price)

        for p, c in employee_sales.items():
            employee_total[f'{p}'] = 0

        for p, c in employee_sales.items():
            for sale in sales:
                if p == sale.profile.name:
                    employee_total[f'{sale.profile.name}'] += sale.total


        product_list = list(product_sales.keys())

        employee_list = list(employee_sales.keys())

        employee_more_sale = employee_list[0]
        employee_less_sale = employee_list[-1]
        product_less_sold = product_list[-1]
        product_most_sold = product_list[0]


        form = SaleDate()

        context = {
            'profile': profile,
            'enterprise': enterprise,
            'sales': sales,
            'products': products,
            'product_sales': product_sales,
            'employee_sales': employee_sales,
            'most_sold': product_most_sold,
            'less_sold': product_less_sold,
            'more_sales': employee_more_sale,
            'less_sales': employee_less_sale,
            'employee_total': employee_total,
            'products_total': products_total,
            'form': form,
            'list_quantity': list_quantity,
        }
        return render(request, 'Sales_Analysis.html', context)

    def post(self, request, profile_id, enterprise_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        products = Product.objects.filter(enterprise=enterprise)
        sales = Sales_Made.objects.filter(enterprise=enterprise)
        sales_p = Sales_Made.objects.filter(enterprise=enterprise)
        employees = Profile.objects.filter(enterprise=enterprise)

        product_sales = {}
        employee_sales = {}

        for product in products:
            product_sales[f'{product.name}'] = 0

        for employee in employees:
            if employee.area.add_sales:
                employee_sales[f'{employee.name}'] = 0

        for sale in sales:
            for employee in employees:
                if employee.name == sale.profile.name and employee.area.add_sales:
                    employee_sales[f'{employee.name}'] += 1

        list_quantity = []
        for sale in sales_p:

            list_sale = []
            sale.quantity = str(sale.quantity)
            sale.quantity = sale.quantity.replace("'", '')

            sale.quantity = sale.quantity.replace('{', '')

            sale.quantity = sale.quantity.replace('}', '')

            sale.quantity = sale.quantity.replace(' ', '')
            sale.quantity = sale.quantity.strip()
            sale.quantity = sale.quantity.split(',')
            for c, i in enumerate(sale.quantity):
                sale.quantity[c] = i.split(':')
            print(sale.quantity)
            # for id, quantity in sale.quantity:
            #     product_quantity = {}
            #     id = int(float(id))
            #     quantity = int(float(quantity))
            #     product_quantity['sale'] = sale
            #     product_quantity['product'] = Product.objects.get(id=id)
            #     product_quantity['quantity'] = quantity
            #     list_sale.append(product_quantity.copy())
            # list_quantity.append(list_sale.copy())
            # list_sale.clear()

        for sale in sales:
            for c in list_quantity:
                for i in c:
                    if i['sale'] == sale:
                        for product in products:
                            if i['product'] == product:
                                product_sales[f'{product.name}'] += i['quantity']

        employee_sales = sorted(employee_sales.items(), key=lambda x:x[1], reverse=True)
        employee_sales = dict(employee_sales)

        product_sales = sorted(product_sales.items(),  key=lambda x:x[1], reverse=True)
        product_sales = dict(product_sales)

        products_total = {}
        employee_total = {}

        for p, c in product_sales.items():
            for product in products:
                if p == product.name:
                    products_total[f'{product.name}'] = c * float(product.price)

        for p, c in employee_sales.items():
            employee_total[f'{p}'] = 0

        for p, c in employee_sales.items():
            for sale in sales:
                if p == sale.profile.name:
                    employee_total[f'{sale.profile.name}'] += sale.total


        product_list = list(product_sales.keys())

        employee_list = list(employee_sales.keys())

        employee_more_sale = employee_list[0]
        employee_less_sale = employee_list[-1]
        product_less_sold = product_list[-1]
        product_most_sold = product_list[0]

        form = SaleDate(request.POST or None)
        if form.is_valid():
            if form.cleaned_data['data_initial'] and form.cleaned_data['data_final']:
                data_initial = str(form.cleaned_data['data_initial'])
                data_final = str(form.cleaned_data['data_final'])
                return redirect('logicapp:SalesAnalysisMonth', profile_id=profile_id, enterprise_id=enterprise.uuid, data_initial=data_initial, data_final=data_final)

        context = {
            'profile': profile,
            'enterprise': enterprise,
            'sales': sales,
            'products': products,
            'product_sales': product_sales,
            'employee_sales': employee_sales,
            'most_sold': product_most_sold,
            'less_sold': product_less_sold,
            'more_sales': employee_more_sale,
            'less_sales': employee_less_sale,
            'employee_total': employee_total,
            'products_total': products_total,
            'form': form,
            'list_quantity': list_quantity,
        }
        return render(request, 'Sales_Analysis.html', context)


method_decorator(login_required, name='dispatch')


class Sales_Profile(View):
    def get(self, request, profile_id, enterprise_id, employee_id,  *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        employee = Profile.objects.get(uuid=employee_id)

        sales = Sales_Made.objects.filter(enterprise=enterprise, profile=employee)
        list_quantity = []
        for sale in sales:

            list_sale = []
            sale.quantity = str(sale.quantity)
            sale.quantity = sale.quantity.replace("'", '')

            sale.quantity = sale.quantity.replace('{', '')

            sale.quantity = sale.quantity.replace('}', '')

            sale.quantity = sale.quantity.replace(' ', '')
            sale.quantity = sale.quantity.strip()
            sale.quantity = sale.quantity.split(',')
            for c, i in enumerate(sale.quantity):
                sale.quantity[c] = i.split(':')

            for id, quantity in sale.quantity:
                product_quantity = {}
                id = int(float(id))
                quantity = int(float(quantity))
                product_quantity['sale'] = sale
                product_quantity['product'] = Product.objects.get(id=id)
                product_quantity['quantity'] = quantity
                list_sale.append(product_quantity.copy())
            list_quantity.append(list_sale.copy())
            list_sale.clear()



        context = {
            'profile': profile,
            'enterprise': enterprise,
            'sales': sales,
            'list_quantity': list_quantity,
            'employee': employee
        }
        return render(request, 'employeeSales.html', context)


method_decorator(login_required, name='dispatch')


class Sales_Control(View):
    def get(self, request, profile_id, enterprise_id,  *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        sales = Sales_Made.objects.filter(enterprise=enterprise)
        list_quantity = []
        for sale in sales:

            list_sale = []
            sale.quantity = str(sale.quantity)
            sale.quantity = sale.quantity.replace("'", '')

            sale.quantity = sale.quantity.replace('{', '')

            sale.quantity = sale.quantity.replace('}', '')

            sale.quantity = sale.quantity.replace(' ', '')
            sale.quantity = sale.quantity.strip()
            sale.quantity = sale.quantity.split(',')
            print(sale.quantity)
            for c, i in enumerate(sale.quantity):
                sale.quantity[c] = i.split(':')

            for id, quantity in sale.quantity:
                 product_quantity = {}
                 id = int(float(id))
                 quantity = int(float(quantity))
                 product_quantity['sale'] = sale
                 product_quantity['product'] = Product.objects.get(id=id)
                 product_quantity['quantity'] = quantity
                 list_sale.append(product_quantity.copy())
            list_quantity.append(list_sale.copy())
            list_sale.clear()


        context = {
            'profile': profile,
            'enterprise': enterprise,
            'sales': sales,
            'list_quantity': list_quantity,
        }
        return render(request, 'sales_control.html', context)


method_decorator(login_required, name='dispatch')


class Change_Password(View):
    def get(self, request, profile_id, enterprise_id, employee_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        employee = Profile.objects.get(uuid=employee_id)
        adm = request.user
        form = PasswordForm()
        context = {
            'profile': profile,
            'enterprise': enterprise,
            'employee': employee,
            'form': form
        }
        return render(request, 'change_password.html', context)

    def post(self, request, profile_id, enterprise_id, employee_id, *args, **kwargs):
        profile = Profile.objects.get(uuid=profile_id)
        enterprise = Enterprise.objects.get(uuid=enterprise_id)
        employee = Profile.objects.get(uuid=employee_id)
        adm = request.user
        form = PasswordForm(request.POST or None)
        if form.is_valid():
            user = CustomUser.objects.get(profiles=employee)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('logicapp:Home_Page', profile_id=profile_id, enterprise_id=enterprise.uuid)
        context = {
            'profile': profile,
            'enterprise': enterprise,
            'employee': employee,
            'form': form
        }
        return render(request, 'change_password.html', context)

class Index(View):
    def get(self, request, *args, **kwargs):
        try:
            profile = ''
            enterprise = ''
            if request.user.profiles:
                for p in request.user.profiles.all():
                    profile = p
                    context = {
                        'profile': profile,

                    }
                if profile.enterprise:
                    return redirect('logicapp:Home_Page', profile_id=profile.uuid, enterprise_id=profile.enterprise.uuid)

            else:
                pass
        except AttributeError:
            context = {}
            pass
        return render(request, 'index.html', context)