from django.db import models

from .workflow import State

class Analysis(State):
    datetime = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100)
    contact = models.EmailField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    value = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Analyse'