import requests
import os
import json
import yaml
from datetime import datetime

def auth():
    path = '../../../_config/keys.yaml'
    with open(path, 'r') as f:
        keys = yaml.safe_load(f)
    return keys['BearerToken']

def create_query(t_start, t_end, n_token=None):
    # query
    query = 'advertisement'
    query += ' lang:en -is:retweet -is:reply'
    query = requests.utils.quote(query) # http encode
    # tweet.fields
    tweet_fields ='''\
        tweet.fields=author_id,public_metrics,attachments,source,entities,\
        conversation_id,created_at,referenced_tweets,context_annotations\
    '''
    tweet_fields = tweet_fields.replace(' ', '')
    # expansions
    expansions = "expansions=author_id,attachments.media_keys"
    # user.fields
    user_fields = '''\
        user.fields=description,created_at,profile_image_url,verified\
    '''
    user_fields = user_fields.replace(' ', '')
    # media.fields
    media_fields = "media.fields=public_metrics,duration_ms,preview_image_url"
    # max_results
    max_results = 'max_results=100'
    # time constraints
    start_time = 'start_time=' + t_start
    end_time = 'end_time=' + t_end
    # next token
    if n_token is not None:
        next_token = 'next_token=' + n_token
    # full query string
    if n_token is None:
        query_url = 'query={}&{}&{}&{}&{}&{}&{}&{}'.format(
            query, tweet_fields, expansions, user_fields, media_fields,
            max_results, start_time, end_time
        )
    else:
        query_url = 'query={}&{}&{}&{}&{}&{}&{}&{}&{}'.format(
            query, tweet_fields, expansions, user_fields, media_fields,
            max_results, start_time, end_time, next_token
        )
    return query_url

def create_url(query_url):
    base_url = 'https://api.twitter.com/2/tweets/search/recent?'
    url = base_url + query_url
    return url


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def connect_to_endpoint(url, headers):
    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def main():
    start_time = '2021-06-17T06:00:00.00Z'
    end_time = '2021-06-18T05:59:00.00Z'
    name = '../../data/raw/advertisement_4_'
    next_token = None
    request_number = 0
    while True and request_number < 450:
        request_number += 1
        bearer_token = auth()
        query_url = create_query(start_time, end_time, n_token=next_token)
        url = create_url(query_url)
        headers = create_headers(bearer_token)
        json_response = connect_to_endpoint(url, headers)
        json_dump = json.dumps(json_response, indent=4, sort_keys=True)
        if next_token is None:
            with open(name[:-1] + '.json', 'w') as f:
                f.write(json_dump)
        else:
            with open(name + next_token + '.json', 'w') as f:
                f.write(json_dump)
        try:
            next_token = json_response['meta']['next_token']
        except:
            break
    if request_number == 450:
        with open('make_raw_data_advertisement_4.log', 'w') as f:
            now = datetime.now()
            f.write(f'Reached maximum number of requests at {now}')
            f.write(f'Next token: {next_token}')


if __name__ == "__main__":
    main()