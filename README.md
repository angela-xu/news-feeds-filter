# News Feeds Filter
## Introduction
This is a News Feeds Filter to monitor news feeds over the Internet, which will filter the news, alerting the user when it 
notices a news story that matches that user's interests (for example, the user may be interested in a notification whenever 
a story related to the "2016 United States' Presidential Election" is posted). 
* Code is written in Python.
* Five files are included: 1) rss_feed_filter.py - the News Feeds Filter program;
                           2) triggers.txt - the trigger configuratgion file for users to set up filtering criteria 
                                             (for example, "election" in news summary);
                           3) feedparser.py - a module that retrieves and parses feeds fot the News Feed Filter;
                           4) project_util.py - a module that includes a function to convert simple HTML fragments to plain text.

## Installation and Usages
* Downlaod all files in this repository and save them in the same folder.
* Set up filtering criteria in triggers.txt.
* Run rss_feed_filter.py.
