from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()  # this is your CustomUser model
admin.site.unregister(User)
