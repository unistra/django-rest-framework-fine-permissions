from django.db import models

class Account(models.Model):

    user = models.OneToOneField('auth.User')
    expired_date = models.DateField()
    wifi_group = models.CharField(max_length=100)
    vpn_group = models.CharField(max_length=100)
    profile = models.CharField(max_length=100)

    @property
    def full_name(self):
        return '{0.first_name} {0.last_name}'.format(self.user)

    def is_expired(self):
        from datetime import date
        return self.expired_date > date.today()

class Service(models.Model):

    name = models.CharField(max_length=100)

class Card(models.Model):

    account = models.ForeignKey(Account, related_name='cards')
    services = models.ManyToManyField(Service, related_name='+')
