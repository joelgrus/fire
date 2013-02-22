#FIRE

This is the code for my "Secrets of Fire Truck Society" talk for the [Ignite at Strata 2013](http://strataconf.com/strata2013/public/schedule/detail/28194).  Really, it's not very interesting, but my slides say I put it here, so I put it here.  I doubt you want to *use* it; however, you might find it interesting to look at, discover mistakes in, and so on.

## Ruby

In the `ruby` directory is the script to scrape the [Seattle Real-Time 911](http://www2.seattle.gov/fire/realtime911/getDatePubTab.asp) site.  It's written in Ruby because I cribbed it from my [Hacker News scraping code](https://github.com/joelgrus/hackernews), which was in Ruby, because I don't know why.  If I were writing it from scratch it would be in Python.

It relies on MongoMapper and it sticks the data in MongoDB on localhost.  Really, there's no reason why you should ever need to use this scraper.  If you want the data that bad, you can ask me or write your own.

THAT SAID, if despite my warnings you really want to use it, just do

    ruby scrape_fire.rb 2011-01-01

which will scrape from 2011-01-01 until today.  

## Python

In the `python` directory is the code I used for my analysis.  None of these files is particularly command-line-able, I mostly copied and pasted from them into iPython.

### `fire.py` 

loads data from the database and defines a few helper functions.  

### `geocode.py` 

geocodes all the locations in the data and then sticks that data in Mongo too.  I ran it against a [DSTK](http://www.datasciencetoolkit.org/) instance running virtually on my laptop, which took about 24 hours to geocode 100K locations.  If you have a better (free) geocoding solution, I'd like to hear it!

### `plots.py`

creates plots from the geocoded data.  Relies on [Basemap](http://matplotlib.org/basemap/), which in turn relies on Matplotlib, which in turn relies on something else, and so on.  I hardcoded the window around Seattle, although that's easy enough to change if you want to plot points elsewhere.

### `networks.py`

does two different things.  First, it produces GEXF files that are suitable for loading into [Gephi](https://gephi.org/) and making those network diagrams that everyone hates.  It also produces graphs in [NetworkX](http://networkx.github.com/) format, to which you can then apply all sorts of graph algorithms.

## Data

Like I mentioned before, the data is too big to post here, but if you want it that badly, I'll find a way to get it to you.

## Slides

I'll put a link here once they're done.

## Talk

I'll put a link here too, if anyone takes a video of it.