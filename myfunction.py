from flask import Flask,render_template,request,url_for,session,config,redirect,flash,get_flashed_messages
import config
from dbMongo import *
from flask_mail import Message,Mail
from threading import Thread
from itsdangerous import URLSafeSerializer,URLSafeTimedSerializer, SignatureExpired

#crea l'oggetto app di classe Flask
app = Flask(__name__)
#configura l'app in base all'ogetto myconfig
app.config.from_object(config.myconfig)
#crea l'oggetto mail (Flask-Mail) per l'invio delle email
mail = Mail(app)



class MyTools(object):
    """memorizza i dati associati all'utente nel database all'interno dell'oggetto session"""
    def createUserRT(self,user):
        session['username']=user.get('username')
        session['email'] = user.get('email')
        session['firstname'] = user.get('firstname')
        session['lastname'] = user.get('lastname')
        session['address'] = user.get('address')
        session['city'] = user.get('city')
        session['bkcoin'] = user.get('bkcoin')
        session['linkPhotoUser'] = user.get('linkPhotoUser')
        session['messagesCount'] = user.get('messagesCount')

    def removeUserRT(self):
        """rimuove tutti i dati dell'utente associati all'oggetto session"""
        del session['username']
        del session['email']
        del session['firstname']
        del session['lastname']
        del session['address']
        del session['city']
        del session['bkcoin']

    def modifyBookJSON(self,cursorListBook):
        """trasforma la data di inserimento del libro in stringa"""
        list1=[]
        for book in cursorListBook:
            list1.append(book)
        for x in range(0, len(list1)):
            list1[x]["dateInsert"] = '{:%m/%d/%Y-%H:%M}'.format(list1[x]["dateInsert"])
            print(list1[x]["dateInsert"])
            list1[x]["_id"] = str(list1[x]["_id"])
            print(list1[x]["_id"])
        cursorListBookJSON = json.dumps(list1)
        return cursorListBookJSON

    def modifyBookJSON1(self,cursorListBook):
        """trasforma la data di inserimento del libro e dell'id(MONGODB) in stringa"""
        list1=[]
        for book in cursorListBook:
            list1.append(book)
        for x in range(0, len(list1)):
            list1[x]["dateInsert"] = '{:%m/%d/%Y-%H:%M}'.format(list1[x]["dateInsert"])
            print(list1[x]["dateInsert"])
            list1[x]["_id"] = str(list1[x]["_id"])
            print(list1[x]["_id"])
        cursorListBookJSON = json.dumps(list1)
        return cursorListBookJSON

    def modifyBookJSON2(self,cursorListBook):
        """trasforma la data di inserimento del libro e dell'id(MONGODB) in stringa"""
        list1=[]
        for book in cursorListBook:
            list1.append(book)
        cursorListBookJSON = json.dumps(list1)
        return cursorListBookJSON

    def modifyPositionJSON1(self,cursorListPosition):
        """trasforma la data dell'ultima posizione e di registrazione alla piattaforma in stringa"""
        list1=[]
        for user in cursorListPosition:
            list1.append(user)
        for x in range(0, len(list1)):
            list1[x]["positionDate"] = '{:%m/%d/%Y-%H:%M}'.format(list1[x]["positionDate"])
            print(list1[x]["positionDate"])
            list1[x]["registrationDate"] = '{:%m/%d/%Y-%H:%M}'.format(list1[x]["registrationDate"])
            print(list1[x]["registrationDate"])
        cursorListPositionJSON = json.dumps(list1)
        return cursorListPositionJSON

    def modifyMessagesJSON(self, cursorListMessages):
        """trasforma la data di inserimento del messaggio in stringa"""
        list1 = []
        for user in cursorListMessages:
            list1.append(user)
        for x in range(0, len(list1)):
            list1[x]["dateInsertMessage"] = '{:%m/%d/%Y-%H:%M}'.format(list1[x]["dateInsertMessage"])
            print(list1[x]["dateInsertMessage"])
            list1[x]["_id"] = str(list1[x]["_id"])
            print(list1[x]["_id"])
        cursorListMessagesJSON = json.dumps(list1)
        return cursorListMessagesJSON

    def send_async_email(self,app,msg):
        """entry point per l'avvio di un thread per l'invio di un'email in modo asincrono"""
        with app.app_context():
            mail.send(msg)

    def bookingSender(self,emailSender,emailRecipient,title,idBook,comment):
        """consente l'invio di un'email al mittente della richiesta di prenotazione di un libro"""
        msg = Message("Prenotazione libro",sender=app.config["MAIL_USERNAME"],recipients=[emailSender])
        msg.body = render_template("mailSender.txt",comment=comment,title=title,idBook=idBook,emailSender=emailSender,emailRecipient=emailRecipient)
        #thr = Thread(target=self.send_async_email,args=[app,msg])
        #thr.start()
        mail.send(msg)

    def bookingRecipient(self,emailSender,emailRecipient,title,idBook,comment,usernameRecipient):
        """consente l'invio di un'email al destinatario della richiesta di prenotazione di un libro"""
        msg = Message("Prenotazione libro",sender=app.config["MAIL_USERNAME"],recipients=[emailRecipient])
        msg.body = render_template("mailRecipient.txt",comment=comment,title=title,idBook=idBook,emailSender=emailSender,emailRecipient=emailRecipient,usernameRecipient=usernameRecipient)
        #thr = Thread(target=self.send_async_email,args=[app,msg])
        #thr.start()
        mail.send(msg)


mytools=MyTools()