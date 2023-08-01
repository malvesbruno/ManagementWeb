from django.contrib import admin
from logicapp.models import Profile, Enterprise, Area, CustomUser, Product, Sale, ShoppingCar, Sales_Made, Text_Message

# Register your models here.
admin.site.register(Profile)
admin.site.register(Enterprise)
admin.site.register(Area)
admin.site.register(Product)
admin.site.register(CustomUser)
admin.site.register(Sale)
admin.site.register(ShoppingCar)
admin.site.register(Sales_Made)
admin.site.register(Text_Message)