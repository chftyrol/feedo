#!/usr/bin/python

#   Feedo is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Feedo is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Feedo.  If not, see <http://www.gnu.org/licenses/>.

import feedparser
import concurrent.futures 
import re
import praw
from optparse import OptionParser
import logging
from logging.handlers import RotatingFileHandler
import sys
import configparser

CREDENTIALS_FILE = sys.path[0] + "/credentials.conf"
SOURCES_FILE = sys.path[0] + "/sources.txt"
LOG_FILE = sys.path[0] + "/feedo.log"
SUBREDDIT = ""
DRYRUN = False
VERSION = "1.0"
ENTRIES_PER_FEED = 5

lastposts = []
logger = None

def main():
    # Poll RSS feeds
    logger.debug("Polling RSS feeds.")
    feeds = []
    try :
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            calls = [executor.submit(feedparser.parse, rss_url) for rss_url in sources]
            for future in concurrent.futures.as_completed(calls):
                feeds.append(future.result())
    except KeyboardInterrupt as ki:
        logger.info("Caught interrupt: quitting.")
        quit()
    except :
        logger.error("An error occurred while polling RSS feeds.")
    # Preparing to post
    logger.debug("Preparing to post.")
    try :
        for feed in feeds:
            for i in range(1, ENTRIES_PER_FEED):
                title = feed['entries'][i]['title']
                title = title.replace("\n", " ")
                title = re.sub(r"\s+", " ", title)
                url = feed['entries'][i]['link']
                if url in lastposts:
                    logger.debug("Already posted: %s", title)
                else :
                    logger.debug("Posting: %s", title)
                    reddit.subreddit(SUBREDDIT).submit(title, url=url)
    except praw.exceptions.APIException as apie:
        logger.error("Something went wrong over at Reddit. Message %s", apie.message)
    except praw.exceptions.ClientException as cerr:
        logger.error("Something went here while posting to Reddit.")
    except KeyboardInterrupt as ki:
        logger.info("Caught interrupt: quitting.")
        quit()

    logger.debug("Completed.")

def init():
    global reddit, lastposts, sources
    credparser = configparser.ConfigParser()
    try :
        logger.debug("Reading credentials from %s.", CREDENTIALS_FILE)
        credparser.read(CREDENTIALS_FILE)
        username = credparser['Redditor']['Username']
        password = credparser['Redditor']['Password']
        clientid = credparser['Application']['ID']
        clientsecret = credparser['Application']['Secret']
        useragent = 'praw:' + clientid + ':' + VERSION
        reddit = praw.Reddit(client_id=clientid, \
                             client_secret=clientsecret, \
                             username=username, \
                             password=password, \
                             user_agent=useragent)
        # Load last 100 posts to check we're not reposting.
        logger.debug("Loading last 100 posts.")
        for p in reddit.subreddit(SUBREDDIT).new(limit=100):
            lastposts.append(p.url)
        logger.debug("Loading sources.")
        with open(SOURCES_FILE, "r") as f:
            sources = f.readlines()
        sources = [ line.strip() for line in sources ]
    except configparser.Error as err:
        logger.error("Could not read credentials from %s . The reason is: %s", CREDENTIALS_FILE, err.msg)
        quit()
    except praw.exceptions.APIException as apie:
        logger.error("Something went wrong over at Reddit. Message %s", apie.message)
    except praw.exceptions.ClientException as cerr:
        logger.error("Something went here while talking with Reddit.")
    except OSError as ose:
        logger.error("Could not load sources from file %s.", SOURCES_FILE)
        quit()
    except KeyError as ke:
        logger.error("The file %s you specified is does not hold valid credentials.", CREDENTIALS_FILE)
        quit()
    except KeyboardInterrupt as ki:
        logger.info("Caught interrupt: quitting.")
        quit()

if __name__ == "__main__":
    optparser = OptionParser(description="A bot for reddit that posts content from RSS feeds", version=VERSION)
    optparser.add_option("-v", "--verbose", help="Print debugging messages to stdout.", action="store_true", dest="verbose")
    optparser.add_option("-n", "--dry-run", help="Only print to stdout: don't post to Reddit.", action="store_true", dest="dry")
    optparser.add_option("-S", "--subreddit", help="Specify the subreddit where you want to post.", action="store", type="str", dest="subreddit")
    optparser.add_option("-l", "--logfile", help="Specify the log file for this bot.", action="store", type="str", dest="logfile")
    optparser.add_option("-c", "--credentials", help="Specify the credentials file for this bot.", action="store", type="str", dest="credentials")
    optparser.add_option("-s", "--sources", help="Specify the file containing the RSS feeds, one per line, for this bot.", action="store", type="str", dest="sources")
    optparser.add_option("-N", "--entries", help="Specify the number of articles per source to be considered.", action="store", type="str", dest="count")
    (options, args) = optparser.parse_args()
    if not options.subreddit:
        optparser.error("You must specify a subreddit.")
    else :
        SUBREDDIT = options.subreddit
    if options.dry:
        DRYRUN = True
    if options.logfile:
        LOG_FILE = options.logfile
    if options.credentials:
        CREDENTIALS_FILE = options.credentials
    if options.sources:
        SOURCES_FILE = options.sources
    if options.count:
        ENTRIES_PER_FEED = options.count
    if options.verbose:
        stdoutlevel = logging.DEBUG
    else :
        stdoutlevel = logging.ERROR
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    rfhandler = RotatingFileHandler(LOG_FILE)
    rfhandler.setLevel(logging.DEBUG)
    stdouthandler = logging.StreamHandler()
    stdouthandler.setLevel(stdoutlevel)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    rfhandler.setFormatter(formatter)
    stdouthandler.setFormatter(formatter)
    logger.addHandler(rfhandler)
    logger.addHandler(stdouthandler)
    logger.debug("Initializing.")
    init()
    logger.debug("Running.")
    main()
