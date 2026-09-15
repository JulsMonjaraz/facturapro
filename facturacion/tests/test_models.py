import pytest
from decimal import Decimal
from facturacion.models import Factura, ItemFactura
from .factories import FacturaFactory, ItemFacturaFactory


@pytest.mark.django_db
class TestItemFactura:
    """Tests para el modelo ItemFactura."""

    def test_subtotal_correcto(self):
        """El subtotal debe ser cantidad × precio."""
        item = ItemFacturaFactory(cantidad=Decimal('5.00'), precio_unitario=Decimal('100.00'))
        assert item.subtotal == Decimal('500.00')

    def test_impuesto_correcto(self):
        """El impuesto debe ser subtotal × 16%."""
        item = ItemFacturaFactory(
            cantidad=Decimal('5.00'),
            precio_unitario=Decimal('100.00'),
            porcentaje_impuesto=Decimal('16.00')
        )
        assert item.impuesto == Decimal('80.00')

    def test_total_correcto(self):
        """El total debe ser subtotal + impuesto."""
        item = ItemFacturaFactory(
            cantidad=Decimal('5.00'),
            precio_unitario=Decimal('100.00'),
            porcentaje_impuesto=Decimal('16.00')
        )
        assert item.total == Decimal('580.00')


@pytest.mark.django_db
class TestFactura:
    """Tests para el modelo Factura."""

    def test_calcular_totales_con_un_item(self):
        """Los totales deben calcularse correctamente con un item."""
        factura = FacturaFactory()
        ItemFacturaFactory(
            factura=factura,
            cantidad=Decimal('10.00'),
            precio_unitario=Decimal('500.00'),
            porcentaje_impuesto=Decimal('16.00')
        )

        factura.calcular_totales()
        factura.refresh_from_db()

        assert factura.subtotal == Decimal('5000.00')
        assert factura.impuestos == Decimal('800.00')
        assert factura.total == Decimal('5800.00')

    def test_calcular_totales_con_varios_items(self):
        """Los totales deben sumarse correctamente con varios items."""
        factura = FacturaFactory()
        ItemFacturaFactory(factura=factura, cantidad=Decimal('2'), precio_unitario=Decimal('100.00'))
        ItemFacturaFactory(factura=factura, cantidad=Decimal('3'), precio_unitario=Decimal('200.00'))

        factura.calcular_totales()
        factura.refresh_from_db()

        assert factura.subtotal == Decimal('800.00')
        assert factura.impuestos == Decimal('128.00')
        assert factura.total == Decimal('928.00')

    def test_calcular_totales_con_descuento(self):
        """El descuento debe restarse del total."""
        factura = FacturaFactory(descuento=Decimal('500.00'))
        ItemFacturaFactory(
            factura=factura,
            cantidad=Decimal('10.00'),
            precio_unitario=Decimal('500.00'),
        )

        factura.calcular_totales()
        factura.refresh_from_db()

        assert factura.total == Decimal('5300.00')