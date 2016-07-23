import os.path
import sys
import time
import json
import signal
import requests
import ConfigParser

from skiplagged import Skiplagged
from pushbullet import Pushbullet
from utils.latlng import latlng_distance, find_bounds, get_cardinal_direction

noteworthy_save_path = 'slack-current-pokemon.json'

# key into this is:
#     %d%f%f % (id, lat, lng)
# should be unique enough for our purposes?
#
# value is expiration and a pushbullet.push object,
# so that we can delete the push when it expires
noteworthy = dict()

def int_handler(signal, frame):
    f = open(noteworthy_save_path, 'w')
    json.dump(noteworthy, f)
    sys.exit(0)

if __name__ == '__main__':
    from pokemon_notify_level import SLACK_RADAR

    EXPIRATION_ERROR = 5

    config = ConfigParser.RawConfigParser()
    config_path = 'config/default.cfg'
    config.read(config_path)

    NOTIFY_RANGE = config.getint('slack', 'notify_range')

    client = Skiplagged()
    webhook_url = config.get('slack', 'webhook_url')

    home = {
        'latitude':  config.getfloat('notify', 'location_lat'),
        'longitude': config.getfloat('notify', 'location_lng')
    }

    if os.path.isfile(noteworthy_save_path):
        noteworthy = json.load(open(noteworthy_save_path, 'r'))

    signal.signal(signal.SIGINT, int_handler)

    search_radius = NOTIFY_RANGE
    bounds = find_bounds(home['latitude'], home['longitude'], search_radius)
    print "search radius:", search_radius
    print "bounds:", bounds

    while 1:
        try:
            # Find pokemon
            while 1:
                # clear expired pushes
                current_time = time.time()
                for key in noteworthy.keys():
                    expiration = noteworthy[key]['expiration']
                    if expiration + EXPIRATION_ERROR < current_time:
                        del noteworthy[key]

                for pokemon in client.query_pokemon(bounds):
                    ploc = pokemon.get_location()
                    pid = pokemon.get_id()
                    expiration = pokemon.get_expires_timestamp()

                    dist = latlng_distance(home['latitude'], home['longitude'],
                                           ploc['latitude'], ploc['longitude'])
                    bearing = get_cardinal_direction(home['latitude'], home['longitude'],
                                                     ploc['latitude'], ploc['longitude'])

                    if pid in SLACK_RADAR and dist < NOTIFY_RANGE and time.time() < expiration:
                        key = '%d%f%f' % (pokemon.get_id(), ploc['latitude'], ploc['longitude'])
                        if not key in noteworthy:
                            body = ':poke%003d: %s spotted %dm %s, until %s (%ds remaining)' % (
                                pid,
                                pokemon.get_name(),
                                int(dist),
                                bearing,
                                time.strftime("%I:%M:%S %p", time.localtime(expiration)),
                                expiration - time.time()
                            )
                            payload = {
                                'text': body,
                                'icon_emoji': ':pokeball:'
                            }
                            requests.post(webhook_url, data=json.dumps(payload))
                            noteworthy[key] = {
                                'expiration': expiration
                            }

                time.sleep(10)

        except Exception as e:
            print "exception:", e
            time.sleep(1)
