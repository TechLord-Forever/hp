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

import configparser
import os
import sys
from datetime import datetime

from fabric.api import local
from fabric.api import runs_once
from fabric.api import task
from fabric.colors import red
from fabric.tasks import Task

from fabric_webbuilders import MinifyCSSTask as MinifyCSSBaseTask
from fabric_webbuilders import MinifyJSTask as MinifyJSBaseTask
from fabric_webbuilders import BuildBootstrapTask
from fabric_webbuilders import BuildJqueryTask


timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
fabdir = os.path.dirname(__file__)

# Currently not working because of general incompetence of the NodeJS community.
build_jquery = BuildJqueryTask(
    excludes='-deprecated',
    dest_dir='hp/core/static/lib/jquery/',
    version='~2'
)
build_bootstrap = BuildBootstrapTask(
    config=os.path.join(fabdir, 'hp/core/static/bootstrap-config.json'),
    dest_dir='hp/core/static/lib/bootstrap/',
    version='~3'
)

configfile = configparser.ConfigParser({
    'home': '/usr/local/home/hp',
    'path': '%(home)s/hp',
    'upstream': 'https://github.com/jabber-at/hp',
    'uwsgi-emperor': '1',
})
configfile.read('fab.conf')


@runs_once
def setup_django(settings_module='hp.settings'):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hp.settings")
    sys.path.insert(0, os.path.join(fabdir, 'hp'))

    import django
    django.setup()


class StaticFilesMixin(object):
    """Mixin to get Django static files."""

    files_setting = None

    def get_file(self, f):
        from django.contrib.staticfiles import finders

        if os.path.isabs(f):
            return f
        return finders.find(f)

    def get_files(self):
        setup_django()

        from django.conf import settings

        if self.files:
            files = self.files
        else:
            files = getattr(settings, self.files_setting)

        for path in files:
            full_path = self.get_file(path)
            if not full_path:
                print(red('Warning: %s could not be found.' % path))
                continue

            yield full_path


class MinifyCSSTask(StaticFilesMixin, MinifyCSSBaseTask):
    files_setting = 'CSS_FILES'


class MinifyJSTask(StaticFilesMixin, MinifyJSBaseTask):
    files_setting = 'JS_FILES'


class DeploymentTaskMixin(object):
    def sudo(self, cmd, chdir=''):
        if chdir:
            return local('ssh %s sudo sh -c \'"cd %s && %s"\'' % (self.host, chdir, cmd))
        else:
            return local('ssh %s sudo %s' % (self.host, cmd))

    def sg(self, cmd, chdir=''):
        if not self.group:
            return self.sudo(cmd, chdir=chdir)

        sg_cmd = 'ssh %s sudo sg %s -c' % (self.host, self.group)
        if chdir:
            return local('%s \'"cd %s && %s"\'' % (sg_cmd, chdir, cmd))
        else:
            return local('%s \'"%s"\'' % (sg_cmd, cmd))

    def pip(self, cmd):
        return self.sudo('%s/bin/pip %s' % (self.venv, cmd))

    def manage(self, cmd):
        return self.sudo('%s/bin/python hp/manage.py %s' % (self.venv, cmd), chdir=self.path)


class SetupTask(DeploymentTaskMixin, Task):
    def run(self, section='DEFAULT'):
        config = configfile[section]
        self.host = config.get('host')
        self.hostname = config.get('hostname')
        self.path = config.get('path')
        self.upstream = config.get('upstream')
        self.venv = config.get('home', self.path).rstrip('/')

        # check source, push it and clone it at remote location
        local('flake8 hp')
        local('git push origin master')
        self.sudo('git clone %s %s' % (self.upstream, self.path))

        # setup virtualenv
        self.sudo('virtualenv -p /usr/bin/python3 %s' % self.venv)
        self.pip('install pip setuptools mysqlclient')
        self.pip('install -U -r %s/requirements.txt' % self.path)

        # setup systemd
        self.sudo('ln -s %s/files/systemd/hp-celery.tmpfiles /etc/tmpfiles.d/hp-celery.conf' %
                  self.path)
        self.sudo('ln -s %s/files/systemd/hp-celery.service /etc/systemd/system/hp-celery.service'
                  % self.path)
        self.sudo('ln -s %s/files/systemd/hp-celery.conf /etc/conf.d/' % self.path)


class DeployTask(DeploymentTaskMixin, Task):
    """Deploy current master."""
    def run(self, section='DEFAULT'):
        local('flake8 hp')
        config = configfile[section]
        self.hostname = config.get('hostname')
        self.host = config.get('host')
        self.path = config.get('path')
        self.venv = config.get('home', self.path).rstrip('/')

        # Run test-suite
        test()

        # push source code
        local('git push origin master')
        self.sudo('git pull origin master', chdir=self.path)
        self.pip('install -U pip setuptools mysqlclient')
        self.pip('install -U -r %s/requirements.txt' % self.path)

        self.sudo('mkdir -p /var/www/%s/static /var/www/%s/media' % (self.hostname, self.hostname))

        # update installation
        self.manage('migrate')
        self.manage('collectstatic --noinput')
        self.manage('compilemessages -l de')

        # restart uwsgi
        if config.getboolean('uwsgi-emperor'):
            vassals_file = config.get('vassals-file',
                                      '/etc/uwsgi-emperor/vassals/%s.ini' % self.hostname)
            self.sudo('touch %s' % vassals_file)

        # reload apache
        self.sudo('systemctl reload apache2')

        # copy logrotate config
        self.sudo('cp %s/files/logrotate/hp-celery /etc/logrotate.d/' % self.path)

        # update systemd files
        systemd_dir = '%s/files/systemd' % self.path
        self.sudo('cp %s/hp-celery.tmpfiles /etc/tmpfiles.d/hp-celery.conf' % systemd_dir)
        self.sudo('cp %s/hp-celery.service /etc/systemd/system/hp-celery.service' % systemd_dir)
        self.sudo('cp %s/hp-celery.conf /etc/conf.d/' % systemd_dir)

        # handle celery
        self.sudo('systemctl daemon-reload')
        self.sudo('systemctl restart hp-celery')

        local('git tag %s/%s' % (self.hostname, datetime.utcnow().strftime('%Y%m%d-%H%M%S')))
        local('git push --tags')


class UploadDoc(DeploymentTaskMixin, Task):
    """Upload documentation to https://jabber.at/doc."""

    def run(self, section='DEFAULT'):
        config = configfile[section]

        local('make -C doc html')
        local('rsync -a --rsync-path="sudo rsync" doc/_build/html/ %s:/var/www/%s/doc/'
              % (config['host'], config['hostname']))


@task
def autodoc():
    """Automatically rebuild documentation on source changes."""
    local('make -C doc clean')
    ignore = '-i *.sw[pmnox] -i *~ -i */4913'
    local('sphinx-autobuild -p 8080 --watch hp %s doc/ doc/_build/html/' % ignore)


@task
def compile_less(dest='hp/core/static/core/css/bootstrap-hp.css'):
    """Compile CSS styles that use bootstrap variables."""

    local('node_modules/.bin/lessc less/bootstrap-hp.less %s' % dest)


@task
def test():
    local('flake8 hp fabfile.py')
    local('isort --check-only --diff -rc hp/ fabfile.py')

    oldcwd = os.getcwd()
    os.chdir('hp')
    local('python -Wd manage.py check')
    local('python manage.py test --settings=hp.test_settings')
    os.chdir(oldcwd)


minify_css = MinifyCSSTask(dest='hp/core/static/hp.css', files=[])
minify_js = MinifyJSTask(dest='hp/core/static/hp.js', files=[])
setup = SetupTask()
deploy = DeployTask()
upload_doc = UploadDoc()
