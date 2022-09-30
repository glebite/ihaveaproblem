# ihaveaproblem
## TL;DR:
A strange little project that I run to keep tabs on the world.  

## Deeper Explanations:
Essentially I stumbled upon the insecam site a while ago and would visit it 
from time to time to just see what was going on in different places around
the world.  However, the site has _ads_ or _.js_ code that messed up my browser.
Seriously, it would lock up.  So I turned off procrastination mode and 
wrote a webscraper to pull in the images.  

Some camera points also have multiple cameras so I find those and attempt to
acquire them all.  

I then put all the images into a _.html_ file with links and voila, magic!  

## TODO:  

All have been converted into issues in github: [Issues](https://github.com/glebite/ihaveaproblem/issues)  
Feel free to raise issues as I haven't tested this on a Windows or MAC.  

## Installation:  
The following steps are installation instructions.  

### clone the repo:  
> $ git clone https://github.com/glebite/ihaveaproblem.git  

### cd into the cloned folder and do some python magic  
> $ cd ihaveaproblem
> $ python3 -m venv venv  
> $ source venv/bin/activate  
> $ python3 -m pip install -r requirements.txt  

### cd into the src folder:
> $ cd src

## Execution:  
> $ python3 camfinder.py -c IR  
	
## Alternative Execution:
Search by city:  
> $ python3 camfinder.py -c Isfahan  

Search by interest:  
> $ python3 -camfinder.py -a Industrial  

## Storage:  
Currently, the executing folder contains all of the downloaded images as 
well as the _index.html_ file that brings it all together.
