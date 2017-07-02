# Feedo
## A bot to post links from RSS feeds to a subreddit 

### Description
I thought of this script when needing a way to populate a small subreddit with some news I'm interested in that I could not find on Reddit.
The idea is that, given a list of RSS feeds and the name of a subreddit, Feedo will check if there are articles from the feed that it hasn't posted yet. In that case he posts them.

You can limit the number of articles per feed that Feedo will post (default is 5).

The best way to deploy Feedo is (on GNU/Linux) to then make a cronjob, a systemd timer or whatever you want. If you're not using GNU/Linux you can use whatever scheduling program you prefer. And then you can switch to GNU/Linux because you're wasting your time and money otherwise.

### Installation
Simply clone the repo:
```sh
$ git clone https://github.com/chftyrol/feedo.git
```
And install the dependencies:
```sh
$ sudo pip install -r requirements.txt
```

### Configuration
Clearly, to make this work you will need a Reddit account. Moreover you will need to [get API credentials](https://www.reddit.com/prefs/apps/) for that account.

Once you've done that fill out your account information in the file `credentials.txt.example` and then rename it to `credentials.txt`.

Finally you will need to specify the RSS feeds you would like to use. An example `sources.txt.example` file is provided and you can edit it at will. Just remember that you need to put one RSS feed per line.

When you are done rename it to `sources.txt`.

You can use command line options to specify different files for credentials and sources, but `credentials.txt` and `sources.txt` are the default values.

#### Tip
If by any chance you wish to use a single RSS feed as source and you use GNU/Linux you can also specify it without creating a file with the following _bashism_, called process substitution:
```sh
$ /path/to/feedo.py -S [thesubreddit] -s <(echo "https://awesomesource.com/feed.xml")
```

### Running
Simply run the script `feedo.py`. You will need Python 3 to do so.
A few command line options are available to change the behavior of the program. To check them out run `feedo.py -h`.

### License
Feedo is Free Software, released under the GPL version 3 or later. When I say *Free* I mean free as in free speech not as in free beer. To learn more about this you can check out the [Free Software Foundation](https://fsf.org).
