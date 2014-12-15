from django.db import models

class Account(models.Model):

    user = models.OneToOneField('auth.User')
    expired_date = models.DateTimeField()

    @property
    def full_name(self):
        return '{0.first_name} {0.last_name}'.format(self.user)

    def is_expired(self):
        from datetime import datetime
        return self.expired_date > datetime.now()

class Service(models.Model):

    name = models.CharField(max_length=100)

class Card(models.Model):

    account = models.ForeignKey(Account, related_name='cards')
    services = models.ManyToManyField(Service, related_name='+')

