import uuid

from apps.logistic.models import Lot
from django.db import models


# Create your models here.

class AnalysisPineapple(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lot = models.OneToOneField(Lot, on_delete=models.PROTECT, related_name='analysis_pineapple')
    m0 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0, verbose_name='M0')
    m1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0, verbose_name='M1')
    m2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0, verbose_name='M2')
    m3 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0, verbose_name='M3')
    m4 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0, verbose_name='M4')
    m5 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0, verbose_name='M5')
    mechanical_damage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                            verbose_name='Daño mecánico')
    injury = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                 verbose_name='Golpe o herida')
    sunburn = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                  verbose_name='Quemadura solar')
    nutritional_quality = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                              verbose_name='Calidad nutricional')
    spot = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0, verbose_name='Rancha')
    c6 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0, verbose_name='Calibre 6',
                             editable=False)
    c8 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0, verbose_name='Calibre 8',
                             editable=False)
    c10 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                              verbose_name='Calibre 10', editable=False)
    c12 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                              verbose_name='Calibre 12', editable=False)
    c14 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                              verbose_name='Calibre 14', editable=False)
    visual_quality = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                         verbose_name='Calidad visual')
    sampling = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                   verbose_name='Muestreo')
    destructive_analysis = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                               verbose_name='Análisis destructivo')
    brix_m0 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                  verbose_name='Brix M0')
    ph_m0 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0, verbose_name='Ph M0')
    brix_m1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                  verbose_name='Brix M1')
    ph_m1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0, verbose_name='Ph M1')
    brix_m2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                  verbose_name='Brix M2')
    ph_m2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0, verbose_name='Ph M2')
    brix_m3 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                  verbose_name='Brix M3')
    ph_m3 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0, verbose_name='Ph M3')
    brix_m4 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                  verbose_name='Brix M4')
    ph_m4 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0, verbose_name='Ph M4')
    brix_m5 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                  verbose_name='Brix M5')
    ph_m5 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0, verbose_name='Ph M5')
    crown_c6 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                   verbose_name='Corona C6')
    fruit_c6 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                   verbose_name='Fruto C6')
    crown_c8 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                   verbose_name='Corona C8')
    fruit_c8 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                   verbose_name='Fruto C8')
    crown_c10 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                    verbose_name='Corona C10')
    fruit_c10 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                    verbose_name='Fruto C10')
    crown_c12 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                    verbose_name='Corona C12')
    fruit_c12 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                    verbose_name='Fruto C12')
    crown_c14 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                    verbose_name='Corona C14')
    fruit_c14 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                    verbose_name='Fruto C14')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Análisis de piña'
        verbose_name_plural = 'Análisis de piñas'
        ordering = ['-lot__datetime_download_started']

    def __str__(self):
        return str(self.lot.lot)


class AnalysisSweetPotato(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lot = models.OneToOneField(Lot, on_delete=models.PROTECT, related_name='analysis_sweet_potato')
    m1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0, verbose_name='M1')
    m2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0, verbose_name='M2')
    mechanical_damage_cracked = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                                    verbose_name='Daño mecánico rajado')
    green_traits = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                       verbose_name='Rasgos verdes')
    worm_damage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                      verbose_name='Daño de gusano')
    fungal_presence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                          verbose_name='Presencia de hongos')
    rot = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0, verbose_name='Podrido')
    root_presence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                        verbose_name='Presencia de raíces')
    length_lt_8 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                      verbose_name='Largo menor a 8cm')
    length_8_11 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                      verbose_name='Largo 8 a 11cm')
    length_11_15 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                       verbose_name='Largo 11 a 15cm')
    length_gt_15 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                       verbose_name='Largo mayor a 15cm')
    width_lt_7 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                     verbose_name='Ancho menor a 7cm')
    width_7_9 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                    verbose_name='Ancho 7 a 9cm')
    width_9_12 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                     verbose_name='Ancho 9 a 12cm')
    width_gt_12 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                      verbose_name='Ancho mayor a 12cm')
    visual = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                 verbose_name='Visual')
    sampling = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                   verbose_name='Muestreo')
    destructive_analysis = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                               verbose_name='Análisis destructivo')
    bm1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0, verbose_name='Brix M1')
    ph_m1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0, verbose_name='Ph M1')
    bm2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0, verbose_name='Brix M2')
    ph_m2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0, verbose_name='Ph M2')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.lot.lot)

    class Meta:
        verbose_name = 'Análisis de camote'
        verbose_name_plural = 'Análisis de camotes'
        ordering = ['-lot__datetime_download_started']
