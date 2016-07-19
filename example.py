from skiplagged import Skiplagged


if __name__ == '__main__':
    client = Skiplagged()
    
    # Log in with a Google or Pokemon Trainer Club account
#     print client.login_with_google('GOOGLE_EMAIL', 'PASSWORD')
    print client.login_with_pokemon_trainer('USERNAME', 'PASSWORD')
    
    # Get specific Pokemon Go API endpoint
    print client.get_specific_api_endpoint()
    
    # Get profile
    print client.get_profile()
    
    # Find pokemon
    bounds = (
              (40.76356269219236, -73.98657795715332), # Lower left lat, lng
              (40.7854671345488, -73.95812508392333) # Upper right lat, lng
              ) # Central park, New York City
    
    for pokemon in client.find_pokemon(bounds):
        print pokemon
        