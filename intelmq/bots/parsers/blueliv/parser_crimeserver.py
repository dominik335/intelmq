# -*- coding: utf-8 -*-
"""
"""

import json

from intelmq.lib import utils
from intelmq.lib.bot import Bot
from intelmq.lib.harmonization import IPAddress

TYPES = {
    'PHISHING': 'phishing',
    'MALWARE': 'malware',
    'EXPLOIT_KIT': 'exploit',
    'BACKDOOR': 'backdoor',
    'TOR_IP': 'proxy',
    'C_AND_C': 'c&c'
}


class BluelivCrimeserverParserBot(Bot):

    def process(self):
        report = self.receive_message()

        raw_report = utils.base64_decode(report.get('raw'))

        for item in json.loads(raw_report):
            event = self.new_event(report)
            tor_node = False
            if 'type' in item:
                event.add('classification.type', TYPES[item['type']])
                if item['type'] == 'TOR_IP':
                    event.add('source.tor_node', True)
                    tor_node = True
            if 'url' in item:
                # crimeserver reports tor ips in url instead of ip field

                if not tor_node:
                    event.add('source.url', item['url'])
                else:
                    valid_ip = IPAddress.is_valid(item['url'])
                    if valid_ip:
                        event.add('source.ip', item['url'])
                    else:
                        event.add('source.url', item['url'])
            if 'ip' in item:
                event.add('source.ip', item['ip'])
            if 'country' in item:
                event.add('source.geolocation.cc', item['country'])
            if 'firstSeenAt' in item:
                event.add('time.source', item['firstSeenAt'][:-4] + '00:00')
            event.add("raw", json.dumps(item, sort_keys=True))
            self.send_message(event)
        self.acknowledge_message()


BOT = BluelivCrimeserverParserBot
