from django.contrib import admin
from . models import Test, Position

# Register your models here.
admin.site.register(Test)
@admin.register(Position)
class AdminPosition(admin.ModelAdmin):
    list_display =['id','name','price','rank','market_cap']