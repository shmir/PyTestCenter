"""
:author: yoram@ignissoft.com
"""

from os import path
from sys import platform

from trafficgenerator.tgn_tcl import TgnTclWrapper, get_args_pairs, tcl_file_name, tcl_list_2_py_list


if platform == 'win32':
    app_subdir = 'Spirent TestCenter Application'
else:
    app_subdir = 'Spirent_TestCenter_Application_Linux'


class StcTclWrapper(TgnTclWrapper):
    """ STC Python API over Tcl interpreter. """

    def __init__(self, logger, stc_install_dir, tcl_interp=None):
        super(self.__class__, self).__init__(logger, tcl_interp)
        self.eval('set dir ' + tcl_file_name(path.join(stc_install_dir, app_subdir)))
        self.source(path.join(stc_install_dir, app_subdir, 'pkgIndex.tcl'))
        self.ver = self.eval('package require SpirentTestCenter')

    def stc_command(self, command, *attributes):
        return self.eval('stc::' + command + ' ' + ' '.join(attributes))

    #
    # SpirentTestCenter Tcl package commands.
    #

    def apply(self):
        """ Sends a test configuration to the Spirent TestCenter chassis. """
        self.stc_command('apply')

    def config(self, obj_ref, **attributes):
        """ Set or modifies one or more object attributes, or a relation.

        :param obj_ref: requested object reference.
        :param attributes: dictionary of {attributes: values} to configure.
        """

        self.stc_command('config', obj_ref, get_args_pairs(attributes))

    def create(self, obj_type, parent, **attributes):
        """ Creates one or more Spirent TestCenter Automation objects.

        :param obj_type: object type.
        :param parent: object parent - object will be created under this parent.
        :param attributes: additional attributes.
        :return: STC object reference.
        """

        return self.stc_command('create ' + obj_type + ' -under ' + parent.obj_ref(),
                                get_args_pairs(attributes))

    def delete(self, obj_ref):
        """ Delete the specified object.

        :param obj_ref: object reference of the object to delete.
        """

        return self.stc_command('delete', obj_ref)

    def get(self, obj_ref, attribute=None):
        """ Returns the value(s) of one or more object attributes or a set of object handles.

        :param obj_ref: requested object reference.
        :param attribute: requested attribute. If empty - return values of all object attributes.
        :return: requested value(s) as returned by get command.
            If all attributes were requested the return value is dictionary
            {attrib_name:attrib_val, attrib_name:attrib_val, ..}
            If single attribute was requested, the returned value is simple str.
        """

        output = self.stc_command('get', obj_ref, '-' + attribute if attribute is not None else '')
        if attribute:
            return output
        attributes_dict = dict(zip(*[iter(tcl_list_2_py_list(output))] * 2))
        return dict(zip([s[1:] for s in attributes_dict.keys()], attributes_dict.values()))

    def getList(self, obj_ref, attribute):

        output = self.stc_command('get', obj_ref, '-' + attribute if attribute is not None else '')
        return tcl_list_2_py_list(output)

    def perform(self, command, **arguments):
        """ Execute a command.

        :param command: requested command.
        :param arguments: additional arguments.
        :return: dictionary {attribute, value} as returned by 'perform command'.
        """

        rc = self.stc_command('perform', command, get_args_pairs(arguments))
        self.command_rc = {k[1:]: v for k, v in dict(zip(*[iter(tcl_list_2_py_list(rc))] * 2)).items()}
        return self.command_rc

    def subscribe(self, **arguments):
        """ Subscribe to statistics view.

        :param arguments: subscribe command arguments.
            must arguments: parent, resultParent, configType, resultType
            + additional arguments.
        :return: ResultDataSet handler
        """

        return self.stc_command('subscribe', get_args_pairs(arguments))

    def unsubscribe(self, result_data_set):
        """ Unsubscribe from statistics view.

        :param result_data_set: ResultDataSet handler
        """

        self.stc_command('unsubscribe', result_data_set)

    def wait(self):
        """ Wait until sequencer is finished. """

        self.stc_command('waituntilcomplete')
