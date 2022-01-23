from testcenter.stc_device import *
from testcenter.stc_hw import *
from testcenter.stc_object import *
from testcenter.stc_port import *
from testcenter.stc_project import *
from testcenter.stc_stream import *

TYPE_2_OBJECT = {
    "analyzer": testcenter.stc_port.StcAnalyzer,
    "bfdipv4controlplaneindependentsession": testcenter.stc_device.StcBfdSession,
    "bfdipv6controlplaneindependentsession": testcenter.stc_device.StcBfdSession,
    "bfdrouterconfig": testcenter.stc_device.StcBfdRouter,
    "bgprouterconfig": testcenter.stc_device.StcBgpRouter,
    "bgpipv4routeconfig": testcenter.stc_device.StcBgpRoute,
    "bgpipv6routeconfig": testcenter.stc_device.StcBgpRoute,
    "capture": testcenter.stc_port.StcCapture,
    "dhcpv4serverconfig": testcenter.stc_device.StcServer,
    "dhcpv4blockconfig": testcenter.stc_device.StcClient,
    "emulateddevice": testcenter.stc_device.StcDevice,
    "externallsablock": testcenter.stc_device.StcOspfLsa,
    "igmphostconfig": testcenter.stc_device.StcIgmpHost,
    "igmprouterconfig": testcenter.stc_device.StcIgmpQuerier,
    "igmpgroupmembership": testcenter.stc_device.StcIgmpGroup,
    "ipv4group": testcenter.stc_project.StcIpv4Group,
    "ipv4prefixlsp": testcenter.stc_device.StcLdpPrefixLsp,
    "ipv6group": testcenter.stc_project.StcIpv6Group,
    "ipv4isisroutesconfig": testcenter.stc_device.StcIsisRouterRange,
    "ipv6isisroutesconfig": testcenter.stc_device.StcIsisRouterRange,
    "isisrouterconfig": testcenter.stc_device.StcIsisRouter,
    "generator": testcenter.stc_port.StcGenerator,
    "groupcollection": testcenter.stc_stream.StcGroupCollection,
    "ldprouterconfig": testcenter.stc_device.StcLdpRouter,
    "mldhostconfig": testcenter.stc_device.StcMldHost,
    "mldgroupmembership": testcenter.stc_device.StcMldGroupMembership,
    "ospfv2routerconfig": testcenter.stc_device.StcOspfv2Router,
    "ospfv3asexternallsablock": testcenter.stc_device.StcOspfLsa,
    "ospfv3interareaprefixlsablk": testcenter.stc_device.StcOspfLsa,
    "ospfv3intraareaprefixlsablk": testcenter.stc_device.StcOspfLsa,
    "ospfv3naaslsablock": testcenter.stc_device.StcOspfLsa,
    "oseswitchconfig": testcenter.stc_device.StcOseSwitch,
    "pimrouterconfig": testcenter.stc_device.StcPimRouter,
    "pimv4groupblk": testcenter.stc_device.StcPimv4Group,
    "port": testcenter.stc_port.StcPort,
    "physicalchassis": testcenter.stc_hw.StcPhyChassis,
    "physicalchassismanager": testcenter.stc_hw.StcHw,
    "physicalport": testcenter.stc_hw.StcPhyPort,
    "physicalportgroup": testcenter.stc_hw.StcPhyPortGroup,
    "physicaltestmodule": testcenter.stc_hw.StcPhyModule,
    "routerlsa": testcenter.stc_device.StcOspfLsa,
    "rsvpegresstunnelparams": testcenter.stc_device.StcRsvpTunnel,
    "rsvpingresstunnelparams": testcenter.stc_device.StcRsvpTunnel,
    "rsvprouterconfig": testcenter.stc_device.StcRsvpRouter,
    "streamblock": testcenter.stc_stream.StcStream,
    "summarylsablock": testcenter.stc_device.StcOspfLsa,
    "trafficgroup": testcenter.stc_stream.StcTrafficGroup,
}
