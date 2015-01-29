#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# Tell the browser to remember the redirection and do not bother you for X seconds, so it reduces the pressure on the server.
# You probably do not want to set it higher than 300, or it will disallow redir-from-china to choose another URL for the client after 5 minutes.
REDIRECT_CACHE_AGE = 300

# Print out the top 10 hostnames the user has originally tended to go to.
STATISTICS_INTERVAL = 300

# Auto pull will get a list of URLs which are suitable to be the redirection target.
# Comment out the following lines to disable auto pull, in which case you will maintain target.txt manually
AUTO_PULL_LIST = "https://raw.githubusercontent.com/greatfire/wiki/master/README.md"
AUTO_PULL_INTERVAL = 86400

# BitTorrent flood protect
# Tell the BitTorrent client not to bother you for X seconds, so it reduces the pressure on the server.
BT_PROTECT_CACHE_AGE = 86400

# Send a message to the BitTorrent client
BT_PROTECT_MESSAGE = "Request is blocked by GFW"
