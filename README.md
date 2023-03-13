# Craftsmen Website
#### Video Demo:  https://www.youtube.com/watch?v=NL_o6t_IUXk

#### Description:
#### The site visitor can register As Craftsman Or As a Client or participate on the site as a visitor
## Requirements
_The Project don't need special requirements Just Flask And some Library in Setup Section_

## Setup
- **Create Project Folder:** 
    -  copy All File(s) in Directory:
      - Active Flask venv 
	- > `. venv/bin/activate` For mac
	- Run Application Use Command:- 
	- > ` flask run ` 

## Front-end :-
_Using Bootstrap , jquery and Some of own CSS_

## Backend :-
- PYTHON /Flask 
- SQLite 3
- Javascript


## Files & directories
- venv
- __pycache__
- static
	- style
		- customstyle file
		- normalize file
		- bootstrap file
	- JS
		- custom script
		- Bootstrap Files
		- sort file 
	- images files
- templates 
	- index.html, layout.html, search.html for Base
	- login.html, register.html 
	- add_request , clprofile, services for Clients
	- add_service , crprofile, requests for Craftsman
- main app files and database:-
	- app.py "main File"
	- crafts.db  Database
	- module,helper.py


##  registering as a craftsman:
### You Can Register As Craftsman
### You can Add Services You Can Do And Accept Work Requests From The Client
###  after log in:- 
### add some services.
#### Go to Profile Page
##### Here the services that You offer appear, and if anyone has requested your Services,
### and it is possible to modify my profile data.
#### Through the search page:
### Search for required services that  can do in your free time

## registering as a Customer
### You Can Register As customer
### You can Add Requests for Work you need to do with a Special craftsman
###  after log in:- 
### add Any Requests You Want
#### Go to Profile Page
#### Here the requests that I present appear, and if anyone has agreed to one of my requests,o
#### Through the search page, I can search for offered services that suit my needs

###  As for the visitor
#### the visitor can only go to the search page and find out only the offered and required services.
### but can't contact any user or ask for any request.
 #### what I used in this Web Application :-
### CS50 SQLite library
### flask framework for python
###  bootstrap library
### HTML ,CSS,  javascript,



