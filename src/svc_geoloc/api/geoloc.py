from fastapi import FastAPI, status, HTTPException, Depends
from sqlalchemy import between
from dotenv import load_dotenv
import uvicorn
from haversine import haversine

from utils.api_utils import get_auth_dependencies

from svc_geoloc.models.geoloc import *
from sqlalchemy import func

load_dotenv()
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

):
    """
    api that provides user with json formated list of countries
    based on input limit and offset values.
    Input: limit and offset values used for pagination purpose
    Output: json formatted list of countries
    """
    db = handler.db

    # create country query object based on limit and offset values
    countries = db.query(DbCountry).offset(
        offset).limit(limit).all()

    # create output list
    result = []
    for country in countries:
        result.append({"id": country.id, "name": country.name})

    return result


@app.get("/country_by_city_name/{city_name}")
def find_country_by_city_name(city_name: str,
                              handler: object = Depends(get_auth_dependencies),
                              ):
    """
    Function returns country name based od city name input value
    Input: city name, allows only alphabetic characters
    Query is case insensitive
    Output: returns json formatted city and country data
    """

    db = handler.db
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
               handler: object = Depends(get_auth_dependencies),

               ):
    """
    Function provides user with list of cities
    based on input limit and offset values.
    Input: limit and offset values used for pagination purposes
    Output: json formatted list of cities
    """
    db = handler.db
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
                              handler: object = Depends(get_auth_dependencies),
                              ):
    """
    Function calculates and returns a dictionary with cities
    with population between min and max values.
    Input: min and max population
    Output: returns sa json formatted with city names and their population
    """
    db = handler.db
    cities = db.query(DbCity).filter(
        between(DbCity.population, min, max)
    ).all()
    result = []
    for city in cities:
        result.append({"id": city.id, "name": city.name, "population": city.population})

    return {"meta": {"limit": limit},
            "cities": result
            }


@app.get("/countries/{country_id}/nearest_and_farthest_cities/")
def nearest_and_farthest_cities(country_id,
                                handler: object = Depends(get_auth_dependencies),
                                ):
    """
    Task A
    Function calculates min and max distances between two cities within a country,
    based on country id input.
    Input: function expects numerical id value for specific country.
    Example input: 88   (Serbia's id our database)
    Output: function returns a dictionary with country name,
    nearest and farthest cities, and their distances
    """

    db = handler.db

    # find country by a specific id input
    country = db.query(DbCountry).filter_by(id=country_id).one_or_none()

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
    return {f"Country - {country.name}": result}


@app.get("/countries/{country_id}/three_nearest_cities")
def three_nearest_cities(country_id: int,
                         handler: object = Depends(get_auth_dependencies),
                         ):
    """
    Task B
    Function calculates cluster of three nearest cities in a country.
    Input: country name, only alphabetic characters allowed.
    Query is case insensitive
    Output: function returns a dictionary with information about specific cluster
    """
    db = handler.db
    # find country by a specific id input
    country = db.query(DbCountry).filter_by(id=country_id).one_or_none()
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="COUNTRY_NOT_FOUND")

    # create a dictionary with combination of three cities,
    #  and calculate distances between them
    distances = {}
    counter1 = 1
    for city1 in country.cities[:-2:]:
        for city2 in country.cities[counter1:-1:]:
            counter2 = counter1 + 1
            for city3 in country.cities[counter2::]:
                distances[f"{city1.name}-"
                          f"{city2.name}-"
                          f"{city3.name}"] \
                    = haversine((city1.lat, city1.lng), (city2.lat, city2.lng)) \
                      + haversine((city1.lat, city1.lng), (city3.lat, city3.lng)) \
                      + haversine((city2.lat, city2.lng),
                                  (city3.lat, city3.lng))
                counter2 += 1
            counter1 += 1

    # calculate min distance

    min_distance = min(distances.values())

    # iterate through distance dict min values list, find key value,
    # and append result dictionary

    result = {}

    for key, value in distances.items():
        if value == min_distance:
            result[f"min distance - {key}"] = f"{value} km"

    # final output
    return {f"Country - {country.name}": result}


@app.get("/countries/{country_id}/nswe_cities/")
def nswe_cities(country_id: int,

                handler: object = Depends(get_auth_dependencies),
                ):
    """
    Task C
    Function calculates northernmost, southernmost,
    easternmost and westernmost cities within a country
    based on country name input data.
    Input: function expects alphabetic input value.
    Example input: serbia
    Query is case insensitive
    Output: function returns a json formatted with northernmost, southernmost,
    easternmost and westernmost cities, and distance between them.
    """

    db = handler.db
    # find country by a specific id input
    country = db.query(DbCountry).filter_by(id=country_id).one_or_none()

    if not country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="COUNTRY_NOT_FOUND")
    else:
        # create lists of lattitude and longitude from every city
        lat_list = [city.lat for city in country.cities]
        lng_list = [city.lng for city in country.cities]

        # find northernmost,southernmost,easternmost and westernmost cities
        northernmost_city = country.cities[lat_list.index(
            max(lat_list))]
        southernmost_city = country.cities[lat_list.index(
            min(lat_list))]
        easternmost_city = country.cities[lng_list.index(
            max(lng_list))]
        westernmost_city = country.cities[lng_list.index(
            min(lng_list))]

        # calculate distance between northernmost and southernmost cities
        north_south_distance = haversine(
            (northernmost_city.lat, northernmost_city.lng),
            (southernmost_city.lat, southernmost_city.lng))

        # calculate distance between easternmost and westernmost cities
        east_west_distance = haversine(
            (easternmost_city.lat, easternmost_city.lng),
            (westernmost_city.lat, westernmost_city.lng))

        return {f"Nothernmost city is {northernmost_city.name},"
                f"southernmost city is {southernmost_city.name}."
                f"Distance between them is ": f"{north_south_distance} km",
                f"Westernmost city is {westernmost_city.name},"
                f"easternmost city is {easternmost_city.name}."
                f"Distance between them is ": f"{east_west_distance} km"
                }


@app.get("/countries/{country_ids}/max_min_population/")
def ls_cities(country_ids: str,
              handler: object = Depends(get_auth_dependencies),
              ):
    """
    Task D
    Function calculates max and min city population number based on
    the input set of country name values.
    Input: Function expects set of values, separated by a coma.
    Output: Function returns a dictionary with city with lowest population
    number from the set o countries, city with largest population number
    the set of countries, and total population number for each country
    """
    db = handler.db

    # Split the country_ids string on commas and convert the resulting list to integers
    country_ids = [int(id) for id in country_ids.split(',')]

    # Get a list of cities for the specified countries, ordered by population

    cities = db.query(DbCity).join(DbCountry). \
        filter(DbCountry.id.in_(country_ids)). \
        order_by(DbCity.population).all()

    # Get the city with the smallest population
    smallest_city = cities[0]

    # Get the city with the largest population
    largest_city = cities[-1]

    total_populations = db.query(DbCountry.name, func.sum(DbCity.population)). \
        join(DbCity). \
        filter(DbCountry.id.in_(country_ids)). \
        group_by(DbCountry.id).all()

    result = {"largest_city": {"name": largest_city.name,
                               "population": largest_city.population},
              "smallest_city": {"name": smallest_city.name,
                                "population": smallest_city.population},
              }
    total_pop_res = {f"country {i}": {"name": c[0], "population": c[1]} \
                     for i, c in enumerate(total_populations)}

    result.update({"total_population": total_pop_res})

    return result


if __name__ == "__main__":
    uvicorn.run("geoloc:app", host="0.0.0.0", port=8002, reload=True)
    ...
