# transport/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User

class FavoriteRoute(models.Model):
    """
    Model for user's saved (favorite) routes
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_routes', verbose_name=_('User'))
    route = models.ForeignKey('Marsruts', on_delete=models.CASCADE, related_name='favorited_by', verbose_name=_('Route'))
    added_at = models.DateTimeField(_('Added At'), auto_now_add=True)

    class Meta:
        unique_together = ('user', 'route')
        verbose_name = _('Favorite Route')
        verbose_name_plural = _('Favorite Routes')

    def __str__(self):
        return f"{self.user.username} - {self.route.numurs}"

class Pilseta(models.Model):
    """
    Pilsētas modelis
    """
    pilseta_id = models.AutoField(primary_key=True)
    nosaukums = models.CharField(_('Name'), max_length=100)
    valsts = models.CharField(_('Country'), max_length=100)
    iedzivotaju_skaits = models.IntegerField(_('Population'), null=True, blank=True)

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')

    def __str__(self):
        return self.nosaukums

class TransportaVeids(models.Model):
    """
    Transporta veida modelis
    """
    veids_id = models.AutoField(primary_key=True)
    nosaukums = models.CharField(_('Name'), max_length=50)
    vides_ietekme = models.DecimalField(_('Environmental Impact'), max_digits=3, decimal_places=1, null=True, blank=True)
    apraksts = models.TextField(_('Description'), null=True, blank=True)

    class Meta:
        verbose_name = _('Transport Type')
        verbose_name_plural = _('Transport Types')

    def __str__(self):
        return self.nosaukums

class Marsruts(models.Model):
    """
    Maršruta modelis
    """
    marsruts_id = models.AutoField(primary_key=True)
    numurs = models.CharField(_('Number'), max_length=20)
    nosaukums = models.CharField(_('Name'), max_length=255)
    apraksts = models.TextField(_('Description'), null=True, blank=True)
    pilseta = models.ForeignKey(Pilseta, on_delete=models.CASCADE, verbose_name=_('City'))

    class Meta:
        db_table = 'transport_marsruts'

    def __str__(self):
        return f"{self.numurs} - {self.nosaukums}"

class Transportlidzeklis(models.Model):
    """
    Transportlīdzekļa modelis
    """
    transp_id = models.AutoField(primary_key=True)
    numurs = models.CharField(_('Number'), max_length=20)
    noslogojums = models.IntegerField(_('Congestion'), null=True, blank=True,
                                      help_text=_('Congestion level from 0 to 5'))
    veids = models.ForeignKey(TransportaVeids, on_delete=models.CASCADE, verbose_name=_('Type'))
    marsruts = models.ForeignKey(Marsruts, on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name=_('Route'))
    statuss = models.CharField(_('Status'), max_length=20, null=True, blank=True,
                               choices=[
                                   ('aktīvs', _('Active')),
                                   ('remontā', _('In Repair')),
                                   ('rezervē', _('In Reserve')),
                                   ('neaktīvs', _('Inactive')),
                               ])

    class Meta:
        verbose_name = _('Vehicle')
        verbose_name_plural = _('Vehicles')

    def __str__(self):
        return f"{self.numurs} ({self.veids.nosaukums})"

class Pietura(models.Model):
    """
    Pieturas modelis
    """
    pietura_id = models.AutoField(primary_key=True)
    nosaukums = models.CharField(_('Name'), max_length=255)
    adrese = models.CharField(_('Address'), max_length=255, null=True, blank=True)
    gps_koordinates = models.CharField(_('GPS Coordinates'), max_length=100, null=True, blank=True)
    pilseta = models.ForeignKey(Pilseta, on_delete=models.CASCADE, verbose_name=_('City'))

    class Meta:
        verbose_name = _('Stop')
        verbose_name_plural = _('Stops')

    def __str__(self):
        return self.nosaukums

class MarsrutaPietura(models.Model):
    """
    Maršruta pieturas modelis - saite starp maršrutu un pieturu
    """
    mars_piet_id = models.AutoField(primary_key=True)
    marsruts = models.ForeignKey(Marsruts, on_delete=models.CASCADE, verbose_name=_('Route'))
    pietura = models.ForeignKey(Pietura, on_delete=models.CASCADE, verbose_name=_('Stop'))
    kartas_nr = models.IntegerField(_('Order'))
    laiks_lidz_nakamai = models.IntegerField(_('Time to Next Stop'), null=True, blank=True,
                                             help_text=_('Time in minutes'))

    class Meta:
        verbose_name = _('Route Stop')
        verbose_name_plural = _('Route Stops')
        ordering = ['marsruts', 'kartas_nr']

    def __str__(self):
        return f"{self.marsruts.numurs} - {self.pietura.nosaukums} ({self.kartas_nr})"

class KustibasGrafiks(models.Model):
    """
    Kustības grafika modelis
    """
    grafiks_id = models.AutoField(primary_key=True)
    marsruts = models.ForeignKey(Marsruts, on_delete=models.CASCADE, verbose_name=_('Route'))
    transp = models.ForeignKey(Transportlidzeklis, on_delete=models.CASCADE, verbose_name=_('Vehicle'))
    atiesanas_laiks = models.TimeField(_('Departure Time'))
    ierasanas_laiks = models.TimeField(_('Arrival Time'))
    nedelas_diena = models.IntegerField(_('Weekday'),
                                        choices=[
                                            (1, _('Monday')),
                                            (2, _('Tuesday')),
                                            (3, _('Wednesday')),
                                            (4, _('Thursday')),
                                            (5, _('Friday')),
                                            (6, _('Saturday')),
                                            (7, _('Sunday')),
                                        ])

    class Meta:
        verbose_name = _('Schedule')
        verbose_name_plural = _('Schedules')

    def __str__(self):
        return f"{self.marsruts.numurs} - {self.get_nedelas_diena_display()} - {self.atiesanas_laiks}"

class SatiksmeStavoklis(models.Model):
    """
    Satiksmes stāvokļa modelis
    """
    stavoklis_id = models.AutoField(primary_key=True)
    tips = models.CharField(_('Type'), max_length=50,
                            choices=[
                                ('sastregums', _('Congestion')),
                                ('cela_darbi', _('Road Works')),
                                ('negadijums', _('Accident')),
                                ('atruma_ierobezojums', _('Speed Limit')),
                                ('cits', _('Other')),
                            ])
    apraksts = models.TextField(_('Description'), null=True, blank=True)
    cela_posms = models.CharField(_('Road Section'), max_length=255)
    intensitate_min = models.IntegerField(_('Intensity (min)'), null=True, blank=True,
                                          help_text=_('Duration of delay in minutes'))
    gps_koordinates = models.CharField(_('GPS Coordinates'), max_length=100, null=True, blank=True)
    sakuma_laiks = models.DateTimeField(_('Start Time'))
    beigu_laiks = models.DateTimeField(_('End Time'), null=True, blank=True)
    pilseta = models.ForeignKey(Pilseta, on_delete=models.CASCADE, verbose_name=_('City'))

    class Meta:
        verbose_name = _('Traffic Condition')
        verbose_name_plural = _('Traffic Conditions')

    def __str__(self):
        return f"{self.get_tips_display()} - {self.cela_posms}"

class LietotajaZinojums(models.Model):
    """
    Lietotāja ziņojuma modelis
    """
    zinojums_id = models.AutoField(primary_key=True)
    lietotajs = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'))
    tips = models.CharField(_('Type'), max_length=100,
                            choices=[
                                ('sastregums', _('Congestion')),
                                ('transporta_noslogojums', _('Vehicle Congestion')),
                                ('cela_stavoklis', _('Road Condition')),
                                ('pietura_stavoklis', _('Stop Condition')),
                                ('negadijums', _('Accident')),
                                ('cits', _('Other')),
                            ])
    apraksts = models.TextField(_('Description'))
    gps_koordinates = models.CharField(_('GPS Coordinates'), max_length=100, null=True, blank=True)
    laiks = models.DateTimeField(_('Time'))
    marsruts = models.ForeignKey(Marsruts, on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name=_('Route'))
    pietura = models.ForeignKey(Pietura, on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name=_('Stop'))
    transp = models.ForeignKey(Transportlidzeklis, on_delete=models.SET_NULL, null=True, blank=True,
                               verbose_name=_('Vehicle'))
    pasazieru_skaits = models.IntegerField(_('Passenger Count'), null=True, blank=True)

    class Meta:
        verbose_name = _('User Report')
        verbose_name_plural = _('User Reports')

    def __str__(self):
        return f"{self.get_tips_display()} - {self.lietotajs.username}"


class Atsauksme(models.Model):
    """
    Atsauksmes modelis (route review)
    """
    atsauksme_id = models.AutoField(primary_key=True)
    lietotajs = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'))
    marsruts = models.ForeignKey(Marsruts, on_delete=models.CASCADE, verbose_name=_('Route'))
    teksts = models.TextField(_('Review Text'))
    laiks = models.DateTimeField(_('Time'), auto_now_add=True)
    novērtējums = models.PositiveSmallIntegerField(_('Rating'), null=True, blank=True)

    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        unique_together = ('lietotajs', 'marsruts')

    def __str__(self):
        return f"{self.lietotajs.username} - {self.marsruts.numurs}: {self.teksts[:30]}"