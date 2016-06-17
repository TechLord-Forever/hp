# -*- coding: utf-8 -*-
#
# This file is part of the jabber.at homepage (https://github.com/jabber-at/hp).
#
# This project is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with django-xmpp-account.
# If not, see <http://www.gnu.org/licenses/>.

from django.conf import settings
from django.contrib.auth.models import BaseUserManager
from django.db import transaction
from django.utils import timezone

from django_xmpp_backends import backend

from .constants import REGISTRATION_MANUAL


class UserManager(BaseUserManager):
    def create_user(self, jid, email, password=None):
        user = self.model(jid=jid, email=email, confirmed=timezone.now(),
                          registration_method=REGISTRATION_MANUAL)

        with transaction.atomic():
            user.save(using=self.db)

            if password is None and settings.XMPP_HOSTS[user.domain].get('reserve', False):
                backend.create_reservation(user.node, user.domain, email=email)
            elif password is not None:
                backend.create_user(user.node, user.domain, password, email=email)
        return user

    def create_superuser(self, jid, email, password):
        user = self.create_user(jid, email, password)
        user.is_superuser = True
        user.save()
        return user