import factory
from decimal import Decimal
from django.contrib.auth import get_user_model
from facturacion.models import Cliente, Proyecto, Factura, ItemFactura

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    plan = 'starter'


class ClienteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cliente

    propietario = factory.SubFactory(UserFactory)
    nombre = factory.Sequence(lambda n: f'Cliente {n}')
    email = factory.LazyAttribute(lambda obj: f'cliente{obj.nombre.lower().replace(" ", "")}@test.com')


class ProyectoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Proyecto

    propietario = factory.SubFactory(UserFactory)
    cliente = factory.SubFactory(ClienteFactory)
    nombre = factory.Sequence(lambda n: f'Proyecto {n}')
    tarifa_hora = Decimal('500.00')


class FacturaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Factura

    propietario = factory.SubFactory(UserFactory)
    cliente = factory.SubFactory(ClienteFactory)
    numero = factory.Sequence(lambda n: f'FAC-{n:04d}')
    fecha_vencimiento = '2026-12-31'


class ItemFacturaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ItemFactura

    factura = factory.SubFactory(FacturaFactory)
    descripcion = factory.Sequence(lambda n: f'Servicio {n}')
    cantidad = Decimal('1.00')
    precio_unitario = Decimal('100.00')
    porcentaje_impuesto = Decimal('16.00')