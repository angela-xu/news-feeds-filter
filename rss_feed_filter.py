import feedparser
import string
import time
from project_util import translate_html
from Tkinter import *


#======================
# Code for retrieving and parsing RSS feeds
#======================

def process(url):
    """
    Fetches news items from the rss url and parses them.
    Returns a list of NewsStory-s.
    """
    feed = feedparser.parse(url)
    entries = feed.entries
    ret = []
    for entry in entries:
        guid = entry.guid
        title = translate_html(entry.title)
        link = entry.link
        summary = translate_html(entry.summary)
        try:
            subject = translate_html(entry.tags[0]['term'])
        except AttributeError:
            subject = ""
        newsStory = NewsStory(guid, title, subject, summary, link)
        ret.append(newsStory)
    return ret


#======================
# Data structure design
#======================

class NewsStory(object):
    def __init__(self, guid, title, subject, summary, link):
        self.guid = guid
        self.title = title
        self.subject = subject
        self.summary = summary
        self.link = link
    
    def getGuid(self):
        return self.guid
    
    def getTitle(self):
        return self.title
    
    def getSubject(self):
        return self.subject

    def getSummary(self):
        return self.summary

    def getLink(self):
        return self.link


#======================
# Triggers
#======================

class Trigger(object):
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        raise NotImplementedError


class WordTrigger(Trigger):
    def __init__(self, word):
        self.word = word
    
    def isWordIn(self, text):
        text = [a.strip(string.punctuation).lower() for a in text.split(' ')]
        for i in text:
            if self.word.lower() in i.split("'"):
                return True
        return False
            

class TitleTrigger(WordTrigger):
    def evaluate(self, story):
        return self.isWordIn(story.getTitle())


class SubjectTrigger(WordTrigger):
    def evaluate(self, story):
        return self.isWordIn(story.getSubject())


class SummaryTrigger(WordTrigger):
    def evaluate(self, story):
        return self.isWordIn(story.getSummary())


# Composite Triggers

class NotTrigger(Trigger):
    def __init__(self, t):
        self.t = t

    def evaluate(self, story):
        return not self.t.evaluate(story)


class AndTrigger(Trigger):
    def __init__(self, t1, t2):
       self.t1 = t1
       self.t2 = t2

    def evaluate(self, story):
       return self.t1.evaluate(story) and self.t2.evaluate(story)


class OrTrigger(Trigger):
    def __init__(self, t1, t2):
       self.t1 = t1
       self.t2 = t2

    def evaluate(self, story):
       return self.t1.evaluate(story) or self.t2.evaluate(story)


# Phrase Trigger

class PhraseTrigger(Trigger):
    def __init__(self, phrase):
        self.phrase = phrase

    def evaluate(self, story):
        l = [story.getGuid(), story.getTitle(), story.getSubject(), story.getSummary(), story.getLink()]
        for i in l:
            if self.phrase in i:
                return True
        return False


#======================
# Filtering
#======================

def filterStories(stories, triggerlist):
    """
    Takes in a list of NewsStory instances.

    Returns: a list of only the stories for which a trigger in triggerlist fires.
    """
    l = []
    for i in stories:
        for j in triggerlist:
            if j.evaluate(i) == True:
                l.append(i)
                break
    return l


#======================
# User-Specified Triggers
#======================

def makeTrigger(triggerMap, triggerType, params, name):
    """
    Takes in a map of names to trigger instance, the type of trigger to make,
    and the list of parameters to the constructor, and adds a new trigger
    to the trigger map dictionary.

    triggerMap: dictionary with names as keys (strings) and triggers as values
    triggerType: string indicating the type of trigger to make (ex: "TITLE")
    params: list of strings with the inputs to the trigger constructor (ex: ["world"])
    name: a string representing the name of the new trigger (ex: "t1")

    Modifies triggerMap, adding a new key-value pair for this trigger.

    Returns a new instance of a trigger (ex: TitleTrigger, AndTrigger).
    """
    if triggerType == "TITLE":
        triggerMap[name] = TitleTrigger(params[0])
 
    elif triggerType == "SUBJECT":
        triggerMap[name] = SubjectTrigger(params[0])
 
    elif triggerType == "SUMMARY":
        triggerMap[name] = SummaryTrigger(params[0])
 
    elif triggerType == "NOT":
        triggerMap[name] = NotTrigger(triggerMap[params[0]])
 
    elif triggerType == "AND":
        triggerMap[name] = AndTrigger(triggerMap[params[0]], triggerMap[params[1]])
 
    elif triggerType == "OR":
        triggerMap[name] = OrTrigger(triggerMap[params[0]], triggerMap[params[1]])
 
    elif triggerType == "PHRASE":
        triggerMap[name] = PhraseTrigger(' '.join(params))
 
    return triggerMap[name]


def readTriggerConfig(filename):
    """
    Returns a list of trigger objects
    that correspond to the rules set
    in the file filename
    """
    # to read in the file and eliminate blank lines and comments
    triggerfile = open(filename, "r")
    all = [ line.rstrip() for line in triggerfile.readlines() ]
    lines = []
    for line in all:
        if len(line) == 0 or line[0] == '#':
            continue
        lines.append(line)

    triggers = []
    triggerMap = {}

    for line in lines:
        linesplit = line.split(" ")

        # Making a new trigger
        if linesplit[0] != "ADD":
            trigger = makeTrigger(triggerMap, linesplit[1],
                                  linesplit[2:], linesplit[0])

        # Add the triggers to the list
        else:
            for name in linesplit[1:]:
                triggers.append(triggerMap[name])

    return triggers

    
import thread
SLEEPTIME = 60 #seconds -- how often we poll


def main_thread(master):
    # A sample trigger list
    try: 
        triggerlist = readTriggerConfig("triggers.txt")

        # **** drawing ****
        frame = Frame(master)
        frame.pack(side=BOTTOM)
        scrollbar = Scrollbar(master)
        scrollbar.pack(side=RIGHT,fill=Y)
        
        t = "Google & Yahoo Top News"
        title = StringVar()
        title.set(t)
        ttl = Label(master, textvariable=title, font=("Helvetica", 18))
        ttl.pack(side=TOP)
        cont = Text(master, font=("Helvetica",14), yscrollcommand=scrollbar.set)
        cont.pack(side=BOTTOM)
        cont.tag_config("title", justify='center')
        button = Button(frame, text="Exit", command=root.destroy)
        button.pack(side=BOTTOM)

        # Gather stories
        guidShown = []
        def get_cont(newstory):
            if newstory.getGuid() not in guidShown:
                cont.insert(END, newstory.getTitle()+"\n", "title")
                cont.insert(END, "\n---------------------------------------------------------------\n", "title")
                cont.insert(END, newstory.getSummary())
                cont.insert(END, "\n*********************************************************************\n", "title")
                guidShown.append(newstory.getGuid())

        while True:

            print "Polling . . .",
            # Get stories from Google's Top Stories RSS news feed
            stories = process("http://news.google.com/?output=rss")

            # Get stories from Yahoo's Top Stories RSS news feed
            stories.extend(process("http://rss.news.yahoo.com/rss/topstories"))

            # Process the stories
            stories = filterStories(stories, triggerlist)

            map(get_cont, stories)
            scrollbar.config(command=cont.yview)


            print "Sleeping..."
            time.sleep(SLEEPTIME)

    except Exception as e:
        print e


if __name__ == '__main__':

    root = Tk()
    root.title("Some RSS parser")
    thread.start_new_thread(main_thread, (root,))
    root.mainloop()


