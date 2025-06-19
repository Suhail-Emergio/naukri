from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class CompanyDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length = 250, default="")
    logo = models.FileField(upload_to="images/company/logo", null=True, blank=True)
    about = models.TextField()
    website = models.URLField(max_length = 200)
    functional_area = models.CharField(max_length=250)
    address = models.JSONField()
    city = models.CharField(max_length = 250)
    state = models.CharField(max_length = 250, default='')
    postal_code = models.CharField(max_length=6)
    pan_no = models.CharField(max_length=10, default='')
    gst_no = models.CharField(max_length=100, default='')
    mca_no = models.CharField(max_length=100, null=True, blank=True)