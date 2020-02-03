from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .models import (get_userprofile, set_userprofile, set_new_device,
update_device,set_new_topic, update_topic, delete_device,
delete_topic,get_user_topic_data,get_user_topic_data_detailed)
from django.template.defaulttags import register
from .forms import CustomUserCreateDeviceForm, CustomUserCreateTopicForm
from jwt import encode, decode
from json import dumps, loads

@login_required(login_url=reverse_lazy('login'))
def main(request):
	currentuser = request.user
	package = currentuser.package
	limit = get_package_limit(package)
	topiclen = len(currentuser.topics)
	devicelen =len(currentuser.devicemacs)

	return render(request, 'userdashboard/main.html',
	{'userdata':currentuser,'limit':limit,'topiclen':topiclen,'devicelen':devicelen})

def get_package_limit(package):
	limit_switch = {
		"bronze":(1,3),
		"silver":(2,5),
		"gold":(3,7),
		"platinum":(5,10),
	}
	return limit_switch.get(package)

@login_required(login_url=reverse_lazy('login'))
def device(request):
	currentuser = request.user
	devicemacs = currentuser.devicemacs
	print(devicemacs)
	return render(request, 'userdashboard/device.html',
	{'devicemacs':devicemacs, 'userdata':currentuser})

@login_required(login_url=reverse_lazy('login'))
def devicecreate(request):
	if request.method == 'POST':
		form = CustomUserCreateDeviceForm(request.POST)

		if form.is_valid():
			currentuser = request.user
			limit = get_package_limit(currentuser.package)
			print(len(currentuser.devicemacs))
			print(limit)
			if len(currentuser.devicemacs) < limit[1]:
				name = form.cleaned_data['name']
				macaddress = form.cleaned_data['macaddress'].lower()
				newmac = ':'.join(macaddress[i:i+2] for i in range(0,12,2))
				print(currentuser.devicemacs)
				if\
				  check_name_and_macaddress(name,macaddress,currentuser.devicemacs):
					description = form.cleaned_data['description']
					status = form.cleaned_data['status']
					location = form.cleaned_data['location']

					device = {
						"macaddress":newmac,
						"name":name,
						"description":description,
						"status":status,
						"location":location,
					}
					print("DEVICE:",device)
					successtatus = set_new_device(get_user_model(),currentuser.id, device)
					if successtatus:
						return redirect('device')
					else:
						form = CustomUserCreateDeviceForm()
						errormessage = "An error occured in inserting data to\
						database: "+str(successtatus)
						return render(request,
						'userdashboard/device.html',{'form':form,'error':errormessage})
				else:
					form = CustomUserCreateDeviceForm()
					errormessage = "Your device 'name' or 'macaddress' is the\
					  same ase other devices. Please use another 'name' or\
					  'macaddress'"
					return render(request,
					'userdashboard/device.html',{'form':form,'error':errormessage})
			else:
				form = CustomUserCreateDeviceForm()
				errormessage = "You cannot add more device because of your\
				current package"
				return render(request,
				'userdashboard/device.html',{'form':form,'error':errormessage})
	else:
		form = CustomUserCreateDeviceForm()
	return render(request, 'userdashboard/devicecreate.html',{'form':form})

def check_name_and_macaddress(name, macaddress, devicemacs):
	for data in devicemacs:
		if data['name'] == name or data['macaddress'].replace(":", "") == macaddress or data['macaddress'] == macaddress:
			return False
	return True

@login_required(login_url=reverse_lazy('login'))
def devicedetail(request, device_name):
	currentuser = request.user
	device = {}
	for i in currentuser.devicemacs:
		if device_name == i['name'] :
			device = i
	#device = {k for k in dict(currentuser.devicemacs)}
	return render(request, 'userdashboard/devicedetail.html', {'device':device})

@login_required(login_url=reverse_lazy('login'))
def deviceupdate(request, device_name):
	device = {}
	currentuser = request.user
	for i in currentuser.devicemacs:
		if device_name == i['name'] :
			i['macaddress'] = i['macaddress'].replace(":", "")
			device = i

	if request.method == 'POST':
		form = CustomUserCreateDeviceForm(request.POST)
		if form.is_valid() and form.has_changed():
			print("Processing updated data..")

			updated_device = form.cleaned_data
			macaddress = updated_device['macaddress'].lower()
			newmac = ':'.join(macaddress[i:i+2] for i in range(0,12,2))
			updated_device.update({'macaddress':newmac})
			device.update({'macaddress':newmac})

			print(updated_device)
			successtatus = update_device(get_user_model(), currentuser.id,
			updated_device, device)

			if successtatus:
				return redirect('device')
			else:
				errormessage = str(successtatus)
				return render(request, 'userdashboard/deviceupdate.html',
				{'device':device,'form':form,'error':errormessage})
		else:
			print("No changed data.")

	else:
		form = CustomUserCreateDeviceForm(initial=device)

	form.fields['macaddress'].widget.attrs['readonly'] = True
	return render(request, 'userdashboard/deviceupdate.html',
	{'device':device,'form':form})

@login_required(login_url=reverse_lazy('login'))
def devicedelete(request, device_name):
	print("Deleting device.. ", device_name)
	currentuser = request.user
	devicemacs = currentuser.devicemacs
	if request.method == 'POST':
		print("Deleting "+ str(device_name) +"..")

		successtatus = delete_device(get_user_model(), currentuser.id,
		device_name)

		if successtatus == True:
			return redirect('device')
		else:
			errormessage = str(successtatus)
			print(errormessage)
			currentuser = request.user
			return render(request, 'userdashboard/device.html',
			{'devicemacs':device,'error':errormessage,})
	#return render(request, 'userdashboard/device.html',
	#{'devicemacs':device,})
	return redirect('device')

@login_required(login_url=reverse_lazy('login'))
def topic(request):
	currentuser = request.user
	topics = currentuser.topics
	print(topics)
	return render(request, 'userdashboard/topic.html',
	{'topics':topics, 'userdata':currentuser})
#REMEMBER: views yang nge-pass parameter di URL, parameternya musti
#didefinisikan di methods yang berhubungan dg URL itU
#PR: add if request.user.is_authenticated insde methods.

@login_required(login_url=reverse_lazy('login'))
def topiccreate(request):
	currentuser = request.user
	if request.method == 'POST':
		form = CustomUserCreateTopicForm(request.POST)
		devicelist = request.POST.getlist('devicelist')
		print(devicelist)

		if form.is_valid() and devicelist:
			limit = get_package_limit(currentuser.package)
			print(len(currentuser.topics))
			print(limit)
			if len(currentuser.topics) < limit[0]:
				name = form.cleaned_data['name'].strip()
				if\
				check_topics_name(name,currentuser.topics):
					print("Topic create form validation, getting data from\
					form..")
					description = form.cleaned_data['description']
					#structure = form.cleaned_data['structure']
					userjwt = get_jwt(currentuser,devicelist)
					topic = {
						"user_id":currentuser.id,
						"name":name,
						"description":description,
						#"structure":structure,
						"connecteddevices":get_macs(currentuser.devicemacs, devicelist),
						"apiendpoint":"/"+name,
						"jwt":userjwt,
					}
					successtatus =\
					set_new_topic(get_user_model(),currentuser.id, topic)
					if successtatus:
						print("Succes in saving topic data.")
						return redirect('topic')
					else:
						form = CustomUserCreateTopicForm()
						errormessage = "An error occured in inserting data to\
						database: "+str(successtatus)
						devices = [i['name'] for i in currentuser.devicemacs]
						print(errormessage)
						return render(request,
						'userdashboard/topiccreate.html',{'form':form,'error':errormessage,'devices':devices})
				else:
					form = CustomUserCreateTopicForm()
					errormessage = "Your topic 'name' is the\
					  same as other topic. Please use another 'name' "
					devices = [i['name'] for i in currentuser.devicemacs]
					print(errormessage)
					return render(request,
					'userdashboard/topiccreate.html',{'form':form,'error':errormessage,'devices':devices})
			else:
				form = CustomUserCreateTopicForm()
				errormessage = "You cannot add more topics because of your\
				current package"
				devices = [i['name'] for i in currentuser.devicemacs]
				print(errormessage)
				return render(request,
				'userdashboard/topiccreate.html',{'form':form,'error':errormessage,'devices':devices})
		else:
			form = CustomUserCreateTopicForm()
			errormessage = "Please tick one of the device box"
			devices = [i['name'] for i in currentuser.devicemacs]
			print(errormessage)
			return render(request,
			'userdashboard/topiccreate.html',{'form':form,'devices':devices,'error':errormessage})
	else:
		form = CustomUserCreateTopicForm()
		currentuser = request.user
		print("Returning topic create form..")
	devices = [i['name'] for i in currentuser.devicemacs]
	return render(request,
	  'userdashboard/topiccreate.html',{'form':form,'devices':devices,})

def check_topics_name(name, topics):
	for data in topics:
		if data['name'] == name :
			return False
	return True

def get_jwt(currentuser,devicelist):
	SECRET_KEY = "Ki6wt83A5txZCX0FV0gbtuDazhhgFwd4"
	macs = get_macs(currentuser.devicemacs, devicelist)
	tokendata = {'username':currentuser.username,'connecteddevices':macs,}
	jwttoken = encode(tokendata, SECRET_KEY, algorithm='HS256')
	return str(jwttoken)

def get_macs(devicemacs, devicelist):
	macs = []
	for i in devicemacs:
		for j in devicelist:
			if i['name'] == j:
				macs.append(i['macaddress'])
	return macs

@login_required(login_url=reverse_lazy('login'))
def topicdetail(request, topic_name):
	currentuser = request.user
	topics = {}
	connecteddevices = []
	devices = []
	for i in currentuser.topics:
		if topic_name == i['name'] :
			topics = i
			connecteddevices = i['connecteddevices']
			for j in currentuser.devicemacs:
				for k in connecteddevices:
					if j['name'] == k or j['macaddress'] == k:
							devices.append(j.copy())
	return render(request, 'userdashboard/topicdetail.html',
	{'topics':topics,'connecteddevices':devices})

@login_required(login_url=reverse_lazy('login'))
def topicupdate(request, topic_name):
	topic = {}
	connected_devices = []
	currentuser = request.user

	devices_mac = [i['connecteddevices'] for i in currentuser.topics if
	i['name'] == topic_name]
	for i in currentuser.topics:
		if topic_name == i['name']:
			topic = i
	for j in currentuser.devicemacs:
		for k in topic['connecteddevices']:
			if k == j['macaddress']:
				connected_devices.append(j['name'])

	unconnected_devices = [i['name'] for i in currentuser.devicemacs if
	i['name'] not in connected_devices]

	if request.method == 'POST':
		form = CustomUserCreateTopicForm(request.POST)
		checked_devicelist = request.POST.getlist('devicelist')
		print('checked_devicelist: ', checked_devicelist)

		#if form.is_valid() and checked_devicelist:
		if form.is_valid():
				print("Topic update form validated. Getting data from form..")
				updated_topic = form.cleaned_data
				device_dict =\
				{'connecteddevices':get_macs(currentuser.devicemacs,
				checked_devicelist)}
				updated_topic.update(device_dict)

				successtatus =\
				update_topic(get_user_model(),currentuser.id, updated_topic,
				topic_name)
				#successtatus = True
				if successtatus:
					print("Success in saving topic data.")
					return redirect('topic')
				else:
					#form = CustomUserCreateTopicForm()
					errormessage = "An error occured in inserting data to\
					database: "+str(successtatus)
					#devices = [i['name'] for i in currentuser.devicemacs]
					print(errormessage)
					return render(request,
					'userdashboard/topiccreate.html',{'form':form,'error':errormessage,'devices':devices})

	else:
		currentuser = request.user
		print("Returning topic create form to update "+topic_name+" topic...")

	form = CustomUserCreateTopicForm(initial=topic)
	form.fields['name'].widget.attrs['readonly'] = True
	return render(request,
	  'userdashboard/topicupdate.html',{'form':form,'topic':topic, 'connected_devices':connected_devices,'unconnected_devices':unconnected_devices, })

@login_required(login_url=reverse_lazy('login'))
def topicdelete(request, topic_name):
	currentuser = request.user
	devicemacs = currentuser.devicemacs
	if request.method == 'POST':
		print("Deleting topic.. ", topic_name)

		successtatus = delete_topic(get_user_model(), currentuser.id,
		topic_name)

		if successtatus == True:
			return redirect('topic')
		else:
			errormessage = str(successtatus)
			print(errormessage)
			currentuser = request.user
			return render(request, 'userdashboard/topic.html',
			{'devicemacs':device,'error':errormessage,})
	#return render(request, 'userdashboard/topic.html',
	#{'devicemacs':currentuser.topics,})
	return redirect('topic')

@login_required(login_url=reverse_lazy('login'))
def topicexplorer(request, topic_name):
	outer_keys = []
	outer_values = []
	payload_keys = []
	payload_values = []
	topic_data = get_user_topic_data(get_user_model(), request.user.id, topic_name)
	for dic in topic_data:
		for key in dic:
			if key == '_id':
				dic['id'] = dic.pop(key)
			elif key == 'payload':
				for inner_key in dic[key]:
					if inner_key not in payload_keys:
						print('payload_key: ', inner_key)
						payload_keys.append(inner_key)
				payload_values.append(dic[key])
			else:
				if key not in outer_keys:
					#print('key: ', key)
					outer_keys.append(key)
				outer_values.append(dic[key])
	#print('payload_values: ',payload_values)
	#print('outer_values: ',outer_values)
	return render(request, 'userdashboard/topicexplorer.html',
	{'topic_name':topic_name, 'topic_data':topic_data, 'outer_keys':outer_keys,
	'outer_values':outer_values, 'payload_keys':payload_keys,
	'payload_values':payload_values})

@login_required(login_url=reverse_lazy('login'))
def topicquery(request, topic_name, data_id):
	topic_data = get_user_topic_data_detailed(get_user_model(),request.user.id, topic_name, data_id)
	# topic_data['_id'] = str(topic_data['_id'])
	json_pretty = dumps(topic_data, indent=4)
	return render(request, 'userdashboard/topicquery.html',
	{'topic_name':topic_name, 'data_id':data_id, 'detailed_data':json_pretty})

@register.filter
def get_item(dictionary, key):
	if key == 'payload':
		list_data = []
		data = dictionary.get(key)
		for dic in data:
			data[dic] = "<th>"+str(data[dic])+"</th>"
			list_data.append(data[dic])
		return ' '.join(str(e) for e in list_data)
	else:
		return dictionary.get(key)

@login_required(login_url=reverse_lazy('login'))
def analytic(request):
	return render(request, 'userdashboard/analytic.html')

@login_required(login_url=reverse_lazy('login'))
def analyticwork(request):
	return render(request, 'userdashboard/analyticwork.html')

@login_required(login_url=reverse_lazy('login'))
def analyticstatistics(request):
	return render(request, 'userdashboard/analyticstatistics.html')

@login_required(login_url=reverse_lazy('login'))
def analytictrain(request):
	return render(request, 'userdashboard/analytictrain.html')

@login_required(login_url=reverse_lazy('login'))
def analyticpredict(request):
	return render(request, 'userdashboard/analyticpredict.html')

@login_required(login_url=reverse_lazy('login'))
def analyticclassify(request):
	return render(request, 'userdashboard/analyticclassify.html')

