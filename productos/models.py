from django.db import models
from authentication.models import User

class Storage(models.Model):

    CATEGORY_OPTIONS=[
        ('ONLINE_SERVICES','ONLINE_SERVICES'),
        ('VIAJES', 'Viajes'),
        ('COMIDA', 'COMIDA'),
        ('DEPORTES', 'DEPORTES'),
        ('OTHERS', 'OTHERS')
        ]

    category = models.CharField(choices=CATEGORY_OPTIONS, max_length=255)
    precios = models.DecimalField(max_digits=10, decimal_places=2,max_length=255)
    descripcion = models.TextField()
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    date = models.DateField(null = False, blank=False)

    class Meta:
        ordering:['-date']
    
    def __str__(self):
        return str(self.owner)+'s income'