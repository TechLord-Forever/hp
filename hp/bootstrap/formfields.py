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
from django.contrib.auth import password_validation
from django.forms.renderers import get_default_renderer
from django.forms.utils import flatatt
from django.utils.html import mark_safe

from . import widgets


class BoundField(forms.boundfield.BoundField):
    """Overwrite BoundField to provide customised widget rendering and the formgroup() method.

    A BoundField is a form field in the context of a form.

    .. seealso:: https://docs.djangoproject.com/en/dev/ref/forms/api/#django.forms.BoundField
    """

    def formgroup_attrs(self):
        """HTML attributes for the top-level form-group div."""

        fg_attrs = dict(self.field.formgroup_attrs)
        fg_attrs.setdefault('id', 'fg_%s' % self.html_name)
        if fg_attrs.get('class'):
            fg_attrs['class'] += ' form-group'
        else:
            fg_attrs['class'] = 'form-group'

        if self.field.formgroup_class:
            fg_attrs['class'] += ' %s' % self.field.formgroup_class

        if self.errors:
            fg_attrs['class'] += ' has-error'

        # Add the success class only in bound (=submitted) and if the field has the add_success
        # property set to True (and there are no errors, obviously).
        elif self.form.is_bound and not self.errors and self.field.add_success:
            # Add the class only if the field is required or data was actually submitted.  The
            # class is thus not added if the user did not enter any data to a field that was not
            # required.
            if self.field.required or self.data:
                fg_attrs['class'] += ' has-success'

        if getattr(self.field.widget, 'feedback', False):
            fg_attrs['class'] += ' has-feedback'  # used by glyphicons

        return flatatt(fg_attrs)

    def input_grid_attrs(self):
        return flatatt(self.field.get_input_grid_attrs())

    @property
    def help_id(self):
        return 'hb_%s' % self.html_name

    @property
    def glyphicon(self):
        raise Exception('glyphicon()')

    def build_widget_attrs(self, attrs, widget):
        attrs = super(BoundField, self).build_widget_attrs(attrs, widget)

        if self.help_text or self.errors:
            # Add the 'aria-describedby' attribute to the <input /> element. It's the id used by
            # the help-block describing the element and helps screen readers. See:
            #   http://getbootstrap.com/css/#forms-help-text
            attrs['aria-describedby'] = self.help_id

        # HACK: we pass the status as attribute that is then pop()'d by widget context
        if self.form.is_bound:
            if self.errors:
                attrs['status'] = 'error'
            elif self.field.required:
                attrs['status'] = 'ok'

        return attrs

    def formgroup(self):
        renderer = self.form.renderer or get_default_renderer()
        context = {'field': self}
        return mark_safe(renderer.render(self.field.formgroup_template, context))

    def label_tag(self, contents=None, attrs=None, label_suffix=None):
        """Add the control-label and col-sm-2 class to label tags."""

        attrs = attrs or {}
        if 'class' in attrs:
            attrs['class'] += ' control-label %s' % self.field.get_label_grid_class()
        else:
            attrs['class'] = 'control-label %s' % self.field.get_label_grid_class()

        return super(BoundField, self).label_tag(contents, attrs=attrs, label_suffix=label_suffix)


class BootstrapMixin(object):
    """Mixin that adds the form-control class used by bootstrap to input widgets."""

    add_success = True
    formgroup_class = None
    label_cols = 2
    input_cols = 10
    col_class = 'sm'

    formgroup_template = 'bootstrap/forms/formgroup.html'

    def __init__(self, **kwargs):
        self.formgroup_attrs = kwargs.pop('formgroup_attrs', {})

        if 'add_success' in kwargs:
            self.add_success = kwargs.pop('add_success')

        self.label_cols = kwargs.pop('label_cols', self.label_cols)
        self.input_cols = kwargs.pop('input_cols', self.input_cols)
        self.col_class = kwargs.pop('col_class', self.col_class)

        super(BootstrapMixin, self).__init__(**kwargs)

    def get_label_grid_class(self):
        return 'col-%s-%s' % (self.col_class, self.label_cols)

    def get_input_grid_class(self):
        return 'col-%s-%s' % (self.col_class, self.input_cols)

    def get_input_grid_attrs(self):
        return {'class': self.get_input_grid_class()}

    def get_bound_field(self, form, field_name):
        return BoundField(form, self, field_name)

    def get_help_text(self):
        return ''


class BootstrapCharField(BootstrapMixin, forms.CharField):
    widget = widgets.BootstrapTextInput


class BootstrapTextField(BootstrapMixin, forms.CharField):
    widget = widgets.BootstrapTextarea


class BootstrapEmailField(BootstrapMixin, forms.EmailField):
    widget = widgets.BootstrapEmailInput

    def clean(self, value):
        value = super(BootstrapEmailField, self).clean(value)
        if value:
            value = value.lower()
        return value


class BootstrapPasswordField(BootstrapMixin, forms.CharField):
    widget = widgets.BootstrapPasswordInput
    add_success = False

    def __init__(self, *args, **kwargs):
        if kwargs.pop('add_min_length', False):
            for validator in password_validation.get_default_password_validators():
                if isinstance(validator, password_validation.MinimumLengthValidator):
                    kwargs.setdefault('min_length', validator.min_length)
                    break
        super(BootstrapPasswordField, self).__init__(*args, **kwargs)


class BootstrapChoiceField(BootstrapMixin, forms.ChoiceField):
    widget = widgets.BootstrapSelect


class BootstrapFileField(BootstrapMixin, forms.FileField):
    widget = widgets.BootstrapFileInput
