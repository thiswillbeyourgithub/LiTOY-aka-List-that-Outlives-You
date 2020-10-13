# LiTOY : the List That Outlives You.

## What is LiTOY?
There are several ways to look at it :
* LiTOY is a python script using sqlite to create and manage a list of your goals, be it short, medium or long term but more importantly : it ranks them in a smart and very flexible way using pairwise comparisons and several [ELO scores](https://en.wikipedia.org/wiki/Elo_rating_system).
* An organizer aiming at centralizing all your goals in a single place while quickly ranking them in an order reflecting user preferences.
* A way for me to practice my Python (very rusty, still a long way to go, don't hesitate to do PRs or open issue, they will be greately appreciated).


The idea behing LiTOY is simple : 
1. have all items in the same sqlite database
2. automatically pick 2 items and prompt the user for which is better according to a user-specified question
3. adjust the ELO score of each item accordingly
4. When enough pairwise comparisons are done, rank the items according to a user-specified formula, for example the ranking could reflect `Books I want to read ordered by importance and by shortest time to read (i.e. "I want the most important short books first")`



## Examples of use :
### Managing a reading queue 
* in this example : the items could only contain : URL ; details
* the user will only have to compare the importance of each article/book, the reading time will be automatically retrieved from the url
* the pairwise comparison of the reading time will correspond to the question "Which is shorter to read" and will be done automatically without user input.
* The final ranking can be something like `reading_time_ELO + importance_ELO`
* This should help the user read in order of what is most important AND shorter to read.


### Managing a movie Watchlist
* in this example : the items could only contain : a movie file path
* the code will, all by itself, retrieve the duration of the movie, the size of the file
* the user could be prompted with the question : "Which movie is the most important for you?", the answer will impact the respective ELO scores of the items
* The final ranking could be a weighted sum : `importance_ELO + duration_ELO + 1.2*size_ELO`
* This should allow the user to watch movies that are taking the most space but are also important while not lasting 4 hours.

### Managing a list where tasks have to be done in a specific order (example : errands, diy builiding)
* in this example : the items could only contain : a goal in text format
* The user could be prompted with the question : "Which task should be done first?", the answer will change the ELO score of each items
* The final ranking should quickly converge towards the correct order for steps. Probably works for finding the shorted path if you have errands too!



## FAQ
**Where does the idea come from?** From Gwern's [media resorted](https://www.gwern.net/Resorter).

**Do you have any idea it will work or at least converge towards something useful without doing thousands of fights a day?** Lol no.

**What does LiTOY stand for?** It's about the List that Outlives You. It is used as a [memento mori](https://en.wikipedia.org/wiki/Memento_mori)


**Do you accept criticism and/or contribution?** Hell Yeah! All help and criticisms are welcome.

**What are ELO scores? Why did you choose this algorithm?** A ranking system initially devised for chess. The idea is that if you have chess players A, B and C : if `A beats B` and `B beats C` then you don't really have to organize a fight between A and C to know which is better. It does so by assigning a score to each oponnent that can then be used to compare opponents that have never met each other. A strength of ELO is that it still behaves well even if some players underperform (or overperform). In the case of LiTOY, you can have some wrong comparisons in your db and it will not throw off the whole ranking. Also, ELO is dead easy to implement and I wanted to have a complete understanding of my code.

**What platform does it run on?** Try to make it as agnostic as possible but I'm on Linux and I might occasionnaly use unix only exec without paying attention. Don't hesitate to tell me if you run into an issue.

** What is manual mode ?** It launches python in a special way that allows yourself to launch script functions directly, very useful for debugging as well as undoing stuffo

**How can I undo X?** It is not really possible for now. But you can access the logs and see what you did wrong. Hopefully this can help you repair damage. Rollback features might be added sometime in the future. If you have any issue feel free to open one, especially if you think your action was not recorded in the log.

**What are answer level number ?** If you answer 1 it means you favor the entry on the left compared to the one on the right. 5 means you favor the right one. 3 is obviously the middle gounrd but is not the same as skipping the fight. Of course, all this is relative to the question that is being considered.

**What are all these fields for?** 
* metadata is used to store information like how long is a webpage to read or how long is a movie to watch etc. It will usually be filled automatically for youtube, webpage etc
* elo1 through elo5 handle elo score, all of them over time separated by a "_".
* date_elo_n store the date at which an elo score has been modified
*


**How is data encoded in all those SQL fields?**
* for the persistent settings :
* for the entries :
* for the metadata field : 
* elo's are containing the sequence of all elo's that this particular card has had over time with a "_" in between. For example : `0_1000_1300_1200_1275`



## How can I use this?
* Read this page thoroughly. Don't be afraid to ask questions.
* `git clone https://github.com/thiswillbeyourgithub/LiTOY/ `
* `cd LiTOY`
* edit the settings in `settings.py`
* `python3 ./__main__.py`

### Syntax example :

`python3 __main__.py --add 'repair the tires' diy 'to do before march'`
   * adds a new entry to deck todo with the tag diy 

`python3 __main__.py --rank --deck="diy" -n 20`
   * shows the rank

`python3 __main__.py --rank --deck="*"`
   * shows all entries

`python3 __main__.py --list="date_added rev`
   * shows all entries, by date added (can be any other sql field), in reverse order

`python3 __main__.py --list="raw"`
   * show all entries, unformatted

`python3 __main__.py --print--field`
   * get the field list

`python3 __main__.py --compare --deck="diy" -n 10`
   * compare 10 cards in a row from the folder called diy

`python3 __main__.py --history`
   * get history

`python3 __main__.py --manual`
   * turn on manual mode

`python3 __main__.py --check-db`
   * check database (do this after major import)

`python3 __main__.py --external`
   * open in sqlite browser

`--verbose`
   * also show output to the console instead of just in the debug file

`python3 __main__.py --edit ID FIELD VALUE`
   * edit FIELD from card with id ID

### Features 
* Automatically retrieves video length, video size, article reading time duration, pdf reading time duration
* Designed with flexibility in mind. You just have to specify a question.

## Code explanation
### Settings
### Data structure of the db

## TODO :
### global :
    * read the anki card and figure out if something is missing from the readme, then suspend the card
    * find the right license
    * write the edit function using this : https://stackoverflow.com/questions/2533120/show-default-value-for-editing-on-python-input-possible/2533142#2533142 and maybe this https://stackoverflow.com/questions/20972367/python-autocomplete-user-input
    * dans whofoght who, the result of the fight should be written in the db, so they should NOT be ordered by ID
    * comment the code and write a good readme, there is on way this project can takeof otherwise
    * make a requirement file and mention in the readme
    * time to read should be stored in seconds in the metadata, and then translated into duration by printing2entries
    * write a example_new_entry.txt and mention it in the readme
    * add a shortcut that only opens the left or right link ?
    * add a short term deck that allows to simply order item by order of when they should be done
    * store in persistent data the number of time litoy is run since its last db check, then print a reminder to check the db if it's above 50
    * use something in ascii to plot the deltas https://stackoverflow.com/questions/20295646/python-ascii-plots-in-terminal
    * metadata should contain the name of the url tab
    * metadata field should actually never appear while fighting, write it in the readme
    * rename all elos to elo1 elo2 etc, and write the dictionnary that translates the name when printing, same with deltas (rename to delta1 etc)
    * investigate wether to user this to manage settings :  https://pypi.org/project/simple-settings/
    * randomly add a warning that YOU'RE GONNA DIE SOMEDAY, along with some stats as to how probable it is
    * investigate how --list and --ranks should differ
    * an argument that opens less on the debug log 
    * check wether it works ok for first timer when they just install it and don't know where to begin, if it doesn't crash etc
    * check if sql works ok if the url contains ' or ```` etc
    * ability to export the rank as csv or text + maniana for flo
    * answer to this guy https://www.lesswrong.com/posts/54Bw7Yxouzdg5KxsF/how-do-you-organise-your-reading
    * shows entries added over time (ascii plotter) as well as entries marked done
    * investigate wether prettytable should be user to show ranks / podiums / dictionnary : http://zetcode.com/python/prettytable/
    * git commit the todo file than read your own litoy db, removing useless junk and doing some stuff, then adding it to new_entry.txt then git comitting the original todo file

### src/litoy/media_retriever.py :
    * if path :
        * if pdf => pdf
        * if video => ffmpeg
        * either way : get file size and file name
    * if link :
        * if pdf : pdftotext then estimation of time to read
        * if youtube link : time to watch via youtube-dl
        * if just text and not video or pdf : time to read
        * if 404 etc, use wayback machine and write it in the metadata
        * else : throws error

### more of a long term issue :
    * tupples are faster than lists, they might be used instead of lists sometimes
    * investigate how to make on online or mobile mode
    * investigate sql rollback or periodic backup
    * maybe manually "rolling back fights" by looking through the persistence db ?
    * is it useful to forbid 2 fights to happen too close to each other? It should not happend often actually
    * remove as many str() and int() function as possible, you put too many of them and there must be a clever way to organize this







