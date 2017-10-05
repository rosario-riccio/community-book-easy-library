# community-book-easy-library
Web application: community for the exchange of books<br>
<br>
1 - Configuration (config.py)
<br>
Set environment variables: LINUX --> export variable=value
<br>
<br>
A) Configuring Flask-Mail:
<br>
<br>
insert your mail server: Google SMTP Server --> smtp.googlemail.com
<br>
MAIL_SERVER =os.environ['MAIL_SERVER']
<br>
<br>
insert your email address
<br>
MAIL_USERNAME = os.environ['MAIL_USERNAME']
<br>
<br>
insert your email password
<br>
MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
<br>
<br>
B) API KEY
<br>
<br>
insert your isbndb API key (isbndb.com) 
<br>
ISBN_TOKEN = os.environ['ISBN_TOKEN']
<br>
<br>
insert your Google API key
<br>
GOOGLE_TOKEN = os.environ['GOOGLE_TOKEN']
<br>
<br>
2 - Requirements:
<br>
<br>
A) Client Side
<br>
JQuery<br>
Bootstrap<br>
QuaggaJS<br>
<br>
<br>
B) Server side:<br>
Python<br>
Moduli Python:<br>
flask<br>
flask-Mail<br>
pyMongo<br>
requests<br>
isbnlib<br>
PIL<br>

C) API KEY:
<br>
API KEY --> GOOGLE MAPS API <br>
API KEY --> ISBNdb.com API <br>

