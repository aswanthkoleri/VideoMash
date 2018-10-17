from django.db import models

class Document(models.Model):
	SUMMARIZE_TYPES = (
		('LR','Lex Rank'),
		('LU','Luhn'),
		('LS','LSA'),
		('TR','Text Rank'),
		('ED','Edmundson'),
	)
	videoFile = models.FileField(upload_to='documents/')
	subtitleFile = models.FileField(upload_to='documents/')
	summarizeType = models.CharField(max_length=2,choices=SUMMARIZE_TYPES,default='LR')