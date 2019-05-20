import requests
import json
import re
from bs4 import BeautifulSoup

USER_URL = 'https://www.instagram.com/'
TAG_URL = 'https://www.instagram.com/explore/tags/'
POST_URL = 'https://www.instagram.com/p/'

def get_shared_data(url: str):
    """Reads shared data from instagram sourcecode.
    
    Arguments:
        url {str} -- URL of the instagram page.
    
    Returns:
        json -- Shared data from URL.
    """

    # Get sourcecode from page
    source = requests.get(url)
    soup = BeautifulSoup(source.text, "html.parser")

    # Search for shared data and parse to json
    for item in soup.findAll('script'):
        if item.string is not None and item.string.startswith('window._sharedData'):
            content = item.string.replace("window._sharedData = ", "", 1)[:-1]
            return json.loads(content)

def get_tags_from_post(post_url: str):
    """Reads all hashtags from instagram post.
    
    Arguments:
        post_url {str} -- URL from instagram post.
    
    Returns:
        [str] -- List of used hashtags.
    """

    # Get page sourcecode 
    source = requests.get(post_url)
    soup = BeautifulSoup(source.text, "html.parser")

    # Parse all hashtags from source
    content = ""
    js = None
    for item in soup.findAll('script'):
        if item.string is not None and item.string.startswith('window._sharedData'):
            tags = re.findall(r"#[\w']+", item.string)
            return [x.lstrip('#') for x in tags]


def get_tags_from_user(user: str, num_of_posts: int = 9):
    """Reads all used hashtags from user of latest posts.
    
    Arguments:
        user {str} -- Username.
    
    Keyword Arguments:
        num_of_posts {int} -- Number of latest posts being used. (default: {9})
    
    Returns:
        [str] -- List of used hashtags.
    """
    
    data = get_shared_data(USER_URL + user)
    posts = data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']
    tags = []
    for post in posts[:num_of_posts]:
        post_tags = get_tags_from_post(POST_URL + post['node']['shortcode'])
        tags.extend(x for x in post_tags if x not in tags)

    return tags


def get_count_of_posts(tag: str):
    """Reads the number of posted contents with a hashtag.
    
    Arguments:
        tag {str} -- Hashtag.
    
    Returns:
        int -- Count of posts.
    """

    # Read shared Data
    data = get_shared_data(TAG_URL + tag)
    return int(data['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['count'])

