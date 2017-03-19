from django import forms
from django.db import models
from django.core.validators import MinValueValidator
from django.core.validators import MaxValueValidator

 
FREQUENCY_CHOICES = (
	('1', 'Daily'),
	('2', 'Twice weekly'),
	('3', 'Weekly'),
	('4', 'Twice monthly'),
	('5', 'Monthly'),
)

class ContactForm(forms.Form):
	name = forms.CharField(max_length=256)
	phone = forms.CharField(max_length=12)
	address = forms.CharField(max_length=256)
	url = forms.CharField(max_length=256)
	email = forms.CharField(max_length=256)
	frequency = forms.ChoiceField(choices=FREQUENCY_CHOICES, initial='3')
	followups = forms.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(25)], initial=15)
	
	def _str_(self):
		return self.name
		

class ReminderData(models.Model):
	name = forms.CharField(max_length=256)
	contacted = forms.IntegerField()
	id = forms.CharField(max_length=256)
	phone = forms.CharField(max_length=12)
	address = forms.CharField(max_length=256)
	
	def __init__(self, name, contacted, id, phone, address):
		self.name = name
		self.contacted = contacted
		self.id = id
		self.phone = phone
		self.address = address