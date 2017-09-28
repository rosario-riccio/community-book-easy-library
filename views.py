from myfunction import *
import time
from os.path import join,dirname,realpath
from PIL import Image, ImageOps
import isbnlib
import requests


UPLOAD_FOLDER=join(dirname(realpath(__file__)),'static/img')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Creeremo un oggetto di classe URLSafeSerializer;
#servira' per creare un token per codificare/decodificare
#l'email dell'utente che si registra alla piattaforma --> s.dumps() / s.loads()

s = URLSafeSerializer(app.config["SECRET_KEY"])


def allowed_file(filename):
    """effettuera' massimo un'unica divisione della stringa partendo dalla fine, poi valutera'
    l'ultimo elemento della lista (estensione) e lo confrontera' con quelli presenti in ALLOWED_EXTENSION"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_async_email(app, msg):
    """send_async_email consente l'invio di un'email in maniera asincrona;
    e' utilizzato in sendConfirmEmail quale entry point
    di un nuovo thread"""
    with app.app_context():
        mail.send(msg)


def sendConfirmEmail(email,username):
    """sendConfirmEmail invia un'email per la relativa convalida;
    utilizzera' la libreria Flask-Mail;
    mediante l'oggetto di tipo Message inseriremo i dati relativi
    al mittente - destinario - titolo;
    poi successivamente inseriremo il relativo contenuto"""
    token = s.dumps(email, salt="email-confirm")
    msg = Message("Conferma email", sender=app.config["MAIL_USERNAME"], recipients=[email])
    link = url_for("confirm_email", token=token, _external=True)
    msg.html = render_template("confirmMail.html", link=link,username=username)
    #crea un thread per l'invio asincrono di un'email
    #thr = Thread(target=send_async_email, args=[app, msg])
    #thr.start()
    mail.send(msg)


def getMessagesCount(username):
    """getMessagesCount prova a interrogare il database
    per ottenere il numero di messaggi ricevuti"""
    try:
	session['messagesCount'] = cursor["messagesCount"]
        cursor = managedb.getUserDB1(username)
    except Exception as e:
        print("errore " + str(e))
    


def getBitCoin(username):
    """getBitCoin prova a interrogare il database
    per ottenere il valore della moneta virtuale
    ottenuta per ogni libro inserito"""
    try:
        cursor = managedb.getUserDB1(username)
	session['bkcoin'] = cursor["bkcoin"]
    except Exception as e:
        print("errore " + str(e))
    


@app.route("/")
def index():
    """index e' la funzione attivata da Flask quando l'utente
    effettua una richiesta HTTP della pagina "index.html";
    la index servira' a) per accedere alla Home fornendo le proprie
    credenziali b) per accedere alla pagina di registrazione"""
    #Flask salvera' un item logged_in se l'utente
    #ha effettuato un accesso con successo"""
    print("logged_in" in session)
    if ("logged_in" in session) and (session["logged_in"]==True):
       return redirect(url_for("libreria"))
    print("Accesso index")
    return render_template('index.html')


@app.route("/login",methods=['GET','POST'])
def login():
    """"login e' la funzione attivata dal form di autenticazione
    della pagina "index.html";
    saranno prelevate email e password --> sara' effettuata
    un'interrogazione nel database mediante il metodo
    managedb.checkUser()"""
    if (request.method == 'POST'):
        print("check login DB")
        email = request.form['email']
        password = request.form['password']
        try:
            #controlla se l'utente e' presente nel database
            count = managedb.checkUser(email, password)
        except Exception as e:
            print("errore " + str(e))
        print("valore count %s " % count)
        if (count == 0):
            session['logged_in'] = False
            print("login fallito")
            return redirect(url_for('index'))
        else:
            try:
                #controlla se l'email sia stata convalidata
                cursor = managedb.getUserDB(email)
                print(cursor['confirmEmail'])
                confirmEmail1 = cursor['confirmEmail']
                if (confirmEmail1 == False):
                    session["confirmEmail_in"] = False
                    print("login fallito, email non convalidata")
                    return redirect(url_for('index'))
            except Exception as e:
                session['logged_in'] = False
                print("login fallito " + str(e))
                return redirect(url_for('index'))
            print("login con successo")
            session['logged_in'] = True
            print(session['logged_in'])
            try:
                user=managedb.getUserDB(email)
            except Exception as e:
                print("errore " +str(e))
            print(user)
            #tale metodo consentira' la memorizzazione delle
            #credenziali dell'utente come elementi dell'oggetto
            #session di Flask
            mytools.createUserRT(user)
            print(session['username'])
            return redirect(url_for('libreria'))

    else:
        print("Accesso index")
        return redirect(url_for('index'))

@app.route("/registratione.html",methods=['GET','POST'])
def registrazione():
    """registrazione e' una funzione attivata da Flask
    alla richiesta HTTP della pagina "registrazione.html";
    si occupera' di prelevare tutti i dati forniti dal form tramite
    l'oggetto request; successivamente si tentera' l'inserimento di tali dati
    all'interno del database mediante il metodo managedb.addUserDB()"""
    if(request.method == 'POST'):
        user={}
        username=request.form['username']
        print(username)
        email = request.form['email']
        print(email)
        password1 = request.form['password1']
        print(password1)
        firstname = request.form['firstname']
        print(firstname)
        lastname = request.form['lastname']
        print(lastname)
        address = request.form['address']
        print(address)
        city = request.form['city']
        print(city)
        username = request.form['username']
        print(username)
        university = request.form['university']
        print(university)
        date1 = datetime.datetime.now()
        print(date1)
        bkcoin=0
        print(bkcoin)
        messagesCount=0
        lat = None
        lon = None
        confirmEmail1=False
        positionDate = None
        photoUser = request.files["photoUser"]
        #valutera' se il file e' vuoto e se la sua estensione
        #e' tra quelle previste in ALLOWED_EXTENSIONS
        if photoUser and allowed_file(photoUser.filename):
            #Si utilizzera' un oggetto di tipo Image (libreria Pillow)
            #per ridimensionare la foto inserita
            img = Image.open(photoUser)
            img.thumbnail((45, 45), Image.ANTIALIAS)
            #protegge dal fenomeno XSS
            pathBook = secure_filename(photoUser.filename)
            #si effettuera' un controllo se il file gia' esista, e nel caso
            #gia' esistesse sara' rinominato e poi salvato
            print(os.path.exists(join(app.config["UPLOAD_FOLDER"],"users",pathBook)))
            if (os.path.exists(join(app.config["UPLOAD_FOLDER"],"users",pathBook))):
                #effettuera' la divisione tra la base e l'estensione di un file
                base, extension = os.path.splitext(pathBook)
                i=1
                newPathBook = "{}-{}{}".format(base, i, extension)
                print(newPathBook)
                #creeremo un nuovo filename (base.extension) fintanto che non sara' gia'esistente
                while (os.path.exists(join(app.config["UPLOAD_FOLDER"],"users",newPathBook))):
                    i += 1
                    newPathBook = "{}-{}{}".format(base, i, extension)
                print(newPathBook)
                linkPhoto = newPathBook
                #creeremo il percorso finale del file immagine
                newPathBookAbs = join(app.config["UPLOAD_FOLDER"],"users",newPathBook)
                #converteremo il file in jpeg e lo salveremo
                #img.convert('RGB').save(newPathBookAbs,"JPEG")
		img.save(newPathBookAbs)
                print(newPathBookAbs)
            else:
                print(pathBook)
                linkPhoto = pathBook
                pathBookAbs = join(app.config["UPLOAD_FOLDER"],"users",pathBook)
                #effettua una conversione in JPEG e poi lo salva
                #img.convert('RGB').save(pathBookAbs,"JPEG")
		img.save(pathBookAbs)
                print(pathBookAbs)
        try:
            linkPhotoUser = linkPhoto
            #inserimento dei dati nel database
            managedb.addUserDB(username,email,password1,firstname,lastname,address,city,university,date1,bkcoin,linkPhotoUser,lat,lon,positionDate,messagesCount,confirmEmail1)
            session["registration_in"] = True
            sendConfirmEmail(email,username)
            return redirect(url_for('index'))
        except Exception as e:
            print("problema DB!!!  "+str(e))
            session["registration_in"] = False
            return redirect(url_for('registrazione'))
    else:
        print("Accesso registrazione")
        return render_template("registrazione.html")




@app.route("/libreria.html")
def libreria():
    """library e' una funzione attivata da Flask quando si accede
    alla pagina libreria.html / HOME dell'applicazione web;
    in questa pagina saranno visualizzati tutti i contenuti pubblicati
    partendo dall'ultimo inviato; sara' possibile effettuare la richiesta
    di prenotazione di un libro"""
    # Flask salvera' un item logged_in se l'utente
    # ha effettuato un accesso con successo
    print("logged_in" in session)
    if('logged_in' not in session) or ( session['logged_in'] != True ):
        print("Accesso negato in libreria")
        return redirect(url_for('index'))
    username = session["username"]
    #calolera' il numero di messaggi ricevuti e di bkcoin
    #prelevandoli dal database
    getMessagesCount(username)
    getBitCoin(username)
    return render_template("libreria.html")

@app.route("/scaffale.html")
def scaffale():
    """la funzione scaffale e' attivata quando l'utente richiede
    la pagina scaffale.html.
    Tale pagina consentira' a) l'inserimento di un nuovo libro
    b) la cancellazione di un libro c) renderlo di nuovo prenotabile"""
    print("logged_in" in session)
    # Flask salvera' un item logged_in se l'utente
    # ha effettuato un accesso con successo
    if ('logged_in' not in session) or (session['logged_in'] != True):
        print("Accesso negato in scaffale")
        return redirect(url_for('index'))
    username = session["username"];
    getMessagesCount(username)
    getBitCoin(username)
    return render_template("scaffale.html")

@app.route("/logout")
def logout():
    """Saranno cancellati tutti i dati di sessione dell'utente"""
    print("logged_in" in session)
    if ('logged_in' not in session) or (session['logged_in'] != True):
        print("Accesso negato in logout")
        return redirect(url_for('index'))
    session.clear()
    return redirect(url_for('index'))

@app.route("/searchtitle",methods=['GET','POST'])
def searchTitle():
    """e' una funzione attivata mediante una richiesta HTTP asincrona (AJAX),
    consentira' la ricerca nel database del titolo di un libro
    mediante la funzione managedb.checkTitle(). La risposta sara' in formato JSON
    """
    # Flask salvera' un item logged_in se l'utente
    # ha effettuato un accesso con successo
    print("logged_in" in session)
    if ('logged_in' not in session) or (session['logged_in'] != True):
        print("Accesso negato in searchTitle")
        return redirect(url_for('index'))
    if request.is_xhr and request.method=='POST':
        title = request.form["title"]
        print(title)
        try:
            result,cursor=managedb.checkTitle1(title)
        except Exception as e:
            print("errore " + str(e))
        if(result == False):
            print("Non ci sono risultati")
            return json.dumps({"result": False})
        elif (result == True):
            try:
                #effettuera' la trasformazione del tipo
                #di alcuni dati in stringhe.
                #i dati saranno richiesti mediante AJAX e la
                #risposta sara' effettuata usando il formato
                #JSON
                cursorJSON = mytools.modifyBookJSON2(cursor)
            except Exception as e:
                print("errore " + str(e))
            print(type(cursorJSON))
            print(cursorJSON)
            return cursorJSON
    else:
        print("Errore accesso")
        return json.dumps({"result": False})

@app.route("/ricerca.html")
def ricerca():
    """research e' una funzione attivata mediante una richiesta HTTP asincrona (AJAX),
     sara' attivato da Flask qualora l'utente
    richieda la pagina ricerca.html; la risposta sara' in formato JSON"""
    # Flask salvera' un item logged_in se l'utente
    # ha effettuato un accesso con successo
    print("logged_in" in session)
    if ('logged_in' not in session) or (session['logged_in'] != True):
        print("Accesso negato in ricerca")
        return redirect(url_for('index'))
    username = session["username"];
    getMessagesCount(username)
    getBitCoin(username)
    return render_template("ricerca.html")

@app.route("/getuserposition",methods=["GET","POST"])
def getUserPosition():
    """getUserPosition e' una funzione attivata mediante una richiesta HTTP asincrona (AJAX),
    restituira' la posizione di utente in base al suo username;
    la risposta sara' inviata in formato JSON;
    i dati saranno prelevati dal database mediante la funzione
    managedb.getUserPositionDB()"""
    print("logged_in" in session)
    # Flask salvera' un item logged_in se l'utente
    # ha effettuato un accesso con successo
    if ('logged_in' not in session) or (session['logged_in'] != True):
        print("Accesso negato in getAllPosition")
        return redirect(url_for('index'))
    if request.is_xhr and request.method=="POST":
        username = request.form["username"]
        try:
            count, cursor1 = managedb.getUserPositionDB(username)
            if(count==0):
                return json.dumps({"result":False})
            else:
                #modifica il tipo di alcune dati in formato stringa
                cursorJSON = mytools.modifyPositionJSON1(cursor1)
                print(cursorJSON)
                return cursorJSON
        except Exception as e:
            print("errore ",str(e))
            return json.dumps({"result": "errore"})
    else:
        print("errore dati inviati")
        return json.dumps({"result": False})


@app.route("/sendposition",methods=["GET","POST"])
def sendPosition():
    """l'utente effettuera' una richiesta HTTP asincrona (AJAX) per inviare la propria
    posizione. Questo dato sara'necessario per la geolocalizzazione di tutti gli utenti dell'applicazione web;
    i dati saranno inviati al database mediante managedb.sendPositionDB()"""
    print("logged_in" in session)
    # Flask salvera' un item logged_in se l'utente
    # ha effettuato un accesso con successo
    if ('logged_in' not in session) or (session['logged_in'] != True):
        print("Accesso negato in sendPosition")
        return redirect(url_for('index'))
    if request.is_xhr and request.method == "POST":
        lat = request.form["lat"]
        lon = request.form["lon"]
        username = session["username"]
        positionDate = datetime.datetime.now()
        print(lat,lon,username,positionDate)
        try:
            managedb.sendPositionDB(lat,lon,username,positionDate)
            return json.dumps({"result":"Invio posizione corretta"})
        except Exception as e:
            print("errore " + str(e))
            return json.dumps({"result":"Errore invio posizione"})
    else:
        print("errore dati inviati")
        return json.dumps({"result": False})


@app.route("/requestisbn",methods=["GET","POST"])
def requestISBN():
    """requestISBN sara' attivata dopo una richiesta HTTP asincrona (AJAX) per ottenere
    eventualmente i dati associati all'isbn interrogando 2 REST API: API Google Books,
    API isbnDB; i dati saranno restituiti in formato JSON"""
    print("logged_in" in session)
    # Flask salvera' un item logged_in se l'utente
    # ha effettuato un accesso con successo
    if ('logged_in' not in session) or (session['logged_in'] != True):
        print("Accesso negato in requestISBN")
        return redirect(url_for('index'))
    if request.is_xhr and request.method == 'POST':
        isbn = str(request.form["isbn"])
        print(type(isbn))
        print(isbn)
        #uso del metodo isbnlib.meta per ottenere i dati
        #sfruttando l'API Google Books
        book = isbnlib.meta(isbn)
        print(book)
        if(bool(book)==False):
            #richiesta HTTP Request GET mediante l'oggetto requests all'API
            #isbnDB
            url1 = "http://isbndb.com/api/v2/json/"+app.config["ISBN_TOKEN"]+"/book/"+isbn
            print(url1)
            book = requests.get(url1)
            bookDict = book.json()
            title = bookDict['data'][0]["title"]
            authors = bookDict['data'][0]["author_data"][0]["name"]
            publisher = bookDict['data'][0]["publisher_name"]
            print(title)
            print(authors)
            print(publisher)
            bookDict2 = {"Title":title,"Authors":authors,"Publisher":publisher}
            return json.dumps(bookDict2)
        return json.dumps(book)
    else:
        print("errore dati inviati")
        return json.dumps({"result": False})



@app.route("/getallbooks",methods=['GET','POST'])
def getAllBooks():
    """getAllBooks e' una funzione attivata dopo una richiesta HTTP asincrona (AJAX);
    interroghera' il database per ottenere tutti libri pubblicati sulla piattaforma;
    tale funzione e' utilizzata nella HOME.
    Sara' invocato il metodo managedb.getAllBooks() per ottenere i dati richiesti
    per restituirli in formato JSON"""
    print("logged_in" in session)
    # Flask salvera' un item logged_in se l'utente
    # ha effettuato un accesso con successo
    if ('logged_in' not in session) or (session['logged_in'] != True):
        print("Accesso negato in getAllBooks")
        return redirect(url_for('index'))
    if request.is_xhr and request.method=='POST':
        try:
            result,cursor=managedb.getAllBooks()
        except Exception as e:
            print("errore " + str(e))
        if(result == False):
            print("Non ci sono risultati")
            dict1={"result":False}
            dict1JSON= json.dumps(dict1)
            return dict1JSON
        elif (result == True):
            cursorJSON = mytools.modifyBookJSON1(cursor)
            print(type(cursorJSON))
            print(cursorJSON)
            return cursorJSON
    else:
        print("errore dati inviati")
        return json.dumps({"result": False})

@app.route("/messaggi.html")
def messaggi():
    """messages sara' attivata da Flask dopo una richiesta HTTP della pagina
    messaggi.html; quando si accede alla pagina messaggi.html l'indice dei messaggi
    ricevuti sara' azzerato mediante managedb.zeroMessagesCount()"""
    print("logged_in" in session)
    # Flask salvera' un item logged_in se l'utente
    # ha effettuato un accesso con successo
    if ('logged_in' not in session) or (session['logged_in'] != True):
        print("Accesso negato in messaggi")
        return redirect(url_for('index'))
    session["messagesCount"]=0
    username = session["username"]
    try:
        managedb.zeroMessagesCount(username)
    except Exception as e:
        print("errore " + str(e))
    return render_template("messaggi.html")



@app.route("/insertbook",methods=["GET","POST"])
def insertBook():
    """insertBook e' inviato dopo una richiesta HTTP asincrona AJAX;
    l'utente richiede l'inserimento di un nuovo libro per il prestito;
    i dati saranno inseriti nel database mediante il metodo managedb.insertBookDB();
    la risposta dell'esito sara' inviato in formato JSON"""
    print("logged_in" in session)
    if ('logged_in' not in session) or (session['logged_in'] != True):
        print("Accesso negato in insertBook")
        return redirect(url_for('index'))
    if request.is_xhr and request.method=="POST":
        print("il risultato e' {}".format(request.is_json))
        coverBook = request.files["coverBook"]
        # valutera' se il file e' vuoto e se la sua estensione
        # e' tra quelle previste in ALLOWED_EXTENSIONS
        if coverBook and allowed_file(coverBook.filename):
            img = Image.open(coverBook)
            img.thumbnail((262, 390),Image.ANTIALIAS)
            # protegge dal fenomeno XSS
            pathBook = secure_filename(coverBook.filename)
            #Si controllera' se il file gia' esista e si effettuera'
            #l'eventuale rinominazione
            if (os.path.exists(join(app.config["UPLOAD_FOLDER"],"books",pathBook))):
                #separa la base e l'estensione di un file
                base, extension = os.path.splitext(pathBook)
                i=1
                newPathBook = "{}-{}{}".format(base, i, extension)
                print(newPathBook)
                #creeremo un nuovo filename (base.extension) fintanto che non sia gia' presente
                while (os.path.exists(join(app.config["UPLOAD_FOLDER"],"books",newPathBook))):
                    i += 1
                    newPathBook = "{}-{}{}".format(base, i, extension)
                print(newPathBook)
                linkPhoto = newPathBook
                #creeremo il nuovo percorso finale completo
                newPathBookAbs = join(app.config["UPLOAD_FOLDER"],"books",newPathBook)
                #effettueremo una conversione e salveremo in formato jpeg
                #img.convert('RGB').save(newPathBookAbs,"JPEG")
		img.save(newPathBookAbs)
                print(newPathBookAbs)
            else:
                print(pathBook)
                linkPhoto = pathBook
                pathBookAbs = join(app.config["UPLOAD_FOLDER"],"books",pathBook)
                #img.convert('RGB').save(pathBookAbs, "JPEG")
		img.save(pathBookAbs)
                print(pathBookAbs)
        linkPhotoUser = session["linkPhotoUser"]
        email = session["email"]
        username = session["username"]
        title = request.form["title"]
        author = request.form["author"]
        publisher = request.form["publisher"]
        comment = request.form["comment"]
        isbn = request.form["isbn1"]
        dateInsert = datetime.datetime.now()
        booking = False
        bookingTo=None
        print(title)
        print(author)
        print(comment)
        print(isbn)
        try:
            #inserimento del libro
            id=managedb.insertBookDB(email,username,title,author,publisher,comment,dateInsert,booking,bookingTo,linkPhoto,linkPhotoUser,isbn)
            print("inserimento libro ok")
            print(id)
        except Exception as e:
            print("errore " + str(e))
            print("inserimento libro fallito")
            response = {"result": False}
            responseJSON = json.dumps(response)
            print(responseJSON)
            return responseJSON
        try:
            #incremento del bkcoin
            managedb.incrementBKcoin(session["username"])
            print("aggiornamento BKcoin ok")
            response = {"result": True}
            responseJSON = json.dumps(response)
            print(responseJSON)
            getMessagesCount(username)
            getBitCoin(username)
            return responseJSON
        except Exception as e:
            print("errore " + str(e))
            print("aggiornamento BKcoin fallito")
            try:
                managedb.deleteBookDB(id)
            except Exception as e:
                print("errore " + str(e))
            print("Eliminazione libro {}".format(id))
            response = {"result": False}
            responseJSON = json.dumps(response)
            print(responseJSON)
            return responseJSON
    else:
        print("errore dati inviati")
        return json.dumps({"result": False})

@app.route("/getbooking",methods=["GET","POST"])
def getBooking():
    """getBooking e' attivata da una richiesta HTTP asincrona (AJAX);
    l'utente richiede la prenotazione di un libro:
    il destinatario ricevera' un messaggio di prenotazione in
    messaggi.html; l'esito dell'operazione sara' restituito in JSON
    """
    print("logged_in" in session)
    # Flask salvera' un item logged_in se l'utente
    # ha effettuato un accesso con successo
    if ('logged_in' not in session) or (session['logged_in'] != True):
        print("Accesso negato in getBooking")
        return redirect(url_for('index'))
    fromUsername = session["username"]
    getMessagesCount(fromUsername)
    getBitCoin(fromUsername)
    if request.is_xhr and request.method=="POST":
        # if(session['bkcoin']<=0):
        #     print("bkcoin terminati")
        #     response = {"result": False}
        #     responseJSON = json.dumps(response)
        #     print(responseJSON)
        #     return responseJSON
        fromEmail = session["email"]
        emailSender = fromEmail
        toUsername = request.form["username"]
        idBook = request.form["id"]
        title = request.form["title"]
        message1 = request.form["message1"]
        comment = message1
        messageTp = request.form["messageTp"]
        if messageTp=="true":
            messageTp=True
        else:
            messageTp=False
        print("tipo"+str(type(messageTp)))
        print(messageTp)
        try:
            #controlla che il libro esista ancora
            count,book = managedb.getBookDB(idBook)
            if count == 0:
                print("libro cancellato")
                response = {"result": False}
                responseJSON = json.dumps(response)
                print(responseJSON)
                return responseJSON
            booking = book["booking"]
            print("booking {}".format(booking))
        except Exception as e:
            print("errore " + str(e))
            print("errore risultato id")
            response = {"result": False}
            responseJSON = json.dumps(response)
            print(responseJSON)
            return responseJSON
        if booking==True:
            print("libro gia' prenotato")
            response = {"result": False}
            responseJSON = json.dumps(response)
            print(responseJSON)
            return responseJSON
        dateInsertMessage = datetime.datetime.now()
        print(message1)
        try:
            #inserisce il messaggio nel database
            managedb.sendMessageDB(fromUsername,toUsername,message1,dateInsertMessage,title,idBook,messageTp)
        except Exception as e :
            print("prenotazione fallita "+str(e))
            response = {"result": False}
            responseJSON = json.dumps(response)
            print(responseJSON)
            return responseJSON
        try:
            #incrementa il numero di messaggi ricevuti dal destinatario
            managedb.incrementMessagesCount(toUsername)
            response = {"result": True}
            responseJSON = json.dumps(response)
            print(responseJSON)
            return responseJSON
        except Exception as e:
            print("prenotazione fallita "+str(e))
            response = {"result": False}
            responseJSON = json.dumps(response)
            print(responseJSON)
            return responseJSON
    else:
        print("errore dati inviati")
        return json.dumps({"result": False})

@app.route("/getsearchbooking",methods=["GET","POST"])
def getsearchbooking():
    """getsearchbooking e' attivata da una richiesta HTTP asincrona (AJAX);
    l'utente richiede la prenotazione di un libro nella pagina "ricerca.html";
    il destinatario ricevera' un messaggio da poter leggere nella pagina
    messaggi.html; l'esito dell'operazione sara' restituito in JSON
    """
    print("logged_in" in session)
    # Flask salvera' un item logged_in se l'utente
    # ha effettuato un accesso con successo
    if ('logged_in' not in session) or (session['logged_in'] != True):
        print("Accesso negato in getBooking")
        return redirect(url_for('index'))
    fromUsername = session["username"]
    getMessagesCount(fromUsername)
    getBitCoin(fromUsername)
    if request.is_xhr and request.method=="POST":
        # if(session['bkcoin']<=0):
        #     print("bkcoin terminati")
        #     response = {"result": False}
        #     responseJSON = json.dumps(response)
        #     print(responseJSON)
        #     return responseJSON
        fromEmail = session["email"]
        emailSender = fromEmail
        toUsername = request.form["username"]
        isbn = request.form["isbn"]
        title = request.form["title"]
        message1 = request.form["message1"]
        messageTp = request.form["messageTp"]
        if messageTp=="true":
            messageTp=True
        else:
            messageTp=False
        print("tipo"+str(type(messageTp)))
        print(messageTp)
        try:
            #controlla che il libro esista ancora e che sia disponibile;
            #se piu' di uno ne restituisce uno in modo random
            count,book = managedb.getBookDBRandom(isbn,toUsername)
            if count == 0:
                print("libro non presente")
                response = {"result": False}
                responseJSON = json.dumps(response)
                print(responseJSON)
                return responseJSON
            booking = book["booking"]
            print("booking {}".format(booking))
        except Exception as e:
            print("errore " + str(e))
            print("errore risultato id")
            response = {"result": False}
            responseJSON = json.dumps(response)
            print(responseJSON)
            return responseJSON
        if booking==True:
            print("libro gia' prenotato")
            response = {"result": False}
            responseJSON = json.dumps(response)
            print(responseJSON)
            return responseJSON
        dateInsertMessage = datetime.datetime.now()
        idBook = str(book["_id"])
        print(message1)
        try:
            #inserisce il messaggio nel database
            managedb.sendMessageDB(fromUsername,toUsername,message1,dateInsertMessage,title,idBook,messageTp)
        except Exception as e :
            print("prenotazione fallita "+str(e))
            response = {"result": False}
            responseJSON = json.dumps(response)
            print(responseJSON)
            return responseJSON
        try:
            #incrementa il numero di messaggi ricevuti dal destinatario
            managedb.incrementMessagesCount(toUsername)
            response = {"result": True}
            responseJSON = json.dumps(response)
            print(responseJSON)
            return responseJSON
        except Exception as e:
            print("prenotazione fallita "+str(e))
            response = {"result": False}
            responseJSON = json.dumps(response)
            print(responseJSON)
            return responseJSON
    else:
        print("errore dati inviati")
        return json.dumps({"result": False})


@app.route("/acceptbooking",methods=["GET","POST"])
def acceptBooking():
    """acceptBooking consentira' al proprietario del libro
    di accettare la prenotazione di un utente"""
    # Flask salvera' un item logged_in se l'utente
    # ha effettuato un accesso con successo
    if ('logged_in' not in session) or (session['logged_in'] != True):
        print("Accesso negato in insertBook")
        return redirect(url_for('index'))
    toUsername = session["username"]
    getMessagesCount(toUsername)
    getBitCoin(toUsername)
    if request.is_xhr and request.method == 'POST':
        idBook = request.form['idBook']
        print("idBook "+idBook)
        fromUsername = request.form['username']
        print("fromUsername " + fromUsername)
        title = request.form["title"]
        try:
            #controlla che il libro esista ancora
            count,book = managedb.getBookDB(idBook)
            if count == 0:
                print("libro cancellato")
                response = {"result": False}
                responseJSON = json.dumps(response)
                print(responseJSON)
                return responseJSON
            booking = book["booking"]
            print("booking {}".format(booking))
        except Exception as e:
            print("errore " + str(e))
            print("errore risultato id")
            response = {"result": False}
            responseJSON = json.dumps(response)
            print(responseJSON)
            return responseJSON
        if booking==True:
            print("libro gia' prenotato")
            response = {"result": False}
            responseJSON = json.dumps(response)
            print(responseJSON)
            return responseJSON
        try:
            #memorizzera' la prenotazione del libro nel database
            managedb.getBookingDB(fromUsername,idBook)
            print("prenotazione ok")
        except Exception as e:
            print("errore " + str(e))
            print("prenotazione fallita")
            response = {"result": False}
            responseJSON = json.dumps(response)
            print(responseJSON)
            return responseJSON
        try:
            message1="Prenotazione accettata!!!"
            dateInsertMessage = datetime.datetime.now()
            #messaggeTp indica la tipologia del messaggio Vero -> Invio richiesta prenotazione
            #Falso -> Risposta messaggio
            messageTp=False
            #inserisce il messaggio nel database
            managedb.sendMessageDB(toUsername,fromUsername,message1,dateInsertMessage,title,idBook,messageTp)
        except Exception as e :
            print("prenotazione fallita "+str(e))
            response = {"result": False}
            responseJSON = json.dumps(response)
            print(responseJSON)
            return responseJSON
        try:
            #incrementa il numero di messaggi ricevuti dal destinatario
            managedb.incrementMessagesCount(fromUsername)
            response = {"result": True}
            responseJSON = json.dumps(response)
            print(responseJSON)
            return responseJSON
        except Exception as e:
            print("prenotazione fallita "+str(e))
            response = {"result": False}
            responseJSON = json.dumps(response)
            print(responseJSON)
            return responseJSON

@app.route("/listbook",methods=["GET","POST"])
def listBook():
    """listBook e' attivata dopo una richiesta HTTP asincrona (AJAX):
    l'utente richiede nella pagina scaffale.html tutti i libri che ha inserito;
    si effettuera' un'interrogazione al database managedb.listBooks();
    la risposta sara' inviato in formato JSON
    """
    # Flask salvera' un item logged_in se l'utente
    # ha effettuato un accesso con successo
    if ('logged_in' not in session) or (session['logged_in'] != True):
        print("Accesso negato in insertBook")
        return redirect(url_for('index'))
    if request.is_xhr and request.method == 'POST':
        email = request.form["email"]
        try:
            result,cursorListBook=managedb.listBooks(email)
            if(result==False):
                print("non ci sono risultati")
                return "non ci sono risultati"
            else:
                print("ci sono risultati")
                #conversione del tipo di alcune variabili in formato stringa
                cursorListBookJSON=mytools.modifyBookJSON(cursorListBook)
                return cursorListBookJSON
        except Exception as e:
            print("errore " + str(e))
            print("errore dati inviati")
            return json.dumps({"result": False})
    else:
        print("errore dati inviati")
        return json.dumps({"result": False})

@app.route("/getlistmessages",methods=["GET","POST"])
def getListMessages():
    """getListMessages sara' attivato dopo una richiesta HTTP asincrona (AJAX);
    l'utente richiedera' nella pagina messaggi.html la lista dei messaggi ricevuti;
    si interroghera' il database mediante managedb.getListMessagesDB();
    la risposta sara' inviata mediante JSON"""
    # Flask salvera' un item logged_in se l'utente
    # ha effettuato un accesso con successo
    if ('logged_in' not in session) or (session['logged_in'] != True):
        print("Accesso negato in insertBook")
        return redirect(url_for('index'))
    if request.is_xhr and request.method == 'POST':
        toUsername = session["username"]
        try:
            count,cursor = managedb.getListMessagesDB(toUsername)
            if count==0:
                print("nessun messaggio")
                return json.dumps({"result": False})
            else:
                cursorJSON = mytools.modifyMessagesJSON(cursor)
                print(cursorJSON)
                return cursorJSON
        except Exception as e:
            print("errore"+str(e))
            return json.dumps({"result":False})
    else:
        print("errore dati inviati")
        return json.dumps({"result": False})

@app.route("/deletebook",methods=["GET","POST"])
def deleteBook():
    """deleteBook sara' attivato dopo una richiesta HTTP asincrona (AJAX);
    l'utente richiede l'eliminazione di un libro dal proprio scaffale;
    effettuera' l'eliminazione del documente dal database mediante
    managedb.deleteBookDB(); la risposta dell'esito sara' fornita in formato
    JSON"""
    # Flask salvera' un item logged_in se l'utente
    # ha effettuato un accesso con successo
    if ('logged_in' not in session) or (session['logged_in'] != True):
        print("Accesso negato in insertBook")
        return redirect(url_for('index'))
    if request.is_xhr and request.method == "POST":
        idBook = request.form["id"]
        email = session["email"]
        username = session["username"]
        try:
            #chiedera' se il libro esista ancora nel database
            count, book = managedb.getBookDB(idBook)
            if(count == 0):
                print("non c'e' nessun libro!")
                response = {"result": False}
                responseJSON = json.dumps(response)
                print(responseJSON)
                return responseJSON
            booking = book["booking"]
            print("booking {}".format(booking))
        except Exception as e:
            print("errore " + str(e))
            print("errore cancellazione")
            response = {"result": False}
            responseJSON = json.dumps(response)
            print(responseJSON)
            return responseJSON
        if booking == True:
            print("libro gia' prenotato")
            response = {"result": False}
            responseJSON = json.dumps(response)
            print(responseJSON)
            return responseJSON
        print(idBook)
        try:
            #cancella il libro dal database
            managedb.deleteBookDB(idBook)
        except Exception as e:
            print("errore " + str(e))
            print("errore cancellazione 1")
            response = {"result": False}
            responseJSON = json.dumps(response)
            print(responseJSON)
            return responseJSON
        try:
            #decremente il numero di bkcoin
            managedb.decrementBKcoin(username)
            getMessagesCount(username)
            getBitCoin(username)
        except Exception as e:
            print("errore " + str(e))
            print("errore decremento")
            response = {"result": False}
            responseJSON = json.dumps(response)
            print(responseJSON)
            return responseJSON
        print("operazione cancellazione conclusa con successo")
        response = {"result": True}
        responseJSON = json.dumps(response)
        print(responseJSON)
        return responseJSON
    else:
        print("errore dati inviati")
        return json.dumps({"result": False})

@app.route('/confirm_email/<token>')
def confirm_email(token):
    """confirm_email e' utilizzato per la conferma di un'email;
    si utilizzera' un oggetto URLSafeSerializer per decodificare il token inviato (s.load());
    tale informazione sara' memorizzato nel database"""
    try:
        email = s.loads(token,salt='email-confirm')
        print(email)
        #salvera' nell'oggetto sessione che l'email sia stata convalidata
        count = managedb.checkUser1(email)
        print(count)
        if count>0:
            session["confirmEmail_in"]=True
            managedb.successConfirmEmail(email)
            return redirect(url_for("index"))
        else:
            link = url_for("index", _external=True)
            return 'il token e\' errato!' + '<a href="' + link + '">clicca qui</a>'
    except Exception as e:
        print("errore " + str(e))
        print("errore conferma email")
        link = url_for("index",_external=True)
        return 'il token e\' errato!'+'<a href="'+link+'">clicca qui</a>'

@app.route("/returnbook",methods=['GET','POST'])
def returnBook():
    """returnBook sara' attivato dopo una richiesta HTTP asincrona (AJAX);
    l'utente informera' il db che il libro sia stato restituito mediante
    il metodo managedb.returnBookDB().
    La risposta sara' in formato JSON
    """
    # Flask salvera' un item logged_in se l'utente
    # ha effettuato un accesso con successo
    if ('logged_in' not in session) or (session['logged_in'] != True):
        print("Accesso negato in insertBook")
        return redirect(url_for('index'))
    if request.is_xhr and request.method == "POST":
        idBook = request.form["id"]
        try:
            managedb.returnBookDB(idBook)
            return json.dumps({"result":True})
        except Exception as e:
            print("errore "+ str(e))
            return json.dumps({"result": True})
    else:
        print("errore dati inviati")
        return json.dumps({"result": False})

@app.errorhandler(403)
def noAuthorization(e):
    return "errore 403 - Accesso negato", 403

@app.errorhandler(404)
def pageNoFound(e):
    return "errore 404 - Pagina non trovata", 404

@app.errorhandler(500)
def internalServerError(e):
    return "errore 500 - Errore interno al server", 500
