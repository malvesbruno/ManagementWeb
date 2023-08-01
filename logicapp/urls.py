from django.urls import path
from .views import Home, CreateProfile, Index, ProfileCreate, EnterpriseCreate, HomePage, EditProfile,\
    EditEnterprise, AddArea, EditArea, DeleteArea, AddEmployee, ListEnterprise, Employee_Control, \
    Employee_Edit, DeleteEmployee, AddProduct, Inventory_Control, Product_Picture, EditProduct, DeleteProduct, AddSale, ShoppingCarConfirm,\
    EditSale, DeleteSale, Sales_Control, AddInventory, Sales_Profile, Sales_Analysis, Sales_Analysis_Month, AddInventory_Minimal, Change_Password
from django.conf import settings
from django.conf.urls.static import static

app_name = 'logicapp'

urlpatterns = [
    path('', Index.as_view(), name='Index'),
    path('home', Home.as_view(), name='Home'),
    path('profiles', CreateProfile.as_view(), name='CreateProfile'),
    path('profiles/create', ProfileCreate.as_view(), name='ProfileCreate'),
    path('<str:profile_id>/enterprises', ListEnterprise.as_view(), name='EnterpriseList'),
    path('<str:profile_id>/enterprise/create', EnterpriseCreate.as_view(), name='EnterpriseCreate'),
    path('<str:profile_id>/<str:enterprise_id>/home', HomePage.as_view(), name='Home_Page'),
    path('<str:profile_id>/<str:enterprise_id>/edit/profile', EditProfile.as_view(), name='EditProfile'),
    path('<str:profile_id>/<str:enterprise_id>/edit/enterprise', EditEnterprise.as_view(), name='EditEnterprise'),
    path('<str:profile_id>/<str:enterprise_id>/area/create', AddArea.as_view(), name='AreaCreate'),
    path('<str:profile_id>/<str:enterprise_id>/sale/create', AddSale.as_view(), name='SaleCreate'),
    path('<str:profile_id>/<str:enterprise_id>/sale/<str:sale_id>/edit', EditSale.as_view(), name='SaleEdit'),
    path('<str:profile_id>/<str:enterprise_id>/sale/<str:sale_id>/delete', DeleteSale.as_view(), name='SaleDelete'),
    path('<str:profile_id>/<str:enterprise_id>/product/create', AddProduct.as_view(), name='AreaProduct'),
    path('<str:profile_id>/<str:enterprise_id>/employee/create', AddEmployee.as_view(), name='EmployeeCreate'),
    path('<str:profile_id>/<str:enterprise_id>/employee/control', Employee_Control.as_view(), name='EmployeeControl'),
    path('<str:profile_id>/<str:enterprise_id>/inventory', Inventory_Control.as_view(), name='InventoryControl'),
    path('<str:profile_id>/<str:enterprise_id>/product/<str:product_id>/add_inventory', AddInventory.as_view(), name='InventoryAdd'),
path('<str:profile_id>/<str:enterprise_id>/product/<str:product_id>/inventory_minimal', AddInventory_Minimal.as_view(), name='InventoryMinimal'),
    path('<str:profile_id>/<str:enterprise_id>/sales_control', Sales_Control.as_view(), name='SalesControl'),
    path('<str:profile_id>/<str:enterprise_id>/sales_analysis', Sales_Analysis.as_view(), name='SalesAnalysis'),
    path('<str:profile_id>/<str:enterprise_id>/sales_analysis/<str:data_initial>/<str:data_final>', Sales_Analysis_Month.as_view(), name='SalesAnalysisMonth'),
    path('<str:profile_id>/<str:enterprise_id>/<str:employee_id>/sales', Sales_Profile.as_view(), name='SalesProfile'),
    path('<str:profile_id>/<str:enterprise_id>/<shoppingcart_id>/shopping_cart', ShoppingCarConfirm.as_view(), name='ShoppingCart'),
    path('<str:profile_id>/<str:enterprise_id>/product/<str:product_id>/picture', Product_Picture.as_view(), name='ProductPicture'),
    path('<str:profile_id>/<str:enterprise_id>/product/<str:product_id>/edit', EditProduct.as_view(), name='ProductEdit'),
    path('<str:profile_id>/<str:enterprise_id>/employee/edit/<str:employee_id>', Employee_Edit.as_view(), name='EmployeeEdit'),
    path('<str:profile_id>/<str:enterprise_id>/password/edit/<str:employee_id>', Change_Password.as_view(), name='PasswordId'),
    path('<str:profile_id>/<str:enterprise_id>/area/edit/<str:area_id>', EditArea.as_view(), name='AreaEdit'),
    path('<str:profile_id>/<str:enterprise_id>/employee/delete/<str:employee_id>', DeleteEmployee.as_view(), name='EmployeeDelete'),
    path('<str:profile_id>/<str:enterprise_id>/product/delete/<str:product_id>', DeleteProduct.as_view(), name='ProductDelete'),
    path('<str:profile_id>/<str:enterprise_id>/area/delete/<str:area_id>', DeleteArea.as_view(), name='AreaDelete'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)