from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Pielāgots lietotāja modelis, kas paplašina Django standarta lietotāju
    """
    ROLE_CHOICES = [
        ('parasts_lietotajs', _('Regular User')),
        ('administrators', _('Administrator')),
        ('transporta_operators', _('Transport Operator')),
        ('pilsetas_planotajs', _('City Planner')),
    ]

    loma = models.CharField(_('Role'), max_length=50, choices=ROLE_CHOICES, default='parasts_lietotajs')
    talrunis = models.CharField(_('Phone'), max_length=20, blank=True, null=True)
    registracijas_datums = models.DateField(_('Registration Date'), auto_now_add=True)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    @property
    def vards(self):
        return self.first_name

    @property
    def uzvards(self):
        return self.last_name

    @property
    def epasts(self):
        return self.email