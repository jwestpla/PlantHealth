import requests
import json

def run():
    """
    This script downloads the relevant JSON file from the mattilsynet webpage and 
    saves it under "godkjente_plantevernmidler_data.json" for further prosessing
    """
    
    base_url = 'https://api.plantevernmidler.mattilsynet.io'
    endpoint = '/godkjente_kjemiske_mikrobiologiske_preparater'

    url = f'{base_url}{endpoint}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
    else:
        print(f'Failed to retrieve data from {endpoint}: {response.status_code}')
        data = {}

    output_file = 'godkjente_plantevernmidler_data.json'

    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)

    print(f'Data has been written to {output_file}')
    
if __name__ == "__main__":
    run()