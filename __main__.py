from bs4 import BeautifulSoup
import datetime
from discord import Color, Embed
import json
from paramiko import AutoAddPolicy, SSHClient, RSAKey
from plexapi.server import PlexServer
import re
import requests
import time

# Constants

colors = {
    'Anime': Color.from_rgb(245, 167, 223),
    'Dramas': Color.from_rgb(145, 240, 100),
    'Movies': Color.from_rgb(233, 33, 33),
    'TV': Color.from_rgb(16, 95, 213)
}

dbid_regex = re.compile('.*(((anidb|tvdb)\d?)-(\d+))', re.IGNORECASE)

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US;en;q=0.5',
    'Host': 'anidb.net',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0'
}


def generate_embed(info, show):
    if info['year'] is None:
        return
    embed = Embed(color=colors.get(show.librarySectionTitle, 0))
    # embed.set_author(name=show.librarySectionTitle)
    embed.title = '{title} ({year})'.format(
        title=info['title'], year=info['year'])
    embed.description = info['summary']
    embed.set_footer(text='{studio} | {genres}'.format(
        studio=info['studio'], genres=', '.join(info['genres'])))

    artwork = get_artwork_url(info['id'], show)
    if artwork is not None:
        embed.set_thumbnail(url=artwork)
    else:
        return None

    db_url = get_db_url(info['id'])
    if db_url is not None:
        embed.url = db_url

    return embed.to_dict()


def generate_info(show):
    dbid = dbid_regex.match(show.guid)
    dbid = dbid.group(1) if dbid is not None else show.guid

    info = {
        "id": dbid,
        "year": show.year,
        "title": show.title,
        "embed": None,
        "studio": show.studio,
        "summary": (show.summary[:2000] + '...') if len(show.summary) > 2000 else show.summary,
        "genres": list(map(lambda genre: genre.tag, show.genres))
    }

    return info


def get_artwork_url(dbid, show):
    if 'anidb' in dbid:
        res = requests.get(get_db_url(dbid), headers=headers)
        soup = BeautifulSoup(res.content, 'html.parser')
        return soup.find('meta', property='og:image')['content']
    if 'tvdb' in dbid:
        id = dbid_regex.match(dbid).group(4)
        return 'https://artworks.thetvdb.com/banners/posters/{id}-1.jpg'.format(id=id)
    if 'plex' in dbid:
        pr = re.compile('plex://(\w+)/(\w+)').match(dbid)
        if pr is not None:
            # /photo/:/transcode?width=480&height=720&url=/library/metadata/26982/thumb/1632127789?X-Plex-Token={token}
            ssh.exec_command('curl "{server}/photo/:/transcode?width=480&height=720&url={thumb}?a=b&X-Plex-Token={token}" -o /var/www/img/plex-{type}-{id}.png'.format(
                server=plex_server, thumb=show.thumb, token=plex_token, type=pr.group(1), id=pr.group(2)
            ))
            time.sleep(2.0)
            return '{server}/plex-{type}-{id}.png'.format(server=config['credentials']['imageServerUrl'], type=pr.group(1), id=pr.group(2))
    return None


def get_db_url(dbid):
    if 'anidb' in dbid:
        id = dbid_regex.match(dbid).group(4)
        return 'https://anidb.net/anime/{id}'.format(id=id)
    if 'tvdb' in dbid:
        id = dbid_regex.match(dbid).group(4)
        response = requests.get(
            'https://api.thetvdb.com/series/{id}'.format(id=id))
        response.raise_for_status()
        return 'https://thetvdb.com/series/{slug}'.format(slug=response.json()['data']['slug'])
    return None


def get_recently_added():
    recentlyAdded = []
    for section in sections:
        for show in section.recentlyAdded(maxresults=7):
            recentlyAdded.append(show)
    return recentlyAdded


def read_config():
    with open('data.json') as data:
        return json.load(data)


def write_config():
    with open('data.json', 'w') as out:
        json.dump(config, out, indent=4)


# Config setup
config = read_config()

plex_server = config['credentials']['plexServerUrl']
plex_token = config['credentials']['plexToken']
webhook_url = config['credentials']['webhookUrl']

# Plex setup

plex = PlexServer(plex_server, plex_token)

anime = plex.library.section('Anime')
dramas = plex.library.section('Dramas')
movies = plex.library.section('Movies')
tv = plex.library.section('TV')

sections = [anime, dramas, movies, tv]

# SSH config

ssh = SSHClient()
ssh_key = RSAKey.from_private_key_file(config['credentials']['sshKeyFile'])

ssh.set_missing_host_key_policy(AutoAddPolicy())
ssh.connect(hostname=config['credentials']['sshHostname'],
            username=config['credentials']['sshUsername'], pkey=ssh_key)

# Start

start = time.time()
loop = config['refreshInterval'] or 60.0

print('[{timestamp}] [info] refreshing every {loop} seconds.'.format(
    loop=loop, timestamp=datetime.datetime.now().strftime("%H:%M:%S.3%f")[:-4]))

while True:
    for show in get_recently_added():
        info = generate_info(show)

        if info['id'] in config['parsed']:
            continue

        embed = generate_embed(info, show)

        if embed is not None:
            print(
                '[{timestamp}] [info] new show detected: `{title} ({year}) [{id}]`'.format(timestamp=datetime.datetime.now().strftime("%H:%M:%S.3%f")[:-4], title=info['title'], year=info['year'], id=info['id']))

            res = requests.post(webhook_url, json={"embeds": [embed]})
            res.raise_for_status()
            config['parsed'][info['id']] = '{title} ({year})'.format(
                title=info['title'], year=info['year'])
            write_config()

        time.sleep(3.0 - ((time.time() - start) % 3.0))
    time.sleep(loop - ((time.time() - start) % loop))
    config = read_config()
    loop = config['refreshInterval'] or 60.0
