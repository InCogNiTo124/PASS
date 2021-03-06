#-------------------------------------------------------------------------------
# Name:        Python Authorization Security Service
# Author:      Marijan Smetko
# Created:     27.02.2016
# Copyright:   (c) Marijan Smetko, 2016
#-------------------------------------------------------------------------------
from tkinter import * #Tk, Button, Label, Frame, Listbox, constants, Entry, StringVar
from tkinter.messagebox import showerror, askyesno
from tkinter.simpledialog import Dialog
from Crypto.Cipher import AES
from Crypto.Hash import SHA512, MD5
from sqlite3 import *
import Constants as Con
import base64

#
#   MAIN CLASS
#

class PASS():
    def __init__(self, root):
        self.root = root
        self.STATE = Con.SCREEN_WELCOME
        root.title("Python Authorization Security Service")
        root.protocol("WM_DELETE_WINDOW", self.exit)
        root.iconbitmap(r'./res/images/icon.ico')
        self.view = None
        self.DB = Database()
        self.activeUser = None
        self.data = []

        self.createGUI()
        return

    def changeState(self, state):
        self.STATE = state
        self.createGUI()
        return

    def createGUI(self):
        self.root.update_idletasks()
        #   x = (self.root.winfo_screenwidth() - self.root.winfo_reqwidth()) // 2
        #   y = (self.root.winfo_screenheight() - self.root.winfo_reqheight()) // 2
        #   self.root.geometry("+{0}+{1}".format(x, y))

        for w in self.root.winfo_children():
            w.destroy()

        if self.STATE == Con.SCREEN_WELCOME:
            self.view = WelcomeScreen(self)
            self.view.registrationButton.config(command = lambda t = Con.SCREEN_REGISTRATION : self.changeState(t))
            self.view.loginButton.config(command = lambda t = Con.SCREEN_LOGIN : self.changeState(t))

        elif self.STATE == Con.SCREEN_LOGIN:
            self.view = LoginScreen(self)
            self.view.loginButton.config(command = self.checkLoginData)
            self.view.cancelButton.config(command = lambda t = Con.SCREEN_WELCOME : self.changeState(t))

        elif self.STATE == Con.SCREEN_REGISTRATION:
            self.view = RegistrationScreen(self)
            self.view.registerButton.config(command = self.registerUser)
            self.view.cancelButton.config(command = lambda t = Con.SCREEN_WELCOME: self.changeState(t))

        elif self.STATE == Con.SCREEN_MAIN:
            self.view = MainScreen(self)
        return

    def registerUser(self):
        #   An assumption is that the method will be called only from RegistrationScreen
        fName = self.view.vFirstName.get()
        lName = self.view.vLastName.get()
        uName = self.view.vUsername.get()
        pWord = self.view.vPassword.get()
        u = User(None, fName, lName, uName, pWord)
        try:
            u = self.DB.addUser(u)
            self.activeUser = u
            self.changeState(Con.SCREEN_MAIN)
        except DatabaseError as e:
            showerror(Con.GUI_ERROR_TITLE, e)
        return

    def loginUser(self):
        #   An assumption is that the method will be called only from LoginScreen
        uName = self.view.vUsername.get()
        pWord = self.view.vPassword.get()
        u = User(None, None, None, uName, pWord)
        u = self.DB.login(u)
        if u != None:
            self.activeUser = u
            self.changeState(Con.SCREEN_MAIN)
        else:
            showerror(Con.GUI_ERROR_TITLE, Con.GUI_ERROR_LOGIN_MESSAGE)
        return

    def exit(self):
        if askyesno(Con.GUI_EXIT_TITLE, Con.GUI_EXIT_MESSAGE):
            self.DB.disconnect()
            self.root.clipboard_clear()
            self.root.destroy()
        return

    def populateListbox(self, listBox):
        listBox.delete(0, END)
        self.data = self.DB.getAllData(self.activeUser)
        if len(self.data) == 0:
            listBox.insert(0, Con.GUI_NO_ACCOUNTS)
        else:
            for row in self.data:
                listBox.insert(END, row.getTitle())
        return

    def checkLoginData(self):
        uName = self.view.vUsername.get()
        pWord = self.view.vPassword.get()

        if len(uName) == 0:
            showerror(Con.GUI_ERROR_TITLE, Con.GUI_ERROR_LOGIN_USERNAME_EMPTY)
            return
        elif len(pWord) == 0:
            showerror(Con.GUI_ERROR_TITLE, Con.GUI_ERROR_LOGIN_PASSWORD_EMPTY)
            return
        else:
            return self.loginUser()

    def togglePassword(self, e, b):
        if e["show"] == Con.DOT:
            e.config(show = "")
            b.config(text = "Hide")
        else:
            e.config(show = Con.DOT)
            b.config(text = "Show")
        return

    def logOff(self):
        if askyesno(Con.GUI_LOGOFF_TITLE, Con.GUI_LOGOFF_MESSAGE):
            self.activeUser = None
            self.changeState(Con.SCREEN_LOGIN)
        return

#
#   GUI CLASSES
#

class WelcomeScreen(Frame):
    def __init__(self, P):
        self.PASS = P
        super().__init__(P.root)
        self.registrationButton = None
        self.loginButton = None
        self.createGUI()
        return

    def createGUI(self):
        self.grid(rows = 4, columns = 1)
        Label(self, text = "Hello!\nWelcome to PASS!", font = ("Arial", 12, "bold"), justify = LEFT).grid(row = 0, column = 0)
        img = PhotoImage(file = "./res/images/logo.gif")
        l = Label(self, image = img)
        l.image = img
        l.grid(row = 1, column = 0)
        self.registrationButton = Button(self, text = "Registration", width = 10)
        self.registrationButton.grid(row = 2, column = 0, pady = 5)
        self.loginButton = Button(self, text = "Login", width = 10)
        self.loginButton.grid(row = 3, column = 0, pady = 5)
        return

class LoginScreen(Frame):
    def __init__(self, P):
        self.PASS = P
        super().__init__(P.root)
        self.vUsername = StringVar()
        self.vPassword = StringVar()
        self.loginButton = None
        self.cancelButton = None
        self.createGUI()
        return

    def createGUI(self):
        self.grid(rows = 5, columns = 2)
        Label(self, text = "Username:").grid(row = 0, column = 0, columnspan = 2)
        Entry(self, textvariable = self.vUsername).grid(row = 1, column = 0, pady = 10, columnspan = 2, padx = 5)
        Label(self, text = "Password:").grid(row = 2, column = 0, columnspan = 2)
        Entry(self, textvariable = self.vPassword, show = Con.DOT).grid(row = 3, column = 0, pady = 10, columnspan = 2, padx = 5)
        self.loginButton = Button(self, text = "Login", width = 5)
        self.loginButton.grid(row = 4, column = 1, pady = 5)
        self.cancelButton = Button(self, text = "Cancel", width = 5)
        self.cancelButton.grid(row = 4, column = 0, pady = 5)
        return

class MainScreen(Frame):
    def __init__(self, P):
        self.PASS = P
        super().__init__(P.root)
        self.vURL = StringVar()
        self.vUsername = StringVar()
        self.vPassword = StringVar()
        self.ACCOUNTS_LIST = None
        self.TOOLBAR = Frame(self)
        self.MAIN_FRAME = Frame(self)

        self.createGUI()
        self.PASS.populateListbox(self.ACCOUNTS_LIST)
        return

    def createGUI(self):
        self.grid(row = 2, columns = 1)

        self.TOOLBAR.grid(row = 0, column = 0, rows = 1, columns = 4, sticky = W, pady = (5, 10), padx = 5)
        self.MAIN_FRAME.grid(row = 1, column = 0, rows = 8, columns = 8, pady = 5, padx = 5)

        for i in range(8):
            self.MAIN_FRAME.rowconfigure(i, weight = 1)
            self.MAIN_FRAME.columnconfigure(i, weight = 2)

        addImage = PhotoImage(file = "./res/images/add.gif")
        addButton = Button(self.TOOLBAR, text = "Add", image = addImage, command = self.addData, compound = TOP)
        addButton.image = addImage
        addButton.grid(row = 0, column = 0, sticky = W, padx = (0, 5))
        removeImage = PhotoImage(file = "./res/images/remove.gif")
        removeButton = Button(self.TOOLBAR, text = "Remove", command = self.remove, image = removeImage, compound = TOP)
        removeButton.image = removeImage
        removeButton.grid(row = 0, column = 1, sticky = W, padx = (0, 5))
        editImage = PhotoImage(file = "./res/images/edit.gif")
        editButton = Button(self.TOOLBAR, text = "Edit", command = self.editData, compound = TOP, image = editImage)
        editButton.image = editImage
        editButton.grid(row = 0, column = 2, sticky = W, padx = (0, 5))
        logoffImage = PhotoImage(file = "./res/images/log_off.gif")
        logoffButton = Button(self.TOOLBAR, text = "Log off", command = self.PASS.logOff, compound = TOP, image = logoffImage)
        logoffButton.image = logoffImage
        logoffButton.grid(row = 0, column = 3, sticky = W, padx = (0, 5))
        exitImage = PhotoImage(file = "./res/images/exit.gif")
        exitButton = Button(self.TOOLBAR, text = "Exit", command = self.PASS.exit, compound = TOP, image = exitImage)
        exitButton.image = exitImage
        exitButton.grid(row = 0, column = 4, sticky = W, padx = (20, 0))

        self.ACCOUNTS_LIST = Listbox(self.MAIN_FRAME, selectmode = SINGLE)
        self.ACCOUNTS_LIST.bind("<<ListboxSelect>>", self.showData)
        self.ACCOUNTS_LIST.grid(row = 0, column = 0, columnspan = 2, rowspan = 8, padx = (0, 20))

        Label(self.MAIN_FRAME, text = "URL:").grid(row = 1, column = 3, sticky = W)
        Entry(self.MAIN_FRAME, textvariable = self.vURL, width = 30, state = DISABLED, disabledforeground = "#000000", disabledbackground = "#ffffff").grid(row = 1, column = 4, sticky = W+E, padx = (10, 10))
        Button(self.MAIN_FRAME, text = "Copy", width = 10, command = lambda : self.copyToClipboard(self.vURL.get())).grid(row = 1, column = 5, sticky = W+E)

        Label(self.MAIN_FRAME, text = "Username:").grid(row = 2, column = 3, sticky = W)
        Entry(self.MAIN_FRAME, textvariable = self.vUsername, state = DISABLED, disabledforeground = "#000000", disabledbackground = "#ffffff").grid(row = 2, column = 4, sticky = W+E, padx = (10, 10))
        Button(self.MAIN_FRAME, text = "Copy", width = 10, command = lambda : self.copyToClipboard(self.vUsername.get())).grid(row = 2, column = 5, sticky = W+E)

        Label(self.MAIN_FRAME, text = "Password:").grid(row = 3, column = 3, sticky = W)
        e = Entry(self.MAIN_FRAME, textvariable = self.vPassword, show = Con.DOT, state = DISABLED, disabledforeground = "#000000", disabledbackground = "#ffffff")
        e.grid(row = 3, column = 4, sticky = W+E, padx = (10, 10))
        Button(self.MAIN_FRAME, text = "Copy", width = 10, command = lambda : self.copyToClipboard(self.vPassword.get())).grid(row = 3, column = 5, sticky = W+E)
        b = Button(self.MAIN_FRAME, text = "Show", width = 7)
        b.config(command = lambda : self.PASS.togglePassword(e, b))
        b.grid(row = 3, column = 6, sticky = W+E, padx = (5, 0))
        return

    def addData(self):
        dialog = AddDialog(self)
        d = dialog.D
        if d != None:
            data = Data(None, self.PASS.activeUser.getID(), d[Con.DB_DATA_TITLE], d[Con.DB_DATA_URL], d[Con.DB_DATA_USERNAME], d[Con.DB_DATA_PASSWORD])
            self.PASS.DB.insertData(data)
            self.PASS.populateListbox(self.ACCOUNTS_LIST)
            self.ACCOUNTS_LIST.selection_set(END)
            self.showData()
        #   TODO: ADD EXCEPTION
        return

    def remove(self):
        selected = self.ACCOUNTS_LIST.curselection()
        if len(self.PASS.data) > 0 and len(selected) > 0:
            if askyesno(Con.GUI_WARNING_TITLE, Con.GUI_REMOVE_MESSAGE):
                index = selected[0]
                self.ACCOUNTS_LIST.delete(index)
                t = self.PASS.data.pop(index)
                self.PASS.DB.removeData(t.getID())
                self.PASS.populateListbox(self.ACCOUNTS_LIST)
                self.ACCOUNTS_LIST.selection_set(min(index, self.ACCOUNTS_LIST.size() - 1))
                self.showData()
        return

    def showData(self, e = None):
        if len(self.PASS.data) > 0:
            index = self.ACCOUNTS_LIST.curselection()[0]
            data = self.PASS.data[index]
            self.vURL.set(data.getURL())
            self.vUsername.set(data.getUsername())
            self.vPassword.set(data.getPassword())
        else:
            self.vURL.set("")
            self.vUsername.set("")
            self.vPassword.set("")
        return

    def editData(self, e = None):
        selected = self.ACCOUNTS_LIST.curselection()
        if len(self.PASS.data) > 0 and len(selected) > 0:
            index = selected[0]
            data = self.PASS.data[index]
            dialog = EditDialog(self, data)
            self.PASS.DB.updateData(dialog.data)
            self.PASS.populateListbox(self.ACCOUNTS_LIST)
            self.ACCOUNTS_LIST.selection_set(index)
            self.showData()
        return

    def copyToClipboard(self, s):
        self.PASS.root.clipboard_clear()
        self.PASS.root.clipboard_append(s)
        return

class RegistrationScreen(Frame):
    def __init__(self, P):
        self.PASS = P
        super().__init__(P.root)
        self.registerButton = None
        self.cancelButton = None
        self.vFirstName = StringVar()
        self.vLastName = StringVar()
        self.vUsername = StringVar()
        self.vPassword = StringVar()
        self.createGUI()
        return

    def createGUI(self):
        self.grid(rows = 9, columns = 2)
        Label(self, text = "First Name").grid(row = 0, column = 0, columnspan = 2, sticky = W + E)
        Label(self, text = "Last Name").grid(row = 2, column = 0, columnspan = 2)
        Entry(self, textvariable = self.vFirstName).grid(row = 1, column = 0, columnspan = 2, pady = (0, 15))
        Entry(self, textvariable = self.vLastName).grid(row = 3, column = 0, columnspan = 2, pady = (0, 15))
        Label(self, text = "Username").grid(row = 4, column = 0, columnspan = 2)
        Label(self, text = "Password").grid(row = 6, column = 0, columnspan = 2)
        Entry(self, textvariable = self.vUsername).grid(row = 5, column = 0, columnspan = 2, pady = (0, 15))
        Entry(self, textvariable = self.vPassword, show = Con.DOT).grid(row = 7, column = 0, columnspan = 2, pady = (0, 25))
        self.registerButton = Button(self, text = "Register", width = 10)
        self.registerButton.grid(row = 8, column = 1, padx = 2)
        self.cancelButton = Button(self, text = "Cancel", width = 10)
        self.cancelButton.grid(row = 8, column = 0, padx = 2)
        return

class AddDialog(Dialog):
    def body(self, parent):
        self.D = None
        self.vTitle = StringVar()
        self.vURL = StringVar()
        self.vUsername = StringVar()
        self.vPassword = StringVar()
        
        Label(parent, text = "Title:").grid(row = 0, column = 0, sticky = W+E, padx = 5)
        Label(parent, text = "URL:").grid(row = 0, column = 1, sticky = W+E, padx = 5)
        Entry(parent, textvariable = self.vTitle).grid(row = 1, column = 0, sticky = W+E, padx = 5, pady = (0, 15))
        Entry(parent, textvariable = self.vURL).grid(row = 1, column = 1, sticky = W+E, padx = 5, pady = (0, 15))
        Label(parent, text = "Username:").grid(row = 2, column = 0)
        Label(parent, text = "Password:").grid(row = 2, column = 1)
        Entry(parent, textvariable = self.vUsername).grid(row = 3, column = 0)
        e = Entry(parent, show = Con.DOT, textvariable = self.vPassword)
        e.grid(row = 3, column = 1)
        b = Button(parent, text = "Show", width = 7)
        b.grid(row = 3, column = 2)
        b.config(command = lambda : self.togglePassword(e, b))
        return

    def validate(self):
        if len(self.vTitle.get()) == 0:
            showerror(Con.GUI_ERROR_TITLE, Con.GUI_ERROR_DIALOG_TITLE_EMPTY)
            return False
        elif len(self.vUsername.get()) == 0:
            showerror(Con.GUI_ERROR_TITLE, Con.GUI_ERROR_DIALOG_USERNAME_EMPTY)
            return False
        elif len(self.vPassword.get()) == 0:
            showerror(Con.GUI_ERROR_TITLE, Con.GUI_ERROR_DIALOG_PASSWORD_EMPTY)
            return False
        elif not(len(self.vURL.get()) == 0 or "://" in self.vURL.get()):
            showerror(Con.GUI_ERROR_TITLE, Con.GUI_ERROR_DIALOG_URL_INCORRECT)
            return False
        else:
            return True
        
    def togglePassword(self, e, b):
        if e["show"] == Con.DOT:
            e.config(show = "")
            b.config(text = "Hide")
        else:
            e.config(show = Con.DOT)
            b.config(text = "Show")
        return
    
    def apply(self):
        self.D = dict()
        self.D[Con.DB_DATA_TITLE] = self.vTitle.get()
        self.D[Con.DB_DATA_URL] = self.vURL.get()
        self.D[Con.DB_DATA_USERNAME] = self.vUsername.get()
        self.D[Con.DB_DATA_PASSWORD] = self.vPassword.get()
        return

class EditDialog(Dialog):
    def __init__(self, parent, data, title = None):
        self.data = data
        super().__init__(parent, title)
        return

    def body(self, parent):
        self.vTitle = StringVar()
        self.vTitle.set(self.data.getTitle())
        self.vURL = StringVar()
        self.vURL.set(self.data.getURL())
        self.vUsername= StringVar()
        self.vUsername.set(self.data.getUsername())
        self.vPassword = StringVar()
        self.vPassword.set(self.data.getPassword())

        Label(parent, text = "Title:").grid(row = 0, column = 0, sticky = W+E, padx = 5)
        Label(parent, text = "URL:").grid(row = 0, column = 1, sticky = W+E, padx = 5)
        Entry(parent, textvariable = self.vTitle).grid(row = 1, column = 0, sticky = W+E, padx = 5, pady = (0, 15))
        Entry(parent, textvariable = self.vURL).grid(row = 1, column = 1, sticky = W+E, padx = 5, pady = (0, 15))
        Label(parent, text = "Username:").grid(row = 2, column = 0)
        Label(parent, text = "Password:").grid(row = 2, column = 1)
        Entry(parent, textvariable = self.vUsername).grid(row = 3, column = 0)
        e = Entry(parent, show = Con.DOT, textvariable = self.vPassword)
        e.grid(row = 3, column = 1)
        b = Button(parent, text = "Show", width = 7)
        b.grid(row = 3, column = 2)
        b.config(command = lambda : self.togglePassword(e, b))
        return

    def togglePassword(self, e, b):
        if e["show"] == Con.DOT:
            e.config(show = "")
            b.config(text = "Hide")
        else:
            e.config(show = Con.DOT)
            b.config(text = "Show")
        return

    def validate(self):
        if len(self.vTitle.get()) == 0:
            showerror(Con.GUI_ERROR_TITLE, Con.GUI_ERROR_DIALOG_TITLE_EMPTY)
            return False
        elif len(self.vUsername.get()) == 0:
            showerror(Con.GUI_ERROR_TITLE, Con.GUI_ERROR_DIALOG_USERNAME_EMPTY)
            return False
        elif len(self.vPassword.get()) == 0:
            showerror(Con.GUI_ERROR_TITLE, Con.GUI_ERROR_DIALOG_PASSWORD_EMPTY)
            return False
        elif not(len(self.vURL.get()) == 0 or "://" in self.vURL.get()):
            showerror(Con.GUI_ERROR_TITLE, Con.GUI_ERROR_DIALOG_URL_INCORRECT)
            return False
        else:
            return True

    def apply(self):
        self.data = Data(self.data.getID(), self.data.getUserID(), self.vTitle.get(), self.vURL.get(), self.vUsername.get(), self.vPassword.get())
        return

#
#   DB CLASS
#

class Crypter():
    def __init__(self):
        return

    def encrypt(self, text, key):
        """
        Text is string
        Key is a hash, string
        """
        
        text = text + Con.PAD_CHAR * (16 - len(text) % 16)
        cipher = AES.new(key.encode("UTF-8"))
        enc = cipher.encrypt(text.encode("UTF-8"))
        return base64.b64encode(enc).decode("UTF-8")

    def decrypt(self, encrypted, key):
        cipher = AES.new(key.encode("UTF-8"))
        deString = base64.b64decode(encrypted.encode("UTF-8"))
        original = cipher.decrypt(deString)
        return original.decode("UTF-8").strip(Con.PAD_CHAR)

class Database():
    FILENAME = "PASS.db"
    CIPHER = Crypter()
    def __init__(self):
        self.CONN = connect(self.FILENAME)
        self.CURSOR = self.CONN.cursor()
        self.KEY = None
        self.prepareDB()
        return

    def disconnect(self):
        self.CONN.commit()
        self.CONN.close()

    def addUser(self, user):
        keygen = MD5.new()
        passgen = SHA512.new()
        keygen.update(user.getPassword().encode("UTF-8"))
        passgen.update(user.getPassword().encode("UTF-8"))
        key = keygen.hexdigest()
        pWord = passgen.hexdigest()
        uName = self.CIPHER.encrypt(user.getUsername(), key)
        query = """
                SELECT {0}, {1}, {2}, {3}, {4}
                FROM {5}
                WHERE
                    Username = '{6}' AND
                    Password = '{7}';
        """.format(Con.DB_USERS_ID, Con.DB_USERS_FIRSTNAME, Con.DB_USERS_LASTNAME, Con.DB_USERS_USERNAME, Con.DB_USERS_PASSWORD, Con.DB_USERS, uName, pWord)
        for row in self.CURSOR.execute(query):
            raise DatabaseError(Con.ERROR_DATABASE_USER_ALREADY_REGISTRATED)
            return
        
        fName = self.CIPHER.encrypt(user.getFirstName(), key)
        lName = self.CIPHER.encrypt(user.getLastName(), key)
        query = """
                INSERT INTO {0}
                ({1}, {2}, {3}, {4})
                VALUES
                ("{5}", "{6}", "{7}", "{8}");
                """.format(Con.DB_USERS, Con.DB_USERS_FIRSTNAME, Con.DB_USERS_LASTNAME, Con.DB_USERS_USERNAME, Con.DB_USERS_PASSWORD, fName, lName, uName, pWord)
        self.CONN.execute(query)
        self.CONN.commit()
        return self.login(user)

    def prepareDB(self):
        query = """
                CREATE TABLE IF NOT EXISTS {0}
                ({1} INTEGER PRIMARY KEY AUTOINCREMENT,
                {2} TEXT NOT NULL,
                {3} TEXT NOT NULL,
                {4} TEXT NOT NULL,
                {5} TEXT NOT NULL);
                """.format(Con.DB_USERS, Con.DB_USERS_ID, Con.DB_USERS_FIRSTNAME, Con.DB_USERS_LASTNAME, Con.DB_USERS_USERNAME, Con.DB_USERS_PASSWORD,)
        self.CONN.execute(query)

        query = """
                CREATE TABLE IF NOT EXISTS {0}
                ({1} INTEGER PRIMARY KEY AUTOINCREMENT,
                {2} INTEGER REFERENCES {3}({4}),
                {5} TEXT NOT NULL,
                {6} TEXT,
                {7} TEXT NOT NULL,
                {8} TEXT NOT NULL);
                """.format(Con.DB_DATA, Con.DB_DATA_ID, Con.DB_DATA_USERID, Con.DB_USERS, Con.DB_USERS_ID, Con.DB_DATA_TITLE, Con.DB_DATA_URL, Con.DB_DATA_USERNAME, Con.DB_DATA_PASSWORD)
        self.CONN.execute(query)
        self.CONN.commit()
        return

    def login(self, user):
        u = None
        keygen = MD5.new()
        passgen = SHA512.new()
        keygen.update(user.getPassword().encode("UTF-8"))
        passgen.update(user.getPassword().encode("UTF-8"))
        key = keygen.hexdigest()
        pWord = passgen.hexdigest()
        uName = self.CIPHER.encrypt(user.getUsername(), key)
        
        query = """
                SELECT {0}, {1}, {2}, {3}, {4}
                FROM {5}
                WHERE
                    Username = '{6}' AND
                    Password = '{7}';
        """.format(Con.DB_USERS_ID, Con.DB_USERS_FIRSTNAME, Con.DB_USERS_LASTNAME, Con.DB_USERS_USERNAME, Con.DB_USERS_PASSWORD, Con.DB_USERS, uName, pWord)

        for row in self.CURSOR.execute(query):  # An asumption is that there will be only one row
            u = User(row[0], row[1], row[2], row[3], row[4])

        self.KEY = key
        return u

    def insertData(self, data):
        key = self.KEY
        title = self.CIPHER.encrypt(data.getTitle(), key)
        URL = self.CIPHER.encrypt(data.getURL(), key)
        uName = self.CIPHER.encrypt(data.getUsername(), key)
        pWord = self.CIPHER.encrypt(data.getPassword(), key)
        query = """
                INSERT INTO {0}
                ({1}, {2}, {3}, {4}, {5})
                VALUES
                ({6}, "{7}", "{8}", "{9}", "{10}");
                """.format(Con.DB_DATA, Con.DB_DATA_USERID, Con.DB_DATA_TITLE, Con.DB_DATA_URL, Con.DB_DATA_USERNAME, Con.DB_DATA_PASSWORD, data.getUserID(), title, URL, uName, pWord)
        self.CURSOR.execute(query)
        self.CONN.commit()
        return

    def getAllData(self, aUser):
        data = []
        key = self.KEY
        query = """
                SELECT {0}, {1}, {2}, {3}, {4}, {5}
                FROM {6}
                WHERE {7} = {8}
                ORDER BY {9} ASC;
                """.format(Con.DB_DATA_ID, Con.DB_DATA_USERID, Con.DB_DATA_TITLE, Con.DB_DATA_URL, Con.DB_DATA_USERNAME, Con.DB_DATA_PASSWORD, Con.DB_DATA, Con.DB_DATA_USERID, aUser.getID(), Con.DB_DATA_TITLE)
        
        for row in self.CURSOR.execute(query):
            title = self.CIPHER.decrypt(row[2], key)
            URL = self.CIPHER.decrypt(row[3], key)
            uName = self.CIPHER.decrypt(row[4], key)
            pWord = self.CIPHER.decrypt(row[5], key)
            data.append(Data(row[0], row[1], title, URL, uName, pWord))

        return data

    def removeData(self, ID):
        query = """
                DELETE
                FROM {0}
                WHERE {1} = {2};
                """.format(Con.DB_DATA, Con.DB_DATA_ID, ID)
        self.CURSOR.execute(query)
        self.CONN.commit()
        return

    def updateData(self, data):
        key = self.KEY
        title = self.CIPHER.encrypt(data.getTitle(), key)
        URL = self.CIPHER.encrypt(data.getURL(), key)
        uName = self.CIPHER.encrypt(data.getUsername(), key)
        pWord = self.CIPHER.encrypt(data.getPassword(), key)
        query = """
                UPDATE {0}
                SET {1} = "{2}",
                    {3} = "{4}",
                    {5} = "{6}",
                    {7} = "{8}"
                WHERE ID = {9};
                """.format(Con.DB_DATA, Con.DB_DATA_TITLE, title, Con.DB_DATA_URL, URL, Con.DB_DATA_USERNAME, uName, Con.DB_DATA_PASSWORD, pWord, data.getID())
        self.CURSOR.execute(query)
        self.CONN.commit()
        return

#
#   DATA CLASSES
#

class User():
    def __init__(self, ID, fName, lName, uName, pWord):
        self.ID = ID
        self.firstName = fName
        self.lastName = lName
        self.username = uName
        self.password = pWord
        return

    def __repr__(self):
        return "{} {} {} {}".format(self.firstName, self.lastName, self.username, self.password)

    def getID(self):
        return self.ID

    def setID(self, ID):
        self.ID = ID
        return

    def getFirstName(self):
        return self.firstName

    def setFirstName(self, fName):
        self.firstName = fName
        return

    def getLastName(self):
        return self.lastName

    def setLastName(self, lName):
        self.lastName = lName
        return

    def getUsername(self):
        return self.username

    def setUsername(self, uName):
        self.username = uName
        return

    def getPassword(self):
        return self.password

    def setPassword(self, pWord):
        self.password = pWord
        return

class Data():
    def __init__(self, ID, uID, title, URL, uName, pWord):
        self.ID = ID
        self.userID = uID
        self.title = title
        self.URL = URL
        self.username = uName
        self.password = pWord
        return

    def __repr__(self):
        return "{} {} {} {} {} {}".format(self.ID, self.userID, self.title, self.URL, self.username, self.password)

    def getID(self):
        return self.ID

    def setID(self, ID):
        self.ID = ID
        return

    def getUserID(self):
        return self.userID

    def setUserID(self, uID):
        self.userID = uID
        return

    def getTitle(self):
        return self.title

    def setTitle(self, title):
        self.title = title
        return

    def getURL(self):
        return self.URL

    def setURL(self, URL):
        self.URL = URL
        return

    def getUsername(self):
        return self.username

    def setUsername(self, uName):
        self.username = uName
        return

    def getPassword(self):
        return self.password

    def setPassword(self, pWord):
        self.password = pWord
        return

#
#   ERROR CLASSES
#

class DatabaseError(Exception):
    pass

#
#   PROGRAM START
#

if __name__ == '__main__':
##    c = Crypter()
##    txts = [""]
##    keys = ["kljuc", "marijan smetko", "kad ti kazu da ne volim tad lazu te"]
##    for k in keys:
##        for t in txts:
##            keygen = MD5.new()
##            keygen.update(k.encode("UTF-8"))
##            
##            enc = c.encrypt(t, keygen.hexdigest())
##            print(enc)
##            dec = c.decrypt(enc, keygen.hexdigest())
##            print(dec)
##            print()
            
    root = Tk()
    PASS(root)
    root.mainloop()
