"""
Python module used to import data from
worldcities.csv file in a database
"""
import pandas as pd
from models import Country_Model, City_Model
from models import session


def country_entry(country_data):
    """
    Function that creates a country orm object and
    stores the country data in a database table "countries"
    """
    try:
        country_entry = Country_Model(
            country_name=country_data
        )
        session.add(country_entry)
        session.commit()
    except Exception as exc:
        print("Error, ", exc)
    finally:
        session.close()


def find_country(country):
    """
    Function that is used to find a country from a database
    and store the data in a orm oject
    """
    country_search = session.query(Country_Model).filter(
        Country_Model.country_name == country).first()
    return country_search


def city_entry(city_data, country_id_data, lat_data, lng_data, population_data):
    """
    Function that creates a city orm object and stores the city
    data in a database table "cities"
    """
    try:
        city = City_Model(
            city_ascii_name=city_data,
            country_id=country_id_data,
            lat=lat_data, lng=lng_data,
            population=population_data)
        session.add(city)
        session.commit()
    except Exception as exc:
        print("Error, ", exc)
    finally:
        session.close()


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

        for country_item, city_item, lat_item, lng_item, \
            population_item in zip(country_list, cities_list,
                                   lat_list, lng_list, population_list):
            country_search = find_country(country_item)
            if country_search is None:
                country_entry(country_item)
                country_search = find_country(country_item)

            city_entry(city_item, country_search.id,
                       lat_item, lng_item, population_item)

    except Exception as exc:
        print("Error, ", exc)


if __name__ == '__main__':
    csv_to_db()
