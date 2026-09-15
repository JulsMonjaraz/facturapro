from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from decimal import Decimal
from decimal import Decimal, ROUND_HALF_UP  


class User(AbstractUser):
    """Usuario personalizado con datos fiscales para facturación."""
    
    RFC = models.CharField('RFC', max_length=13, blank=True, null=True)
    razon_social = models.CharField('Razón social', max_length=200, blank=True, null=True)
    telefono = models.CharField('Teléfono', max_length=20, blank=True, null=True)
    direccion = models.TextField('Dirección', blank=True, null=True)
    
    # Plan de suscripción (lo usaremos con Stripe después)
    PLAN_CHOICES = [
        ('starter', 'Starter'),
        ('pro', 'Pro'),
        ('business', 'Business'),
    ]
    plan = models.CharField('Plan', max_length=20, choices=PLAN_CHOICES, default='starter')
    
    def __str__(self):
        return self.username


class Cliente(models.Model):
    """Cliente del freelancer. Cada freelancer solo ve sus propios clientes."""
    
    propietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clientes')
    nombre = models.CharField('Nombre', max_length=200)
    email = models.EmailField('Email', blank=True, null=True)
    telefono = models.CharField('Teléfono', max_length=20, blank=True, null=True)
    RFC = models.CharField('RFC', max_length=13, blank=True, null=True)
    razon_social = models.CharField('Razón social', max_length=200, blank=True, null=True)
    direccion = models.TextField('Dirección', blank=True, null=True)
    
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['nombre']
        unique_together = ['propietario', 'nombre']
    
    def __str__(self):
        return self.nombre


class Proyecto(models.Model):
    """Proyecto de un cliente."""
    
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('pausado', 'Pausado'),
        ('completado', 'Completado'),
    ]
    
    propietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proyectos')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='proyectos')
    nombre = models.CharField('Nombre', max_length=200)
    descripcion = models.TextField('Descripción', blank=True, null=True)
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_CHOICES, default='activo')
    tarifa_hora = models.DecimalField('Tarifa por hora', max_digits=10, decimal_places=2, null=True, blank=True)
    
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-creado']
    
    def __str__(self):
        return f"{self.nombre} — {self.cliente.nombre}"


class Factura(models.Model):
    """Factura de un cliente."""
    
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('emitida', 'Emitida'),
        ('pagada', 'Pagada'),
        ('vencida', 'Vencida'),
        ('cancelada', 'Cancelada'),
    ]
    
    propietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='facturas')
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='facturas')
    proyecto = models.ForeignKey(Proyecto, on_delete=models.SET_NULL, null=True, blank=True, related_name='facturas')
    
    numero = models.CharField('Número', max_length=50, unique=True)
    fecha_emision = models.DateField('Fecha de emisión', default=timezone.now)
    fecha_vencimiento = models.DateField('Fecha de vencimiento')
    
    # Cálculos (los llenaremos automáticamente con propiedades)
    subtotal = models.DecimalField('Subtotal', max_digits=12, decimal_places=2, default=Decimal('0.00'))
    impuestos = models.DecimalField('Impuestos', max_digits=12, decimal_places=2, default=Decimal('0.00'))
    descuento = models.DecimalField('Descuento', max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField('Total', max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_CHOICES, default='borrador')
    notas = models.TextField('Notas', blank=True, null=True)
    
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-fecha_emision', '-creado']
    
    def __str__(self):
        return f"{self.numero} — {self.cliente.nombre}"
    
    def calcular_totales(self):
        """Recalcula subtotal, impuestos y total desde los items."""
        items = self.items.all()
        dos_decimales = Decimal('0.01')
        
        self.subtotal = sum((item.subtotal for item in items), Decimal('0.00')).quantize(dos_decimales, rounding=ROUND_HALF_UP)
        self.impuestos = sum((item.impuesto for item in items), Decimal('0.00')).quantize(dos_decimales, rounding=ROUND_HALF_UP)
        self.total = (self.subtotal + self.impuestos - self.descuento).quantize(dos_decimales, rounding=ROUND_HALF_UP)
        self.save(update_fields=['subtotal', 'impuestos', 'total'])
    


class ItemFactura(models.Model):
    """Línea de una factura (concepto, cantidad, precio, impuesto)."""
    
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='items')
    descripcion = models.CharField('Descripción', max_length=300)
    cantidad = models.DecimalField('Cantidad', max_digits=10, decimal_places=2, default=Decimal('1.00'))
    precio_unitario = models.DecimalField('Precio unitario', max_digits=10, decimal_places=2)
    porcentaje_impuesto = models.DecimalField('Impuesto (%)', max_digits=5, decimal_places=2, default=Decimal('16.00'))
    
    def __str__(self):
        return f"{self.descripcion} — {self.cantidad} x {self.precio_unitario}"
    
    @property
    def subtotal(self):
        return (self.cantidad * self.precio_unitario).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @property
    def impuesto(self):
        return (self.subtotal * (self.porcentaje_impuesto / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @property
    def total(self):
        return (self.subtotal + self.impuesto).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    class Meta:
        ordering = ['id']