"""Main module"""
from fastapi import FastAPI, Query, status, HTTPException, Depends,Header
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import func
from haversine import haversine
from passlib.hash import bcrypt
import jwt
from models import CountryModel, CityModel, User
from db_utils import get_db
from user_pydantic_models import PyUser
from validators import username_validator, password_validator,\
    country_set_validator, country_validator
from logging_setup import log
import os
from dotenv import load_dotenv
import uvicorn
load_dotenv()


JWT_SECRET = os.getenv("JWT_KEY")
ALGORITHM = os.getenv("ALGORITHM")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/login')

app = FastAPI()





@app.get("/")
def root():
    """
    Root endpoint function
    """
    return {"Message": "Welcome"}


@app.post("/api/users/sign_up")
def create_new_user(user: PyUser, db: Session = Depends(get_db)):
    """
    Function used for registering new user.
    Input: allowed only alphanumeric characters
    and special characters (_ and -).
    Output: funtions returns json with new user's token
    """

    # search user table for existing username
    existing_user = db.query(User).filter_by(
        username = user.username).one_or_none()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail="USER_ALREADY_EXISTS")

    try:
        # create new user
        new_user = User(username=user.username,
                             password=bcrypt.hash(user.password))
        db.add(new_user)
        db.commit()

        log.info(f"New user created. Username {user.username}")

        # create a new user token
        user_dict = {"username": new_user.username,
                     "password": new_user.password}

        token = jwt.encode(user_dict, JWT_SECRET)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="ERROR_WHILE_CREATING_USER")

    return {"access_token": token, "token_type": "bearer"}



@app.post("/api/users/login")
def login(user:PyUser,
        # form_data: OAuth2PasswordRequestForm = Depends(PyUser),

          db: Session = Depends(get_db)):
    """
    Function used for user login.
    Input: user provides username and password
    Output: if user exists, function returns json with user's token
    """


    # find user based on input username value
    db_user = db.query(User).filter_by(
        username=user.username).one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="USER_NOT_FOUND")

    # Verify input password
    try:
        bcrypt.verify(user.password, db_user.password)
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="password doesn't match")

    # create a new user token
    user_dict = {"username": db_user.username,
                 "password": db_user.password}
    token = jwt.encode(user_dict, JWT_SECRET)
    return {"access_token": token, "token_type": "bearer"}


def check_token(token:str, db):
    try:
        print(token)
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])

        db_user = db.query(User).filter_by(
            username=decoded_token["username"], password=decoded_token["password"]).one_or_none()
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="USER_NOT_FOUND")

    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")



def get_database_dependency(db: Session = Depends(get_db)):
    return db

def get_token_dependency(token: str = Header(..., name="Authorization", alias="Authorization")):
    if not token:
        raise HTTPException(status_code=401, detail="Invalid token format")
    return {"token": token}

def get_auth_dependencies(token_data: dict = Depends(get_token_dependency), db: Session = Depends(get_database_dependency)):
    token = token_data["token"]
    check_token(token=token, db=db)
    return {"token": token, "db": db}

@app.get("/protected")
async def protected_route(auth: dict = Depends(get_auth_dependencies)):
    db  = auth["db"]
    return {"success":"yeah"}
#
# @app.get("/api/list_countries/")
# def list_of_countries(offset_val: int = Query(None, description="please enter offset value"),
#                       limit_val: int = Query(None, description="Please enter limit value"),db: Session = Depends(get_db)):
#     """
#     api that provides user with json formated list of countries
#     based on input limit and offset values.
#     Input: limit and offset values used for pagination purpose
#     Output: json formatted list of countries
#     """
#     if isinstance(offset_val, int) and isinstance(limit_val, int):
#         try:
#             # create country query object based on limit and offset  values
#             countries_list = db.query(CountryModel).offset(
#                 offset_val).limit(limit_val).all()
#
#             # create output dictionary
#             dict_countries = {}
#             for country in countries_list:
#                 dict_countries[country.id] = country.country_name
#
#             return dict_countries
#
#         except Exception as exc:
#             log.debug("Error", exc)
#             return {"Error": exc}
#     else:
#         log.debug("User provides values that are not numeric")
#         raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#                             detail="limit and offset values must be numeric values")
#
#
# @app.get("/api/find_country_by_city_name")
# def find_country_by_city_name(city: str = Query(None, description="Please enter city name"), db: Session = Depends(get_db)):
#     """
#     Function returns country name based od city name input value
#     Input: city name, allows only alphabetic characters
#     Query is case insensitive
#     Output: returns json formatted city and country data
#     """
#     if city.isalpha():
#         city_data = db.query(CityModel).filter(
#             func.lower(CityModel.city_ascii_name) ==
#             func.lower(city)).first()
#         if city_data is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND, detail="city not found")
#         return {f"City name: {city}":
#                 f"Country name: {city_data.parent.country_name}"}
#     else:
#         log.debug(f"Incorrect input values")
#         raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#                             detail="only alphabetic characters allowed")
#
#
# @app.get("/api/list_cities/")
# def list_of_cities(offset_val: int = Query(None, description="Please enter offset value"),
#                    limit_val: int = Query(None, description="Please enter limit value"),db: Session = Depends(get_db)):
#     """
#     Function provides user with json formated list of cities
#     based on input limit and offset values.
#     Input: limit and offset values used for pagination purposes
#     Output: json formatted list of cities
#     """
#     if isinstance(offset_val, int) and isinstance(limit_val, int):
#         try:
#             cities_list = db.query(CityModel).offset(
#                 offset_val).limit(limit_val)
#             dict_cities = {}
#             for city in cities_list:
#                 dict_cities[city.id] = city.city_ascii_name
#             return dict_cities
#
#         except Exception as exc:
#             log.debug("Error", exc)
#             return {"Error": exc}
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail="Numerical values accepted")
#
#
# @app.get("/api/list_cities_by_population/")
# def list_cities_by_population(min: int = Query(None,
#                                                description="Please enter minimum value"),
#                               max: int = Query(None,
#                                                description="Please enter maximum value"),db: Session = Depends(get_db)):
#     """
#     Function calculates and returns a dictionary with cities
#     with population between min and max values.
#     Input: min and max population
#     Output: returns sa json formatted with city names and their population
#     """
#     if isinstance(min, int) and isinstance(max, int):
#         try:
#             search_cities = db.query(CityModel).filter(
#                 CityModel.population > min).filter(CityModel.population < max)
#             city_dict = {}
#             for city in search_cities:
#                 city_dict[f"City name: {city.city_ascii_name}"] = \
#                     f"Population: {city.population}"
#             return city_dict
#         except Exception as exc:
#             log.debug(f"Error, {exc}")
#             return {"Error": exc}
#     raise HTTPException(
#         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Numerical values allowed")
#
#
# @app.get("/api/nearest_and_farthest_cities")
# def nearest_and_farthest_cities(country_id,
#                                 token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
#     """
#     Task A
#     Function calculates min and max distances between two cities within a country,
#     based on country id input.
#     Input: function expects numerical id value for specific country.
#     Example input: 88   (Serbia's id our database)
#     Query is case insensitive
#     Output: function returns a dictionary with country name,
#     nearest and farthest cities, and their distances
#     """
#
#     # input data validation
#     if country_id.isdigit():
#
#         # find country by a specific id input
#         country_obj = db.query(CountryModel).filter(
#             CountryModel.id == country_id).first()
#         if country_obj is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")
#
#         else:
#
#             # create a dictionary with city pairs, and distances between them
#             distances = {}
#             counter = 1
#             for city1 in country_obj.children[:-1:]:
#                 for city2 in country_obj.children[counter::]:
#                     distances[f"{city1.city_ascii_name}-{city2.city_ascii_name}"] \
#                         = haversine(
#                         (city1.lat, city1.lng), (city2.lat, city2.lng))
#                 counter += 1
#
#             # calculate max and min distances
#             max_distance = max(distances.values())
#             min_distance = min(distances.values())
#
#             # iterate through distance dict max values list, find key value,
#             # and append result dictionary
#             result = {f"max distance - {k}": f"{v} km" for k,
#                       v in distances.items() if v == max_distance}
#             # iterate through distance dict min values list, find key value,
#
#             # and append result dictionary
#             for key, value in distances.items():
#                 if value == min_distance:
#                     result[f"min distance - {key}"] = f"{value} km"
#
#             # final output
#             return {f"Country - {country_obj.country_name}": result}
#     else:
#         raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#                             detail="Only numeric value allowed")
#
#
# @app.get("/api/three_nearest_cities")
# def three_nearest_cities(country, token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
#     """
#     Task B
#     Function calculates cluster of three nearest cities in a country.
#     Input: country name, only alphabetic characters allowed.
#     Query is case insensitive
#     Output: function returns a dictionary with information about specific cluster
#     """
#     # input data validation
#     if country_validator(country):
#
#         # find country by a specific id input
#         country_obj = db.query(CountryModel).filter(
#             func.lower(CountryModel.country_name) == func.lower(country)).first()
#         if country_obj is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")
#
#         else:
#
#             # create a dictionary with combination of three cities,
#             #  and calculate distances between them
#             distances = {}
#             counter1 = 1
#             for city1 in country_obj.children[:-2:]:
#                 for city2 in country_obj.children[counter1:-1:]:
#                     counter2 = counter1+1
#                     for city3 in country_obj.children[counter2::]:
#                         distances[f"{city1.city_ascii_name}-"
#                                   f"{city2.city_ascii_name}-"
#                                   f"{city3.city_ascii_name}"] \
#                             = haversine((city1.lat, city1.lng), (city2.lat, city2.lng))\
#                             + haversine((city1.lat, city1.lng), (city3.lat, city3.lng))\
#                             + haversine((city2.lat, city2.lng),
#                                         (city3.lat, city3.lng))
#                         counter2 += 1
#                     counter1 += 1
#
#             # calculate min distance
#
#             min_distance = min(distances.values())
#
#             # iterate through distance dict min values list, find key value,
#             # and append result dictionary
#
#             result = {}
#
#             for key, value in distances.items():
#                 if value == min_distance:
#                     result[f"min distance - {key}"] = f"{value} km"
#
#             # final output
#             return {f"Country - {country_obj.country_name}": result}
#     else:
#         raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#                             detail="Only alphabetic characters allowed")
#
#
# @app.get("/nswe_cities/")
# def nswe_cities(country_name_input, token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
#     """
#     Task C
#     Function calculates northernmost, southernmost,
#     easternmost and westernmost cities within a country
#     based on country name input data.
#     Input: function expects alphabetic input value.
#     Example input: serbia
#     Query is case insensitive
#     Output: function returns a json formatted with northernmost, southernmost,
#     easternmost and westernmost cities, and distance between them.
#     """
#     # input validation
#     if country_name_input.isalpha():
#
#         # find specific country, and create a query object
#         country_obj = db.query(CountryModel).filter(
#             func.lower(CountryModel.country_name) ==
#             func.lower(country_name_input)).first()
#         if country_obj is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")
#         else:
#             # create lists of lattitude and longitude from every city
#             lat_list = [city.lat for city in country_obj.children]
#             lng_list = [city.lng for city in country_obj.children]
#
#             # find northernmost,southernmost,easternmost and westernmost cities
#             northernmost_city = country_obj.children[lat_list.index(
#                 max(lat_list))]
#             southernmost_city = country_obj.children[lat_list.index(
#                 min(lat_list))]
#             easternmost_city = country_obj.children[lng_list.index(
#                 max(lng_list))]
#             westernmost_city = country_obj.children[lng_list.index(
#                 min(lng_list))]
#
#             # calculate distance between northernmost and southernmost cities
#             north_south_distance = haversine(
#                 (northernmost_city.lat, northernmost_city.lng),
#                 (southernmost_city.lat, southernmost_city.lng))
#
#             # calculate distance between easternmost and westernmost cities
#             east_west_distance = haversine(
#                 (easternmost_city.lat, easternmost_city.lng),
#                 (westernmost_city.lat, westernmost_city.lng))
#
#             return {f"Nothernmost city is {northernmost_city.city_ascii_name},"
#                     f"southernmost city is {southernmost_city.city_ascii_name}."
#                     f"Distance between them is ": f"{north_south_distance} km",
#                     f"Westernmost city is {westernmost_city.city_ascii_name},"
#                     f"easternmost city is {easternmost_city.city_ascii_name}."
#                     f"Distance between them is ": f"{east_west_distance} km"
#                     }
#     else:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
#                             detail="Only alphabetic characters allowed")
#
#
# @app.get("/api/max_min_population/")
# def ls_cities(value_set,
#               token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
#     """
#     Task D
#     Function calculates max and min city population number based on
#     the input set of country name values.
#     Input: Function expects set of values, separated by a coma.
#     Example input value: serbia,croatia.
#     Query is case insensitive
#     Output: Function returns a dictionary with city with lowest population
#     number from the set o countries, city with largest population number
#     the set of countries, and total population number for each country
#     """
#     # input validation
#     if country_set_validator(value_set):
#
#         input_list = value_set.split(',')
#
#         # create a list of country query objects from elements of input list
#         country_list = [db.query(CountryModel).filter(
#             func.lower(CountryModel.country_name) == func.lower(country)).first()
#             for country in input_list]
#
#         if None in country_list:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="One or more countries not found")
#         else:
#             # create a dictionary with a country name, city name and population
#             city_dict = {}
#             counter = 1
#             for country in country_list:
#                 for city in country.children:
#                     city_dict[f"country - {country.country_name}, city -"
#                               f"{city.city_ascii_name}"] = city.population
#                 counter += 1
#
#             # calculate min city population
#             min_population_city = min(
#                 value for value in city_dict.values() if value is not None)
#
#             # create a dictionary with min population city name and it's population
#             out_min = {}
#             for key, value in city_dict.items():
#                 if value == min_population_city:
#                     out_min[key] = f"Population {value}"
#
#             # calculate max city population
#             max_population_city = max(
#                 value for value in city_dict.values() if value is not None)
#
#             # create a dictionary with max population city name and it's population
#             out_max = {}
#             for key, value in city_dict.items():
#                 if value == max_population_city:
#                     out_max[key] = f"Population {value}"
#
#             # calculate total population for each country
#             total_population = {}
#             counter = 1
#             for country in country_list:
#                 total_temp = 0
#                 for city in country.children:
#                     if city.population is not None:
#                         total_temp += city.population
#                 total_population[f"Country - {country.country_name}"] = \
#                     f"Total population - {total_temp}"
#
#             return {"Smallest city from the set of countries": out_min,
#                     "Largest city from the set of countries": out_max,
#                     "Total population for each country": total_population}
#
#     else:
#         raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#                             detail="Only alphabetic characters allowed,"
#                             "separated by a ','")
#


if __name__ == "__main__":

    # print("aca")
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
    ...













