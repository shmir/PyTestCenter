"""
Classes and utilities to manage STC statistics views.
"""

from testcenter.stc_object import StcObject


class StcStats(object):
    """ Represents statistics view.

    The statistics dictionary represents a table:
    Statistics Name | Object 1 Value | Object 2 Value | ...
    object          |                |                |
    parents         |                |                |
    topLevelName    |                |                |
    Stat 1          |                |                |
    ...

    For example, generatorportresults statistics for two ports might look like the following:
    Statistics Name     | Object 1 Value           | Object 2 Value
    object              | analyzerportresults1     | analyzerportresults2
    parents             | project1/port1/analyzer1 | project1/port2/analyzer2
    topLevelName        | Port 1                   | Port 2
    GeneratorFrameCount | 1000                     | 2000
    ...
    """

    statistics = {}

    def __init__(self, project, view):
        """ Subscribe to view with default configuration type as defined by config_2_type.

        :param project: parent project object for all statistics.
        :param view: statistics view to subscribe to. If view is None it is the test responsibility to subscribe with
            specific config_type.
        """

        super(StcStats, self).__init__()
        self.project = project
        if view:
            self.subscribe(view, view_2_config_type[view.lower()])
        self.statistics = {}

    def subscribe(self, view, config_type):
        """ Subscribe to statistics view.

        :parama view: statistics view to subscribe to.
        :parama config_type: configuration type to subscribe to.
        """

        rds = self.project.api.subscribe(Parent=self.project.obj_ref(), ResultParent=self.project.obj_ref(),
                                         ConfigType=config_type, ResultType=view)
        self.rds = StcObject(ObjType='ResultDataSet', parent=self.project, objRef=rds)

    def unsubscribe(self):
        """ UnSubscribe from statistics view. """

        self.project.api.unsubscribe(self.rds.obj_ref())

    def read_stats(self, *stats):
        """ Reads the statistics view from STC and saves it in statistics dictionary.

        :param stats: list of statistics names to read, empty list will read all statistics.

        :todo: add support for user and dynamic statistics.
        """

        self.statistics = {}

        objs_stats = []
        self.project.api.perform('RefreshResultView', ResultDataSet=self.rds.obj_ref())
        for page_number in range(1, int(self.rds.get_attribute('TotalPageCount')) + 1):
            self.rds.set_attributes(PageNumber=page_number)
            for results in self.rds.get_objects_from_attribute('ResultHandleList'):
                parent = results.get_object_from_attribute('parent')
                parents = parent.obj_ref()
                name = ''
                while parent != self.project:
                    if not name and parent.obj_type().lower() in ('port', 'emulateddevice', 'streamblock'):
                        name = parent.get_name()
                    parent = parent.obj_parent()
                    parents = parent.obj_ref() + '/' + parents
                obj_stats = ({'object': results.obj_ref(), 'parents': parents, 'topLevelName': name})
                obj_stats.update(results.get_attributes(*stats))
                obj_stats.pop('parent', None)
                obj_stats.pop('Name', None)
                obj_stats.pop('resultchild-Sources', None)
                objs_stats.append(obj_stats.values())
                keys = obj_stats.keys()
        if objs_stats:
            self.statistics = dict(zip(keys, zip(*objs_stats)))

    def get_stats(self, row='topLevelName'):
        """
        :param row: requested row (== statistic name)
        :returns: all statistics values for the requested row.
        """
        return self.statistics[row]

    def get_object_stats(self, obj_id, obj_id_stat='topLevelName'):
        """
        :param obj_id: requested object ID.
        :param obj_id_stat: which statistics name to use as object ID, sometimes topLevelName is
            not meaningful and it is better to use other unique identifier like stream ID.
        :returns: all statistics values for the requested object ID.
        """

        obj_statistics = {}
        for counter in self.statistics.keys():
            if self.statistics[counter]:
                obj_statistics[counter] = self.get_stat(obj_id, counter, obj_id_stat)
        return obj_statistics

    def get_stat(self, obj_id, counter, obj_id_stat='topLevelName'):
        """
        :param obj_id: requested object id.
        :param counter: requested statistics (note that some statistics are not counters).
        :param obj_id_stat: which statistics name to use as object ID, sometimes topLevelName is
            not meaningful and it is better to use other unique identifier like stream ID.
        :returns: the value of the requested counter for the requested object ID.
        """
        obj_index = self.statistics[obj_id_stat].index(obj_id)
        return self.statistics[counter][obj_index]

    def get_counter(self, obj_id, counter, obj_id_stat='topLevelName'):
        """
        :param obj_id: requested object ID.
        :param counter: requested statistics (note that some statistics are not counters).
        :param obj_id_stat: which statistics name to use as object ID, sometimes topLevelName is
            not meaningful and it is better to use other unique identifier like stream ID.
        :returns: the int value of the requested counter for the requested object ID.
        """
        return int(self.get_stat(obj_id, counter, obj_id_stat))

view_2_config_type = {
    'igmpgroupmembershipresults': 'IgmpGroupMembership',
    'igmprouterresults': 'IgmpRouterConfig',
    'ldplspresults': 'LdpRouterConfig',
    'eoamlinktraceresults': 'EoamMaintenancePointConfig',
    'ospfv2routerresults': 'Ospfv2RouterConfig',
    'portavglatencyresults': 'Analyzer',
    'riprouterresults': 'RipRouterConfig',
    'eoamloopbackresults': 'EoamMaintenancePointConfig',
    'dhcpv4portresults': 'Dhcpv4PortConfig',
    'txstreamresults': 'StreamBlock',
    'pppoeportresults': ('PppoaClientBlockConfig', 'PppoaServerBlockConfig', 'PppoeClientBlockConfig',
                         'PppoeServerBlockConfig', 'PppoL2tpv2ClientBlockConfig', 'PppoL2tpv2ServerBlockConfig',
                         'PppoxPortConfig', 'PppProtocolConfig'),
    'eoamlossmeasurementresponserxresults': 'EoamMaintenancePointConfig',
    'eoammegresults': 'EoamMegConfig',
    'dhcpv4blockresults': 'Dhcpv4BlockConfig',
    'eoamloopbackmessagerxresults': 'EoamMaintenancePointConfig',
    'generatorportresults': 'Generator',
    'dhcpv6blockresults': 'Dhcpv6PdBlockConfig Dhcpv6BlockConfig',
    'mldrouterresults': 'MldRouterConfig',
    'mldgroupmembershipresults': 'MldGroupMembership',
    'eoamloopbackmessagetxresults': 'EoamMaintenancePointConfig',
    'dhcpv6sessionresults': 'Dhcpv6PdBlockConfig Dhcpv6BlockConfig',
    'eoamaisresults': 'EoamMaintenancePointConfig',
    'eoamportresults': 'EoamPortConfig',
    'iptvportresults': 'Port',
    'txcpuportresults': 'Generator',
    'bridgeportresults': 'BridgePortConfig MstiConfig',
    'bgprouterresults': 'BgpRouterConfig',
    'cifsserverresults': 'CifsServerProtocolConfig',
    'eoamlinktracepathresults': 'EoamMaintenancePointConfig',
    'iptvchannelresults': 'IptvViewedChannels',
    'bfdipv6sessionresults': 'BfdRouterConfig',
    'eoamlinktracemessagerxresults': 'EoamMaintenancePointConfig',
    'pimrouterresults': 'PimRouterConfig',
    'bfdsessionresults': 'BfdRouterConfig',
    'eoamcontchkremoteresults': 'EoamMaintenancePointConfig',
    'eoamdelaymeasurementresponserxresults': 'EoamMaintenancePointConfig',
    'eoamlinktracemessagetxresults': 'EoamMaintenancePointConfig',
    'sonetalarmsresults': 'Port',
    'igmphostresults': 'IgmpHostConfig',
    'arpndresults': 'Port',
    'eoamloopbackresponserxresults': 'EoamMaintenancePointConfig',
    'rxcpuportresults': 'Analyzer',
    'eoamdelaymeasurementresults': 'EoamMaintenancePointConfig',
    'eoamloopbackresponsetxresults': 'EoamMaintenancePointConfig',
    'sonetresults': 'Port',
    'isisrouterresults': 'IsisRouterConfig',
    'ancpaccessnoderesults': 'AncpAccessNodeConfig',
    'eoamlossmeasurementresponserxresults': 'EoamMaintenancePointConfig',
    'igmpportresults': 'IgmpPortConfig',
    'txstreamblockresults': 'StreamBlock',
    'analyzerportresults': 'Analyzer',
    'filteredstreamresults': 'Analyzer',
    'rxstreamsummaryresults': 'StreamBlock',
    'eoamlckresults': 'EoamMaintenancePointConfig',
    'rxstreamresults': 'StreamBlock',
    'iptvstbblockresults': 'IptvStbBlockConfig',
    'eoamcontchklocalresults': 'EoamMaintenancePointConfig',
    'dhcpv4serverresults': 'Dhcpv4ServerConfig',
    'diffservresults': 'Analyzer',
    'rsvplspresults': 'RsvpRouterConfig',
    'pppprotocolresults': 'PppProtocolConfig',
    'ospfv3routerresults': 'Ospfv3RouterConfig',
    'mldhostresults': 'MldHostConfig',
    'rsvprouterresults': 'RsvpRouterConfig',
    'dhcpv4sessionresults': 'Dhcpv4BlockConfig',
    'rxtrafficgroupresults': 'StreamBlock TrafficGroup',
    'ancpportresults': 'AncpPortConfig',
    'txtrafficgroupresults': 'StreamBlock TrafficGroup',
    'eoamlossmeasurementmessagerxresults': 'EoamMaintenancePointConfig',
    'rxstreamblockresults': 'StreamBlock',
    'mldportresults': 'MldPortConfig',
    'bfdipv4sessionresults': 'BfdRouterConfig',
    'lacpportconfig': 'IsisRouterConfig',
    'iptvviewingprofileresults': 'IptvViewingProfileConfig',
    'bfdrouterresults': 'BfdRouterConfig',
    'eoamdelaymeasurementmessagerxresults': 'EoamMaintenancePointConfig',
    'pppoesessionresults': ('PppoeClientBlockConfig', 'PppoeServerBlockConfig'),
    'dhcpv6portresults': 'Dhcpv6PortConfig',
    'eoamlinktraceresponserxresults': 'EoamMaintenancePointConfig',
    'ldprouterresults': 'LdpRouterConfig',
    'eoamlinktraceresponsetxresults': 'EoamMaintenancePointConfig',
    'rxportpairresults': 'Port',
    'iptvtestresults': 'Project',
    'overflowresults': 'Analyzer',
    'cifsclientresults': 'CifsClientProtocolConfig',
    'txportpairresults': 'Port',
    }
