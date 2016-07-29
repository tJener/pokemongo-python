from __future__ import print_function
import sys
import os.path
import time
import argparse
import ConfigParser

from skiplagged import Skiplagged

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', action='store', nargs=1, default='default', required=False)
    options = parser.parse_args()

    if isinstance(options.config, basestring):
        config_path = 'config/%s.cfg' % options.config
    else:
        config_path = 'config/%s.cfg' % options.config[0]

    if not os.path.isfile(config_path):
        default_config = 'config/default.cfg'
        eprint(config_path, ': file not found, defaulting to ', default_config)
        config_path = default_config

    config = ConfigParser.RawConfigParser()
    print('Using config', config_path)
    config.read(config_path)

    client = Skiplagged()

    bounds = (
        (config.getfloat('scan', 'bot_left_lat'),
         config.getfloat('scan', 'bot_left_lng')),
        (config.getfloat('scan', 'top_right_lat'),
         config.getfloat('scan', 'top_right_lng'))
    ) # Central park, New York City
    # bounds = client.get_bounds_for_address('Central Park, NY')

    while 1:
        try:
            # Log in with a Google or Pokemon Trainer Club account
            method = config.get('pogo', 'login_method')
            if method == 'ptc':
                print(
                    client.login_with_pokemon_trainer(
                        config.get('pogo', 'ptc_username'),
                        config.get('pogo', 'ptc_password')
                    )
                )
            elif method == 'google':
                print(
                    client.login_with_google(
                        config.get('pogo', 'google_username'),
                        config.get('pogo', 'google_password')
                    )
                )
            else:
                sys.exit('Unrecognized login_method "%s" in %s' % (method, config_path))

            # Get specific Pokemon Go API endpoint
            print(client.get_specific_api_endpoint())

            # Get profile
            print(client.get_profile())

            while True:
                # Find pokemon
                for pokemon in client.find_pokemon(bounds):
                    print(pokemon)

        except Exception as e:
            print("Exception: {0} {1}".format(e.message, e.args))
            time.sleep(1)
