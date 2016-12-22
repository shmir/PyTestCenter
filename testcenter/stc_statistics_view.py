"""
Classes and utilities to manage STC statistics views.
"""

from stc_object import StcObject


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

    api = None
    statistics = {}

    def __init__(self, view):
        super(StcStats, self).__init__()
        self.view = view
        self.api = StcObject.api
        self.subscribe()
        self.statistics = {}

    def subscribe(self):
        """ Subscribe to statistics view. """

        project = StcObject.project
        rds = self.api.subscribe(Parent=project.obj_ref(), ResultParent=project.obj_ref(),
                                 ConfigType=view_2_config_Type[self.view], ResultType=self.view)
        self.rds = StcObject(ObjType='ResultDataSet', parent=project, objRef=rds)

    def unsubscribe(self):
        """ UnSubscribe from statistics view. """

        self.api.unsubscribe(self.rds.obj_ref())

    def read_stats(self, *stats):
        """ Reads the statistics view from STC and saves it in statistics dictionary.

        :param stats: list of statistics names to read, empty list will read all statistics.

        :todo: add support for user and dynamic statistics.
        """

        project = StcObject.project
        self.statistics = {}

        objs_stats = []
        self.api.perform('RefreshResultView', ResultDataSet=self.rds.obj_ref())
        for page_number in range(1, int(self.rds.get_attribute('TotalPageCount')) + 1):
            self.rds.set_attributes(PageNumber=page_number)
            for results in self.rds.get_objects_from_attribute('ResultHandleList'):
                parent = results.get_object_from_attribute('parent')
                parents = parent.obj_ref()
                name = ''
                while parent != project:
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

view_2_config_Type = {'generatorportresults': 'Generator',
                      'analyzerportresults': 'Analyzer',
                      'txstreamblockresults': 'StreamBlock',
                      'rxstreamblockresults': 'StreamBlock',
                      'txstreamresults': 'StreamBlock',
                      'rxstreamsummaryresults': 'StreamBlock',
                      }
