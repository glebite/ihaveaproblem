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
> $ python3 camfinder.py -i Industrial  

List Searches:  
(find all supported Interests/tags)  
> $ python3 camfinder.py -I  
> Advertisement  
> Airliner  
> Animal  
> Architecture  
> Bar  
> Barbershop  
> ...  
> Weather  

(find all supported Cities):  
> $ python3 camfinder.py -L  
>  A Coruna ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,  4  
>  Aabenraa ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,  1  
>  Aalborg ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,  2  
>  Aarau ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,  1  
>  Abana ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,  1  
>  Abbotsford ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,  1  
> ...  
>  Zwickau ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,  1   
>  Zwolle ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,  10  

(find all supported countries):  
> $ python3 camfinder.py -l  
> US United States........................... 2501  
> JP Japan................................... 1153  
> TW Taiwan, Province Of .................... 787  
> KR Korea, Republic Of...................... 593  
> ...  
> NA Namibia................................. 1  
> UZ Uzbekistan.............................. 1  


## Storage:  
Currently, the executing folder contains all of the downloaded images as 
well as the _index.html_ file that brings it all together.


