PASS v1.0
#########

Python Authorization Security Software

Contents:
	1. Overview
	2. How to use PASS?
	3. Technical Details
	4. Thanks, contributors and etc.

1. Overview
###############################################################################
	Python Authorization Security Software is a small program which saves your
passwords so you don't need to memorize them. It's very lightweight, uses SQLite
database for storing data which is encrypted by AES alghoritm so any attempt to
steal the data by direct reading from the database shall fail, miserably. While
designing both the software and the graphical design, a special care was taken
for the simplicity of usage.
	I hope this small project of mine will help you in your everyday activities
and you will enjoy it as mush as I enjoyed coding it.

																  the developer
												Marijan Smetko, Novska, Croatia

2. How to use PASS?
###############################################################################
	PASS is very simple to use. When you first launch the app, you'll be greeted
with a welcome message, where you can choose to register yourself. The register
screen is self-explainatory, you just type your data in. When the registering is
done, one is lead to the main screen, the ground of the project. Here you see at
left part of the screen a list of you saved sites, but its empty. You can add 
passwords on the "Add" button. If you don't want it anymore, you can delete it
with "Delete" button. If you accidentally made a mistake, you can edit it with a
"Edit" button. If somebody else is using the computer, but they need their
password, you can simply log off with "Log off". Finally, when you're done with
using PASS, you can exit an application with an "Exit" button.

3. Technical Details
###############################################################################
	The software is written in Python 3, with an attempt of MVC architecture.
Entire software is in the file called 'Python Authorization Security
Software.py', with multiple classes inside, such as the main class PASS, some
GUI classes, Database Managment class and other.

	The main class, PASS, has next:
		FIELDS:
			root					- Tk window
			STATE					- Current state of the software
			view					- Current view the software is
			DB						- Database Managment
			activeUser				- Holds user that is logged in
			data					- A list of user's data
		
		METHODS:
			changeState()			- Method for passing through various states
			createGUI()				- Method that creates user interface
			registerUser()			- Method which adds a user in a DB
			loginUser()				- Method which logs in a user
			exit()					- Method which exits the application
			populateListbox()		- Method which fills a Listbox with titles
			checkLoginData()		- Method which checks inputs before logging in
			togglePassword()		- Method which toggles between dots and letters
			logOff()				- Method which logs off a user
			
	GUI classes:
	WelcomeScreen:
		FIELDS:
			PASS 					- The PASS object
			registrationButton		- Button to go to registration
			loginButton				- Button to go to login
		
		METHODS:
			createGUI()				- Method that creates user interface
			
	LoginScreen:
		FIELDS:
			PASS 					- The PASS object
			loginButton				- Button to go to login
			cancelButton			- Button to go back to WelcomeScreen
			vUsername				- Variable that holds User's username
			vPassword				- Variable that holds User's password
		
		METHODS:
			createGUI()				- Method that creates user interface	
	
	MainScreen:
		FIELDS:
			PASS					- The PASS object
			vURL 					- Variable that holds Data's URL
			vUsername 				- Variable that holds Data's Username
			vPassword				- Variable that holds Data's Password
			ACCOUNTS_LIST			- Sidebar listbox with entries
			TOOLBAR					- Frame that hold buttons on top
			MAIN_FRAME				- Frame that holds main part of the app
			
		METHODS:
			createGUI()				- Method that creates user interface
			addData()				- Method that opens Add dialog
			showData()				- Method that updates Data fields
			remove()				- Method which removes selected entry
			showData()				- Data which shows data for an entry
			editData()				- Method that opens Edit dialog
			copyToClipboard()		- Method which copies content from Entry
			
	RegistrationScreen:
		FIELDS:
			PASS 					- The PASS object
			registerButton			- Button which registers a User
			cancelButton			- Button to go back to WelcomeScreen
			vFirstName				- Variable that holds User's first name
			vLastName				- Variable that holds User's last name
			vUsername				- Variable that holds User's username
			vPassword				- Variable that holds User's password
			
		METHODS:
			createGUI()				- Method that creates user interface
	
	AddDialog, EditDialog:
		FIELDS:
			*none specific*
		
		METHODS:
			body()					- Overriden method that builds dialog's GUI
			validate()				- Overriden method that validates entries
			apply()					- Overriden method that closes the dialog
			
	Model class:
	Database:
		FIELDS:
			FILENAME				- Filename string
			CONN					- Connection object for SQLIte DB
			CURSOR					- Cursor object for executing SQL statements
		
		METHODS:
			disconnect()			- Method which disconnects from the DB
			addUser()				- If the user is not in the DB, adds it
			prepareDB()				- Prepares the DB for usage
			login()					- Returns a user by username and password
			insertData()			- Inserts data from dialog into DB
			getAllData()			- Method that returns all data for a user
			removeData()			- Method that removes data from DB
			updateData()			- Method that updates data in DB
			
	Data Classes:
	User:
		FIELDS:
			ID						- ID of a User in the DB
			firstName				- User's first name
			lastName				- User's last name
			username				- User's username
			password				- User's password
			
		METHODS:
			get******				- Getter for a specific field
			set******				- Setter for a specific field
			
	Data:
		FIELDS:
			ID						- ID of a Data object in the DB
			userID					- ID of the Data's owner User
			title					- Data's title
			URL						- Data's URL
			username				- User's username
			password				- User's password
			
		METHODS:
			get******				- Getter for a specific field
			set******				- Setter for a specific field
	
	Other:
	DatabaseError					- Error in the DB

*****DATABASE*****

	The SQLite database is called PASS.db. The database itself is not encrypted
but the content is what's encrypted, using AES-256 encryption algorithm for
everything but for password, which are stored as SHA-512 hashes. Database
encoding is UTF-8.

STRUCTURE:
*****************			*****************
*Users			*			*Data			*
*****************			*****************
*ID				*--1:N--|	*ID				*
*FirstName		*		|---*UserID			*
*LastName		*			*Title			*
*Username		*			*URL			*
*Password		*			*Username		*
*****************			*Password		*
							*****************
4. Thanks, contributors and etc.
###############################################################################
	
	- Special thanks to Anja Vasyliv, my graphical designer
	- Special thanks to my proffessor Predrag Broðanac who saw a programming
	potential in me and encouraged it
	- Thanks to my parents for all the support I've been given
	- Thanks to all the translators
	- And thanks to YOU, my fellow user, for who all theese people worked for