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
import os.path
import shutil
from imgfac.ApplicationConfiguration import ApplicationConfiguration
from imgfac.OSDelegate import OSDelegate
from imgfac.ImageFactoryException import ImageFactoryException
from novaimagebuilder.Builder import Builder as NIB
from novaimagebuilder.StackEnvironment import StackEnvironment

PROPERTY_NAME_GLANCE_ID = 'x-image-properties-glance_id'


class Nova(object):
    zope.interface.implements(OSDelegate)

    def __init__(self):
        super(Nova, self).__init__()
        self.app_config = ApplicationConfiguration().configuration
        self.log = logging.getLogger('%s.%s' % (__name__, self.__class__.__name__))
        self.nib = None

    def abort(self):
        if self.nib and isinstance(self.nib, NIB):
            status = self.nib.abort()
            self.log.debug('aborting... status: %s' % status)
        else:
            self.log.debug('No active Nova Image Builder instance found, nothing to abort.')

    def create_base_image(self, builder, template, parameters):
        self.log.info('create_base_image() called for Nova plugin - creating a BaseImage')

        self.log.debug('Nova.create_base_image() called by builder (%s)' % builder)
        parameters = parameters if parameters else {}
        self.log.debug('parameters set to %s' % parameters)

        builder.base_image.update(5, 'PENDING', 'Collecting build arguments to pass to Nova Image Builder...')
        # Derive the OSInfo OS short_id from the os_name and os_version in template
        if template.os_version:
            if template.os_name[-1].isdigit():
                install_os = '%s.%s' % (template.os_name, template.os_version)
            else:
                install_os = '%s%s' % (template.os_name, template.os_version)
        else:
            install_os = template.os_name

        install_location = template.install_location
        install_type = template.installtype
        install_script = parameters.get('install_script')
        install_config = {'admin_password': parameters.get('admin_password'),
                          'license_key': parameters.get('license_key'),
                          'arch': template.os_arch,
                          'disk_size': parameters.get('disk_size'),
                          'flavor': parameters.get('flavor'),
                          'storage': parameters.get('storage'),
                          'name': template.name}

        builder.base_image.update(10, 'BUILDING', 'Created Nova Image Builder instance...')
        self.nib = NIB(install_os, install_location, install_type, install_script, install_config)
        self.nib.run()

        builder.base_image.update(10, 'BUILDING', 'Waiting for Nova Image Builder to complete...')
        os_image_id = self.nib.wait_for_completion(180)
        if os_image_id:
            builder.base_image.properties[PROPERTY_NAME_GLANCE_ID] = os_image_id
            builder.base_image.update(100, 'COMPLETE', 'Image stored in glance with id (%s)' % os_image_id)
        else:
            exc_msg = 'Nova Image Builder failed to return a Glance ID, failing...'
            builder.base_image.update(status='FAILED', error=exc_msg)
            self.log.exception(exc_msg)
            raise ImageFactoryException(exc_msg)

    def create_target_image(self, builder, target, base_image, parameters):
        self.log.info('create_target_image() called for Nova plugin - creating TargetImage')
        base_img_path = base_image.data
        target_img_path = builder.target_image.data

        builder.target_image.update(5, 'PENDING', 'Copying base image...')
        if os.path.exists(base_img_path) and os.path.getsize(base_img_path):
            try:
                shutil.copyfile(base_img_path, target_img_path)
            except IOError as e:
                builder.target_image.update(status='FAILED', error='Error copying base image: %s' % e)
                self.log.exception(e)
                raise e
        else:
            glance_id = base_image.properties[PROPERTY_NAME_GLANCE_ID]
            base_img_file = StackEnvironment().download_image_from_glance(glance_id)
            with open(builder.target_image.data, 'wb') as target_img_file:
                shutil.copyfileobj(base_img_file, target_img_file)
            base_img_file.close()

    def add_cloud_plugin_content(self, content):
        self.log.info('add_cloud_plugin_content() currently unsupported')