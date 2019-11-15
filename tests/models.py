from django.db import models


class TestUser(models.Model):
    username = models.CharField(max_length=255)


class Account(models.Model):

    user = models.OneToOneField(TestUser, on_delete=models.CASCADE)
    expired_date = models.DateTimeField()

    @property
    def full_name(self):
        return '{0.first_name} {0.last_name}'.format(self.user)

    def is_expired(self):
        from datetime import datetime
        return self.expired_date > datetime.now()

    @property
    def services(self):
        return Service.objects.filter(cards__account__pk=self.pk)


class Service(models.Model):

    name = models.CharField(max_length=100)


class Card(models.Model):

    account = models.ForeignKey(Account, related_name='cards',
                                on_delete=models.CASCADE)
    services = models.ManyToManyField(Service, related_name='cards')
