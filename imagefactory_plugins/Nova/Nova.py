#
#   Copyright 2014 Red Hat, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import logging
import zope
from imgfac.ApplicationConfiguration import ApplicationConfiguration
from imgfac.OSDelegate import OSDelegate
from novaimagebuilder.Builder import Builder as NIB


class Nova(object):
    zope.interface.implements(OSDelegate)

    def __init__(self):
        super(Nova, self).__init__()
        self.app_config = ApplicationConfiguration().configuration
        self.log = logging.getLogger('%s.%s' % (__name__, self.__class__.__name__))
        self.tdlobj = None
        self.cloud_plugin_content = []
        self.parameters = None
        self.builder = None
        self.nib = None

    def abort(self):
        status = self.nib.abort()
        self.log.debug('aborting... status: %s' % status)

    def create_base_image(self, builder, template, parameters):
        self.log.info('create_base_image() called for Nova plugin - creating a BaseImage')

        self.builder = builder
        self.log.debug('builder set to %s' % builder)
        self.parameters = parameters if parameters else {}
        self.log.debug('parameters set to %s' % parameters)

        # Derive the OSInfo OS short_id from the os_name and os_version in template
        if(template.os_version):
            if(template.os_name[-1].isdigit()):
                install_os = '%s.%s' % (template.os_name, template.os_version)
            else:
                install_os = '%s%s' % (template.os_name, template.os_version)
        else:
            install_os = template.os_name

        install_location = template.install_location
        install_type = self.tdlobj.installtype
        install_script = parameters['install_script']
        install_config = {'admin_password': parameters.get('admin_password'),
                          'license_key': parameters.get('license_key'),
                          'arch': template.os_arch,
                          'disk_size': parameters.get('disk_size'),
                          'flavor': parameters.get('flavor'),
                          'storage': parameters.get('storage'),
                          'name': template.name}

        self.nib = NIB(install_os,
                           install_location,
                           install_type,
                           install_script,
                           install_config)
        #TODO: this needs to be changed to return some reference to the base_image that was created (sloranz)
        self.nib.run()
        self.nib.wait_for_completion(180)

    def create_target_image(self, builder, target, base_image, parameters):
        #self.log.info('create_target_image() called for Nova plugin - creating a TargetImage')
        self.log.info('create_target_image() currently unsupported')

    def add_cloud_plugin_content(self, content):
        self.log.info('add_cloud_plugin_content() currently unsupported')