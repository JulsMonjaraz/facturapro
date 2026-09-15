from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Cliente, Proyecto, Factura, ItemFactura


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'plan', 'is_staff', 'is_active')
    list_filter = ('plan', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'RFC', 'razon_social')
    
    # Añade los campos personalizados a los formularios del admin
    fieldsets = UserAdmin.fieldsets + (
        ('Datos fiscales', {
            'fields': ('RFC', 'razon_social', 'telefono', 'direccion', 'plan')
        }),
    )


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'propietario', 'email', 'RFC', 'activo', 'creado')
    list_filter = ('activo', 'creado')
    search_fields = ('nombre', 'email', 'RFC', 'razon_social')
    date_hierarchy = 'creado'
    readonly_fields = ('creado', 'actualizado')


class ItemFacturaInline(admin.TabularInline):
    """Permite editar items directamente dentro de la factura."""
    model = ItemFactura
    extra = 1
    fields = ('descripcion', 'cantidad', 'precio_unitario', 'porcentaje_impuesto')


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'cliente', 'propietario', 'fecha_emision', 'total', 'estado')
    list_filter = ('estado', 'fecha_emision', 'propietario')
    search_fields = ('numero', 'cliente__nombre')
    date_hierarchy = 'fecha_emision'
    readonly_fields = ('creado', 'actualizado')
    inlines = [ItemFacturaInline]


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cliente', 'propietario', 'estado', 'tarifa_hora', 'creado')
    list_filter = ('estado', 'creado')
    search_fields = ('nombre', 'cliente__nombre')
    readonly_fields = ('creado', 'actualizado')


@admin.register(ItemFactura)
class ItemFacturaAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'factura', 'cantidad', 'precio_unitario', 'porcentaje_impuesto')
    search_fields = ('descripcion', 'factura__numero')