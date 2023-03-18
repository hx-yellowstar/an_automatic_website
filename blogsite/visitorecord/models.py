from django.db import models


class VisitorInfo(models.Model):
    host = models.CharField(max_length=150)
    full_request = models.CharField(max_length=20000)
    remote_addr = models.CharField(max_length=600)
    proxy_remote_ip = models.CharField(max_length=600)
    user_agent = models.CharField(max_length=600)
    visitime = models.CharField(max_length=600)

    objects = models.Manager()
