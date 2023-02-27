# Hotel Manager


## How to run
Create new enviorment install the requirements and then python app.py flask run.

## Explaining the project
My final project is helpful hand for hotel owners, managers, and even staff to handle the hotel operations on-the-move from their laptops or smartphones. They can easily access data for the hotel like how many reservations there are for given period. The users have also the ability to reserve rooms, check for free rooms in given period of time, see statistics for the hotel.
### Databases
The application database is named hotel.db and it has 2 tables

-The first table, hotels,  contains information about the hotel (hotel_id, username, hash (for password), hotelname, tworoom (stores the number of rooms with 2 beds), threeroom (stores the number of rooms with 3 beds), apartments (stores the number of apartments)). The hotel_id column is the PRIMARY KEY of the table

-The second table, reservations, contains information about every reservation of the hotel. This table uses hotel_id from the first table as FOREIGN KEY and order_id as PRIMARY KEY. Columns: order_id, hotel_id, resname (the name of the reservation), roomtype (what type of room they reserved), fromdate, todate. Fromdate and todate columns are the period of time of the reservation
### Different functions
Loading:
The website has custom page loader made using simple javascript functions

Register:
You must enter the name of the hotel, how many rooms for two people the hotel has, how many rooms for three people the hotel has, how many apartments the hotel has and in the end username and password so you can easily access the account.

Login:
You must enter username and password. If they don`t match with enything from the database it returns error and gives you a chance to correct the input.

Homepage:
Home page doesn`t have any specific function rather than to display usefull data. The app calculates how many reservations there are for the last and for the next month and prints them, so the user can determine if the next month will be more profitable.

Reserve page:
When entering the reserve page you must enter how many rooms you want to make reservations for. Once you entered it you will be automatically redirected to another page where you need to fill every information needed to make the reservation if any of the input is wrong the app will give error and give you a chance to correct the mistake.

All reservations page:
When entering the all reservations page every reservation will be selected from the database and will be displayed on your display. No matter if the reservation is in the past or in the future everything will be displayed. Every reservation has order_id which is unique they may be completly random but they will be unique.

Check page:
The check page will make a check if there are free rooms of a given type and in a given period of time. You must select the period of time and the type of room and hit submit. A message will show up with the answer.
### How functions work
Loading: There is a div that covers everything behind it. We add eventlistener and when the page loads this div display is set to none and everything shows up.

Register:
Every input from the user is checked. If the user forgot to fill one of the input tags it returns error. When the input is correct every information is stored in the database

Login:
The code firstly is checking if the user input is correct, if not the code gives a chance for the user to correct the input. It then searches for rows in hotels table where usernames match. If it found more or less than 1 rows the code returns error. If it found exactly 1 row the code checks if the password from the input and password from the row match using check_password_hash function from werkzeug.security module. If they match the session is given value of hotel_id

Reserve page:
Reserve page gets the input from the user using flask and than calculates how many free rooms the hotel has, but how it does that. When entering the dates we get them by strings, the code then converts them to datetime objects so it can easily compare them. These dates are compared with every reservation dates and if they cross the count is up. Then it reads how many room the hotel has and subtracts the count of the crossed dates.

All reservations page:
Every reservations of the hotel are selected from the database and added to the html file. Then using table and bootstrap I made the page look better.

Check page:
The check page gets input from user( type of room, from date and to date ). If the user hasn`t filled every input it returns error. If the input is correct the code uses the same function as in reserve page. hen entering the dates we get them by strings, the code then converts them to datetime objects so it can easily compare them. These dates are compared with every reservation dates and if they cross the count is up. Then it reads how many room the hotel has and subtracts the count of the crossed dates.

### Technologies used
This web application was built using Flask (Python), SQLite3 for the database, CSS, bootstrap, html,  javascript.