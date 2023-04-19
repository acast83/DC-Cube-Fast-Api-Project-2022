### DC Cube Geoloc Assignment Backend Project

DC Cube geoloc assignment is as part of a Digital Cube's technical interview.
---

## Getting Started

### Requirements

docker engine, docker-compose, git

### Installation:

Create project folder and get inside the project folder

```
mkdir project_folder
cd project_folder
```

Clone github repository

```
git clone git@github.com:acast83/DC-Cube-Fast-Api-Project-2022.git .
```

### Run the application using docker

Build docker image and run docker containers

```
docker-compose build
docker-compose up -d
```

If successfully built, aplication will be live on localhost, port 80.

### Sample non authorized api calls

```
api: http://localhost/api/users/about
method: get
response: {"service": "users"}
```

```
api: http://localhost/api/users/sign_up
method: post
sample body: {"username":"test_user", "password":"123"}
response: {
    "access_token": "eyJhbGciOiJIUzI1N............",
    "token_type": "bearer"
}
```

### Sample authorized api calls

```
api: http://localhost/api/geoloc/countries?limit=50&offset=100
method: get
response: [
    {
        "id": 101,
        "name": "Armenia"
    },
    {
        "id": 102,
        "name": "Mauritania"
    },
    {
        "id": 103,
        "name": "Tunisia"
    },....]
```

```
api: http://localhost/api/geoloc/cities_by_population/min/1000000/max/2000000
method: get
response: {
    "meta": {
        "limit": 50
    },
    "cities": [
        {
            "id": 392,
            "name": "Chongzuo",
            "population": 1994285
        },
        {
            "id": 393,
            "name": "Sanliurfa",
            "population": 1985753
        },
        {
            "id": 394,
            "name": "Kananga",
            "population": 1971704
        },
        {
            "id": 395,
            "name": "Peshawar",
            "population": 1970042
        },
        {
            "id": 396,
            "name": "Sapporo",
            "population": 1961690
        }.....]
```
