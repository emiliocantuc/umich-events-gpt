import requests, argparse, json, os, re
import utils

def get_events(url):
    """Gets the events from the url and returns them as a list of dictionaries"""
    r = requests.get(url)
    try:
        return r.json()
    except:
        raise Exception('Could not parse events from the url. Make sure its the JSON version of the events page.')
    

def filter_events(events, blacklist, verbose=False):
    """Filters the events that have words on the blacklist"""

    filtered_events = []
    for event in events:
        title = event['event_title'].lower()
        if not any(re.search(r'\b{}\b'.format(word), title) for word in blacklist):
            filtered_events.append(event)
        else:
            if verbose: print(f'Filtered out {title}')
    
    return filtered_events

def event_to_string(event, max_length=150):
    """Converts an event to a string to be passed to GPT to filter out. TODO make GPT do this?"""

    event_type = event['event_type']
    if '/' in event_type: event_type = event_type.split('/')[0].strip()
    
    s = '.'.join([event_type, event['combined_title'], event['description']])
    s = re.sub(r'\s+', ' ', s)
    s = s[:max_length]

    return s


def prompt_gpt(str_events, preferences, key):
    """Prompts GPT-3 to filter the events"""

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + key,
    }

    json_data = {
        'model': 'gpt-3.5-turbo-1106',
        'response_format':{
            'type': 'json_object',
        },
        'messages': [
            {
                'role': 'system',
                'content': f'You are an assistant that will recommend events from my university to me based on my preferences. {preferences}. I will prompt you with an event description per line and you must respond with an "events" JSON formated array with the events which you think are the most relevant to me. Only include the line number of the event in the array. For example, if you think the first and third events are relevant, you should respond with [1, 3].',
            },
            {
                'role': 'user',
                'content': str_events,
            },
        ],
    }

    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=json_data)
    return response
    

def filter_events_gpt(str_events, preferences, key, n_tries=3, verbose=False):
    """Filters the events using GPT-3"""
    
    for i in range(n_tries):
        try:
            response = prompt_gpt(str_events, preferences, key)
            if verbose: print(response, response.json())
            gpt_json = json.loads(response.json()['choices'][0]['message']['content'])
            gpt_recommendations_ixs = [int(j) for j in gpt_json['events']]
            assert all(0 < j < len(str_events.split('\n')) for j in gpt_recommendations_ixs), f'Invalid index in GPT response ({response.json()})'
            return gpt_recommendations_ixs
        
        except:
            print(f'Failed to get response from GPT-3. Trying again ({i+1}/{n_tries})')
            if i == n_tries-1: raise Exception('Failed to get response from GPT-3.')

if __name__ == '__main__':
    
    # Parse the url and Open AI key from the command line
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True, help='Umich events url to get events from in JSON format')
    parser.add_argument('--key', required=True, help='Open AI API key')
    parser.add_argument('-v', '--verbose', type=bool, default=1, help='Prints more information')
    args = parser.parse_args()

    # url = 'https://events.umich.edu/week/json?filter=types:21,5,13,19,18,&v=2'
    events = get_events(url)
    print(f'Got {len(events)} events from events.umich.edu\'s API.')

    # Read blacklist from blacklist.txt if it exists and filter
    blacklist = []
    filtered_events = events
    if os.path.exists('blacklist.txt'):
        with open('blacklist.txt','r') as f:
            blacklist = f.read().split('\n')
            filtered_events = filter_events(events, blacklist, args.verbose)
            print(f'Removed {len(events)-len(filtered_events)} events using {len(blacklist)} blacklisted words.')
            print(f'{len(filtered_events)} events remaining.')
    
    # Convert the events to strings and concat them (numbered)
    str_events = '\n'.join([f'{i}. {event_to_string(event)}' for i, event in enumerate(filtered_events)])
    if args.verbose: print(str_events)

    # Filter the events using GPT and user preferences
    if os.path.exists('prompt.txt'):

        with open('prompt.txt','r') as f: preferences = f.read()
        filtered_events_by_gpt = filter_events_gpt(str_events, preferences, args.key, 3, args.verbose)
        print(filtered_events_by_gpt)
    
    # Update HTML page
    recommended_events = [filtered_events[i] for i in filtered_events_by_gpt]
    utils.update_page(recommended_events)