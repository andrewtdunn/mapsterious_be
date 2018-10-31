![alt text](https://github.com/andrewtdunn/map_db_vm/blob/master/map.png "screenshot")

# api.mapsterious.com

[live site](http://api.mapsterious.com)

This DB allows you to locate items on a google map, identify them with a lat/lng location,
and classify the location as either a recreation site or a restaurant or a school. The location is given
 an icon and linked to either a wikipedia page or a yelp page. Users, once logged in via FB oauth, can create, read, update or delete a location, as well as leave comments on any location

The admin publishes a REST API consumed by [mapsterious.com](http://mapsterious.com)

example endpoint: [http://api.mapsterious.com/locations/JSON](http://api.mapsterious.com/locations/JSON)

## Local Development

- to run:

```bash

$ python database_setup.py
$ python init_db.py
added users!
added locations!
added reviews!
$ python application.py
 * Running on http://0.0.0.0:5000/
 * Restarting with reloader

```

map should load at localhost:5000

from there, performing CRUD operations on locations should be intuitive, using the emojis
