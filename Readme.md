# Redir-From-China

Redirecting away to fight back mysterious redirection from China

## Introduction

As of January 2015, a large number of site owners have reported mysterious access from China, which request for Facebook, Twitter or YouTube on their servers.

This is because China has set up a nation-wide Internet censorship program (like what NSA does in the USA), named [the Great Firewall](https://en.wikipedia.org/wiki/Internet_censorship_in_China), which blocks and redirects the access to the websites the government dislikes to a random IP address.

Yes! **Random address**, [even porn sites](http://chinadigitaltimes.net/2015/01/gfw-fail-visitors-blocked-sites-redirected-porn/) or **your site**.

It is reported that [some site was suffering from 300 Mbps of requests for YouTube](https://twitter.com/felixonmars/status/553207645838925824). If you suffer from that too, why don't you fight back?

By using Redir-From-China, you may redirect those requests away to a **politic site telling the truth of censorship**.

By doing this, Redir-From-China can also reduce the amount of the mysterious traffic with cache settings (see below).

## How to use?

Redir-From-China requires Python (either version 2 or 3) and [Python-Tornado](http://www.tornadoweb.org/). You also need your usual HTTP server (Nginx or Apache, etc) to serve normal requests.

```bash
apt-get install python-tornado
git clone https://github.com/m13253/redir-from-china.git
cd redir-from-china
vim config.py   # Edit config.py to suit your need
./redir.py 8000
```

Now, `redir.py` listens on `127.0.0.1:8000`.

You can then [configure your Nginx or Apache](http://nginx.com/resources/admin-guide/reverse-proxy/) to forward mysterious requests from China for Facebook, Twitter, YouTube or many other sites to `127.0.0.1:8000`.

## Redirection targets

By default, Redir-From-China uses [a list of URLs](https://github.com/greatfire/wiki) maintained by [GreatFire.org](https://greatfire.org/). Or if you disable auto pull in `config.py`, you can type in as many as real porn or politic sites you know into `target.txt`.

## Which benefit can you get?

Redir-From-China sets up a 5-minute cache on the client machine. So that the client will probably not bother you within another 5 minutes.

This can release the burden on your server by redirecting away the traffic. It also protects your server from [BitTorrent flood](http://furbo.org/2015/01/28/grass-mud-horse/) side-effect.

## Which benefit can the users get?

You helped them realize that they have been monitored and censored. The globe has been concerned about NSA and helped the Americans protect their rights, why can't we help Chinese this time?

## What about HTTPS?

It is said that _Qihoo 360 ~~Secure~~ Dangerous Browser_ and _Kingsoft Liebao Browser_ [does not check HTTPS certificate](http://www.zdnet.com/article/icloud-attack-is-blunt-and-obvious/) (see the last but one paragraph). Those are two of the major browsers in China.

So HTTPS can not protect you or them. It is recommended to deploy Redir-From-China on both HTTP or HTTPS if you originally have an HTTPS site.
