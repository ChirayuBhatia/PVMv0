from django.contrib import admin
from .models import File, Wallet


# Register your models here.
@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('user', 'Subject', 'fid', 'count', 'Printed')


admin.site.register(Wallet)
