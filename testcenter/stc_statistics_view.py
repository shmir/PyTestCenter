"""
Classes and utilities to manage STC statistics views.
"""
from typing import Optional

from trafficgenerator.tgn_object import TgnObjectsDict
from trafficgenerator.tgn_utils import is_false

from testcenter.stc_object import StcObject


class StcStats:
    """Represents statistics view.

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

    def __init__(self, view: str) -> None:
        """Subscribe to view with default configuration type as defined by config_2_type.

        :param view: statistics view to subscribe to. If view is None it is the test responsibility to subscribe with
            specific config_type.
        """
        self.rds = None
        self.statistics = TgnObjectsDict()
        if view:
            self.subscribe(view)

    def subscribe(self, view: str, config_type: Optional[str] = None) -> None:
        """Subscribe to statistics view.

        :param view: statistics view to subscribe to.
        :param config_type: configuration type to subscribe to.
        """
        if view.lower() in view_2_config_type:
            if not config_type:
                config_type = view_2_config_type[view.lower()]
            rds = StcObject.project.api.subscribe(
                Parent=StcObject.project.ref, ResultParent=StcObject.project.ref, ConfigType=config_type, ResultType=view
            )
            self.rds = StcObject(objType="ResultDataSet", parent=StcObject.project, objRef=rds)
        else:
            StcObject.project.get_children("DynamicResultView")
            drv = StcObject.project.get_object_by_name(view)
            rc = StcObject.project.command("SubscribeDynamicResultView", DynamicResultView=drv.ref)
            self.rds = StcObject(objType="DynamicResultView", parent=StcObject.project, objRef=rc["DynamicResultView"])

    def unsubscribe(self) -> None:
        """UnSubscribe from statistics view."""
        StcObject.project.api.unsubscribe(self.rds.ref)

    def read_stats(self, obj_id_stat: Optional[str] = "topLevelName") -> TgnObjectsDict:
        """Reads the statistics view from STC and saves it in statistics dictionary.

        :param obj_id_stat: which statistics name to use as object ID, sometimes topLevelName is
            not meaningful and it is better to use other unique identifier like stream ID.
        """
        self.statistics = TgnObjectsDict()
        if self.rds.type == "dynamicresultview":
            self._read_custom_view()
        else:
            self._read_view(obj_id_stat)
        return self.statistics

    def get_column_stats(self, name: str) -> TgnObjectsDict:
        """Returns all statistics values for the requested statistics.

        N/A for custom views.

        :param name: requested statistic name.
        """
        column_statistics = TgnObjectsDict()
        for obj, obj_values in self.statistics.items():
            column_statistics[obj] = obj_values[name]
        return column_statistics

    #
    # Private methods.
    #

    def _read_custom_view(self):

        StcObject.project.command("RefreshResultView", ResultDataSet=self.rds.ref)
        StcObject.project.command("UpdateDynamicResultViewCommand", DynamicResultView=self.rds.ref)
        presentationResultQuery = self.rds.get_child("PresentationResultQuery")
        selectedProperties = presentationResultQuery.get_list_attribute("SelectProperties")
        self.objs_stats = []
        for rvd in presentationResultQuery.get_children("ResultViewData"):
            self.objs_stats.append(rvd.get_list_attribute("ResultData")[: len(selectedProperties)])
            self._get_result_data(rvd, len(selectedProperties))
        self.statistics = dict(zip(selectedProperties, zip(*self.objs_stats)))

    def _get_result_data(self, rvd, num_columns):
        StcObject.project.command("ExpandResultViewDataCommand", ResultViewData=rvd.ref)
        for child_rvd in rvd.get_children("ResultViewData"):
            if is_false(child_rvd.get_attribute("IsDummy")):
                self.objs_stats.append(child_rvd.get_list_attribute("ResultData")[:num_columns])
            self._get_result_data(child_rvd, num_columns)

    def _read_view(self, obj_id_stat: Optional[str] = "topLevelName") -> None:

        StcObject.project.command("RefreshResultView", ResultDataSet=self.rds.ref)
        for page_number in range(1, int(self.rds.get_attribute("TotalPageCount")) + 1):
            self.rds.set_attributes(PageNumber=page_number)
            for results in self.rds.get_objects_from_attribute("ResultHandleList"):
                parent = results.get_object_from_attribute("parent")
                parents = parent.ref
                name = ""
                while parent != StcObject.project:
                    if not name and parent.obj_type().lower() in ("port", "emulateddevice", "streamblock"):
                        name = parent.get_name()
                    parent = parent.get_object_from_attribute("parent")
                    parents = parent.ref + "/" + parents
                obj_stats = {"object": results.ref, "parents": parents, "topLevelName": name}
                obj_stats.update(results.get_attributes())
                obj_stats.pop("parent", None)
                obj_stats.pop("Name", None)
                obj_stats.pop("resultchild-Sources", None)
                for stat in obj_stats:
                    try:
                        obj_stats[stat] = int(obj_stats[stat])
                    except ValueError:
                        pass
                self.statistics[StcObject.project.get_object_by_name(obj_stats[obj_id_stat])] = obj_stats


view_2_config_type = {
    "igmpgroupmembershipresults": "IgmpGroupMembership",
    "igmprouterresults": "IgmpRouterConfig",
    "ldplspresults": "LdpRouterConfig",
    "eoamlinktraceresults": "EoamMaintenancePointConfig",
    "ospfv2routerresults": "Ospfv2RouterConfig",
    "portavglatencyresults": "Analyzer",
    "riprouterresults": "RipRouterConfig",
    "eoamloopbackresults": "EoamMaintenancePointConfig",
    "dhcpv4portresults": "Dhcpv4PortConfig",
    "txstreamresults": "StreamBlock",
    "pppoeportresults": (
        "PppoaClientBlockConfig",
        "PppoaServerBlockConfig",
        "PppoeClientBlockConfig",
        "PppoeServerBlockConfig",
        "PppoL2tpv2ClientBlockConfig",
        "PppoL2tpv2ServerBlockConfig",
        "PppoxPortConfig",
        "PppProtocolConfig",
    ),
    "eoamlossmeasurementresponserxresults": "EoamMaintenancePointConfig",
    "eoammegresults": "EoamMegConfig",
    "dhcpv4blockresults": "Dhcpv4BlockConfig",
    "eoamloopbackmessagerxresults": "EoamMaintenancePointConfig",
    "generatorportresults": "Generator",
    "dhcpv6blockresults": "Dhcpv6PdBlockConfig Dhcpv6BlockConfig",
    "mldrouterresults": "MldRouterConfig",
    "mldgroupmembershipresults": "MldGroupMembership",
    "eoamloopbackmessagetxresults": "EoamMaintenancePointConfig",
    "dhcpv6sessionresults": "Dhcpv6PdBlockConfig Dhcpv6BlockConfig",
    "eoamaisresults": "EoamMaintenancePointConfig",
    "eoamportresults": "EoamPortConfig",
    "iptvportresults": "Port",
    "txcpuportresults": "Generator",
    "bridgeportresults": "BridgePortConfig MstiConfig",
    "bgprouterresults": "BgpRouterConfig",
    "cifsserverresults": "CifsServerProtocolConfig",
    "eoamlinktracepathresults": "EoamMaintenancePointConfig",
    "iptvchannelresults": "IptvViewedChannels",
    "bfdipv6sessionresults": "BfdRouterConfig",
    "eoamlinktracemessagerxresults": "EoamMaintenancePointConfig",
    "pimrouterresults": "PimRouterConfig",
    "bfdsessionresults": "BfdRouterConfig",
    "eoamcontchkremoteresults": "EoamMaintenancePointConfig",
    "eoamdelaymeasurementresponserxresults": "EoamMaintenancePointConfig",
    "eoamlinktracemessagetxresults": "EoamMaintenancePointConfig",
    "sonetalarmsresults": "Port",
    "igmphostresults": "IgmpHostConfig",
    "arpndresults": "Port",
    "eoamloopbackresponserxresults": "EoamMaintenancePointConfig",
    "rxcpuportresults": "Analyzer",
    "eoamdelaymeasurementresults": "EoamMaintenancePointConfig",
    "eoamloopbackresponsetxresults": "EoamMaintenancePointConfig",
    "sonetresults": "Port",
    "isisrouterresults": "IsisRouterConfig",
    "ancpaccessnoderesults": "AncpAccessNodeConfig",
    "igmpportresults": "IgmpPortConfig",
    "txstreamblockresults": "StreamBlock",
    "analyzerportresults": "Analyzer",
    "filteredstreamresults": "Analyzer",
    "rxstreamsummaryresults": "StreamBlock",
    "eoamlckresults": "EoamMaintenancePointConfig",
    "rxstreamresults": "StreamBlock",
    "iptvstbblockresults": "IptvStbBlockConfig",
    "eoamcontchklocalresults": "EoamMaintenancePointConfig",
    "dhcpv4serverresults": "Dhcpv4ServerConfig",
    "diffservresults": "Analyzer",
    "rsvplspresults": "RsvpRouterConfig",
    "pppprotocolresults": "PppProtocolConfig",
    "ospfv3routerresults": "Ospfv3RouterConfig",
    "mldhostresults": "MldHostConfig",
    "rsvprouterresults": "RsvpRouterConfig",
    "dhcpv4sessionresults": "Dhcpv4BlockConfig",
    "rxtrafficgroupresults": "StreamBlock TrafficGroup",
    "ancpportresults": "AncpPortConfig",
    "txtrafficgroupresults": "StreamBlock TrafficGroup",
    "eoamlossmeasurementmessagerxresults": "EoamMaintenancePointConfig",
    "rxstreamblockresults": "StreamBlock",
    "mldportresults": "MldPortConfig",
    "bfdipv4sessionresults": "BfdRouterConfig",
    "lacpportconfig": "IsisRouterConfig",
    "iptvviewingprofileresults": "IptvViewingProfileConfig",
    "bfdrouterresults": "BfdRouterConfig",
    "eoamdelaymeasurementmessagerxresults": "EoamMaintenancePointConfig",
    "pppoesessionresults": ("PppoeClientBlockConfig", "PppoeServerBlockConfig"),
    "dhcpv6portresults": "Dhcpv6PortConfig",
    "eoamlinktraceresponserxresults": "EoamMaintenancePointConfig",
    "ldprouterresults": "LdpRouterConfig",
    "eoamlinktraceresponsetxresults": "EoamMaintenancePointConfig",
    "rxportpairresults": "Port",
    "iptvtestresults": "Project",
    "overflowresults": "Analyzer",
    "cifsclientresults": "CifsClientProtocolConfig",
    "txportpairresults": "Port",
}
