from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Cliente, Proyecto, Factura, ItemFactura
from .serializers import (
    UserSerializer, ClienteSerializer, ProyectoSerializer,
    FacturaSerializer, ItemFacturaSerializer
)
from .permissions import EsPropietario

User = get_user_model()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Endpoint de solo lectura para el usuario actual."""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Solo el usuario actual
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Endpoint /api/users/me/ que devuelve el usuario autenticado."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class ClienteViewSet(viewsets.ModelViewSet):
    """CRUD completo de clientes con multi-tenancy."""
    
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated, EsPropietario]
    
    def get_queryset(self):
        # Solo los clientes del usuario autenticado
        return Cliente.objects.filter(propietario=self.request.user)
    
    def perform_create(self, serializer):
        # Asigna automáticamente al usuario autenticado
        cliente = serializer.save(propietario=self.request.user)
        
        # Envía email de bienvenida en background (NO bloquea la respuesta)
        if cliente.email:
            from .tasks import enviar_email_bienvenida
            enviar_email_bienvenida.delay(cliente.email, cliente.nombre)


class ProyectoViewSet(viewsets.ModelViewSet):
    """CRUD de proyectos con multi-tenancy."""
    
    serializer_class = ProyectoSerializer
    permission_classes = [permissions.IsAuthenticated, EsPropietario]
    
    def get_queryset(self):
        return Proyecto.objects.filter(propietario=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(propietario=self.request.user)


class FacturaViewSet(viewsets.ModelViewSet):
    """CRUD de facturas con multi-tenancy."""
    
    serializer_class = FacturaSerializer
    permission_classes = [permissions.IsAuthenticated, EsPropietario]
    
    def get_queryset(self):
        return Factura.objects.filter(propietario=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(propietario=self.request.user)
    
    @action(detail=True, methods=['post'])
    def calcular(self, request, pk=None):
        """Endpoint /api/facturas/{id}/calcular/ que recalcula totales."""
        factura = self.get_object()
        factura.calcular_totales()
        serializer = self.get_serializer(factura)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def generar_pdf(self, request, pk=None):
        """Dispara la generación del PDF en background."""
        factura = self.get_object()
        from .tasks import generar_pdf_factura
        resultado = generar_pdf_factura.delay(factura.id)
        return Response({
            'mensaje': 'Generación de PDF iniciada',
            'task_id': resultado.id,
            'factura': factura.numero,
        })


class ItemFacturaViewSet(viewsets.ModelViewSet):
    """CRUD de items de factura."""
    
    serializer_class = ItemFacturaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Solo los items de las facturas del usuario
        return ItemFactura.objects.filter(factura__propietario=self.request.user)