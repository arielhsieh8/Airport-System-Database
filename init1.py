#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       port=8889,
                       user='root',
                       password='root',
                       db='Flights',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)



#Define a route to hello function
@app.route('/')
def hello():
	return render_template('home.html')

######################### CUSTOMER (ARIEL) PARTS ##############

@app.route('/customer_index')
def index():
        return render_template('customer_index.html')

#Define route for login
@app.route('/customer_login')
def login():
	return render_template('customer_login.html')

#Define route for register
@app.route('/customer_register')
def register():
	return render_template('customer_register.html')

#Authenticates the login
@app.route('/customer_loginAuth', methods=['GET', 'POST'])
def loginAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM customer WHERE email = %s and password = %s'
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		return redirect(url_for('customer_home'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('customer_login.html', error=error)

#Authenticates the register
@app.route('/customer_registerAuth', methods=['GET', 'POST'])
def registerAuth():
        #grabs information from the forms
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        building_number = request.form['building number']
        street_address = request.form['street address']
        city = request.form['city']
        state = request.form['state']
        phone_number = request.form['phone number']
        passport_number = request.form['passport number']
        passport_expiration = request.form['passport expiration date']
        passport_country = request.form['passport country']
        DOB = request.form['date of birth'] 

        #cursor used to send queries
        cursor = conn.cursor()
        #executes query
        query = 'SELECT * FROM customer WHERE email = %s'
        cursor.execute(query, (email))
        #stores the results in a variable
        data = cursor.fetchone()
        #use fetchall() if you are expecting more than 1 data row
        error = None
        if(data):
                #If the previous query returns data, then user exists
                error = "This user already exists"
                return render_template('customer_register.html', error = error)
        else:
                ins = 'INSERT INTO customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                cursor.execute(ins, (name, email, password, building_number,
                                     street_address, city, state, phone_number,
                                     passport_number,passport_expiration, passport_country, DOB))
                conn.commit()
                cursor.close()
                return render_template('customer_index.html')

@app.route('/customer_home')
def customer_home():
        # creates a session for the customer with the username, and goes to template to
        # find out what the user wants to do 
        username = session['username']
        return render_template('customer_home.html', username=username) 


@app.route('/customer_view_flights', methods=['GET', 'POST'])
def view_flights():
        username = session['username']
        cursor = conn.cursor();
        query = 'SELECT flight_number, departure_date, departure_time FROM \
                customer,purchase,sold_for WHERE \
                ((departure_date > (SELECT CURDATE()) OR \
                (departure_date = (SELECT CURDATE()) AND \
                departure_time > (SELECT CURRENT_TIME()))) AND \
                (Email = %s) AND (customer.email = purchase.Customer_email)\
                AND (purchase.Ticket_id = sold_for.Ticket_id))'
        cursor.execute(query,(username))
        flights = cursor.fetchall()
        flight_info = []
        for f in flights:
                vals = []
                for key,val in f.items():
                     vals.append(val)
                flight_info.append(vals) 

        if (flights):
                return render_template('customer_display_flights.html',flights=flight_info, username = username)
        else:
                return render_template('customer_display_flights.html',flights=None, username=username) 
                
@app.route('/customer_rating', methods=['GET','POST'])
def rating():
        username = session['username']
        return render_template('customer_rating.html', username = username)


@app.route('/customer_give_rating', methods=['GET', 'POST'])
def give_rating():
        #make html file
        username = session['username']
        flight_number = request.form['flight number']
        rating = request.form['rating']
        comment = request.form['comment']
        #cursor used to send queries
        cursor = conn.cursor()
        #executes query
        query = 'SELECT flight_number,departure_date, departure_time, airline_name,customer_email\
                FROM customer,purchase,sold_for WHERE (email = %s AND flight_number = %s) \
                AND ((departure_date < (SELECT CURDATE()) OR \
                (departure_date = (SELECT CURDATE()) AND \
                departure_time < (SELECT CURRENT_TIME()))) \
                AND (customer.email = purchase.customer_email) AND (sold_for.ticket_id = purchase.ticket_id))'
        cursor.execute(query, (username,flight_number))
        #stores the results in a variable
        data = cursor.fetchone()
        #use fetchall() if you are expecting more than 1 data row
        error = None
        if (data):
                values = []
                for key,val in data.items():
                        values.append(val)
                ins = 'INSERT INTO rate VALUES(%s, %s, %s, %s, %s, %s, %s)'
                cursor.execute(ins, (values[0], values[1], values[2], values[3],
                                     values[4], rating, comment))
                conn.commit()
                cursor.close()
                return render_template('customer_rating.html', error = error) 
        else:
                error = "You cannot rate this flight."
                return render_template('customer_rating.html', error = error) 
        
@app.route('/customer_search_flights', methods=['GET','POST'])
def search():
        username = session['username']
        return render_template('customer_search_flights.html', username = username)

@app.route('/customer_search_flights_results', methods=['GET', 'POST'])
def results():
        username = session['username']
        d_city = request.form['departing city']
        a_city = request.form['destination city']
        date = request.form['date']

        cursor = conn.cursor()
        #executes query
        query1 = 'DROP VIEW IF EXISTS arrivals_view'
        query2 = 'DROP VIEW IF EXISTS departures_view'
        query3 = 'CREATE VIEW arrivals_view AS SELECT * FROM (flight NATURAL JOIN arrival NATURAL JOIN airport) \
                WHERE airport.city = %s'
        query4 = 'CREATE VIEW departures_view AS SELECT * FROM (flight NATURAL JOIN departure NATURAL JOIN airport)\
                WHERE airport.city = %s'
        cursor.execute(query1)
        cursor.execute(query2)
        cursor.execute(query3,(a_city))
        cursor.execute(query4,(d_city))
        
        
        query5 = 'SELECT d.flight_number, d.departure_date, d.departure_time, d.base_price, d.status, d.airline_name \
                FROM arrivals_view as a, departures_view as d WHERE (a.flight_number = d.flight_number\
                AND a.departure_date = d.departure_date AND a.departure_time = d.departure_time)\
                AND (d.departure_date = %s)'
        cursor.execute(query5,(date))
        #stores the results in a variable
        data = cursor.fetchall()
        flight_vals = []
        for elem in data:
                vals = []
                for key,val in elem.items():
                        vals.append(val)
                flight_vals.append(vals)
        #use fetchall() if you are expecting more than 1 data row
        error = None
        if (data):
                return render_template('customer_search_flights_results.html', flights = flight_vals, error=error)
        else:
                error = 'There are no flights matching your search parameters'
                return render_template('customer_search_flights_results.html', flights=None, error = error)

@app.route('/customer_search_flights_choice', methods=['GET','POST'])
def choice():
        username = session['username']
        return render_template('customer_search_flights_choice.html', username = username)

@app.route('/customer_search_flights_roundtrip', methods=['GET','POST'])
def roundtrip_search():
        username = session['username']
        return render_template('customer_search_flights_roundtrip.html', username = username)

@app.route('/customer_search_flights_results_roundtrip', methods=['GET', 'POST'])
def results_roundtrip():
        username = session['username']
        leaving_d_city = request.form['departing city']
        leaving_a_city = request.form['destination city']
        leaving_date = request.form['date']

        returning_d_city = request.form['returning departing city']
        returning_a_city = request.form['returning destination city']
        returning_date = request.form['returning date']

        cursor = conn.cursor()
        #executes query
        query1 = 'DROP VIEW IF EXISTS leaving_arrivals_view'
        query2 = 'DROP VIEW IF EXISTS leaving_departures_view'
        query3 = 'CREATE VIEW leaving_arrivals_view AS SELECT * FROM (flight NATURAL JOIN arrival NATURAL JOIN airport) \
                WHERE airport.city = %s'
        query4 = 'CREATE VIEW leaving_departures_view AS SELECT * FROM (flight NATURAL JOIN departure NATURAL JOIN airport)\
                WHERE airport.city = %s'
        cursor.execute(query1)
        cursor.execute(query2)
        cursor.execute(query3,(leaving_a_city))
        cursor.execute(query4,(leaving_d_city))

        query1b = 'DROP VIEW IF EXISTS returning_arrivals_view'
        query2b = 'DROP VIEW IF EXISTS returning_departures_view'
        query3b = 'CREATE VIEW returning_arrivals_view AS SELECT * FROM (flight NATURAL JOIN arrival NATURAL JOIN airport) \
                WHERE airport.city = %s'
        query4b = 'CREATE VIEW returning_departures_view AS SELECT * FROM (flight NATURAL JOIN departure NATURAL JOIN airport)\
                WHERE airport.city = %s'
        cursor.execute(query1b)
        cursor.execute(query2b)
        cursor.execute(query3b,(returning_a_city))
        cursor.execute(query4b,(returning_d_city))
        
        
        query5 = 'SELECT d.flight_number, d.departure_date, d.departure_time, d.base_price, d.status, d.airline_name \
                FROM arrivals_view as a, departures_view as d WHERE (a.flight_number = d.flight_number\
                AND a.departure_date = d.departure_date AND a.departure_time = d.departure_time)\
                AND (d.departure_date = %s)'
        cursor.execute(query5,(leaving_date))

        data = cursor.fetchall()
        leaving_flight_vals = []
        for elem in data:
                vals = []
                for key,val in elem.items():
                        vals.append(val)
                leaving_flight_vals.append(vals)

        query5b = 'SELECT d.flight_number, d.departure_date, d.departure_time, d.base_price, d.status, d.airline_name \
                FROM arrivals_view as a, departures_view as d WHERE (a.flight_number = d.flight_number\
                AND a.departure_date = d.departure_date AND a.departure_time = d.departure_time)\
                AND (d.departure_date = %s)'
        cursor.execute(query5b,(returning_date))
        
        #stores the results in a variable
        data1 = cursor.fetchall()
        returning_flight_vals = []
        for elem in data:
                print(str(elem['Flight_number']), str(elem['Departure_date']),
                                            str(elem['Departure_time']), str(elem['Airline_name']))
                vals = []
                sold_price = get_sold_price(str(elem['Flight_number']), str(elem['Departure_date']),
                                            str(elem['Departure_time']), str(elem['Airline_name']))
                for key,val in elem.items():
                        if key == 'Base_price':
                                vals.append(sold_price)
                        else:
                                vals.append(val)
                returning_flight_vals.append(vals)
        #use fetchall() if you are expecting more than 1 data row
        error = None
        if (data and data1):
                return render_template('customer_search_flights_results_roundtrip.html',
                                       leaving_flights = leaving_flight_vals,
                                       returning_flights = returning_flight_vals, error=error)
        else:
                error = 'There are no flights matching your search parameters'
                return render_template('public_search_flights_results_roundtrip.html',
                                       leaving_flights = None,
                                       returning_flights = None, error=error)
        

def get_sold_price(flight_number, departure_date, departure_time, airline_name):
        cursor = conn.cursor()
        query2 = 'SELECT base_price FROM Flight WHERE (flight_number = %s AND departure_date = %s \
                AND departure_time = %s AND airline_name = %s)'
        cursor.execute(query2, (flight_number, departure_date, departure_time, airline_name))
        base_price = cursor.fetchone()

        query2a = 'SELECT seats from Airplane, Uses WHERE (Airplane.ID = Uses.Airplane_id)\
                   AND (flight_number = %s and departure_date = %s \
                   and departure_time = CAST(%s as TIME) and airplane.airline_name = %s)'
        # number of seats on the plane
        cursor.execute(query2a, (flight_number, departure_date, departure_time, airline_name))
        num_of_seats = cursor.fetchone()

        query2ba = 'DROP VIEW IF EXISTS all_tickets_for_flight'
        query2bb = 'CREATE VIEW all_tickets_for_flight AS SELECT ticket_id \
                  FROM Sold_For WHERE (flight_number = %s and departure_date = %s \
                   and departure_time = CAST(%s as TIME) and airline_name = %s)'
        query2bc = 'SELECT COUNT(*) FROM all_tickets_for_flight, Purchase\
                    WHERE purchase.ticket_id = all_tickets_for_flight.ticket_id'
        cursor.execute(query2ba)
        cursor.execute(query2bb, (flight_number, departure_date, departure_time, airline_name))
        cursor.execute(query2bc)
        num_purchased = cursor.fetchone()

        print(num_purchased['COUNT(*)'],num_of_seats,base_price)

        if int(num_purchased['COUNT(*)']) / int(num_of_seats['seats']) >= 0.75:
                sold_price = float(base_price['base_price']) * 1.25
        else:
                sold_price = float(base_price['base_price'])
        sold_price = str(round(sold_price,2))
        return sold_price 

@app.route('/purchase_ticket', methods=['GET', 'POST'])
def purchase_ticket():
        email = session['username']
        flight_number = request.form['flight number']
        departure_date = request.form['departure date']
        departure_time = request.form['departure time']
        airline_name = request.form['airline name']

        card_type = request.form['card type']
        card_number = request.form['card number']
        name_on_card = request.form['name on card']
        card_expiration_date = request.form['card expiration date'] 

        #cursor used to send queries
        cursor = conn.cursor()
        #executes query
        #print(flight_number, departure_date, departure_time, airline_name)
        query1 = 'SELECT ticket_id FROM Sold_For as s WHERE (flight_number = %s AND departure_date = %s\
                AND departure_time = %s AND airline_name = %s) AND s.ticket_id NOT IN (SELECT p.ticket_id \
                FROM Purchase as p)'
        cursor.execute(query1, (flight_number, departure_date, departure_time, airline_name))
        #stores the results in a variable
        ticket_id = cursor.fetchone()
        #use fetchall() if you are expecting more than 1 data row

        sold_price = get_sold_price(flight_number, departure_date, departure_time, airline_name)
        
        query3 = 'SELECT CURDATE()'
        cursor.execute(query3)
        cur_date = cursor.fetchone()

        query4 = 'SELECT CURRENT_TIME()'
        cursor.execute(query4)
        cur_time = cursor.fetchone()

        
        error = None
        if(ticket_id):
                #If the previous query returns data, then user exists
                # show a success page
                ins = 'INSERT INTO purchase VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
                cursor.execute(ins, (ticket_id['ticket_id'], email, sold_price, card_type, card_number, name_on_card,
                                     card_expiration_date, cur_date['CURDATE()'], cur_time['CURRENT_TIME()']))
                return redirect(url_for('customer_home'))
                #return render_template('purchased_ticket', error=error)
        else:
                error = "There are no tickets for this flight"
                return render_template('customer_search_flights_results_roundtrip.html', error=error)


@app.route('/customer_spending', methods=['GET', 'POST'])
def spending():
        username = session['username']
        cursor = conn.cursor();
        query1 = 'SELECT EXTRACT(year FROM purchase_date) AS y, \
                  SUM(sold_price) as money_spent FROM Purchase\
                  WHERE purchase_date > DATE_SUB(CURDATE(), INTERVAL 1 year) AND customer_email = %s \
                  GROUP BY y'
        cursor.execute(query1, (username))
        year_spending = cursor.fetchone()

        year_spending_info = []
        for key,val in year_spending.items():
                year_spending_info.append(val)

        query2 = 'SELECT EXTRACT(month FROM purchase_date) AS m, \
                  SUM(sold_price) as montly_spending FROM Purchase\
                  WHERE purchase_date > DATE_SUB(CURDATE(), INTERVAL 6 month) AND customer_email = %s \
                  GROUP BY m'
        cursor.execute(query2, (username))
        month_spending = cursor.fetchall()

        month_spending_info = []
        for elem in month_spending:
                vals = []
                for key,val in elem.items():
                        vals.append(val)
                month_spending_info.append(vals)

        return render_template('customer_spending_default.html', year_info = year_spending_info,
                               month_info = month_spending_info)
        
@app.route('/customer_spending_interval', methods=['GET', 'POST'])
def interval():
        username = session['username']
        cursor = conn.cursor();
        beginning_date = request.form['beginning date']
        end_date = request.form['end date']

        query1 = 'SELECT SUM(sold_price) as money_spent FROM Purchase \
                  WHERE purchase_date > %s AND purchase_date < %s \
                  AND customer_email = %s'
        cursor.execute(query1, (beginning_date, end_date, username))
        year_spending = cursor.fetchone()

        year_spending_info = []
        for key,val in year_spending.items():
                year_spending_info.append(val)

        query2 = 'SELECT EXTRACT(month FROM purchase_date) AS m, \
                 SUM(sold_price) as montly_spending FROM Purchase\
                 WHERE purchase_date >= %s AND purchase_date <= %s AND customer_email = %s \
                 GROUP BY m'
        cursor.execute(query2,(beginning_date, end_date, username))
        month_spending = cursor.fetchall()

        month_spending_info = []
        for elem in month_spending:
                vals = []
                for key,val in elem.items():
                        vals.append(val)
                month_spending_info.append(vals)

        error = None
        if (year_spending_info != [None]):
                return render_template('customer_spending_interval.html', year_info = year_spending_info,
                               month_info = month_spending_info)
        else:
                error='You did not spend any money in this date range.'
                return render_template('customer_spending_interval.html', error=error)
                

@app.route('/customer_logout', methods=['GET','POST'])
def logout():
	session.pop('username')
	return redirect('/')

######################### CUSTOMER (ARIEL) PARTS END ##############



######################### STAFF (ALISHA) PARTS BEGIN ##############

@app.route('/staff_index')
def s_index():
        return render_template('staff_index.html')

#Define route for login
@app.route('/staff_login')
def s_login():
	return render_template('staff_login.html')

#Define route for register
@app.route('/staff_register')
def s_register():
	return render_template('staff_register.html')

#Authenticates the login
@app.route('/staff_loginAuth', methods=['GET', 'POST'])
def s_loginAuth():							#makes sure user can log in
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM Staff WHERE username = %s and password = %s' #selects username and password from database with values entered 
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		return redirect(url_for('s_home'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('staff_login.html', error=error)

#Authenticates the register
@app.route('/staff_registerAuth', methods=['GET', 'POST'])
def s_registerAuth():	
	#grabs information from the forms
	first_name = request.form['first_name']
	last_name = request.form['last_name']
	username = request.form['email']
	password = request.form['password']
	DOB = request.form['DOB']
	airline = request.form['airline_name']
	phone_number = request.form['phone_num']
	

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM staff WHERE username = %s'
	cursor.execute(query, (username))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('staff_register.html', error = error)
	else:
		ins = 'INSERT INTO staff (date_of_birth, first_name, last_name, password, username ) VALUES(%s,%s, %s, %s, %s)'
		cursor.execute(ins, (DOB, first_name, last_name, password, username))
		ins1 = 'INSERT INTO Works_for (staff_username, airline_name) VALUES(%s,%s)'
		cursor.execute(ins1, (username, airline))
		ins2 = 'INSERT INTO Phone_Number (staff_username, phone_number) VALUES (%s,%s)'
		cursor.execute(ins2, (username, phone_number))
		conn.commit()
		cursor.close()
		return render_template('staff_index.html')

@app.route('/staff_home')
def s_home():
    username = session['username']
    cursor = conn.cursor();
    cursor.close()
    return render_template('staff_home.html', username=username)

@app.route('/staff_logout')
def s_logout():
	session.pop('username')
	return redirect('/')

@app.route('/staff_viewflights')
def s_viewflights():
	cursor = conn.cursor();
	username = session['username']
	query = 'SELECT * from Flight f natural join Works_For j where j.staff_username = %s and f.Airline_name = j.airline_name and (f.departure_date > (SELECT CURDATE()) AND f.departure_date < (SELECT CURDATE()+ 30)) OR (f.departure_date = (SELECT CURDATE())) and f.departure_time > (SELECT CURRENT_TIME())'
	cursor.execute(query,username)
	data = cursor.fetchall()
	if(data):
		return render_template("staff_viewflights.html", data = data)
	else:
		error = 'There are no flights you can view'
		conn.commit()
		cursor.close()
		return render_template ('staff_viewflights.html', error=error)


@app.route('/staff_searchflights_dates')
def s_searchflights_dates():
	return render_template('staff_searchflights_dates.html')

@app.route('/staff_find_flights_range', methods=['GET', 'POST'])
def s_find_flights_range():
	#grabs information from the forms
	username = session['username']
	start_date = request.form['startdate']
	end_date = request.form['enddate']
	cursor = conn.cursor();
	query = 'SELECT * from Flight f natural join works_for j where f.departure_date > %s and f.departure_date < %s and j.staff_username = %s and f.Airline_name = j.airline_name' #double check that this query is completely correct! (check edge cases)
	cursor.execute(query,(start_date, end_date,username))
	data = cursor.fetchall()
	if(data):
		return render_template("staff_viewflights.html", data = data)
	else:
	#	returns an error message to the html page
		error = 'there was an error'
		conn.commit()
		cursor.close()
		return render_template ('staff_searchflights_dates.html', error=error)

@app.route('/staff_customers_on_flights')
def s_customers_on_flights():
	return render_template('staff_customers_on_flights.html')	

@app.route('/staff_customers_on_flights_Auth', methods=['GET', 'POST'])
def s_customers_on_flights_Auth():
	username = session['username']
	flight_number = request.form['flight_number']
	cursor = conn.cursor();
	query = 'SELECT  flight_number, customer_email from Purchase p natural join sold_for s where p.ticket_id = s.ticket_id and s.Flight_number = %s'
	cursor.execute(query,(flight_number))
	data = cursor.fetchall()
	if(data):
		return render_template("staff_customers_on_flights.html", data = data)
	else:
		error = 'there was an error'
		conn.commit()
		cursor.close()
		return render_template ('staff_searchflights_dates.html', error=error)	

@app.route('/staff_searchflights_route')
def search_flights_route():
	return render_template('staff_searchflights_route.html')	

@app.route('/staff_searchflights_route_Auth_citySource', methods=['GET', 'POST'])
def search_flights_route_Auth_citySource():
	username = session['username']
	city_name= request.form['city_name']
	cursor = conn.cursor();
	query = 'Select flight_number from departure d natural join Airport a where d.Airport_code = a.Airport_code and a.City = %s' #did not test query with actual values in database
	cursor.execute(query,(city_name))
	data = cursor.fetchall()
	if(data):
		return render_template("staff_searchflights_route.html", data = data)#
	else:
		error = 'there was an error'#
		conn.commit()
		cursor.close()
		return render_template ('staff_searchflights_dates.html')# error=error)	

#
@app.route('/staff_searchflights_route_Auth_airportSource', methods=['GET', 'POST'])
def search_flights_route_Auth_airportSource():#
	username = session['username']
	airport_name= request.form['airport_name']
	cursor = conn.cursor();
	query = 'Select flight_number from departure d natural join Airport a where d.Airport_code = a.Airport_code and a.Name = %s' #did not test query with actual values in database
	cursor.execute(query,(airport_name))
	data = cursor.fetchall()
	if(data):
		return render_template("staff_searchflights_route.html", data = data)#
	else:
		error = 'there was an error'#
		conn.commit()
		cursor.close()
		return render_template ('staff_viewflights.html')# error=error)	

#@app.route('/searchflights_route_Auth_cityDestination', methods=['GET', 'POST'])
#def search_flights_route_Auth_cityDestination():##
	#username = session['username']
	#city_name= request.form['city_name']
	#cursor = conn.cursor();
	#query = 'Select flight_number from arrival d natural join Airport a where d.Airport_code = a.Airport_code and a.City = %s' #did not test query with actual values in database
	#cursor.execute(query,(city_name))
	#data = cursor.fetchall()
	#if(data):
	#	return render_template("searchflights_route.html", data = data)##
	#else:
#		error = 'there was an error'##
	#	conn.commit()#
	#	cursor.close()
#		return render_template ('login.html')# error=error)	
#
@app.route('/staff_searchflights_route_Auth_airportDestination', methods=['GET', 'POST'])
def search_flights_route_Auth_airportDestination():#
	username = session['username']
	airport_name= request.form['airport_name']
	cursor = conn.cursor();
	query = 'Select flight_number from arrival d natural join Airport a where d.Airport_code = a.Airport_code and a.Name = %s' #did not test query with actual values in database
	cursor.execute(query,(airport_name))
	data = cursor.fetchall()
	if(data):
		return render_template("staff_searchflights_route.html", data = data)##
	else:
		error = 'there was an error'#
		conn.commit()#
		cursor.close()
		return render_template ('staff_register.html')# error=error)	

@app.route('/staff_createflights', methods=['GET', 'POST'])
def createflights():
	return render_template("staff_createflights.html")#

@app.route('/staff_createflights_Auth', methods=['GET', 'POST'])
def createflights_Auth():
        flight_number = request.form['flight_number']
        departure_date =  request.form['departure_date']
        departure_time =  request.form['departure_time']
        base_price =  request.form['base_price']
        status =  request.form['status']
        airline_name =  request.form['airline_name']
        arrival_date = request.form['arrival_date']
        arrival_time = request.form['arrival_time']
        airplane_id = request.form['airplane_id']
        d_airport_code = request.form['d_airport_code']
        a_airport_code = request.form['a_airport_code']
        cursor = conn.cursor();
        query = 'Insert INTO Flight (flight_number, departure_date, departure_time, base_price, status, airline_name) values (%s, %s, %s, %s, %s, %s)'
        cursor.execute(query,(flight_number, departure_date, departure_time, base_price, status, airline_name))
        query1 = 'INSERT INTO Arrival (airport_code, flight_number, departure_date, departure_time,airline_name, arrival_date, arrival_time) values (%s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(query1,(a_airport_code, flight_number, departure_date, departure_time, airline_name, arrival_date, arrival_time))
        query2 = 'INSERT INTO Departure (airport_code, flight_number, departure_date, departure_time,airline_name) values (%s, %s, %s, %s, %s)'
        cursor.execute(query2,(d_airport_code, flight_number, departure_date, departure_time, airline_name))
        query3 = 'INSERT INTO Uses (flight_number, departure_date, departure_time, airline_name, airplane_id) values (%s, %s, %s, %s, %s)'
        cursor.execute(query3,(flight_number, departure_date, departure_time, airline_name, airplane_id))
        conn.commit()
        cursor.close()
        return render_template("staff_createflights.html")

@app.route('/staff_changestatus', methods=['GET', 'POST'])
def changestatus():
	return render_template("staff_changestatus.html")#

@app.route('/staff_changestatus_Auth', methods=['GET', 'POST'])
def changestatus_Auth():
	flight_number = request.form['flight_number']
	status =  request.form['status']
	cursor = conn.cursor();
	query = 'Update Flight SET status = %s WHERE flight_number = %s'
	cursor.execute(query,(status, flight_number))
	conn.commit()#
	cursor.close()
	return render_template("staff_changestatus.html")#

@app.route('/staff_addairplane', methods=['GET', 'POST'])
def addairplane():
	return render_template("staff_addairplane.html")#

@app.route('/staff_addairplane_Auth', methods=['GET', 'POST'])
def addairplane_auth():
	airline_name = request.form['airline_name']
	airplane_id =  request.form['airplane_id']
	number_of_seats =  request.form['number_of_seats']
	cursor = conn.cursor();
	query = 'Insert INTO Airplane (airline_name, ID, seats) values (%s, %s,%s)'
	cursor.execute(query,(airline_name, airplane_id,number_of_seats))
	conn.commit()#
	cursor.close()
	return render_template("staff_addairplane.html")##
	
@app.route('/staff_addairport', methods=['GET', 'POST'])
def addairport():
	return render_template("staff_addairport.html")

@app.route('/staff_addairport_Auth', methods=['GET', 'POST'])
def addairport_auth():
	airport_name = request.form['airport_name']
	airport_city =  request.form['airport_city']
	airport_code =  request.form['airport_code']
	cursor = conn.cursor();
	query = 'Insert INTO Airport (Airport_code, City, Name) values (%s, %s,%s)'
	cursor.execute(query,(airport_code,airport_city, airport_name))
	conn.commit()
	cursor.close()
	return render_template("staff_addairport.html")##

@app.route('/staff_view_flight_ratings', methods=['GET', 'POST'])
def view_flight_ratings():
	return render_template("staff_view_flight_ratings.html")

@app.route('/staff_view_flight_ratings_Auth', methods=['GET', 'POST'])
def view_flight_ratings_auth():
        total = 0
        avg = 0
        counter = 0
        flight_number = request.form['flight_number']
        cursor = conn.cursor();
        query = 'Select customer_email, comment, rating from Rate where flight_number = %s'
        cursor.execute(query,(flight_number))
        data = cursor.fetchall()
        if (data):
                for index in (data):
                        total += (index["rating"])
                        counter+=1
                        
        if counter != 0: 
                avg = total/counter
        else:
                avg= -1

        if avg != -1:    
                return render_template("staff_view_flight_ratings.html", data = data, avg = avg )#, data = total)
        else:
                error = 'There were no ratings for this flight.'
                return render_template("staff_view_flight_ratings.html", error=error )

	
@app.route('/staff_view_frequent_customer', methods=['GET', 'POST'])
def view_frequent_customer():
	#customer_email = request.form['customer_email']
	cursor = conn.cursor();
	query = 'Select customer_email FROM Purchase where purchase_date between DATE_SUB( CURDATE( ) ,INTERVAL 1 YEAR ) AND CURDATE( ) GROUP BY customer_email ORDER BY COUNT(*) DESC LIMIT 1'
	cursor.execute(query)
	most_frequent_customer_tuple = cursor.fetchone()
	if (most_frequent_customer_tuple):
			customer_email = (most_frequent_customer_tuple["customer_email"])
			return render_template("staff_view_frequent_customer.html", most_frequent_customer = customer_email)
	else:
		return render_template("staff_home.html", most_frequent_customer = customer_email)


@app.route('/staff_view_frequent_customer_Auth', methods=['GET', 'POST'])
def view_frequent_customer_Auth():#
	customer_email = request.form['customer_email']
	username = session['username']
	cursor = conn.cursor();
	query = 'Select flight_number from works_for wf natural join purchase p natural join sold_for sf where wf.staff_username = %s and p.Customer_email = %s and p.Ticket_id = sf.Ticket_id'
	cursor.execute(query,(username, customer_email))
	data = cursor.fetchall()
	flights = []
	for elem in data:
                vals = []
                for key,val in elem.items():
                       vals.append(val)
                flights.append(vals)
	return render_template("staff_flights_for_customer.html",customer= customer_email, data = flights)#, data = data)#, data = total)

@app.route('/staff_view_reports', methods=['GET', 'POST'])
def view_reports():
	return render_template("staff_view_reports.html")

@app.route('/staff_view_reports_Auth', methods=['GET', 'POST'])
def view_reports_Auth():#
	start_date = request.form['start_date']
	end_date = request.form['end_date']
	cursor = conn.cursor();
	query = 'SELECT count(*) ticket_id from Purchase where purchase_date > %s and purchase_date < %s' 
	cursor.execute(query,(start_date, end_date))
	data = cursor.fetchall()
	ticket_yr_total = data[0]["ticket_id"]
	#query_january = 'SELECT count(Ticket_id) from Purchase where MONTH(purchase_date) =12 '
	#cursor.execute(query_january)
	data = cursor.fetchone()
	
	return render_template("staff_view_reports.html", data= ticket_yr_total)#, data = data)#, data = total)

##@app.route('/staff_view_reports_Auth', methods=['GET', 'POST'])
##def view_reports_Auth():#
##	start_date = request.form['start_date']
##	end_date = request.form['end_date']
##	cursor = conn.cursor();
##	query = 'SELECT count(*) ticket_id from Purchase where purchase_date > %s and purchase_date < %s' 
##	cursor.execute(query,(start_date, end_date))
##	data = cursor.fetchall()
##	ticket_yr_total = data[0]["ticket_id"]
##	monthly_ticket_sales='SELECT EXTRACT(month FROM purchase_date) AS month, count(ticket_id) FROM purchase group by month'
##	cursor.execute(monthly_ticket_sales)
##	data2 = cursor.fetchall()
##	month_sales = []
##	vals=[]
##	counter = 0
##	for elem in data2:
##			vals.append(elem["month"])
##			month_sales.append(elem["count(ticket_id)"])
##			counter+=1
##	#query_january = 'SELECT count(Ticket_id) from Purchase where MONTH(purchase_date) =12 '
##	#cursor.execute(query_january)
##	data = cursor.fetchone()
##	
##	return render_template("staff_view_reports.html", data= ticket_yr_total, vals= vals, month_sales = month_sales, counter = counter)#, data = data)#, data = total)

@app.route('/staff_view_earned_revenue', methods=['GET', 'POST'])
def view_earned_revenue():
	cursor = conn.cursor();
	year_revenue = 'select sum(sold_price) from purchase where purchase_date between DATE_SUB( CURDATE( ) ,INTERVAL 1 YEAR ) AND CURDATE( ) '
	cursor.execute(year_revenue)
	revenue_in_last_year = cursor.fetchone()['sum(sold_price)']
	month_revenue = 'select sum(sold_price) from purchase where purchase_date between DATE_SUB( CURDATE( ) ,INTERVAL 1 MONTH ) AND CURDATE( )'
	cursor.execute(month_revenue)
	revenue_in_last_month = cursor.fetchone()['sum(sold_price)']
	return render_template("staff_view_earned_revenue.html", revenue_in_last_year = revenue_in_last_year, revenue_in_last_month= revenue_in_last_month)#, data = data)#, data = total)

@app.route('/staff_view_top_destinations', methods=['GET', 'POST'])
def view_top_destinations():
	cursor = conn.cursor();
	query_1_year = 'SELECT city, COUNT(city) AS `value_occurrence` FROM airport a natural join purchase p natural join Sold_For sf natural join flight f where purchase_date between DATE_SUB( CURDATE( ) ,INTERVAL 1 year ) AND CURDATE( ) and sf.Ticket_id = p.Ticket_id GROUP BY city ORDER BY `value_occurrence` DESC LIMIT 3'
	cursor.execute(query_1_year)
	data_1_year = cursor.fetchall()
	one_year_vals = []
	for elem in data_1_year:
                vals = []
                for key,val in elem.items():
                        vals.append(val)
                one_year_vals.append(vals)

	query_3_months = 'SELECT city, COUNT(city) AS `value_occurrence` FROM airport a natural join purchase p natural join Sold_For sf natural join flight f where purchase_date between DATE_SUB( CURDATE( ) ,INTERVAL 3 month ) AND CURDATE( ) and sf.Ticket_id = p.Ticket_id GROUP BY city ORDER BY `value_occurrence` DESC LIMIT 3'
	cursor.execute(query_3_months)
	data_3_months = cursor.fetchall()
	three_month_vals = []
	for elem in data_3_months:
                vals = []
                for key,val in elem.items():
                        vals.append(val)
                three_month_vals.append(vals) 
	return render_template ("staff_view_top_destinations.html", data_3_months = one_year_vals, data_1_year = three_month_vals)


############################### PUBLIC USER

@app.route('/public_home')
def p_index():
        return render_template('public_home.html')

@app.route('/public_search_flight', methods = ['GET', 'POST'])
def p_search_flight():
        return render_template('public_search.html')

@app.route('/public_flightstatus', methods = ['GET', 'POST'])
def p_search():
    if request.method == 'POST':
        # Fetch form data
        checkDetails = request.form
        airlineName = checkDetails['airlineName'] or None
        fNumber = checkDetails['fNumber'] or None
        arrdepdate = checkDetails['arrdepdate'] or None
        cur = conn.cursor()
        query = 'SELECT flight.Status \
                 FROM flight \
                 JOIN arrival \
                 ON arrival.Flight_number = flight.Flight_number \
                 AND arrival.Departure_time = flight.Departure_time \
                 AND arrival.Airline_name = flight.Airline_name \
                 WHERE flight.Airline_name = %s \
                 AND flight.Flight_number = %s \
                 AND (flight.Departure_date = %s OR \
                 arrival.Arrival_date = %s)'
        result = cur.execute(query, (airlineName, fNumber, arrdepdate, arrdepdate))
        statusData = cur.fetchone() or 'error: no flight found'
        return render_template('public_flightstatus.html', statusData = statusData)
    return render_template('public_search.html')

@app.route('/public_search_flights', methods=['GET','POST'])
def public_search():
        return render_template('public_search_flights.html')

@app.route('/public_search_flights_results', methods=['GET', 'POST'])
def p_results():
        d_city = request.form['departing city']
        a_city = request.form['destination city']
        date = request.form['date']

        cursor = conn.cursor()
        #executes query
        query1 = 'DROP VIEW IF EXISTS arrivals_view'
        query2 = 'DROP VIEW IF EXISTS departures_view'
        query3 = 'CREATE VIEW arrivals_view AS SELECT * FROM (flight NATURAL JOIN arrival NATURAL JOIN airport) \
                WHERE airport.city = %s'
        query4 = 'CREATE VIEW departures_view AS SELECT * FROM (flight NATURAL JOIN departure NATURAL JOIN airport)\
                WHERE airport.city = %s'
        cursor.execute(query1)
        cursor.execute(query2)
        cursor.execute(query3,(a_city))
        cursor.execute(query4,(d_city))
        
        
        query5 = 'SELECT d.flight_number, d.departure_date, d.departure_time, d.base_price, d.status, d.airline_name \
                FROM arrivals_view as a, departures_view as d WHERE (a.flight_number = d.flight_number\
                AND a.departure_date = d.departure_date AND a.departure_time = d.departure_time)\
                AND (d.departure_date = %s)'
        cursor.execute(query5,(date))
        #stores the results in a variable
        data = cursor.fetchall()
        flight_vals = []
        for elem in data:
                vals = []
                for key,val in elem.items():
                        vals.append(val)
                flight_vals.append(vals)
        #use fetchall() if you are expecting more than 1 data row
        error = None
        if (data):
                return render_template('public_search_flights_results.html', flights = flight_vals, error=error)
        else:
                error = 'There are no flights matching your search parameters'
                return render_template('public_search_flights_results.html', flights=None, error = error)

@app.route('/public_search_flights_choice', methods=['GET','POST'])
def p_choice():
        return render_template('public_search_flights_choice.html')

@app.route('/public_search_flights_roundtrip', methods=['GET','POST'])
def p_roundtrip_search():
        return render_template('public_search_flights_roundtrip.html')

@app.route('/public_search_flights_results_roundtrip', methods=['GET', 'POST'])
def p_results_roundtrip():
        leaving_d_city = request.form['departing city']
        leaving_a_city = request.form['destination city']
        leaving_date = request.form['date']

        returning_d_city = request.form['returning departing city']
        returning_a_city = request.form['returning destination city']
        returning_date = request.form['returning date']

        cursor = conn.cursor()
        #executes query
        query1 = 'DROP VIEW IF EXISTS leaving_arrivals_view'
        query2 = 'DROP VIEW IF EXISTS leaving_departures_view'
        query3 = 'CREATE VIEW leaving_arrivals_view AS SELECT * FROM (flight NATURAL JOIN arrival NATURAL JOIN airport) \
                WHERE airport.city = %s'
        query4 = 'CREATE VIEW leaving_departures_view AS SELECT * FROM (flight NATURAL JOIN departure NATURAL JOIN airport)\
                WHERE airport.city = %s'
        cursor.execute(query1)
        cursor.execute(query2)
        cursor.execute(query3,(leaving_a_city))
        cursor.execute(query4,(leaving_d_city))

        query1b = 'DROP VIEW IF EXISTS returning_arrivals_view'
        query2b = 'DROP VIEW IF EXISTS returning_departures_view'
        query3b = 'CREATE VIEW returning_arrivals_view AS SELECT * FROM (flight NATURAL JOIN arrival NATURAL JOIN airport) \
                WHERE airport.city = %s'
        query4b = 'CREATE VIEW returning_departures_view AS SELECT * FROM (flight NATURAL JOIN departure NATURAL JOIN airport)\
                WHERE airport.city = %s'
        cursor.execute(query1b)
        cursor.execute(query2b)
        cursor.execute(query3b,(returning_a_city))
        cursor.execute(query4b,(returning_d_city))
        
        
        query5 = 'SELECT d.flight_number, d.departure_date, d.departure_time, d.base_price, d.status, d.airline_name \
                FROM arrivals_view as a, departures_view as d WHERE (a.flight_number = d.flight_number\
                AND a.departure_date = d.departure_date AND a.departure_time = d.departure_time)\
                AND (d.departure_date = %s)'
        cursor.execute(query5,(leaving_date))

        data = cursor.fetchall()
        leaving_flight_vals = []
        for elem in data:
                vals = []
                for key,val in elem.items():
                        vals.append(val)
                leaving_flight_vals.append(vals)

        query5b = 'SELECT d.flight_number, d.departure_date, d.departure_time, d.base_price, d.status, d.airline_name \
                FROM arrivals_view as a, departures_view as d WHERE (a.flight_number = d.flight_number\
                AND a.departure_date = d.departure_date AND a.departure_time = d.departure_time)\
                AND (d.departure_date = %s)'
        cursor.execute(query5b,(returning_date))
        
        #stores the results in a variable
        data1 = cursor.fetchall()
        returning_flight_vals = []
        for elem in data:
                vals = []
                sold_price = get_sold_price(str(elem['Flight_number']), str(elem['Departure_date']),
                                            str(elem['Departure_time']), str(elem['Airline_name']))
                for key,val in elem.items():
                        if key == 'Base_price':
                                vals.append(sold_price)
                        else:
                                vals.append(val)
                returning_flight_vals.append(vals)
        #use fetchall() if you are expecting more than 1 data row
        error = None
        if (data and data1):
                return render_template('public_search_flights_results_roundtrip.html',
                                       leaving_flights = leaving_flight_vals,
                                       returning_flights = returning_flight_vals, error=error)
        else:
                error = 'There are no flights matching your search parameters'
                return render_template('public_search_flights_results_roundtrip.html',
                                       leaving_flights = None,
                                       returning_flights = None, error=error)
		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
