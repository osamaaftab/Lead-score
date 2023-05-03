from django.contrib import admin

from .models import MLAlgorithm, MLAlgorithmStatus, MLRequest

# Register your models here.
admin.site.register(MLRequest)
admin.site.register(MLAlgorithm)
admin.site.register(MLAlgorithmStatus)
