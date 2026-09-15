from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Cliente, Proyecto, Factura, ItemFactura

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer para el usuario (datos públicos)."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'RFC', 'razon_social', 'telefono', 'plan']
        read_only_fields = ['id', 'plan']


class ClienteSerializer(serializers.ModelSerializer):
    """Serializer para clientes."""
    
    class Meta:
        model = Cliente
        fields = [
            'id', 'nombre', 'email', 'telefono', 'RFC', 'razon_social',
            'direccion', 'creado', 'actualizado', 'activo'
        ]
        read_only_fields = ['id', 'creado', 'actualizado']


class ItemFacturaSerializer(serializers.ModelSerializer):
    """Serializer para items de factura (incluye campos calculados)."""
    
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    impuesto = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = ItemFactura
        fields = [
            'id', 'descripcion', 'cantidad', 'precio_unitario',
            'porcentaje_impuesto', 'subtotal', 'impuesto', 'total'
        ]
        read_only_fields = ['id']


class FacturaSerializer(serializers.ModelSerializer):
    """Serializer para facturas (con items anidados)."""
    
    items = ItemFacturaSerializer(many=True, read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    
    class Meta:
        model = Factura
        fields = [
            'id', 'numero', 'cliente', 'cliente_nombre', 'proyecto',
            'fecha_emision', 'fecha_vencimiento',
            'subtotal', 'impuestos', 'descuento', 'total',
            'estado', 'notas', 'items', 'creado', 'actualizado'
        ]
        read_only_fields = ['id', 'subtotal', 'impuestos', 'total', 'creado', 'actualizado']


class ProyectoSerializer(serializers.ModelSerializer):
    """Serializer para proyectos."""
    
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    
    class Meta:
        model = Proyecto
        fields = [
            'id', 'nombre', 'descripcion', 'cliente', 'cliente_nombre',
            'estado', 'tarifa_hora', 'creado', 'actualizado'
        ]
        read_only_fields = ['id', 'creado', 'actualizado']