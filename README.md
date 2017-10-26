# minori

### features
* execute actions when scraping from RSS feeds
* no mal support

### requirements
* [feedparser](https://pypi.python.org/pypi/feedparser)

### examples
Add a show:

`./minori.py addshow "Onyankopon" 12 "[HorribleSubs],1080p,mkv"`

Add a rss feed:

`./minori.py addrss "HorribleSubs" "urlhere"`

Scan rss feeds for shows

`./minori.py --scan`

Scan rss feeds for shows, and execute actions

`./minori.py --download`

A continuous version of --download

`./minori.py --minorin`

### todo
* add pre/post scan hooks
* add a hook for each minorin iteration
* add support for .torrent files (only tested magnet links)
* do something with a downloads folder?
* add mal support?
* frontend?

### sample
``` ./minori.py --download
2017-10-11 20:37:00,324 [DEBUG] Parsed feed HorribleSubs RSS with 50 entries
2017-10-11 20:37:00,324 [DEBUG] Parsed all entries, ended up with compiled length 50
2017-10-11 20:37:00,324 [DEBUG] Compiled this list of keywords: ['[HorribleSubs]', '1080p', 'mkv', '01', 'Onyankopon']
2017-10-11 20:37:00,325 [DEBUG] Compiled a filtered list of length 1
2017-10-11 20:37:00,552 [INFO] Sent download to deluge: [HorribleSubs] Onyankopon - 01 [1080p].mkv
2017-10-11 20:37:00,552 [INFO] Added [HorribleSubs] Onyankopon - 01 [1080p].mkv to downloads
```
