from django.db import models

class Document(models.Model):
	SUMMARIZE_TYPES = (
		('LR','Lex Rank'),
		('LU','Luhn'),
		('LS','LSA'),
		('TR','Text Rank'),
		('ED','Edmundson'),
	)
	videoDwldURL = models.CharField(max_length=100,default='https://www.youtube.com/watch?v=X0lXytdjzQo')
	summarizeType = models.CharField(max_length=2,choices=SUMMARIZE_TYPES,default='LR')
	summarizationTime = models.DecimalField(max_digits=4, decimal_places=0, default=60)
	bonusWordsFile = models.FileField(upload_to='documents/',default='dummy.txt')
	stigmaWordsFile = models.FileField(upload_to='documents/',default='dummy.txt')
