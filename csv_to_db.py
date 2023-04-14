"""
Python module used to import data from
worldcities.csv file in a database
"""
import pandas as pd
from models import CountryModel, CityModel
from models import Session
from sqlalchemy import func

def add_country(country_name:str):
    """
    Function that creates a country orm object and
    stores the country data in a database table "countries"
    """
    try:
        with Session() as session:
            country = CountryModel(
                country_name=country_name
            )
            session.add(country)
            session.commit()
            session.refresh(country)

            return country

    except Exception as exc:
        print("Error, ", exc)


def find_country(name):
    """
    Function that is used to find a country from a database
    and store the data in a orm boject
    """
    country = Session().query(CountryModel).filter(
        func.lower(CountryModel.country_name) == func.lower(name)).first()
    return country


def add_city(city_name, country_id, lat, lon, population):
    """
    Function that creates a city orm object and stores the city
    data in a database table "cities"
    """
    try:
        with Session() as session:
            city = CityModel(
                city_ascii_name=city_name,
                country_id=country_id,
                lat=lat, lng=lon,
                population=population)
            session.add(city)
            session.commit()
    except Exception as exc:
        print("Error, ", exc)



def csv_to_db():
    """
    Function that imports the data from worldcities.csv into a database
    """
    try:
        df = pd.read_csv('worldcities.csv', usecols=[
            'city_ascii', 'lat', 'lng', 'country', 'population'])

        cities_list = df['city_ascii'].values.tolist()
        lat_list = df['lat'].values.tolist()
        lng_list = df['lng'].values.tolist()
        country_list = df['country'].values.tolist()
        population_list = df['population'].values.tolist()

        for country_name, city_name, city_lat, city_lon, \
            city_population in zip(country_list, cities_list,
                                   lat_list, lng_list, population_list):
            country = find_country(country_name)
            if not country:
                country = add_country(country_name=country_name)

            add_city(city_name=city_name, country_id=country.id,
                       lat=city_lat, lon=city_lon, population=city_population)


    except Exception as exc:
        print("Error, ", exc)


if __name__ == '__main__':
    csv_to_db()
