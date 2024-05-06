import os
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser, User


# Create your models here.
class File(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    subject = models.CharField(name="Subject", max_length=255)
    fid = models.IntegerField(name="fid")
    count = models.IntegerField(name="count")
    filename = models.CharField(max_length=255, name="filename")
    pages = models.IntegerField(name="pages")
    file = models.FileField(upload_to="files", name="file")
    printed = models.BooleanField(name="Printed", default=False)
    copies = models.IntegerField(name="Copies", default=1)
    doubleSided = models.BooleanField(name="DoubleSided", default=False)
    paymentStatus = models.BooleanField(name="PaymentStatus", default=False)

    def __str__(self):
        return f"{self.fid}-{self.count}"


@receiver(pre_delete, sender=File)
def delete_file_with_entry(sender, instance, **kwargs):
    if instance.file:
        file_path = instance.file.path
        if os.path.exists(file_path):
            os.remove(file_path)


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    fid = models.ForeignKey(File, on_delete=models.DO_NOTHING)
    transactionId = models.CharField(name="TransactionID", max_length=100)
    amount = models.FloatField(name="Amount")
    status = models.CharField(name="Status", max_length=100)


class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    balance = models.FloatField(verbose_name="Wallet Balance", name="Wallet Balance")
