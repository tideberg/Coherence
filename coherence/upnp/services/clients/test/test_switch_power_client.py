# -*- coding: utf-8 -*-

# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php

# Copyright 2008, Frank Scholz <coherence@beebits.net>
# Copyright 2014 Hartmut Goebel <h.goebel@crazy-compilers.com>

"""
Test cases for L{upnp.services.clients.switch_power_client}
"""

import os

from twisted.trial import unittest
from twisted.internet import reactor
from twisted.internet.defer import Deferred

from coherence import __version__
from coherence.base import Coherence
from coherence.upnp.core import uuid
from coherence.upnp.devices.control_point import DeviceQuery
import coherence.extern.louie as louie

from coherence.test import wrapped


class TestSwitchPowerClient(unittest.TestCase):

    def setUp(self):
        louie.reset()
        self.coherence = Coherence(
            {'unittest': 'yes',
             'logmode': 'error',
             'subsystem_log': {'controlpoint': 'error'},
             'controlpoint': 'yes'
             })
        self.uuid = str(uuid.UUID())
        p = self.coherence.add_plugin('SimpleLight',
                                      name='test-light-%d' % os.getpid(),
                                      uuid=self.uuid)

    def tearDown(self):

        def cleaner(r):
            self.coherence.clear()
            return r

        dl = self.coherence.shutdown()
        dl.addBoth(cleaner)
        return dl

    def test_get_state(self):
        """ tries to find the activated SimpleLight backend
            and queries its state.
            The state is expected to be "off"
        """
        d = Deferred()

        @wrapped(d)
        def the_result(r):
            self.assertEqual(self.uuid, r.udn)
            call = r.client.switch_power.get_status()
            call.addCallback(got_answer)

        @wrapped(d)
        def got_answer(r):
            self.assertEqual(int(r['ResultStatus']), 0)
            d.callback(None)

        self.coherence.ctrl.add_query(
            DeviceQuery('uuid', self.uuid, the_result,
                        timeout=10, oneshot=True))
        return d
