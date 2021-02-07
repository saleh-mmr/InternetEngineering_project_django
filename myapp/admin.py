from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

admin.site.register(MyUser, UserAdmin)
admin.site.register(Trip)
admin.site.register(Participant)
admin.site.register(Transaction)
admin.site.register(Table)
admin.site.register(Bedehkar)
admin.site.register(Bestankar)
