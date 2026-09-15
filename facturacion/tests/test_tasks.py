import pytest
from decimal import Decimal
from datetime import timedelta
from django.core import mail
from django.utils import timezone

from facturacion.tasks import (
    enviar_email_bienvenida,
    enviar_email_recordatorio,
    enviar_recordatorios_pago,
    generar_pdf_factura,
)
from .factories import FacturaFactory, ItemFacturaFactory, ClienteFactory


@pytest.mark.django_db
class TestEnviarEmailBienvenida:
    """Tests para la tarea enviar_email_bienvenida."""

    def test_envia_email_correctamente(self):
        """Debe enviar un email con los datos correctos."""
        resultado = enviar_email_bienvenida('test@example.com', 'Juan Pérez')
        
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == ['test@example.com']
        assert 'Juan Pérez' in mail.outbox[0].subject
        assert 'enviado a test@example.com' in resultado


@pytest.mark.django_db
class TestEnviarEmailRecordatorio:
    """Tests para la tarea enviar_email_recordatorio."""

    def test_envia_recordatorio(self):
        """Debe enviar un recordatorio con los datos de la factura."""
        resultado = enviar_email_recordatorio(
            factura_id=1,
            email='cliente@example.com',
            cliente_nombre='María López',
            numero='FAC-001',
            total='5800.00',
            fecha_vencimiento='20/09/2026',
        )
        
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == ['cliente@example.com']
        assert 'FAC-001' in mail.outbox[0].subject
        assert 'Recordatorio enviado' in resultado


@pytest.mark.django_db
class TestEnviarRecordatoriosPago:
    """Tests para la tarea enviar_recordatorios_pago."""

    def test_sin_facturas_proximas(self):
        """Si no hay facturas próximas a vencer, retorna mensaje."""
        resultado = enviar_recordatorios_pago()
        assert resultado == 'No hay recordatorios que enviar'

    def test_envia_recordatorio_factura_proxima(self):
        """Debe enviar recordatorio si hay factura que vence en 3 días."""
        hoy = timezone.localdate()
        fecha_vencimiento = hoy + timedelta(days=3)
        
        cliente = ClienteFactory(email='cliente@example.com')
        FacturaFactory(
            cliente=cliente,
            estado='emitida',
            fecha_vencimiento=fecha_vencimiento,
        )
        
        resultado = enviar_recordatorios_pago()
        assert '1 recordatorios enviados' in resultado

    def test_no_envia_factura_pagada(self):
        """No debe enviar recordatorio para facturas pagadas."""
        hoy = timezone.localdate()
        fecha_vencimiento = hoy + timedelta(days=3)
        
        FacturaFactory(
            estado='pagada',
            fecha_vencimiento=fecha_vencimiento,
        )
        
        resultado = enviar_recordatorios_pago()
        assert resultado == 'No hay recordatorios que enviar'

    def test_no_envia_sin_email_cliente(self):
        """No debe enviar si el cliente no tiene email."""
        hoy = timezone.localdate()
        fecha_vencimiento = hoy + timedelta(days=3)
        
        cliente = ClienteFactory(email=None)
        FacturaFactory(
            cliente=cliente,
            estado='emitida',
            fecha_vencimiento=fecha_vencimiento,
        )
        
        resultado = enviar_recordatorios_pago()
        # La tarea encuentra la factura pero no envía email
        assert '0 recordatorios enviados' in resultado or resultado == 'No hay recordatorios que enviar'


@pytest.mark.django_db
class TestGenerarPdfFactura:
    """Tests para la tarea generar_pdf_factura."""

    def test_genera_pdf_correctamente(self, tmp_path, settings):
        """Debe generar un PDF y guardarlo en disco."""
        settings.MEDIA_ROOT = str(tmp_path)
        
        factura = FacturaFactory()
        ItemFacturaFactory(
            factura=factura,
            cantidad=Decimal('10'),
            precio_unitario=Decimal('100'),
        )
        
        resultado = generar_pdf_factura(factura.id)
        
        assert 'PDF generado' in resultado
        assert factura.numero in resultado

    def test_factura_inexistente(self):
        """Si la factura no existe, debe retornar mensaje."""
        resultado = generar_pdf_factura(99999)
        assert 'no encontrada' in resultado