import pytest
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from facturacion.models import Cliente, Factura
from .factories import (
    UserFactory, ClienteFactory, ProyectoFactory,
    FacturaFactory, ItemFacturaFactory
)


@pytest.fixture
def api_client():
    """Cliente HTTP para hacer requests a la API."""
    return APIClient()


@pytest.fixture
def user(db):
    """Usuario de prueba."""
    return UserFactory()


@pytest.fixture
def authenticated_client(api_client, user):
    """Cliente autenticado con JWT."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.mark.django_db
class TestAutenticacion:
    """Tests de autenticación y permisos."""

    def test_endpoint_protegido_sin_token(self, api_client):
        """Sin autenticación debe dar 401."""
        response = api_client.get('/api/clientes/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_endpoint_protegido_con_token(self, authenticated_client):
        """Con autenticación debe dar 200."""
        response = authenticated_client.get('/api/clientes/')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestClienteAPI:
    """Tests del endpoint de clientes."""

    def test_listar_solo_mis_clientes(self, authenticated_client, user):
        """Solo debe listar los clientes del usuario autenticado."""
        # Cliente del usuario autenticado
        ClienteFactory(propietario=user, nombre='Mi cliente')
        # Cliente de otro usuario
        ClienteFactory(nombre='Cliente ajeno')

        response = authenticated_client.get('/api/clientes/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['nombre'] == 'Mi cliente'

    def test_crear_cliente_asigna_propietario(self, authenticated_client, user):
        """Al crear un cliente, el propietario se asigna automáticamente."""
        data = {
            'nombre': 'Nuevo cliente',
            'email': 'nuevo@test.com',
        }
        response = authenticated_client.post('/api/clientes/', data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        cliente = Cliente.objects.get(id=response.data['id'])
        assert cliente.propietario == user

    def test_no_puedo_ver_cliente_ajeno(self, authenticated_client, user):
        """No puedo ver un cliente que no es mío."""
        otro_cliente = ClienteFactory(nombre='Ajeno')
        
        response = authenticated_client.get(f'/api/clientes/{otro_cliente.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_no_puedo_editar_cliente_ajeno(self, authenticated_client):
        """No puedo editar un cliente que no es mío."""
        otro_cliente = ClienteFactory(nombre='Ajeno')
        
        response = authenticated_client.patch(
            f'/api/clientes/{otro_cliente.id}/',
            {'nombre': 'Hackeado'},
            format='json'
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestFacturaAPI:
    """Tests del endpoint de facturas."""

    def test_listar_solo_mis_facturas(self, authenticated_client, user):
        """Solo debo ver mis facturas."""
        FacturaFactory(propietario=user, numero='MIA-001')
        FacturaFactory(numero='AJENA-001')

        response = authenticated_client.get('/api/facturas/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['numero'] == 'MIA-001'

    def test_endpoint_calcular_totales(self, authenticated_client, user):
        """El endpoint /calcular/ debe recalcular totales."""
        factura = FacturaFactory(propietario=user)
        ItemFacturaFactory(
            factura=factura,
            cantidad=Decimal('10'),
            precio_unitario=Decimal('100')
        )

        response = authenticated_client.post(f'/api/facturas/{factura.id}/calcular/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['subtotal'] == '1000.00'
        assert response.data['impuestos'] == '160.00'
        assert response.data['total'] == '1160.00'

    def test_factura_incluye_items(self, authenticated_client, user):
        """La respuesta de una factura debe incluir sus items."""
        factura = FacturaFactory(propietario=user)
        ItemFacturaFactory(factura=factura, descripcion='Diseño web')
        ItemFacturaFactory(factura=factura, descripcion='Hosting')

        response = authenticated_client.get(f'/api/facturas/{factura.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['items']) == 2


@pytest.mark.django_db
class TestUserAPI:
    """Tests del endpoint de usuarios."""

    def test_endpoint_me_devuelve_usuario_actual(self, authenticated_client, user):
        """El endpoint /me/ debe devolver el usuario autenticado."""
        response = authenticated_client.get('/api/users/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == user.username