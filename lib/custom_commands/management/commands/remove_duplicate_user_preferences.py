#!/usr/bin/env python
import os
import logging

from django.core.management.base import BaseCommand, CommandError
from desktop.models import UserPreferences
from django.db import models, transaction
from django.contrib.auth.models import User


import desktop.conf

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Handler for deleting duplicate UserPreference objects
    """

    def handle(self, *args, **options):
        LOG.warn("HUE_CONF_DIR: %s" % os.environ['HUE_CONF_DIR'])
        LOG.info("DB Engine: %s" % desktop.conf.DATABASE.ENGINE.get())
        LOG.info("DB Name: %s" % desktop.conf.DATABASE.NAME.get())
        LOG.info("DB User: %s" % desktop.conf.DATABASE.USER.get())
        LOG.info("DB Host: %s" % desktop.conf.DATABASE.HOST.get())
        LOG.info("DB Port: %s" % str(desktop.conf.DATABASE.PORT.get()))
        LOG.warn("Deleting ducpliate UserPreference objects")

        for user in User.objects.filter():
            duplicated_records = UserPreferences.objects \
               .values('user', 'key') \
               .annotate(key_count=models.Count('key')) \
               .filter(key_count__gt=1, user = user)
            # Delete all but the first document.
            for record in duplicated_records:
                preferences = UserPreferences.objects \
                    .values_list('id', flat=True) \
                    .filter(
                        user = user,
                        key = record['key'],
                    )[1:]
                preferences = list(preferences)
                LOG.warn("Deleting UserPreferences duplicate ids: %s" % preferences)
                UserPreferences.objects.filter(id__in=preferences).delete()


        transaction.commit()

