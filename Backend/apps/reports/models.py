from django.db import models
from apps.accounts.models import CustomUser

class Report(models.Model):
    REPORT_TYPES = [
        ('excel', 'Excel'),
        ('pdf', 'PDF'),
        ('analytics', 'Analytics')
    ]
    generated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    file_path = models.FileField(upload_to='reports/', blank=True, null=True)

    def __str__(self):
        return f"{self.report_type} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
