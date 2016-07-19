import base64
import json
import time
import traceback

from auth.google import Google
from auth.pokemon_trainer_club import PokemonTrainerClub
from utils.general import get_requests_session
from utils.pokemon import Pokemon


class Skiplagged():
    SKIPLAGGED_API = 'http://skiplagged.com/api/pokemon.php'
    GENERAL_API = 'https://pgorelease.nianticlabs.com/plfe/rpc'
    SPECIFIC_API = None
    PROFILE = None
    PROFILE_RAW = None
    
    _requests_skiplagged_session = None
    _requests_niantic_session = None
    
    _username = None
    _password = None
    _access_token = None
    _auth_provider = None
    
    def __init__(self):
        self._requests_skiplagged_session = get_requests_session('pokemongo-python')
        self._requests_niantic_session = get_requests_session('Niantic App')
        
    # Login
    
    def login_with_google(self, username, password):
        print time.time(), "called login_with_google"     
        google_auth = Google()
        auth_provider = google_auth.get_auth_provider()
        access_token = google_auth.get_access_token(username, password)
        access_token = access_token
        
        return self._update_login(auth_provider, access_token, username, password)
    
    def login_with_pokemon_trainer(self, username, password):
        print time.time(), "called login_with_pokemon_trainer" 
        ptc_auth = PokemonTrainerClub()
        auth_provider = ptc_auth.get_auth_provider()
        access_token = ptc_auth.get_access_token(username, password)

        return self._update_login(auth_provider, access_token, username, password)
    
    def _update_login(self, auth_provider, access_token, username, password):        
        if self._access_token:
            self._auth_provider = auth_provider
            self._access_token = str(access_token)
            self._username = username
            self._password = password
            
            return (self._auth_provider, self._access_token)
        
        return False
    
    def is_logged_in(self): return self._access_token is not None
    
    def _refresh_login(self):
        if not self.is_logged_in(): raise Exception('needs an existing log in')
        
        self.SPECIFIC_API = None
        self.PROFILE = None
        self.PROFILE_RAW = None
        
        if self.auth_provider == 'google': return self.login_with_google(self._username, self._password)
        elif self.auth_provider == 'ptc': return self.login_with_pokemon_trainer(self._username, self._password)
        
    def get_access_token(self): return self._access_token
    def get_auth_provider(self): return self._auth_provider
    
    # Calls
    
    def _call(self, endpoint, data):
        is_skiplagged_api = 'skiplagged' in endpoint
        requests_session = self._requests_skiplagged_session if is_skiplagged_api else self._requests_niantic_session
        
        for _ in xrange(3):
            try:
                if is_skiplagged_api:
                    r = requests_session.post(endpoint, data, verify=False)
                    return json.loads(r.content)
                else:
                    r = requests_session.post(endpoint, base64.b64decode(data), verify=False)
                    return base64.b64encode(r.content)  
            except Exception:
                print "post exception", traceback.format_exc()
                time.sleep(1)
    
    def get_specific_api_endpoint(self):
        print time.time(), "called get_specific_api_endpoint" 
        response = self._call(self.SKIPLAGGED_API, {
                                                    'access_token': self.get_access_token(), 
                                                    'auth_provider': self.get_auth_provider()
                                                    })
        if not 'pdata' in response: raise Exception('failed to get pdata 1')
        
        response = self._call(self.GENERAL_API, response['pdata'])
        if not response: raise Exception('pdata api call failed')
        
        response = self._call(self.SKIPLAGGED_API, {
                                                    'access_token': self.get_access_token(),
                                                    'auth_provider': self.get_auth_provider(),
                                                    'pdata': response
                                                    })
        if not 'api_endpoint' in response: raise Exception('failed to retrieve specific api endpoint')
        self.SPECIFIC_API = response['api_endpoint']
        return self.SPECIFIC_API
        
    def get_profile(self):
        print time.time(), "called get_profile" 
        if not self.SPECIFIC_API: self.get_specific_api_endpoint()
        
        response = self._call(self.SKIPLAGGED_API, {
                                                    'access_token': self.get_access_token(), 
                                                    'auth_provider': self.get_auth_provider(),
                                                    'api_endpoint': self.SPECIFIC_API
                                                    })
        if not 'pdata' in response: raise Exception('failed to get pdata 1')
        
        response = self._call(self.SPECIFIC_API, response['pdata'])
        if not response: raise Exception('pdata api call failed')
        
        self.PROFILE_RAW = response
        
        response = self._call(self.SKIPLAGGED_API, {
                                                    'access_token': self.get_access_token(),
                                                    'auth_provider': self.get_auth_provider(),
                                                    'api_endpoint': self.SPECIFIC_API,
                                                    'pdata': self.PROFILE_RAW
                                                    })

        if not 'username' in response: raise Exception('failed to retrieve profile')
        self.PROFILE = response
        return self.PROFILE
    
    # Generates a realistic path to traverse the bounds and find spawned pokemon
    # Processed sequentially and with delay to minimize chance of getting account banned
    def find_pokemon(self, bounds, step_size=0.002):
        print time.time(), "called find_pokemon" 
        if not self.PROFILE_RAW: self.get_profile()
        
        bounds = '%f,%f,%f,%f' % (bounds[0] + bounds[1])
                
        response = self._call(self.SKIPLAGGED_API, {
                                                    'access_token': self.get_access_token(), 
                                                    'auth_provider': self.get_auth_provider(),
                                                    'profile': self.PROFILE_RAW,
                                                    'bounds': bounds,
                                                    'step_size': step_size
                                                    })
        if not 'requests' in response: raise Exception('failed to get requests')
                
        for request in response['requests']:
            print time.time(), "moving player"
            pokemon_data = self._call(self.SPECIFIC_API, request['pdata'])
            response = self._call(self.SKIPLAGGED_API, {'pdata': pokemon_data})
            
            num_pokemon_found = len(response['pokemons'])
            if num_pokemon_found > 0: print time.time(), "found %d pokemon" % (num_pokemon_found)
            for pokemon in response['pokemons']: yield Pokemon(pokemon )
            
            time.sleep(.5)
            