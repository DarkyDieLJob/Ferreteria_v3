# models.py
from django.db import models

class Document(models.Model):
    uploaded_file = models.FileField(upload_to='media/')
