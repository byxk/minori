# minori

### features
* only supports deluge
* no mal support
* no configuration options

### todo
* add pre/post download hooks
* add pre/post scan hooks

### sample
``` ./minori.py --download
2017-10-11 20:37:00,324 [DEBUG] Parsed feed HorribleSubs RSS with 50 entries
2017-10-11 20:37:00,324 [DEBUG] Parsed all entries, ended up with compiled length 50
2017-10-11 20:37:00,324 [DEBUG] Compiled this list of keywords: ['[HorribleSubs]', '1080p', 'mkv', '01', 'Onyankopon']
2017-10-11 20:37:00,325 [DEBUG] Compiled a filtered list of length 1
2017-10-11 20:37:00,552 [INFO] Sent download to deluge: [HorribleSubs] Onyankopon - 01 [1080p].mkv
2017-10-11 20:37:00,552 [INFO] Added [HorribleSubs] Onyankopon - 01 [1080p].mkv to downloads
```
