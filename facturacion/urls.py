from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, ClienteViewSet, ProyectoViewSet,
    FacturaViewSet, ItemFacturaViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'proyectos', ProyectoViewSet, basename='proyecto')
router.register(r'facturas', FacturaViewSet, basename='factura')
router.register(r'items', ItemFacturaViewSet, basename='item')

urlpatterns = [
    path('', include(router.urls)),
]