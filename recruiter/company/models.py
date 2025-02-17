from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class CompanyDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length = 250, default="")
    logo = models.FileField(upload_to="images/company/logo")
    about = models.TextField()
    website = models.URLField(max_length = 200)
    functional_area = models.CharField(max_length=250)
    address = models.JSONField()
    city = models.CharField(max_length = 250)
    country = models.CharField(max_length = 250)
    postal_code = models.CharField(max_length=6)
    contact_name = models.CharField(max_length = 100)
    contact_land_number = models.CharField(max_length = 10)
    contact_mobile_number = models.CharField(max_length = 10)
    designation = models.CharField(max_length = 200)