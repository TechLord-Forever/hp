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
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect

from .models import CachedMessage


class SiteMiddleware(object):
    def process_request(self, request):
        host = request.META.get('HTTP_HOST', request.META.get('SERVER_NAME'))
        config = getattr(settings, 'XMPP_HOSTS_MAPPING', {}).get(host)
        if config is None:
            config = settings.DEFAULT_XMPP_HOST

        request.site = settings.XMPP_HOSTS[config]
        request.site['DOMAIN'] = config
        request.site.setdefault('BRAND', getattr(settings, 'BRAND', config))


class TranslatedUrlConfigMiddleware(object):
    """Middleware to handle translated paths."""

    def process_view(self, request, view_func, view_args, view_kwargs):
        match = request.resolver_match
        if getattr(match.func, 'translated_match', False):
            url_name = match.url_name  # "name" parameter in the URL config
            if match.namespace:
                url_name = '%s:%s' % (match.namespace, url_name)

            return HttpResponseRedirect(reverse(url_name))


class CeleryMessageMiddleware(object):
    def process_request(self, request):
        if request.user.is_anonymous():
            return

        with transaction.atomic():
            stored_msgs = CachedMessage.objects.filter(user=request.user)
            if stored_msgs:
                for msg in stored_msgs:
                    messages.add_message(request, msg.level, msg.message)

                stored_msgs.delete()
