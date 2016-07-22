import time
from skiplagged import Skiplagged
import argparse


def parseargs():
    argparser = argparse.ArgumentParser(
            description='Find some Pokemon for the greater good'
    )
    
    argparser.add_argument(
                '--location',
                help='Location Google Maps understands',
                required=True
        )
    argparser.add_argument(
                '--user',
                help='Pokemon Go User',
                required=True
        )

    argparser.add_argument(
                '--password',
                help='Pokemon Go Password',
                required=True
        )
        
    argparser.add_argument(
                '--auth-method',
                help='Authentication method, specify google or ptc',
                required=True,
                dest='auth_method',
                choices=['google', 'ptc']
        )    
        
    command = argparser.parse_args(namespace=FindPokemon())

    return command
        
class FindPokemon(argparse.Namespace):
    def __init__(self, **kwargs):
        self.user = None
        self.password = None
        self.location = None
        self.auth_method = None
        
        super(FindPokemon, self).__init__(**kwargs)

    def run(self):
        client = Skiplagged()
        bounds = client.get_bounds_for_address(self.location)
        while 1:
            try:
                # Log in with a Google or Pokemon Trainer Club account
                if self.auth_method == 'ptc':
                    print client.login_with_pokemon_trainer(self.user, self.password)
                elif self.auth_method == 'google':
                    print client.login_with_google(self.user, self.password)
        
                # Get specific Pokemon Go API endpoint
                print client.get_specific_api_endpoint()
        
                # Get profile
                print client.get_profile()
        
                # Find pokemon
                for pokemon in client.find_pokemon(bounds):
                    print pokemon
            except Exception as e:
                print('Unexpected error: {0}'.format(e))
                time.sleep(1)

def main():
    find_pokemon = parseargs()
    find_pokemon.run()


if __name__ == '__main__':
    main()
