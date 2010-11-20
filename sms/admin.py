from django.contrib import admin
from sms.models import LargeAccount, Prefix, ServiceProviderData

class LargeAccountAdmin(admin.ModelAdmin):
    pass

class PrefixAdmin(admin.ModelAdmin):
    pass

class ServiceProviderDataAdmin(admin.ModelAdmin):
    pass

admin.site.register(LargeAccount, LargeAccountAdmin)
admin.site.register(ServiceProviderData, ServiceProviderDataAdmin)
admin.site.register(Prefix, PrefixAdmin)

