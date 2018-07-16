"""
:author: yoram@ignissoft.com
"""

import getpass
from random import randint

from stcrestclient import stchttp


class StcRestWrapper(object):

    def __init__(self, logger, server, port=80, user_name=getpass.getuser(), session_name=None):
        """ Init STC REST client.

        :param server: STC REST API server address.
        :param port: STC REST API HTTP port.
        :param user_name: user name, part of session ID.
        :param session_name: session, name part of session ID.

        Add logger to log STC REST commands only.
        This creates a clean REST script that can be used later for debug.
        """

        super(self.__class__, self).__init__()
        debug_print = True if logger.level == 10 else False
        self.ls = stchttp.StcHttp(server, port, debug_print=debug_print)
        if session_name:
            self.session_id = self.ls.join_session(session_name)
        else:
            session_name = 'session' + str(randint(0, 99))
            self.session_id = self.ls.new_session(user_name, session_name, kill_existing=True)

    def disconnect(self, terminate):
        self.ls.end_session(terminate)

    def create(self, obj_type, parent, **attributes):
        """ Creates one or more Spirent TestCenter Automation objects.

        :param obj_type: object type.
        :param parent: object parent - object will be created under this parent.
        :param attributes: additional attributes.
        :return: STC object reference.
        """

        return self.ls.create(obj_type, under=parent.obj_ref(), **attributes)

    def perform(self, command, **arguments):
        """ Execute a command.

        :param command: requested command.
        :param arguments: additional arguments.
        """

        if (command in ['CSTestSessionConnect', 'CSTestSessionDisconnect']):
            return
        self.command_rc = self.ls.perform(command, **arguments)
        return self.command_rc

    def get(self, obj_ref, attribute=''):
        """ Returns the value(s) of one or more object attributes or a set of object handles.

        :param obj_ref: requested object reference.
        :param attribute: requested attribute. If empty - return values of all object attributes.
        :return: requested value(s) as returned by get command.
        """

        return self.ls.get(obj_ref, attribute)

    def getList(self, obj_ref, attribute):
        """ Returns the value of the object attributes or a python list.

        :param obj_ref: requested object reference.
        :param attribute: requested attribute.
        :return: requested value as returned by get command.
        """

        return self.ls.get(obj_ref, attribute).split()

    def config(self, obj_ref, **attributes):
        """ Set or modifies one or more object attributes, or a relation.

        :param obj_ref: requested object reference.
        :param attributes: dictionary of {attributes: values} to configure.
        """

        self.ls.config(obj_ref, **attributes)

    def subscribe(self, **arguments):
        """ Subscribe to statistics view.

        :param arguments: subscribe command arguments.
            must arguments: parent, resultParent, configType, resultType
            + additional arguments.
        :return: ResultDataSet handler
        """

        return self.perform('ResultsSubscribe', **arguments)['ReturnedDataSet']

    def unsubscribe(self, result_data_set):
        """ Unsubscribe from statistics view.

        :param result_data_set: ResultDataSet handler
        """

        self.perform('ResultDataSetUnsubscribe', ResultDataSet=result_data_set)

    def apply(self):
        """ Sends a test configuration to the Spirent TestCenter chassis. """

        self.ls.apply()

    def wait(self):
        """ Wait until sequencer is finished. """

        self.ls.wait_until_complete()
