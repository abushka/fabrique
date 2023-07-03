from django.contrib import admin

from apps.clients.models import Tag, Client, Operator


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    filter_horizontal = ('tags',)
    list_display = ('phone', 'operator_code', 'time_zone')
    search_fields = ('phone',)
    list_filter = ('operator_code', 'tags', 'time_zone')

    readonly_fields = ('operator_code',)

    class Meta:
        model = Client


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'name': ('name',)}

    class Meta:
        model = Tag


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):

    class Meta:
        model = Operator
