"""
STC REST wrapper.
"""
import getpass
import logging
from random import randint
from typing import List, Optional

from stcrestclient import stchttp


class StcRestWrapper:
    """STC Python API over REST Server."""

    def __init__(self, logger: logging.Logger, server, port=80, user_name=getpass.getuser(), session_name=None):
        """Init STC REST client.

        :TODO: Add logger to log STC REST commands only. This creates a clean REST script that can be used later for debug.

        :param logger: Package logger.
        :param server: STC REST API server address.
        :param port: STC REST API HTTP port.
        :param user_name: user name, part of session ID.
        :param session_name: session, name part of session ID.
        """
        debug_print = logger.level == 10
        self.client = stchttp.StcHttp(server, port, debug_print=debug_print)
        if session_name:
            self.session_id = self.client.join_session(session_name)
        else:
            session_name = "session" + str(randint(0, 99))
            self.session_id = self.client.new_session(user_name, session_name, kill_existing=True)
        self.command_rc = None

    def disconnect(self, terminate):
        self.client.end_session(terminate)

    def create(self, obj_type, parent, **attributes):
        """Creates one or more Spirent TestCenter Automation objects.

        :param obj_type: object type.
        :param parent: object parent - object will be created under this parent.
        :param attributes: additional attributes.
        :return: STC object reference.
        """
        return self.client.create(obj_type, under=parent.ref, **attributes)

    def delete(self, obj_ref):
        """Delete Spirent TestCenter Automation object.

        :param obj_ref: object handle to delete.
        """
        self.client.delete(obj_ref)

    def perform(self, command, **arguments):
        """Execute a command.

        :param command: requested command.
        :param arguments: additional arguments.
        """
        if command in ["CSTestSessionConnect", "CSTestSessionDisconnect"]:
            return
        self.command_rc = self.client.perform(command, **arguments)
        return self.command_rc

    def get(self, obj_ref: str, attribute: Optional[str] = "") -> str:
        """Returns the value(s) of one or more object attributes or a set of object handles.

        :param obj_ref: requested object reference.
        :param attribute: requested attribute. If empty - return values of all object attributes.
        :return: requested value(s) as returned by get command.
        """
        output = self.client.get(obj_ref, attribute)
        return output if isinstance(output, str) else " ".join(output)

    def getList(self, obj_ref: str, attribute: str) -> List[str]:
        """Returns the value of the object attributes or a python list.

        :param obj_ref: requested object reference.
        :param attribute: requested attribute.
        :return: requested value as returned by get command.
        """
        return self.client.get(obj_ref, attribute).split()

    def config(self, obj_ref, **attributes):
        """Set or modifies one or more object attributes, or a relation.

        :param obj_ref: requested object reference.
        :param attributes: dictionary of {attributes: values} to configure.
        """
        self.client.config(obj_ref, attributes)

    def subscribe(self, **arguments):
        """Subscribe to statistics view.

        :param arguments: subscribe command arguments.
            must arguments: parent, resultParent, configType, resultType
            + additional arguments.
        :return: ResultDataSet handler
        """
        return self.perform("ResultsSubscribe", **arguments)["ReturnedDataSet"]

    def unsubscribe(self, result_data_set):
        """Unsubscribe from statistics view.

        :param result_data_set: ResultDataSet handler
        """
        self.perform("ResultDataSetUnsubscribe", ResultDataSet=result_data_set)

    def apply(self):
        """Sends a test configuration to the Spirent TestCenter chassis."""
        self.client.apply()

    def wait(self):
        """Wait until sequencer is finished."""
        self.client.wait_until_complete()
