from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from .models import ContactForm
from .models import ReminderData
from django.core import serializers
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template import RequestContext, loader
from datetime import datetime
import time
import json
import os


# Code for the input form
def contact(request):
	json_data = open('contactData.json', 'a')
	if request.method == 'GET':
		form = ContactForm()
		json_data.close()
	else:
        # A POST request: Handle Form Upload
		form = ContactForm(request.POST) # Bind data from request.POST into a PostForm
 
        # If data is valid, proceeds to create a new post and redirect the user
		if form.is_valid():
			name = form.cleaned_data['name']
			phone = form.cleaned_data['phone']
			address = form.cleaned_data['address']
			url = form.cleaned_data['url']
			email = form.cleaned_data['email']
			frequency = form.cleaned_data['frequency']
			followups = form.cleaned_data['followups']
			id = str(datetime.now()).replace(" ","")
			
			# Creates a dict, converts it to a json string, and writes it to file.  LastContactDate is set to a past date so that it will appear on the reminder page when it's first added.
			data = {'Id': id, 'Name': name, 'Phone': phone, 'Address': address, 'Url': url, 'Email': email, 'Frequency': frequency, 'Followups': followups, 'Contacted': 0, 'LastContactDate': "01/01/00", 'Active': 1}
			json_string = json.dumps(data)
			json_data.write(json_string + '\n')
			json_data.close()
			return HttpResponseRedirect('')
	return render(request, 'AddContact/contact.html', {
		'form': form,
	})

# Code for the reminder page.  Parses the json file and sends the data to the template
def reminder(request):
	with open('contactData.json', 'r+') as file:
		data = []
		# Parses through each line of the json file
		for line in file:
			json_object = json.loads(line)
			json_id = json_object['Id']
			json_active = json_object['Active']
			json_name = json_object['Name']
			json_phone = json_object['Phone']
			json_address = json_object['Address']
			json_contacted = json_object['Contacted']
			json_followups = json_object['Followups']
			json_contactDate = json_object['LastContactDate']
			json_frequency = json_object['Frequency']
			entry = {'name': json_name, 'contacted': json_contacted}
			# Creates a new instance of the ReminderData class
			rdata = ReminderData(json_name, json_contacted, json_id, json_phone, json_address)
			# Checks if the entry should be displayed on the reminder form today
			display = checkEntry(json_contactDate, json_active, int(json_frequency), int(json_followups), int(json_contacted))
			if display == True:
				data.append(rdata)
	return render(request, 'AddContact/reminder.html', {'data': data})

# Code for both of the buttons on the reminder page
def update(request):
	id = request.POST['id']
	action = ""
	json_file = open('contactData.json', 'r+')
	json_string = ""
	
	# Checks whether the Mark as Contact or Remove from Contact button was selected
	if 'contacted' in request.POST:
		action = "contacted"
	if 'removed' in request.POST:
		action = "removed"
		
	for line in json_file:
		data = json.loads(line)
		if (id == data['Id']):
			# Contact button, increases the number of times contacted by 1 and updates the last contact date
			if action == "contacted":
				data['Contacted'] = str(int(data['Contacted'])+1)
				data['LastContactDate'] = time.strftime("%x")
				json_string += json.dumps(data) + "\n"
			# Remove button, sets the "Active" attribute to 0, preventing the entry from ever being displayed.  The entry isn't deleted from the database though
			elif action == "removed":
				data['Active'] = '0'
				json_string += json.dumps(data) + "\n"
		else:
			json_string += json.dumps(data) + "\n"
	json_file.close()
	
	with open('contactData.json', 'w+') as file:
		file.write(json_string)
	return HttpResponseRedirect('../reminder')

# Finds if the entry in the list should appear in the reminder page today
def checkEntry(date, active, frequency, followups, contacted):
	# Finds number of days passed and determines whether or not to display the data depending on how often the person is supposed to be contacted
	d = datetime.strptime(date, '%x').date()
	now = datetime.now().date()
	daysPassed = (now-d).days
	numDaysContact = 0
	if frequency == 1:
		numDaysContact = 1
	elif frequency == 2:
		numDaysContact = 3
	elif frequency == 3:
		numDaysContact = 7
	elif frequency == 4:
		numDaysContact = 15
	elif frequency == 5:
		numDaysContact = 30
    
	# Checks if enough days have passed, if the entry was removed, or if they've been contacted too many times
	if daysPassed < numDaysContact:
		return False
	elif active == '0':
		return False
	elif contacted >= followups:
		return False
	else:
		return True