from django.contrib import admin
from .models import User, OTPVerification

admin.site.register(User)
admin.site.register(OTPVerification)
