#vers. 6.0
#Consente l'avvio dell'applicazione
from views import *
from jinja2 import Environment

#aggiunge un metodo al template JINJA2
app.jinja_env.add_extension('jinja2.ext.do')
#print(app.config["MAIL_USERNAME"])

#avvia l'applicazione
if (__name__ == "__main__"):
    app.run()
