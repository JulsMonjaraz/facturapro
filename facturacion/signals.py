from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ItemFactura


@receiver([post_save, post_delete], sender=ItemFactura)
def actualizar_totales_factura(sender, instance, **kwargs):
    """Recalcula los totales de la factura cuando se agrega/edita/borra un item."""
    factura = instance.factura
    factura.calcular_totales()