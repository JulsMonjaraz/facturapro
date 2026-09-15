from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from io import BytesIO
import os


@shared_task
def enviar_email_bienvenida(email, nombre):
    """Envía un email de bienvenida cuando se crea un cliente."""

    asunto = f'Bienvenido a FacturaPro, {nombre}'
    mensaje = f'''
Hola {nombre},

¡Bienvenido a FacturaPro!

Estamos emocionados de tenerte con nosotros. Desde ahora podrás:

- Crear y gestionar clientes
- Generar facturas automáticas
- Recibir recordatorios de pago
- Y mucho más...

Si tienes alguna duda, responde a este email.

Saludos,
El equipo de FacturaPro
    '''

    send_mail(
        asunto,
        mensaje,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )

    return f'Email enviado a {email}'


@shared_task
def enviar_email_recordatorio(factura_id, email, cliente_nombre, numero, total, fecha_vencimiento):
    """Envía un email de recordatorio de pago."""

    asunto = f'Recordatorio de pago — Factura {numero}'
    mensaje = f'''
Hola {cliente_nombre},

Te recordamos que tu factura {numero} por un total de ${total} 
vence el próximo {fecha_vencimiento}.

Por favor realiza el pago antes de la fecha límite para evitar 
recargos por mora.

Si ya realizaste el pago, ignora este mensaje.

Saludos,
El equipo de FacturaPro
    '''

    send_mail(
        asunto,
        mensaje,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )

    return f'Recordatorio enviado a {email} para factura {numero}'


@shared_task
def enviar_recordatorios_pago():
    """Envía recordatorios de pago para facturas que vencen en 3 días."""
    from .models import Factura
    from django.utils import timezone
    from datetime import timedelta

    fecha_objetivo = timezone.localdate() + timedelta(days=3)

    facturas = Factura.objects.filter(
        fecha_vencimiento=fecha_objetivo,
        estado__in=['emitida', 'vencida'],
    ).exclude(estado='pagada')

    if not facturas:
        return 'No hay recordatorios que enviar'

    enviados = 0
    for factura in facturas:
        if factura.cliente.email:
            enviar_email_recordatorio.delay(
                factura.id,
                factura.cliente.email,
                factura.cliente.nombre,
                factura.numero,
                str(factura.total),
                factura.fecha_vencimiento.strftime('%d/%m/%Y'),
            )
            enviados += 1

    return f'{enviados} recordatorios enviados'


@shared_task
def generar_pdf_factura(factura_id):
    """Genera un PDF de la factura y lo guarda en media/facturas/."""
    from .models import Factura
    from xhtml2pdf import pisa   # Import local, dentro de la función

    try:
        factura = Factura.objects.get(id=factura_id)
    except Factura.DoesNotExist:
        return f'Factura {factura_id} no encontrada'

    html_string = render_to_string('facturacion/factura_pdf.html', {
        'factura': factura,
    })

    resultado = BytesIO()
    pdf_status = pisa.CreatePDF(
        src=html_string,
        dest=resultado
    )

    if pdf_status.err:
        return f'Error al generar PDF para la factura {factura.numero}'

    carpeta = os.path.join(settings.MEDIA_ROOT, 'facturas')
    os.makedirs(carpeta, exist_ok=True)

    ruta = os.path.join(carpeta, f'{factura.numero}.pdf')
    with open(ruta, 'wb') as f:
        f.write(resultado.getvalue())

    return f'PDF generado: {ruta}'