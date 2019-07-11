from django.contrib import admin

# Register your models here.
from Crm.models import *
from django.contrib.auth.admin import UserAdmin


admin.site.register(UserInfo, UserAdmin)
admin.site.register(Campuses)
admin.site.register(ClassList)
admin.site.register(Customer)
admin.site.register(Department)
