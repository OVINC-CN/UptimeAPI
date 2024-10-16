from django.contrib import admin
from django.utils.translation import gettext_lazy


class NicknameMixinAdmin:
    @admin.display(description=gettext_lazy("Updated By"))
    def updated_by_username(self, inst) -> str:
        return f"{inst.updated_by.nick_name}({inst.updated_by.username})"

    @admin.display(description=gettext_lazy("Created By"))
    def created_by_username(self, inst) -> str:
        return f"{inst.created_by.nick_name}({inst.created_by.username})"
