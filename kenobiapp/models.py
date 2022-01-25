from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from datetime import timedelta

CENIT_SYSTEM_CHOICES = [
    ('NA', 'N/A'),
    ('OAP', 'Oleoducto Araguaney - Porvenir'),
    ('PA', 'Poliducto Andino'),
    ('PO', 'Poliducto de Oriente'),
    ('OCC', 'Oleoducto Caño Limón - Coveñas'),
    ('PGC', 'Poliducto Galan - Chimitá'),
    ('PSM', 'Poliducto Salgar - Mansilla'),
    ('PSC', 'Poliducto Salgar - Cartago'),
    ('YB', 'Yumbo - Buenaventura'),
    ('MC', 'Medellín - Cartago'),
    ('SM', 'Sebastopol - Medellín'),
    ('OTA', 'OTA - Orito Tumaco'),
    ('OAP', 'Oleoducto Araguaney - Porvenir'),
    ('SGN', 'Salgar - Gualanday - Neiva'),
]

MAINTENANCE_TYPE = [
    ('P', 'Preventive'),
    ('C', 'Corrective')
]


class Project(models.Model):
    name = models.CharField(
        verbose_name=_('Name'),
        help_text=_('Type the name of the project.'),
        max_length=50
    )
    description = models.TextField(
        verbose_name=_('Description'),
        max_length=300
    )
    state = models.BooleanField(default=True)
    modifier_user = models.ForeignKey(
        verbose_name=_('Modifier user'),
        to=User,
        on_delete=models.CASCADE
    )
    created_at = models.DateField(auto_now_add=True)
    update_at = models.DateField(auto_now=True)

    class Meta:
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')
        ordering = ['name']

    def __str__(self):
        return f'{self.name}'


class Client(models.Model):
    name = models.CharField(
        verbose_name=_('Name'),
        help_text=_('Enter the name of the client.'),
        max_length=50
    )
    phone = models.CharField(max_length=14, null=True, blank=True)
    cell_phone = models.CharField(max_length=10, null=True, blank=True)
    email = models.EmailField(verbose_name='E-mail')
    state = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    update_at = models.DateField(auto_now=True)

    class Meta:
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')
        ordering = ['name']

    def __str__(self):
        return f'{self.name}'


class Engineer(User):
    identification = models.CharField(
        blank=True,
        null=True,
        max_length=12)
    phone = models.CharField(max_length=14)

    class Meta:
        verbose_name = _('Engineer')
        verbose_name_plural = _('Enginers')
        ordering = ['first_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Station(models.Model):
    project = models.ManyToManyField(Project)
    client = models.ManyToManyField(Client)
    modifier_user = models.ForeignKey(
        verbose_name=_('Modifier user'),
        to=User,
        on_delete=models.CASCADE
    )
    id_intern = models.CharField(
        verbose_name=_('internal identification'),
        max_length=6
    )
    name = models.CharField(
        verbose_name=_('Name'),
        help_text=_('Enter the name of the client.'),
        max_length=12
    )
    maintenance_frecuency_months = models.IntegerField(
        verbose_name=_('Maintenance frequency'),
        help_text=_('Enter the frequency of maintenance in months.')
    )
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    system = models.CharField(
        max_length=3,
        choices=CENIT_SYSTEM_CHOICES,
        default='NA'
    )
    owner_phone = models.CharField(
        max_length=14,
        null=True,
        blank=True
    )
    state = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    update_at = models.DateField(auto_now=True)

    class Meta:
        verbose_name = _('Station')
        verbose_name_plural = _('Stations')
        ordering = ['name']

    def __str__(self):
        return f'{self.name} - {self.project}'


class ServiceOrder(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    engineer = models.ForeignKey(Engineer, on_delete=models.CASCADE)
    author = models.CharField(max_length=100)
    execution_date = models.DateField()
    service_description = models.TextField(max_length=300)
    observation = models.TextField(max_length=300, null=True, blank=True)
    state = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    update_at = models.DateField(auto_now=True)

    class Meta:
        verbose_name = _('Service Order')
        verbose_name_plural = _('Service orders')
        ordering = ['-update_at']

    def __str__(self):
        os = 100 + self.id
        if self.state:
            state = _('Open')
        else:
            state = _('Close')
        return f'OS{os} | {self.station} | {state}'


class Maintenance(models.Model):
    service_order = models.ForeignKey(ServiceOrder, on_delete=models.CASCADE)
    type_maintenance = models.CharField(
        max_length=1,
        choices=MAINTENANCE_TYPE,
        default='P'
    )
    next_maintenance = models.DateField(blank=True, null=True)

    def cal_next_maintenance(self):
        delta = timedelta(days=30*self.service_order.station.maintenance_frecuency_months)
        next_maintenance = self.service_order.execution_date + delta
        self.next_maintenance = next_maintenance
        self.save()

    class Meta:
        verbose_name = _('Maintenance')
        verbose_name_plural = _('Maintenance')
        ordering = ['-service_order']

    def __str__(self):
        return f'{self.service_order} - {self.type_maintenance}'


class DataPlanDavis(models.Model):
    code = models.CharField(max_length=30)
    reference = models.CharField(max_length=10)
    state = models.BooleanField(default=True)
    start_date = models.DateField()
    expire = models.DateField(blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    update_at = models.DateField(auto_now=True)

    def expire_plan(self):
        delta = timedelta(days=180)
        self.expire = self.start_date + delta
        self.save()

    class Meta:
        verbose_name = _('Davis data Plan')
        verbose_name_plural = _('Davis data Plans')
        ordering = ['code']

    def __str__(self):
        return f'{self.code} - {self.expire}'


class DavisStation(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    plan = models.ForeignKey(DataPlanDavis, on_delete=models.CASCADE)
    modifier_user = models.ForeignKey(
        verbose_name=_('Modifier user'),
        to=User,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=20)
    did = models.CharField(
        max_length=20,
        verbose_name=_('DID'),
        help_text=_('This code is located on the device')
    )
    key = models.CharField(
        max_length=20,
        verbose_name=_('DID'),
        help_text=_('This code is located on the device')
    )
    af = models.CharField(
        max_length=15,
        verbose_name=_('Código Activos Fijos'),
        help_text=_('This code is provided by the Infrastructure leader or the administrative area.'),
        null=True,
        blank=True
    )
    state = models.BooleanField(default=True)
    observation = models.TextField(max_length=300)
    created_at = models.DateField(auto_now_add=True)
    update_at = models.DateField(auto_now=True)

    class Meta:
        verbose_name = _('Service Order')
        verbose_name_plural = _('Service orders')
        ordering = ['name']

    def __str__(self):
        return f'{self.name} - {self.did}'
