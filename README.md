## Airport API System

## Overview
This project is a Django based web application using the Django REST framework 
designed to manage airport operations including users, aircraft, crew, 
airports, routes, flights, bookings and tickets.   

## Features
- **User Management**: Custom user model using email as the username.
- **Airplane Management**: Manage airplane types, airplanes, and their details.
- **Crew Management**: Manage crew members and their roles.
- **Airport Management**: Manage airport details including location and code 
validation. It also provides current weather at each airport 
(use [weatherapi.com](https://www.weatherapi.com/)).
- **Route Management**: Define routes between airports and calculate distances 
(use geopy module).
- **Flight Management**: Manage flight details, schedules, and assign crews.
- **Order Management**: Handle orders and ticket bookings.
- **Ticket Management**: Validate and manage ticket bookings for flights. 
- **JSON Web Tokens**: JSON Web Tokens are used to authenticate users. 

## Project Structure

- **User**: Custom user model and views for user management.
- **Airplane**: Models and views to manage airplanes.
- **Crew**: Models and views to manage crew members.
- **Airport**: Models and views to manage airport details.
- **Route**: Models to define routes between airports.
- **Flight**: Models and views to manage flight details.
- **Order**: Models and views to manage orders.
- **Ticket**: Models and views to manage ticket bookings.
  

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/AlexGrytsai/AirportAPI
    cd https://github.com/AlexGrytsai/AirportAPI
    ```
2. **Environment Variables:**
		Ensure you have a `.env` file in the root directory with the following variables:
		
	```env
	WEATHER_KEY=<WEATHERAPI_API_KEY>
	POSTGRES_PASSWORD=airport
	POSTGRES_USER=airport
	POSTGRES_DB=airport
	POSTGRES_HOST=db
	POSTGRES_PORT=5432
	```
	If you want to use weather information, you must register with 
[Weatherapi.com](https://www.weatherapi.com/) and use your API KEY.
		
3. **Build and start the application using Docker:**
    ```sh
    docker-compose up
    ```
4. **Loading data into a database (examples):**
	Open a new terminal and enter the command:
	```sh
    docker exec -it airportapi-app-1 /bin/sh
    python manage.py loaddata airports_exemple_for_db_data.json
    python manage.py loaddata data_exemple_for_db.json
    ```
5. **Create a superuser:**
	```sh
    python manage.py createsuperuser
    ```
    After created Super User, exit from container using the following command:
    ```sh
    exit
    ```
    
6. **Access the application:**
    
    Open your web browser and navigate to [http://localhost:8000](http://localhost:8000) 
or [http://127.0.0.1:8000](http://127.0.0.1:8000).
	You need to get access token for use app - [get token](http://127.0.0.1:8000/api/v1/token/).
	For use an access token, you can use [ModHeader - Modify HTTP headers](https://chromewebstore.google.com/detail/modheader-modify-http-hea/idgpnmonknjnojddfkpgkljpfnnfcklj?pli=1) 
for Chrome. After installing it, you need added Authorization with "Bearer <your_access_token>".
	Now, you can use all application's feathers.
	
7. **Access the application's documentation:**
    
    You can familiarize yourself with all the documentation and methods of 
using the Airport API System by clicking on the link: [swagger](http://localhost:8000/api/v1/doc/swagger/) or [redoc](http://127.0.0.1:8000/api/v1/doc/redoc/).