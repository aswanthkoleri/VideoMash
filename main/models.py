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
	summarizationTime = models.DecimalField(max_digits=4, decimal_places=0)
	bonusWordsFile = models.FileField(upload_to='documents/')
	stigmaWordsFile = models.FileField(upload_to='documents/')
