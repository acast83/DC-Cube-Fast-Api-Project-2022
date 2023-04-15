"""
Python module used to import data from
worldcities.csv file in a database
"""
import pandas as pd
from src.svc_users.models.users import CountryModel, CityModel
from src.utils.db_utils import Session
from sqlalchemy import func


def add_country(name: str):
    """
    Function that creates a country orm object and
    stores the country data in a database table "countries"
    """
    try:
        with Session() as session:
            country = CountryModel(
                name=name
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
    with Session() as session:
        country = session.query(CountryModel).filter(
            func.lower(CountryModel.name) == func.lower(name)).first()
    return country


def add_city(name, country_id, lat, lon, population):
    """
    Function that creates a city orm object and stores the city
    data in a database table "cities"
    """
    try:
        with Session() as session:
            city = CityModel(
                name=name,
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
                try:
                    country = add_country(name=country_name)
                except Exception as e:
                    raise
            try:
                add_city(name=city_name, country_id=country.id,
                         lat=city_lat, lon=city_lon, population=city_population)
            except Exception as e:
                print(city_name, city_lat, city_lon, city_population)
                raise


    except Exception as exc:
        print("Error, ", exc)


if __name__ == '__main__':
    csv_to_db()
