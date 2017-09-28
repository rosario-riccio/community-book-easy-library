from pymongo import MongoClient,DESCENDING,ASCENDING
from bson import Binary, Code
from bson.json_util import dumps
import json
import sys
from werkzeug.utils import secure_filename
import datetime
from bson.objectid import ObjectId
import os

try:
    #tenta l'accesso al database
    client = MongoClient("mongodb://localhost:27017/")
    db = client.easyLibraryDB

except Exception as e:
    print("Db non pronto"+str(e))


class ManageDB(object):
    """la classe ManageDB servira' per l'intera gestione del database mascherando i reali metodi di accesso"""
    def __init__(self,db):
        self.db=db

    def checkUser(self,email, password):
        """Valuta la presenza di un utente"""
        count = self.db.userCollection.count({'email': email, 'password1': password});
        return count

    def checkUser1(self,email):
        """Valuta la presenza di un utente mediante email"""
        count = self.db.userCollection.count({'email': email});
        return count

    def checkTitle(self,title):
        """Valuta la presenza di un libro con il titolo passato come argomento"""
        count = self.db.booksCollection.find({'title':{"$regex":title,"$options":"$i"}}).count()
        print("numero %s" % count)
        if(count >= 1 ):
            result = True
            cursor = self.db.booksCollection.find({'title':{"$regex":title,"$options":"$i"}})
            return result,cursor
        else:
            result = False
            cursor = None
            return result,cursor

    def checkTitle1(self,title):
        """Valuta la presenza di un libro con il titolo passato come argomento;
        selezioneremo i documenti in base al titolo e sono ancora disponibili;
        poi li raggrupperemo per isbn e username;
        restituiremo il titolo, autore, casa editrice, foto del primo documento di ciascun gruppo;
        effettueremo il conteggio nel numero di documento per gruppo."""
        count = self.db.booksCollection.find({'title':{"$regex":title,"$options":"$i"}}).count()
        print("numero %s" % count)
        if(count >= 1 ):
            result = True
            cursor = self.db.booksCollection.aggregate([{"$match":{"title":{"$regex":title,"$options":"$i"},"booking":False}},{"$group":{"_id":{"isbn":"$isbn","username":"$username"},"title":{"$first":"$title"},"author":{"$first":"$author"},"publisher":{"$first":"$publisher"},"linkPhoto":{"$first":"$linkPhoto"},"total":{"$sum":1}}}])
            return result,cursor
        else:
            result = False
            cursor = None
            return result,cursor

    def getAllBooks(self):
        """restituisce tutti i libri presenti nel database"""
        count = self.db.booksCollection.find({}).count()
        print("numero %s" % count)
        if(count >= 1 ):
            result = True
            cursor = self.db.booksCollection.find({}).sort('dateInsert',-1)
            return result,cursor
        else:
            result = False
            cursor = None
            return result,cursor

    def addUserDB(self,username,email,password1,firstname,lastname,address,city,university,date1,bkcoin,linkPhotoUser,lat,lon,positionDate,messagesCount,confirmEmail1):
           """Inserisce un nuovo utente nel database"""
           result1=self.db.userCollection.insert_one({"username":username,"email":email,"password1":password1,"firstname":firstname,"lastname":lastname,"address":address,"city":city,"university":university,"registrationDate":date1,"bkcoin":bkcoin,"linkPhotoUser":linkPhotoUser,"lat":lat,"lon":lon,"positionDate":positionDate,"messagesCount":messagesCount,"confirmEmail":confirmEmail1})
           print("Numero utente inserito {}".format(result1.inserted_id))

    def getUserDB(self,email):
        """richiede i dati dell'utente in base al paramentro email"""
        cursor=self.db.userCollection.find({"email":email});
        user=cursor.next()
        return user

    def getUserDB1(self,username):
        """richiede i dati dell'utente in base al paramentro username"""
        cursor=self.db.userCollection.find({"username":username});
        user = cursor.next()
        return user

    def getBookDB(self,id):
        """richiede i dati di un libro in base all'isbn"""
        count=self.db.booksCollection.find({"_id":ObjectId(id)}).count()
        print("numero {}".format(count))
        if(count >=1):
            cursor = self.db.booksCollection.find({"_id": ObjectId(id)})
            book = cursor.next()
            return count,book
        else:
            book = None
            return count,book

    def getBookDBRandom(self,isbn,username):
        """richiede i dati di un libro disponibile in base all'isbn e username;
        selezionera' un unico documento random tra quelli presenti"""
        count=self.db.booksCollection.find({"isbn":isbn,"username":username,"booking":False}).count()
        print("numero {}".format(count))
        if(count >=1):
            cursor = self.db.booksCollection.aggregate([{"$match":{"isbn":isbn,"username":username,"booking":False}},{"$sample":{"size":1}}])
            book = cursor.next()
            return count,book
        else:
            book = None
            return count,book


    def insertBookDB(self,email,username,title,author,publisher,comment,dateInsert,booking,bookingTo,linkPhoto,linkPhotoUser,isbn):
        """inserisce un nuovo libro"""
        id=self.db.booksCollection.insert({"email":email,"username":username,"title":title,"author":author,"publisher":publisher,"comment":comment,"dateInsert":dateInsert,"booking":booking,"bookingTo":bookingTo,"linkPhoto":linkPhoto,"linkPhotoUser":linkPhotoUser,"isbn":isbn})
        return id

    def incrementBKcoin(self,username):
        """incrementa i bkcoin di un utente in base al suo username"""
        result1=self.db.userCollection.update_one({"username":username},{"$inc":{"bkcoin":1}})
        print("Numero bkcoin incrementati {}".format(result1.modified_count))

    def sendPositionDB(self,lat,lon,username,positionDate):
        """aggiorna la posizione dell'utente in base al suo username"""
        result1=self.db.userCollection.update_one({"username":username},{"$set":{"lat":lat,"lon":lon,"positionDate":positionDate}})
        print("Numero modifiche posizione {}".format(result1.modified_count))

    def getUserPositionDB(self,username):
        """fornisce la posizione dell'utente in base al suo usename"""
        count = self.db.userCollection.find({"username":username}).count()
        print("Numero posizione utente individuato {}".format(count))
        if(count==0):
            cursor1 = False
            return count, cursor1
        else:
            cursor1 = self.db.userCollection.find({"username":username},{"password1":0,"_id":0})
            return count,cursor1

    def decrementBKcoin(self,username):
        """decrementa i bkcoin di un utente in base al suo username"""
        result1=self.db.userCollection.update_one({"username":username}, {"$inc": {"bkcoin": -1}})
        print("Numero bkcoin decrementati {}".format(result1.modified_count))

    # def penaltyDecrementBKcoin(self,username):
    #     result1=self.db.userCollection.update_one({"username":username}, {"$inc": {"bkcoin": -2}})
    #     print("Numero bkcoin decrementati {}".format(result1.modified_count-1))

    def getBookingDB(self,username,id):
        """consente di memorizzare i dati relativi alla prenotazione effettuata"""
        count1 = self.db.booksCollection.find({"_id":ObjectId(id)}).count()
        print("Numero {}".format(count1))
        result1=self.db.booksCollection.update_one({"_id":ObjectId(id)},{"$set":{"bookingTo": username,"booking":True}})
        print("Numero prenotazioni effettuate {}".format(result1.modified_count))

    def deleteBookDB(self,id):
        """cancellera' un libro dal database"""
        result1=self.db.booksCollection.delete_one({"_id":ObjectId(id)})
        print("numero libri eliminati {}".format(result1.deleted_count))

    def listBooks(self,email):
        """fornira' la lista dei libri associati ad utente in base all'email"""
        count = self.db.booksCollection.find({'email': email}).count()
        print("numero %s" % count)
        if (count >= 1):
            result = True
            cursorListBook = self.db.booksCollection.find({'email': email})
            return result, cursorListBook
        else:
            result = False
            cursorListBook = None
            return result, cursorListBook

    def sendMessageDB(self,fromUsername,toUsername,message,dateInsertMessage,title,idBook,messageTp):
        """consentira' l'inserimento di un nuovo messaggio che notifica la prenotazione: sara' visualizzato nella pagina messaggi.html"""
        result1 = self.db.messagesCollection.insert_one({"fromUsername":fromUsername,"toUsername":toUsername,"message":message,"dateInsertMessage":dateInsertMessage,"title":title,"idBook":idBook,"messageTp":messageTp})
        print("Numero id messaggio inserito {}".format(result1.inserted_id))

    def incrementMessagesCount(self,username):
        """incrementa il valore dei messaggi ricevuti"""
        result1 = self.db.userCollection.update_one({"username":username},{"$inc":{"messagesCount":1}})
        print("numero messaggi notificati {}".format(result1.modified_count))

    def zeroMessagesCount(self,username):
        """azzera il numero di messaggi ricevuti"""
        result1 = self.db.userCollection.update_one({"username":username},{"$set":{"messagesCount":0}})
        print("numero messaggi notificati {}".format(result1.modified_count))


    def getMessagesCount(self,username):
        """restituisce il numero di messaggi ricevuti"""
        count = self.db.userCollection.find({'username': username}).count()
        print("numero %s" % count)
        if (count >= 1):
            result = True
            cursor = self.db.userCollection.find({'username': username})
            return result, cursor
        else:
            result = False
            cursorListBook = None
            return result, cursorListBook

    def getListMessagesDB(self,toUsername):
        """restituisce i messaggi ricevuti"""
        count = self.db.messagesCollection.find({'toUsername': toUsername}).count()
        print("numero %s" % count)
        if (count >= 1):
            cursorListMessages = self.db.messagesCollection.find({'toUsername': toUsername}).sort('dateInsertMessage',-1)
            return count, cursorListMessages
        else:
            cursorListMessages = None
            return count, cursorListMessages

    def successConfirmEmail(self,email):
        """memorizza la convalida di un'email"""
        result1 = self.db.userCollection.update_one({"email": email}, {"$set": {"confirmEmail": True}})
        print("numero messaggi notificati {}".format(result1.modified_count))

    def returnBookDB(self, id):
        """consente la rimozione di una prenotazione di un libro per renderlo di nuovo disponibile """
        result1 = self.db.booksCollection.update_one({"_id":ObjectId(id)}, {"$set": {"bookingTo": None,"booking": False}})
        print("numero messaggi notificati {}".format(result1.modified_count))

managedb=ManageDB(db)
