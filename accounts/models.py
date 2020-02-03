from django.db import models
from djongo import models as djongo_models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from macaddress.fields import MACAddressField

from pymongo import MongoClient
from jsonfield import JSONField

class CustomUser(AbstractUser):
	username = models.CharField(max_length=30, unique=True)
	firstname = djongo_models.CharField(max_length=30)
	lastname = djongo_models.CharField(max_length=30)
	password = models.CharField(max_length=100)
	email = models.CharField(max_length=200, unique=True)

	MALE = 'male'
	FEMALE = 'female'
	GENDER_CHOICES = [
		(MALE,'male'),
		(FEMALE,'female'),
	]
	gender = models.CharField(max_length=6,
			choices=GENDER_CHOICES,default=MALE,)
	age = models.PositiveSmallIntegerField(blank=True)
	body_height = models.FloatField(blank=True)
	body_weight = models.FloatField(blank=True)
	is_email_verified = models.BooleanField(default=False)

	BRONZE = 'bronze'
	SILVER = 'silver'
	GOLD = 'gold'
	PLATINUM = 'platinum'
	PACKAGES_CHOICES= [
		(BRONZE, 'Bronze'),
		(SILVER, 'Silver'),
		(GOLD, 'Gold'),
		(PLATINUM, 'Platinum'),
	]
	package = models.CharField(max_length=8,
			choices=PACKAGES_CHOICES,default=BRONZE,)
	topics = JSONField()
	devicemacs = JSONField()

	#Override save() function to add user's JWT token,
	#and save the fields to mongoDB as new collection.
	def save(self, *args, **kwargs):
		if 'registering' in kwargs:
			print('In save, registering')
			if kwargs.get('registering'):
				print('Inserting to Mongo by pymongo...')
				self.insert_to_mongo_as_collection()

				kwargs.pop('registering')
				super().save(*args, **kwargs)
		else:
			if not self.topics:
				print("Initializing topics as empty JSON...")
				self.topics = []
			if not self.devicemacs:
				print("Initializing topics as empty JSON...")
				self.devicemacs= []

			super().save(*args, **kwargs)

	def insert_to_mongo_as_collection(self):
		info={'username':self.username,'email':self.email,'age':self.age,'gender':self.gender,'body_height_cm':self.body_height,'body_weight_kg':self.body_weight,'package':self.package,'topics':self.topics,}

		result = create_user(**info)

# Connect to mongoDB and create new collection if not exist yet
def connect():
	hostname = settings.DB_USER
	password = settings.DB_PASS
	hostaddress = settings.DB_ADDR
	hostport = settings.DB_PORT
	dbname = settings.DB_NAME

	try:
		conn = MongoClient('mongodb://%s:%s/%s'\
				%(hostaddress,hostport,dbname))
		db = conn[dbname]
	except Exception as e:
		print('Exception occured when connecting to mongo: ',e)

	return db

def is_user_and_email_exists(db, username, email):
	try:
		collnames = db.list_collection_names()

		if username in collnames:
			return True
		else:
			for coll in collnames:
				if db.coll.find_one(email):
					return True
			return False
	except Exception as e:
		print('Exception has occured in is_user_and_email_exists:', e)

	print("Try-catch cant catch something at is_user_and_email_exists")
	return True

def create_user(**info):
	username = info['username']
	email = info['email']
	db = connect()
	status = is_user_and_email_exists(db, username, email)

	if status:
		message = 'User or email already exists. Try another username or email'
		print(message)
		return [None, message]
	else:
		coll = db[username]
		createresult = coll.insert_one(info)
		message = 'Insert as collection successful. Insert id:\
			'+str(createresult.inserted_id)
		print(message)
		return [createresult.inserted_id,message]

def get_userprofile(username):
	collection = connect()
	userprofile = collection.find_one({'username':username})
	if userprofile:
		return userprofile
	else:
		print('NOT FOUND!')

