from django.db import models


class Case(models.Model):
    title = models.CharField('Наименование', max_length=200)
    path = models.FilePathField('Путь к конфигурации', path='')
