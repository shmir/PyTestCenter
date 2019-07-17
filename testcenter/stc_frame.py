"""
This module implements classes and utility functions to manage packet headers within streamblock.
"""
from collections import OrderedDict
from enum import Enum

from testcenter.stc_object import StcObject


class StcFrame_Layers(object):

    class DataLinkLayer(Enum):
        Undefined = None
        Eth2 = 0

    class UpperLayerProtocols_I(Enum):
        Undefined = None
        IpV4 = 0
        IpV6 = 1

    class UpperLayerProtocols_II(Enum):
        Undefined = None
        TCP = 0
        UDP = 1
        Custom = 3

class StcPacketHeader(StcObject):
    def __init__(self, **data):
        super(StcPacketHeader, self).__init__(**data)

class StcEthII(StcPacketHeader):
    def __init__(self, **data):
        data['objType'] = 'ethernet:EthernetII'
        super(StcEthII, self).__init__(**data)

class StcVlans(StcPacketHeader):
    def __init__(self, **data):
        data['objType'] = 'Vlans'
        super(StcVlans, self).__init__(**data)
        self._vlans = OrderedDict()

class StcVlan(StcPacketHeader):
    def __init__(self, **data):
        data['objType'] = 'Vlan'
        super(StcVlan, self).__init__(**data)


class StcV4(StcPacketHeader):
    def __init__(self, **data):
        data['objType'] = 'ipv4:Ipv4'
        super(StcV4, self).__init__(**data)

class StcCustomHeader(StcPacketHeader):
    def __init__(self, **data):
        data['objType'] = 'custom:Custom'
        super(StcCustomHeader, self).__init__(**data)


class StcCustomFillPattern(StcObject):
    def __init__(self, **data):
        data['objType'] = 'CustomFillPattern'
        super(StcCustomFillPattern, self).__init__(**data)

class StcFrame(object):

    def __init__(self,parrent_stream):
        self.L2 = StcFrameLayer2(parrent_stream)
        self.L3 = StcFrameLayer(parrent_stream)
        self.parent_stream = parrent_stream

    def add_header(self,header_type, **data):
        new_h = header_creator.create(self.parent_stream, header_type)
        new_h.set_attributes(**data)

    #not applicable on 400G hw
    # def custom_pl(self, pattern):
    #     pl = CustomFillPattern(parent=self.parent_stream.project, PatternData=pattern)
    #     self.parent_stream.set_attributes(FillType='CUSTOM', AffiliationCustomFillPattern=pl.ref)


class StcFrameLayer(object):
    def __init__(self,parent_stream):
        self._obj = None
        self.parent_stream = parent_stream

    def update_fields(self, **data):
        self._obj.set_attributes(**data)

    def set_type(self, header_type):
        if self._obj:
            self._obj.delete()
        self._obj = header_creator.create(self.parent_stream,header_type)


class StcFrameLayer2(StcFrameLayer):
    def __init__(self,parent_stream):
        super(StcFrameLayer2, self).__init__(parent_stream)
        self.vlans = None

    def add_vlan(self,**data):
        if not self.vlans:
            self.vlans = StcVlans(parent=self._obj)
        idx = len(self.vlans._vlans)
        self.vlans._vlans[idx] = StcVlan(parent=self.vlans, **data)
        return self.vlans._vlans[idx]


class header_creator(object):
    _headers_map = {
        StcFrame_Layers.DataLinkLayer.Eth2: StcEthII,
        StcFrame_Layers.UpperLayerProtocols_I.IpV4: StcV4,
        StcFrame_Layers.UpperLayerProtocols_II.Custom:StcCustomHeader
    }

    @classmethod
    def create(cls,parent,header_type):
        return header_creator.obj_type(header_type)(parent=parent)

    @classmethod
    def obj_type(cls,header_type):
        return header_creator._headers_map[header_type]

