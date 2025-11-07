# members/location_models.py
from django.db import models


class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class District(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='districts')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'District'
        verbose_name_plural = 'Districts'
        ordering = ['name']
        unique_together = ('city', 'name')
    
    def __str__(self):
        return f"{self.name} ({self.city.name})"


class Neighborhood(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='neighborhoods')
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Neighborhood'
        verbose_name_plural = 'Neighborhoods'
        ordering = ['name']
        unique_together = ('district', 'name')
    
    def __str__(self):
        return f"{self.name} ({self.district.name}, {self.district.city.name})"
    
    @property
    def city(self):
        return self.district.city