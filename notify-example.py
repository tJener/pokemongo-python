import time

from skiplagged import Skiplagged
from pushbullet import Pushbullet
from utils.latlng import latlng_distance, find_bounds

if __name__ == '__main__':
    # BEGIN CONFIG
    #
    # If code scares you, only change stuff until it says END CONFIG
    pushbullet_api_key = "o.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

    ALWAYS_NOTIFY_RANGE = 45    # meters (fine, I'll open the app)
    UNCOMMON_NOTIFY_RANGE = 200 # meters (what gets you off the couch?)
    RARE_NOTIFY_RANGE = 1000    # meters (how fast can you walk?)
    ULTRA_NOTIFY_RANGE = 2500   # meters (how fast can you sprint?)

    home = { 'latitude': 42.000000, 'longitude': -72.000000 } # where are you

    UNCOMMONS = (
        1,                      # Bulbasaur
        4,                      # Charmander
        7,                      # Squirtle
    )

    RARES = (
        2,                      # Ivysaur
        5,                      # Charmeleon
        8,                      # Wartortle
        138, 139,               # Omanyte+
        140, 141,               # Kabuto+
        142,                    # Aerodactyl
        143,                    # Snorlax
        148, 149,               # Dragonair+
    )

    ULTRAS = (
        3,                      # Venusaur
        6,                      # Charizard
        9,                      # Blastoise
        122,                    # Mr. Mime
        123,                    # Scyther
        131,                    # Lapras
        149,                    # Dragonite
    )
    # END CONFIG

    client = Skiplagged()
    pb = Pushbullet(pushbullet_api_key)

    search_radius = max(
        ALWAYS_NOTIFY_RANGE,
        UNCOMMON_NOTIFY_RANGE if UNCOMMONS else 0,
        RARE_NOTIFY_RANGE if RARES else 0,
        ULTRA_NOTIFY_RANGE if ULTRAS else 0
    )
    bounds = find_bounds(home['latitude'], home['longitude'], search_radius)
    print "search radius:", search_radius
    print "bounds:", bounds

    # key into this is:
    #     %d%f%f % (id, lat, lng)
    # should be unique enough for our purposes?
    #
    # value is expiration and a pushbullet.push object,
    # so that we can delete the push when it expires
    noteworthy = dict()

    # get existing pushes, so we don't re-notify
    for push in pb.get_pushes():
        if not push.get("title").startswith('[pogo]'):
            continue
        body = push.get("body")
        tokens = body.split('|')
        expiration = float(tokens[1])
        if expiration < time.time():
            pb.delete_push(push.get("iden"))
            continue
        noteworthy[tokens[0]] = {
            'expiration': expiration,
            'push': push
        }

    while 1:
        try:
            # Find pokemon
            while 1:
                # clear expired pushes
                current_time = time.time()
                for key in noteworthy.keys():
                    expiration = noteworthy[key]['expiration']
                    if expiration < current_time:
                        pb.delete_push(noteworthy[key]['push'].get("iden"))
                        del noteworthy[key]

                for pokemon in client.query_pokemon(bounds):
                    ploc = pokemon.get_location()
                    pid = pokemon.get_id()
                    expiration = pokemon.get_expires_timestamp()

                    dist = latlng_distance(home['latitude'], home['longitude'],
                                           ploc['latitude'], ploc['longitude'])
                    is_uncommon = pid in UNCOMMONS
                    is_rare = pid in RARES
                    is_ultra = pid in ULTRAS

                    if ((dist < ALWAYS_NOTIFY_RANGE
                         or (is_uncommon and dist < UNCOMMON_NOTIFY_RANGE)
                         or (is_rare and dist < RARE_NOTIFY_RANGE)
                         or (is_ultra and dist < ULTRA_NOTIFY_RANGE)) and
                        time.time() < expiration):
                        key = '%d%f%f' % (pokemon.get_id(), ploc['latitude'], ploc['longitude'])
                        if not key in noteworthy:
                            print pokemon, 'distance: %.2f' % (dist)
                            push = pb.push_link('[pogo] %s %.2fm' % (pokemon.get_name(), dist),
                                                "https://skiplagged.com/pokemon",
                                                body='%s|%f' % (key, expiration))
                            noteworthy[key] = {
                                'expiration': expiration,
                                'push': push
                            }

                time.sleep(10)

        except Exception as e:
            print "exception:", e
            time.sleep(1)
