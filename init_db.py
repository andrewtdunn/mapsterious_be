from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Location, Recreation, Restaurant, School, Base, User, Review
import os

engine = create_engine(os.environ['DB_KEY'])

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a 'staging zone' for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the dtatabase until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

#add Andrew Dunn
user1 = User(name=os.environ['FIRST_USER_NAME'],
                email=os.environ['FIRST_EMAIL'],
                picture=os.environ['FIRST_USER_PIC'])
session.add(user1)
session.commit()

#add second user
user2 = User(name=os.environ['SECOND_USER_NAME'],
                email=os.environ['SECOND_EMAIL'],
                picture=os.environ['SECOND_USER_PIC'])
session.add(user2)
session.commit()

#add third user
user3 = User(name=os.environ['THIRD_USER_NAME'],
                email=os.environ['THIRD_EMAIL'],
                picture=os.environ['THIRD_USER_PIC'])
session.add(user3)
session.commit()

print "added users!"

# Location for Fort Greene Park
location1 = Recreation(label='Fort Greene Park',
                     lat=40.689752,
                     lng=-73.973224,
                     menuLabel='Ft. Greene Park',
                     wiki_id=629083,
                     icon='img/dog.png',
                     active='yes',
                     user_id=1)

session.add(location1)
session.commit()


# Location for Lulu & Po
location2 = Restaurant(label='Lulu & Po',
                     lat=40.693037,
                     lng=-73.973006,
                     menuLabel='Lulu & Po',
                     yelp_id='lulu-and-po-brooklyn',
                     icon='img/lulupo.png',
                     active='yes',
                     user_id=1)


session.add(location2)
session.commit()


# Location for Pratt
location3 = School(label='Pratt Institute',
                     lat=40.691107,
                     lng=-73.963735,
                     menuLabel='Pratt',
                     wiki_id='778086',
                     icon='img/pratt.png',
                     active='yes',
                     user_id=1)


session.add(location3)
session.commit()

# Location for Barclays Center
location4 = Recreation(label='Barclays Center',
                     lat=40.683154,
                     lng=-73.976168,
                     menuLabel='Barclays Center',
                     wiki_id='778086',
                     icon='img/barclays.png',
                     active='yes',
                     user_id=1)


session.add(location4)
session.commit()

# Location for Cafe Habana
location5 = Restaurant(label='Cafe Habana',
                     lat=40.686392,
                     lng=-73.974368,
                     menuLabel='Cafe Habana',
                     yelp_id='habana-outpost-brooklyn',
                     icon='img/habana.png',
                     active='yes',
                     user_id=1)


session.add(location5)
session.commit()

# Location for Graziella's
location6 = Restaurant(label='Graziella\'s',
                     lat=40.6905515721,
                     lng=-73.9694785356,
                     menuLabel='Graziella\'s',
                     yelp_id='graziellas-brooklyn-11',
                     icon='img/graziellas.png',
                     active='yes',
                     user_id=1)


session.add(location6)
session.commit()

# Location for Martha
location7 = Restaurant(label='Martha',
                     lat=40.6896170603121,
                     lng=-73.972475145998,
                     menuLabel='Martha',
                     yelp_id='martha-brooklyn-5',
                     icon='img/marthabk.png',
                     active='no',
                     user_id=1)


session.add(location7)
session.commit()


# Location for Juniors
location8 = Restaurant(label='Junior\'s',
                     lat=40.690100,
                     lng=-73.981686,
                     menuLabel='Junior\'s',
                     yelp_id='juniors-restaurant-brooklyn',
                     icon='img/juniors1.png',
                     active='yes',
                     user_id=1)


session.add(location8)
session.commit()

# Location for Chez Oskar
location9 = Restaurant(label='Chez Oskar',
                     lat=40.6822733971642,
                     lng=-73.9290857000809 ,
                     menuLabel='Chez Oskar',
                     yelp_id='chez-oskar-brooklyn',
                     icon='img/chezoskar.png',
                     active='no',
                     user_id=1)


session.add(location9)
session.commit()

# Location for Brooklyn Tech
location10 = School(label='Brooklyn Technical High School',
                      lat=40.688645,
                      lng=-73.976391,
                      menuLabel='Brooklyn Tech',
                      wiki_id=378883,
                      icon='img/bths.png',
                      active='yes',
                      user_id=1)


session.add(location10)
session.commit()

# Location for BAM
location11 = Recreation(label='Brooklyn Academy of Music',
                      lat=40.686808,
                      lng=-73.977584,
                      menuLabel='BAM',
                      wiki_id=215190,
                      icon='img/bam.png',
                      active='yes',
                      user_id=1)


session.add(location11)
session.commit()


# Location for Maison May
location12 = Restaurant(label='Maison May',
                      lat=40.689272,
                      lng=-73.967966,
                      menuLabel='Maison May',
                      yelp_id='maison-may-dekalb-brooklyn-2',
                      icon='img/mm.png',
                      active='yes',
                      user_id=1)


session.add(location12)
session.commit()

# Location for St. Joseph's
location13 = School(label='St. Joseph\'s College (New York)',
                      lat=40.690460,
                      lng=-73.967966,
                      menuLabel='St. Joseph\'s',
                      wiki_id=910252,
                      icon='img/sjc.png',
                      active='yes',
                      user_id=1)


session.add(location13)
session.commit()

# Location for Castro's
location14 = Restaurant(label='Castro\'s Restaurant',
                      lat=40.693773,
                      lng=-73.964390,
                      menuLabel='Castro\'s',
                      yelp_id='castros-restaurant-brooklyn',
                      icon='img/castros.png',
                      active='yes',
                      user_id=1)


session.add(location14)
session.commit()

# Location for The Smoke Joint
location15 = Restaurant(label='The Smoke Joint',
                      lat=40.6869657292783,
                      lng=-73.975421945755,
                      menuLabel='The Smoke Joint',
                      yelp_id='the-smoke-joint-brooklyn',
                      icon='',
                      active='yes',
                      user_id=2)


session.add(location15)
session.commit()

# Location for Mega Bites
location16 = Restaurant(label='Mega Bites Diner',
                      lat=40.6896171690248,
                      lng=-73.9693386957092,
                      menuLabel='Mega Bites',
                      yelp_id='mega-bites-brooklyn ',
                      icon='',
                      active='yes',
                      user_id=2)


session.add(location16)
session.commit()

# Location for Staten Island zoom
location17 = Recreation(label='Staten Island Zoo',
                      lat=40.625155503767,
                      lng=-74.1153796121521,
                      menuLabel='Staten Island Zoo',
                      wiki_id=910252,
                      icon='',
                      active='yes',
                      user_id=2)


session.add(location17)
session.commit()

print "added locations!"

review1 = Review(review_text="great plays here",
                    location_id=11,
                    user_id=1)

session.add(review1)
session.commit()

review2 = Review(review_text="castro especial ~",
                    location_id=14,
                    user_id=1)

session.add(review2)
session.commit()

review3 = Review(review_text="recently relocated to bed-stuy",
                    location_id=9,
                    user_id=1)

session.add(review3)
session.commit()

review4 = Review(review_text="ain't no more",
                    location_id=7,
                    user_id=1)

session.add(review4)
session.commit()

review5 = Review(review_text="great catfish burrito",
                    location_id=5,
                    user_id=2)

session.add(review5)
session.commit()

review6 = Review(review_text="Mama mia pizzeria!",
                    location_id=6,
                    user_id=3)

session.add(review6)
session.commit()

review7 = Review(review_text="Lots o' cool animals",
                    location_id=17,
                    user_id=3)

session.add(review7)
session.commit()

review8 = Review(review_text="I will check it out",
                    location_id=17,
                    user_id=1)

session.add(review8)
session.commit()


review9 = Review(review_text="good but not great",
                    location_id=15,
                    user_id=1)

session.add(review9)
session.commit()

print("added reviews!")
