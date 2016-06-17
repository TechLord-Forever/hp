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

from django import forms
from django.utils.html import format_html


class BootstrapWidgetMixin(object):
    def __init__(self, attrs=None):
        attrs = attrs or {}
        if attrs.get('class'):
            attrs['class'] += ' form-control'
        else:
            attrs['class'] = ' form-control'
        super(BootstrapWidgetMixin, self).__init__(attrs=attrs)

    def render(self, *args, **kwargs):
        widget = super(BootstrapWidgetMixin, self).render(*args, **kwargs)
        return format_html('<div class="col-sm-10">{}</div>', widget)


class BootstrapTextInput(BootstrapWidgetMixin, forms.TextInput):
    pass


class BootstrapEmailInput(BootstrapWidgetMixin, forms.EmailInput):
    pass