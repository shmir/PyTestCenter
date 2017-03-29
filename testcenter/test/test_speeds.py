"""
Base class for all STC package tests.

@author yoram@ignissoft.com
"""

import unittest
import itertools
import re


descriptions = {'1000 Series - 8 PORT 1G Fiber SFP': (1000,),
                '2X10G PERFORMANCE INTERFACE, SFP+': (10000,),
                '4x1G INTERFACE, RJ-45': (1000,),
                'HYPERMETRICS DX 10GBE SFP+ 32-PORTS': (10000,),
                'HYPERMETRICS PG 10G SFP+ 2-PORTS': (10000,),
                'HYPERMETRICS MX 10GBASE-T 2-PORTS': (10000,),
                'HYPERMETRICS MX 40/100G CFP 1-PORT': (40000, 100000),
                'SPIRENT MX 2-PORT 100GBE CFP2': (100000,),
                'SPIRENT FX2 5-PORT 40/10GBE QSFP+': (10000, 40000),
                'SPIRENT FX2 16-PORT 10G/1G SFP+': (1000, 10000),
                'SPIRENT FX2 16-PORT 1G/100M/10M SFP': (10, 100, 1000),
                'SPIRENT MX2 4-PORT 10/1GBE SFP+': (1000, 10000),
                'SPT-C1 4x1G Copper': (1000,),
                'SPT-C100-S3 2x100G, 8x10G': (10000, 100000),
                'SPIRENT DX2 16-PORT QUINT 10G/5G/2.5G/1G/100M Copper': (100, 1000, 2500, 5000, 10000),
                'SPIRENT FX3 2-PORT 100/50/40/25/10GBE QSFP28': (10000, 25000, 40000, 50000, 100000),
                '2 PORT 10/100/1000 Dual Media': (10, 100, 1000),
                'HYPERMETRICS CM 10/100/1000 DUAL MEDIA 4-PORTS': (10, 100, 1000),
                'HYPERMETRICS CM 10/100/1000 DUAL MEDIA 4-PORTS': (10, 100, 1000),
                '12 PORT 10/100/1000 Dual Media Rev B': (10, 100, 1000),
                'HYPERMETRICS CM 10/100/1000 DUAL MEDIA 12-PORTS': (10, 100, 1000),
                'HYPERMETRICS CV 2/4/8G FC SFP+ 2-PORTS': (2000, 4000, 8000),
                '2 PORT 10G/2.5G HOST MODULE': (2500, 10000)}


class StcSpeeds(unittest.TestCase):

    def testRegExp(self):
        # Take a look at https://regex101.com/ to see how the reg exp work on above samples.
        self.speeds_pattern = re.compile('([\dGM]*[\/].*? )|(\d+[GM])')
        self.num_pattern = re.compile('\d+[\.]?\d*')
        for descriptin, expected in descriptions.items():
            assert(set(self._extract_speeds(descriptin)) == set(expected))

    def _extract_speeds(self, descriptin):
        speeds = []
        groups = self.speeds_pattern.findall(descriptin)
        speeds_strings_list = list(filter(None, list(itertools.chain.from_iterable(groups))))
        for speeds_string in speeds_strings_list:
            for speed_string in speeds_string.strip().split('/'):
                if 'G' in speed_string:
                    speeds.append(int(float(self.num_pattern.search(speed_string).group(0)) * 1000))
                elif 'M' in speed_string:
                    speeds.append(int(self.num_pattern.search(speed_string).group(0)))
                else:
                    if any('G' in s for s in speeds_strings_list):
                        speeds.append(int(float(self.num_pattern.search(speed_string).group(0)) * 1000))
                    elif any('M' in s for s in speeds_strings_list):
                        speeds.append(int(self.num_pattern.search(speed_string).group(0)))
                    else:
                        speeds.append(int(speed_string))
        return sorted(speeds)
