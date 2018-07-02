"""
:author: yoram@ignissoft.com
"""

import os
import posixpath
import imp
from sys import platform

if platform == 'win32':
    app_subdir = 'Spirent TestCenter Application'
else:
    app_subdir = 'Spirent_TestCenter_Application_Linux'


class StcPythonWrapper(object):

    def __init__(self, logger, stc_install_dir):
        """ Init STC Python package.

        Add logger to log STC python package commands only.
        This creates a clean python script that can be used later for debug.
        """

        super(self.__class__, self).__init__()
        stc_private_install_dir = posixpath.sep.join([stc_install_dir, app_subdir])
        os.environ['STC_PRIVATE_INSTALL_DIR'] = stc_private_install_dir
        stc_python_module = posixpath.sep.join([stc_private_install_dir, 'API/Python/StcPython.py'])
        self.stc = imp.load_source('StcPython', stc_python_module).StcPython()

    def create(self, obj_type, parent, **attributes):
        """ Creates one or more Spirent TestCenter Automation objects.

        :param obj_type: object type.
        :param parent: object parent - object will be created under this parent.
        :param attributes: additional attributes.
        :return: STC object reference.
        """

        return self.stc.create(obj_type, under=parent.obj_ref(), **attributes)

    def perform(self, command, **arguments):
        """ Execute a command.

        :param command: requested command.
        :param arguments: additional arguments.
        :return: dictionary {attribute, value} as returned by 'perform command'.
        """

        self.command_rc = self.stc.perform(command, **arguments)
        return self.command_rc

    def get(self, obj_ref, attribute=[]):
        """ Returns the value(s) of one or more object attributes or a set of object handles.

        :param obj_ref: requested object reference.
        :param attribute: requested attribute. If empty - return values of all object attributes.
        :return: requested value(s) as returned by get command.
        """

        return self.stc.get(obj_ref, attribute)

    def getList(self, obj_ref, attribute):
        """ Returns the value of the object attributes or a python list.

        :param obj_ref: requested object reference.
        :param attribute: requested attribute.
        :return: requested value as returned by get command.
        """

        return self.stc.get(obj_ref, attribute).split()

    def config(self, obj_ref, **attributes):
        """ Set or modifies one or more object attributes, or a relation.

        :param obj_ref: requested object reference.
        :param attributes: dictionary of {attributes: values} to configure.
        """

        self.stc.config(obj_ref, **attributes)

    def apply(self):
        """ Sends a test configuration to the Spirent TestCenter chassis. """

        self.stc.apply()

    def subscribe(self, **arguments):
        """ Subscribe to statistics view.

        :param arguments: subscribe command arguments.
            must arguments: parent, resultParent, configType, resultType
            + additional arguments.
        :return: ResultDataSet handler
        """

        return self.stc.subscribe(**arguments)

    def unsubscribe(self, result_data_set):
        """ Unsubscribe from statistics view.

        :param result_data_set: ResultDataSet handler
        """

        self.stc.unsubscribe(result_data_set)

    def wait(self):
        """ Wait until sequencer is finished. """

        self.stc.waitUntilComplete()
