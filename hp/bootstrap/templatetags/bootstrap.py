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
# You should have received a copy of the GNU General Public License along with this project. If
# not, see <http://www.gnu.org/licenses/>.

from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def glyph(glyph, context=None):
    """Outputs the HTML for a glyphicon.

    .. seealso::

       * `Available glyphs <http://getbootstrap.com/components/#glyphicons-glyphs>`_
       * `Available context <http://getbootstrap.com/css/#helper-classes-colors>`_

    Examples::

        {% glyph "ok" %}
        {% glyph "remove" context="danger" %}

    Parameters
    ----------

    glyph : str
        Name of the glyphicon. You only have to give the bare name, e.g. ``"ok"``.
    context : str, optional
        Contextual color of the glyphicon, e.g. ``"danger"``.

    """
    css_class = 'glyphicon glyphicon-%s' % glyph
    if context is not None:
        css_class += ' text-%s' % context
    return format_html('<span class="{}" aria-hidden="true"></span>', css_class)


@register.simple_tag
def glyph_yes():
    """An alias for an "ok" glyph in success context.

    This is the same as ``{% glyph "ok" context="success" %}``.
    """
    return glyph('ok', context='success')


@register.simple_tag
def glyph_no():
    """An alias for a "remove" glyph in danger context.

    This is the same as ``{% glyph "remove" context="danger" %}``.
    """
    return glyph('remove', context='danger')
