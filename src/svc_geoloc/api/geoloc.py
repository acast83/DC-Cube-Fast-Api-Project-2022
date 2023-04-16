from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import between
from src.svc_geoloc.utils.logging_setup import log
from src.svc_geoloc.utils.db_utils import get_db
from dotenv import load_dotenv
import uvicorn
from haversine import haversine

load_dotenv()
from src.utils.api_utils import get_auth_dependencies

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/login')
from src.svc_geoloc.models.geoloc import *
from sqlalchemy import func

app = FastAPI()


@app.get("/about")
def root():
    """
    Root endpoint function
    """
    return {"service": "geoloc"}


@app.get("/countries")
def get_all_countries(
        offset: int = 0,
        limit: int = 20,
        handler: object = Depends(get_auth_dependencies),
        db: Session = Depends(get_db)
):
    """
    api that provides user with json formated list of countries
    based on input limit and offset values.
    Input: limit and offset values used for pagination purpose
    Output: json formatted list of countries
    """

    # create country query object based on limit and offset  values
    countries = db.query(DbCountry).offset(
        offset).limit(limit).all()

    # create output list
    result = []
    for country in countries:
        result.append({"id": country.id, "name": country.name})

    return result


@app.get("/country_by_city_name/{city_name}")
def find_country_by_city_name(city_name: str,
                              db: Session = Depends(get_db),
                              handler: object = Depends(get_auth_dependencies),
                              ):
    """
    Function returns country name based od city name input value
    Input: city name, allows only alphabetic characters
    Query is case insensitive
    Output: returns json formatted city and country data
    """

    cities = db.query(DbCity).filter(
        func.lower(DbCity.name) == city_name.lower()
    ).all()

    result = []
    for city in cities:
        result.append({'id': city.id, 'city_name': city.name, 'country_name': city.country.name})
    return result


@app.get("/cities")
def get_cities(offset: int = 0,
               limit: int = 50,
               db: Session = Depends(get_db),
               handler: object = Depends(get_auth_dependencies),
               ):
    """
    Function provides user with list of cities
    based on input limit and offset values.
    Input: limit and offset values used for pagination purposes
    Output: json formatted list of cities
    """

    cities = db.query(DbCity).offset(
        offset).limit(limit).all()

    # create output list
    result = []
    for city in cities:
        result.append({"id": city.id, "name": city.name})

    return result


@app.get("/cities_by_population/min/{min}/max/{max}")
def list_cities_by_population(min: int,
                              max: int,
                              limit: int = 50,
                              db: Session = Depends(get_db),
                              handler: object = Depends(get_auth_dependencies),
                              ):
    """
    Function calculates and returns a dictionary with cities
    with population between min and max values.
    Input: min and max population
    Output: returns sa json formatted with city names and their population
    """

    cities = db.query(DbCity).filter(
        between(DbCity.population, min, max)
    ).all()
    result = []
    for city in cities:
        result.append({"id": city.id, "name": city.name, "population": city.population})

    return {"meta": {"limit": limit},
            "cities": result
            }


@app.get("/nearest_and_farthest_cities/{country_id}")
def nearest_and_farthest_cities(country_id,
                                handler: object = Depends(get_auth_dependencies),
                                db: Session = Depends(get_db)):
    """
    Task A
    Function calculates min and max distances between two cities within a country,
    based on country id input.
    Input: function expects numerical id value for specific country.
    Example input: 88   (Serbia's id our database)
    Output: function returns a dictionary with country name,
    nearest and farthest cities, and their distances
    """

    # find country by a specific id input
    country = db.query(DbCountry).filter(
        DbCountry.id == country_id).first()
    if not country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="COUNTRY_NOT_FOUND")
    # create a dictionary with city pairs, and distances between them
    distances = {}
    counter = 1
    for city1 in country.cities[:-1:]:
        for city2 in country.cities[counter::]:
            distances[f"{city1.name}-{city2.name}"] = haversine((city1.lat, city1.lng), (city2.lat, city2.lng))
        counter += 1

    # calculate max and min distances
    max_distance = max(distances.values())
    min_distance = min(distances.values())

    # iterate through distance dict max values list, find key value,
    # and append result dictionary
    result = {f"max distance - {k}": f"{v} km" for k,
    v in distances.items() if v == max_distance}
    # iterate through distance dict min values list, find key value,

    # and append result dictionary
    for key, value in distances.items():
        if value == min_distance:
            result[f"min distance - {key}"] = f"{value} km"

    # final output
    return {f"Country - {country.country_name}": result}


#
# @app.get("/api/three_nearest_cities")
# def three_nearest_cities(country, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
#                     counter2 = counter1 + 1
#                     for city3 in country_obj.children[counter2::]:
#                         distances[f"{city1.city_ascii_name}-"
#                                   f"{city2.city_ascii_name}-"
#                                   f"{city3.city_ascii_name}"] \
#                             = haversine((city1.lat, city1.lng), (city2.lat, city2.lng)) \
#                               + haversine((city1.lat, city1.lng), (city3.lat, city3.lng)) \
#                               + haversine((city2.lat, city2.lng),
#                                           (city3.lat, city3.lng))
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
# def nswe_cities(country_name_input, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
#               token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
#                         for country in input_list]
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
#                                    "separated by a ','")


if __name__ == "__main__":
    uvicorn.run("geoloc:app", host="0.0.0.0", port=8002, reload=True)
    ...
