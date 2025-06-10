# transport/admin.py
from django.contrib import admin
from .models import *

admin.site.register(Pilseta)
admin.site.register(TransportaVeids)
admin.site.register(Marsruts)
admin.site.register(Transportlidzeklis)
admin.site.register(Pietura)
admin.site.register(MarsrutaPietura)
admin.site.register(KustibasGrafiks)
admin.site.register(SatiksmeStavoklis)
admin.site.register(LietotajaZinojums)