from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from bdd.models import Proveedor


class MedioPago(models.TextChoices):
    EFECTIVO = "efectivo", _("Efectivo")
    BANCO = "banco", _("Banco")
    MP = "mp", _("MercadoPago")
    TARJETA = "tarjeta", _("Tarjeta de crédito")


class ProveedorFinanciero(models.Model):
    proveedor = models.OneToOneField(Proveedor, on_delete=models.CASCADE, related_name="financiero")
    plazo_unidad = models.CharField(max_length=10, choices=(("dias", _("Días")), ("meses", _("Meses"))), default="meses")
    plazo_valor = models.PositiveIntegerField(default=1)
    descuento_boleta_A = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # porcentaje
    descuento_boleta_B = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # porcentaje
    punto_venta = models.CharField(max_length=8, default="0001")

    class Meta:
        app_label = 'administracion_financiera'

    def __str__(self):
        return f"Financiero {self.proveedor}"


class Cuenta(models.Model):
    tipo = models.CharField(max_length=16, choices=MedioPago.choices)
    nombre = models.CharField(max_length=80)
    banco = models.CharField(max_length=80, blank=True, null=True)
    identificador = models.CharField(
        max_length=120, blank=True, null=True
    )  # CBU/alias/ID MP u otro
    activa_desde = models.DateField(blank=True, null=True)
    activa_hasta = models.DateField(blank=True, null=True)

    class Meta:
        app_label = 'administracion_financiera'

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


class TarjetaCredito(models.Model):
    cuenta_liquidacion = models.ForeignKey(
        Cuenta, on_delete=models.PROTECT, related_name="tarjetas"
    )
    nombre = models.CharField(max_length=80, blank=True, null=True)
    ult4 = models.CharField(max_length=4, blank=True, null=True)
    cierre_dia = models.PositiveSmallIntegerField()
    vencimiento_dia = models.PositiveSmallIntegerField()

    class Meta:
        app_label = 'administracion_financiera'

    def __str__(self):
        suf = f" ****{self.ult4}" if self.ult4 else ""
        return f"{self.nombre or 'Tarjeta'}{suf}"


class Carga(models.Model):
    nombre = models.CharField(max_length=120)
    sujeto_pasivo = models.CharField(max_length=120)
    periodo = models.CharField(max_length=7)  # YYYY-MM
    ult_fecha = models.DateField(blank=True, null=True)
    ult_monto = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    metodos_permitidos = models.JSONField(default=list, blank=True)
    # Lista de IDs de cuentas permitidas; validación dura al liquidar
    cuentas_permitidas = models.ManyToManyField(Cuenta, blank=True)

    class Meta:
        abstract = True


class Servicio(Carga):
    identificador_contrato = models.CharField(max_length=120, blank=True, null=True)

    class Meta:
        app_label = 'administracion_financiera'

    def __str__(self):
        return f"{self.nombre}"


class Impuesto(Carga):
    class Tipo(models.TextChoices):
        NACIONAL = "nacional", _("Nacional")
        PROVINCIAL = "provincial", _("Provincial")
        MUNICIPAL = "municipal", _("Municipal")

    tipo = models.CharField(max_length=12, choices=Tipo.choices)
    jurisdiccion = models.CharField(max_length=120, blank=True, null=True)

    class Meta:
        app_label = 'administracion_financiera'

    def __str__(self):
        suf = f" - {self.jurisdiccion}" if self.jurisdiccion else ""
        return f"{self.nombre} ({self.get_tipo_display()}{suf})"


class Boleta(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField()
    numero = models.CharField(max_length=30)
    punto_venta = models.CharField(max_length=8)
    numero_completo = models.CharField(max_length=50)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    pronto_pago_limite = models.DateField(blank=True, null=True)
    estado = models.CharField(
        max_length=12,
        choices=(
            ("pendiente", "Pendiente"),
            ("pagada", "Pagada"),
            ("vencida", "Vencida"),
            ("caduco", "Caduco"),
        ),
        default="pendiente",
    )
    fecha_pago = models.DateField(blank=True, null=True)
    semana_iso = models.CharField(max_length=8, blank=True, null=True)  # YYYY-Www

    class Meta:
        app_label = 'administracion_financiera'
        constraints = [
            models.UniqueConstraint(
                fields=["proveedor", "punto_venta", "numero_completo"],
                name="uniq_boleta_prov_pv_num",
            )
        ]

    def __str__(self):
        return f"{self.proveedor} {self.numero_completo}"


class TicketDePago(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.PROTECT, blank=True, null=True)
    impuesto = models.ForeignKey(Impuesto, on_delete=models.PROTECT, blank=True, null=True)
    periodo = models.CharField(max_length=7, blank=True, null=True)  # YYYY-MM
    vencimiento = models.DateField()
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    pagado = models.BooleanField(default=False)
    fecha_pago = models.DateField(blank=True, null=True)
    metodo_pago = models.CharField(max_length=16, choices=MedioPago.choices, blank=True, null=True)
    cuenta_pago = models.ForeignKey(Cuenta, on_delete=models.PROTECT, blank=True, null=True)
    caduco = models.BooleanField(default=False)
    semana_iso = models.CharField(max_length=8, blank=True, null=True)  # YYYY-Www

    class Meta:
        app_label = 'administracion_financiera'

    def __str__(self):
        target = self.servicio or self.impuesto
        return f"Ticket {target} {self.periodo or ''} {self.monto}"


class Pago(models.Model):
    # Origen polimórfico: Boleta o TicketDePago
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    origen = GenericForeignKey("content_type", "object_id")

    importe = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField()
    medio_pago = models.CharField(max_length=16, choices=MedioPago.choices)
    cuenta = models.ForeignKey(Cuenta, on_delete=models.PROTECT)
    referencia = models.CharField(max_length=120, blank=True, null=True)
    semana_iso = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        app_label = 'administracion_financiera'

    def __str__(self):
        return f"Pago {self.importe} {self.get_medio_pago_display()}"


class CtaCteProveedor(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)

    class Meta:
        app_label = 'administracion_financiera'

    def __str__(self):
        return f"Ctacte {self.proveedor}"


class MovimientoCtaCte(models.Model):
    class Tipo(models.TextChoices):
        CARGO = "cargo", _("Cargo")
        ABONO = "abono", _("Abono")

    ctacte = models.ForeignKey(CtaCteProveedor, on_delete=models.CASCADE, related_name="movimientos")
    fecha = models.DateField()
    semana_iso = models.CharField(max_length=8)

    # Origen polimórfico para trazar movimientos (Pago o ajuste manual)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    origen = GenericForeignKey("content_type", "object_id")

    tipo = models.CharField(max_length=8, choices=Tipo.choices)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    saldo_acumulado = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        app_label = 'administracion_financiera'


class Cheque(models.Model):
    class Estado(models.TextChoices):
        EMITIDO = "emitido", _("Emitido")
        COBRADO = "cobrado", _("Cobrado")
        DEVUELTO = "devuelto", _("Devuelto")
        SALVADO = "salvado", _("Salvado")

    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    cuenta_emisora = models.ForeignKey(Cuenta, on_delete=models.PROTECT)
    numero = models.CharField(max_length=40)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_emision = models.DateField()
    fecha_diferido = models.DateField(blank=True, null=True)
    fecha_cobro = models.DateField(blank=True, null=True)
    banco = models.CharField(max_length=80, blank=True, null=True)
    serie = models.CharField(max_length=40, blank=True, null=True)
    plaza = models.CharField(max_length=80, blank=True, null=True)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.EMITIDO)

    class Meta:
        app_label = 'administracion_financiera'

    def __str__(self):
        return f"Cheque {self.numero} {self.monto} ({self.get_estado_display()})"


class DebitoAutomatico(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, blank=True, null=True)
    impuesto = models.ForeignKey(Impuesto, on_delete=models.CASCADE, blank=True, null=True)
    ticket = models.ForeignKey(TicketDePago, on_delete=models.CASCADE, blank=True, null=True)
    cuenta = models.ForeignKey(Cuenta, on_delete=models.PROTECT, blank=True, null=True)
    tarjeta = models.ForeignKey(TarjetaCredito, on_delete=models.PROTECT, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        app_label = 'administracion_financiera'
        constraints = [
            models.CheckConstraint(
                check=(
                    # Debe haber exactamente uno objetivo entre servicio, impuesto o ticket
                    (
                        models.Q(servicio__isnull=False)
                        & models.Q(impuesto__isnull=True)
                        & models.Q(ticket__isnull=True)
                    )
                    | (
                        models.Q(servicio__isnull=True)
                        & models.Q(impuesto__isnull=False)
                        & models.Q(ticket__isnull=True)
                    )
                    | (
                        models.Q(servicio__isnull=True)
                        & models.Q(impuesto__isnull=True)
                        & models.Q(ticket__isnull=False)
                    )
                ),
                name="debito_auto_objetivo_xor",
            ),
            models.CheckConstraint(
                check=(
                    (models.Q(cuenta__isnull=False) & models.Q(tarjeta__isnull=True))
                    | (models.Q(cuenta__isnull=True) & models.Q(tarjeta__isnull=False))
                ),
                name="debito_auto_cuenta_xor_tarjeta",
            ),
        ]

    def __str__(self):
        target = self.servicio or self.impuesto or self.ticket
        medio = self.cuenta or self.tarjeta
        return f"DebitoAuto {target} -> {medio} ({'on' if self.activo else 'off'})"
