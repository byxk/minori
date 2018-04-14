# minori

### features
* execute actions when scraping from RSS feeds
* no mal support

### requirements
* [feedparser](https://pypi.python.org/pypi/feedparser)
* [click](http://click.pocoo.org/5/)

### install

`pip install .` 

or

`python3 setup.py install`

### workflow
Add a feed first:

`minori manage_feeds add_feed nyaa "https://nyaa.pantsu.cat/feed?"`

Then add a show:

```minori manage_shows add_show "Legend of the Galactic Heroes - Die Neue These" "[HorribleSubs] Legend of the Galactic Heroes - Die Neue These - @@EP_VAR@@ [1080p].mkv" --feed nyaa```

Scan rss feeds for shows

`minori check`

### actions

Minori will load 'actions', which are basically plugins installed in `actions/`.
These actions can add their own functionality and subcommands, see `download.py`.

TODO: Update with some dev api info

When a show has been found on a feed, Minori will execute all loaded actions,
providing them with the internal db, and the Minori 'context' - a dictionary containing
info about the show/link/feed.

### todo
* we want custom feed paths!
* clear documentation/standards for the action api
* documentation on the Minori context
* mvar replacer documentation/standards
* add mal support?
* frontend?

### sample
```
 minori check
[INFO] Looking for Legend of the Galactic Heroes - Die Neue These with title_format [HorribleSubs] Legend of the Galactic Heroes - Die Neue These - 03 [1080p].mkv
[INFO] Looking for Darling in the FranXX with title_format [HorribleSubs] Darling in the FranXX - 13 [1080p].mkv
[INFO] Looking for 3D Kanojo Real Girl with title_format [HorribleSubs] 3D Kanojo Real Girl - 03 [1080p].mkv
[INFO] Looking for Steins Gate 0 with title_format [HorribleSubs] Steins Gate 0 - 02 [1080p].mkv
[INFO] Looking for Wotaku ni Koi wa Muzukashii with title_format [HorribleSubs] Wotaku ni Koi wa Muzukashii - 02 [1080p].mkv
```
