from django.db import models
from pymongo import MongoClient
from django.conf import settings
#from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from jwt import encode, decode
from bson.objectid import ObjectId
import json, requests
from django.conf import settings

gtwhost = settings.GTW_HOST
gtwport = settings.GTW_PORT

def set_new_device(usermodel, userid, newdevice):
	successtatus = ''
	userdata = ''
	collection_user = ''
	try:
		userdata = get_object_or_404(usermodel,pk=userid)
		collection_user = connect(userdata.username)
	except Exception as e:
		userdata = None
		print("Exception at set_new_device:", e)
		successtatus = e
	if userdata is not None:
		userdevice = userdata.devicemacs
		userdevice.append(newdevice)
		userdata.devicemacs = userdevice

		#Set db.[username] (username collection) with new devicemacs
		collection_user.update_one({'username':userdata.username},{'$set':{'devicemacs':userdevice}})
		userdata.save()

		return True
	else:
		return successtatus


def update_device(usermodel, userid, updated_device, old_device):
	successtatus = ''
	userdata = ''
	collection_user = ''
	try:
		userdata = get_object_or_404(usermodel,pk=userid)
		collection_user = connect(userdata.username)
	except Exception as e:
		userdata = None
		print("Exception at set_new_device:", e)
		successtatus = e

	if userdata is not None:
		print('Old data:', userdata.devicemacs)
		userdevice = userdata.devicemacs
		for index, element in enumerate(userdevice):
			if old_device['macaddress'] in element['macaddress']:
				print('FOUND!')
				userdevice[index] = updated_device

		print('New data:', userdata.devicemacs)
		userdata.devicemacs = userdevice

		collection_user_devicemacs = collection_user.find_one({'username':userdata.username})

		if collection_user_devicemacs is not None:
			collection_user.update_one({'username':userdata.username},{'$set':{'devicemacs':userdata.devicemacs}})
			print("collection '"+userdata.username+"' is updated with new device data")
		else:
			print("collection_user is NONE!")

		userdata.save()

		return True

	return successtatus

"""
Modifies db.accounts_customuser, db.[user] and db.topics to remove chosen device.
At db.accounts_customuser, removes the 'devicemacs' field that contains device.
At db.[user], removes the mac address of the device at
..'connecteddevices' field, and recalculates new jwt inside the 'topics'.
At db.topics, removes the devices from the documents.

Side-note: DO NOT forget to convert encoded JWT to string!
"""
def delete_device(usermodel, userid, device_name):
	successtatus = ''
	userdata = ''
	collection_user = ''
	SECRET_KEY = "Ki6wt83A5txZCX0FV0gbtuDazhhgFwd4"
	try:
		userdata = get_object_or_404(usermodel,pk=userid)
		collection_user = connect(userdata.username)
		collection_topics = connect('topics')
	except Exception as e:
		userdata = None
		print("Exception at set_new_device:", e)
		successtatus = e
		return e

	if userdata is not None:
		userdevice_copy1 = userdata.devicemacs
		userdevice_copy2 = list(userdata.devicemacs)
		user_topics = userdata.topics
		device_mac = ''
		userid_and_topicname = []

		#Find and delete chosen device from userdata.devicemacs
		for index, element in enumerate(userdevice_copy1):
			if device_name in element['name']:
				device_mac = element['macaddress']
				del userdevice_copy1[index]

				#Find and delete chosen device from userdata.topics
				if not user_topics:
					for index, element in enumerate(user_topics):
						for key, value in element.items():
							if type(value) == list:
								if device_mac in value:
									element['connecteddevices'].remove(device_mac)
									tokendata = {'username':userdata.username,
									  'connecteddevices':element['connecteddevices'],}
									new_jwt = str(encode(tokendata, SECRET_KEY, 
									  algorithm='HS256'))
									element['jwt'] = new_jwt

									userid_and_topicname.append((element['user_id'],
									  element['name'],element['connecteddevices'],
									  element['jwt']))
									print('userid_and_topicname: ',userid_and_topicname)
		print("userdata after delete: ", userdata.topics)
		print()
		
		userdata.save()
		coll_user_data = collection_user.find_one({'devicemacs':userdevice_copy2})
		#temp2 = coll_user_data.copy()
		coll_topics_data = collection_topics.find({'user_id':userdata.id})
		#temp3 = coll_topics_data.copy()

		if coll_user_data is not None :
			collection_user.update_many(
				{'username':userdata.username},
				{
					'$set': {
						'devicemacs':userdata.devicemacs,
						'topics':userdata.topics,
					}
				}
			)
		else:
			print("Device not found in collection_user.")

		if coll_topics_data is not None :
			for field in coll_topics_data:
				for quaduple in userid_and_topicname:
					print('quaduple: ', quaduple)
					print('TUPLE: ',field['user_id'], field['name'])
					if field['user_id'] == quaduple[0] and field['name'] == quaduple[1]:
						collection_topics.update_many(
							{
								'user_id':quaduple[0],
								'name':quaduple[1],
							},
							{
								'$set': {
									'connecteddevices':quaduple[2],
									'jwt':quaduple[3],
								}
							}
						)
		else:
			print("Device not found in collection_user.")

		return True

	return successtatus

def set_new_topic(usermodel, userid, topic):
	successtatus = ''
	userdata = ''
	collection_topic = ''
	temp = topic.copy()
	try:
		userdata = get_object_or_404(usermodel,pk=userid)
		collection_topic = connect('topics')
	except Exception as e:
		userdata = None
		print("Exception at set_new_topic:", e)
		successtatus = e

	if userdata is not None:
		usertopics = userdata.topics
		usertopics.append(temp)
		userdata.topics = usertopics
		print("userdata.topics TOPIC: ",userdata.topics )

		is_topic_exists = collection_topic.find_one({'name' :topic['name']})
		if is_topic_exists is None:
			collection_topic.insert(topic)

			collection_user = connect(userdata.username)
			collection_user.update_one({'username':userdata.username},{'$set':{'topics':usertopics}})
			userdata.save()

			return True

	print("Saving new topic from model failed ", successtatus)
	return successtatus

def update_topic(usermodel, userid, updated_topic, old_topic_name):
	successtatus = ''
	userdata = ''
	collection_user = ''
	SECRET_KEY = "Ki6wt83A5txZCX0FV0gbtuDazhhgFwd4"
	try:
		userdata = get_object_or_404(usermodel,pk=userid)
		collection_user = connect(userdata.username)
		collection_topics = connect('topics')
	except Exception as e:
		userdata = None
		print("Exception at set_new_device:", e)
		successtatus = e

	if userdata is not None:
		print('Old data:', userdata.topics)
		usertopics = userdata.topics
		updated_topic.update({'apiendpoint':'/'+updated_topic['name'].replace(" ","") })
		tokendata = {'username':userdata.username,
					'connecteddevices':updated_topic['connecteddevices'],}
		new_jwt = str(encode(tokendata, SECRET_KEY, algorithm='HS256'))
		updated_topic.update({'jwt':new_jwt})

		for index, element in enumerate(usertopics):
			if old_topic_name == element['name']:
				usertopics[index] = updated_topic

		print('New data: ', userdata.topics,'\n')
		userdata.topics = usertopics

		coll_user_topics_data = collection_user.find_one({'username':userdata.username})
		coll_topics_data = collection_topics.find_one({'user_id':userdata.id,'name':old_topic_name})

		if coll_user_topics_data is not None:
			collection_user.update_one(
				{'username':userdata.username},
				{'$set':
					{'topics':userdata.topics}
				})
			print("collection '"+userdata.username+"' is updated with new topic data")
		else:
			print("collection_user is NONE!")

		if coll_topics_data is not None:
			collection_topics.update_one(
				{'user_id':userdata.id,'name':old_topic_name},
				{'$set': {
					'description':updated_topic['description'],
					#'structure':updated_topic['structure'],
					'connecteddevices':updated_topic['connecteddevices'],
					'apiendpoint':updated_topic['apiendpoint'],
					'jwt':updated_topic['jwt'],
					}
				})
			print("collection 'topics' is updated with new topic data")
		else:
			print("collection 'topics' is NONE!")

		userdata.save()

		return True

	return successtatus

def delete_topic(usermodel, userid, old_topic_name):
	successtatus = ''
	userdata = ''
	collection_user = ''
	SECRET_KEY = "Ki6wt83A5txZCX0FV0gbtuDazhhgFwd4"
	try:
		userdata = get_object_or_404(usermodel,pk=userid)
		collection_user = connect(userdata.username)
		collection_topics = connect('topics')
	except Exception as e:
		userdata = None
		print("Exception at set_new_device:", e)
		successtatus = e
		return e

	if userdata is not None:
		user_topics = userdata.topics

		print("OLD DATA: ", user_topics)
		for index, topic in enumerate(user_topics):
			if old_topic_name == topic['name']:
				del user_topics[index]

		print("NEW DATA: ", user_topics, "\n")

		coll_user_topics_data = collection_user.find({'username':userdata.username})
		coll_topics_data = collection_user.find({'user_id':userdata.id,'name':old_topic_name})

		if coll_user_topics_data is not None:
			collection_user.update_one(
				{'username':userdata.username},
				{'$set':
					{'topics':userdata.topics}
				})
			print(old_topic_name+" topic deleted from collection '"+userdata.username+"'")
		else:
			print("collection_user is NONE!")

		if coll_topics_data is not None:
			collection_topics.delete_one(
				{
					'user_id':userdata.id,
					'name':old_topic_name
				})
			print(old_topic_name+" topic deleted from collection 'topics'")
		else:
			print("collection 'topics' is NONE!")

		userdata.save()
		return True
	return successtatus

def get_user_topic_data(usermodel, userid, topic_name):
	successtatus = ''
	userdata = ''
	collection_user = ''
	data_list = []

	try:
		userdata = get_object_or_404(usermodel,pk=userid)
		args = {
			"user": userdata.username,
			"topic": topic_name
		}
		conn = requests.post(
			"http://{}:{}/api/topicdata".format(gtwhost,gtwport),
			json=json.dumps(args),
			headers={
				'Content-type': 'application/json; charset=UTF-8'}
			)
		print(conn.status_code)
		if conn.status_code:
			data = json.loads(conn.text)
			data = data["data_list"]
	except Exception as e:
		userdata = None
		print("Exception at set_new_device:", e)
		successtatus = e
		return e

	if userdata is not None:
		data_list = data

		#return data_list, outer_keys, payload_keys
		return data_list
	else:
		return e

def get_user_topic_data_detailed(usermodel, userid, topic_name, data_id):
	successtatus = ''
	userdata = ''
	collection_user = ''
	data_list = []

	try:
		userdata = get_object_or_404(usermodel,pk=userid)
		args = {
			"user": userdata.username,
			"topic": topic_name,
			"oid": data_id
		}
		conn = requests.post(
			"http://{}:{}/api/datadetail".format(gtwhost,gtwport),
			json=json.dumps(args),
			headers={
				'Content-type': 'application/json; charset=UTF-8'}
			)
		print(conn.status_code)
		if conn.status_code:
			data = json.loads(conn.text)
			data = data["detailed_data"]
	except Exception as e:
		userdata = None
		print("Exception at set_new_device:", e)
		successtatus = e
		return e

	if userdata is not None:
		detailed_data = data
		# detailed_data = collection_user.find_one({"_id":ObjectId(data_id),"topic":'/'+topic_name})

		#return data_list, outer_keys, payload_keys
		return detailed_data
	else:
		return e


def connect(collname):
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

	coll = db[collname]

	return coll
	#PR: nanti buat collection yang di-return berdasarkan
	#username, ssuai kata Yani yaitu 1 user = 1 collection

def get_documentid(username):
	doc_id = get_userprofile(username)
	print(doc_id['_id'])
	return doc_id['_id']

def get_userprofile(username):
	collection = connect(username)
	userprofile = collection.find_one({'username':username})
	if userprofile:
		return userprofile
	else:
		print('NOT FOUND!')

#def set_userprofile(username, age, gender, body_height, body_weight):
def set_userprofile(username, info):
	type(info)
	newinfodict = info
	collection = connect(username)
	doc_id	 = get_userprofile(username)['_id']
	print("userjwt: ", get_userprofile(username)['userjwt'])
	result = collection.update_one({'_id':doc_id}, {"$set":newinfodict},upsert=False)

	return result


