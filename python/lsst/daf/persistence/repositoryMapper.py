#!/usr/bin/env python

#
# LSST Data Management System
# Copyright 2016 LSST Corporation.
#
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the LSST License Statement and
# the GNU General Public License along with this program.  If not,
# see <http://www.lsstcorp.org/LegalNotices/>.
#

from lsst.daf.persistence import Mapper, ButlerLocation, Policy


class RepositoryMapper(Mapper):
    """"Base class for a mapper to find repository configurations within a butler repository.

    .. warning::

            cfg is 'wet paint' and very likely to change. Use of it in production code other than via the 'old
            butler' API is strongly discouraged.
    """

    def __init__(self, storage, policy):
        # todo I'm guessing the policy would probably want to come from the default in-package location, and
        # then be overridden where desired by policy in repository root, and then
        # have the cfg policy applied
        self.policy = Policy(policy)
        self.storage = storage

    def __repr__(self):
        if 'policy' in self.__dict__ and 'storageCfg' in self.__dict__:
            return 'RepositoryMapper(policy=%s, storageCfg=%s)' % (self.policy, self.storageCfg)
        else:
            return 'uninitialized RepositoryMapper'

    def map_cfg(self, dataId, write):
        """Map a location for a cfg file.

        :param dataId: keys & values to be applied to the template.
        :param write: True if this map is being done do perform a write operation, else assumes read. Will
                      verify location exists if write is True.
        :return: a butlerLocation that describes the mapped location.
        """
        # todo check: do we need keys to complete dataId? (search Registry)
        template = self.policy['repositories.cfg.template']
        location = template % dataId
        if not write and not self.storage.exists(location):
            return None
        bl = ButlerLocation(
            pythonType=self.policy['repositories.cfg.python'],
            cppType=None,
            storageName=self.policy['repositories.cfg.storage'],
            locationList=(self.storage.locationWithRoot(location),),
            dataId=dataId,
            mapper=self)
        return bl

    def map_repo(self, dataId, write):
        if write:
            return None

        # todo check: do we need keys to complete dataId? (search Registry)

        template = self.policy['repositories.repo.template']
        location = template % dataId
        if self.storage.exists(location):
            bl = ButlerLocation(
                pythonType=self.policy['repositories.repo.python'],
                cppType=None,
                storageName=None,
                locationList=(location,),
                dataId=dataId,
                mapper=self)
            return bl
        return None
