from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import SignUpForm
from .models import Account


class AccountAdmin(UserAdmin):
    add_form = SignUpForm

    list_display = (
        "full_name",
        "email",
        "date_joined",
        "last_login",
        "is_admin",
        "is_staff",
    )
    search_fields = (
        "full_name",
        "email",
    )
    ordering = (
        "full_name",
        "email",
    )

    readonly_fields = ("id", "date_joined", "last_login")

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Account, AccountAdmin)
