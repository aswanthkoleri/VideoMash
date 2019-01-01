from django.db import models

class Document(models.Model):
	SUMMARIZE_TYPES = (
		('LR','Lex Rank'),
		('LU','Luhn'),
		('LS','LSA'),
		('TR','Text Rank'),
	)
	videoFile = models.FileField(upload_to='documents/',default='dummy.txt')
	subtitleFile = models.FileField(upload_to='documents/',default='dummy.txt')
	summarizeType = models.CharField(max_length=2,choices=SUMMARIZE_TYPES,default='LR')
	summarizationTime = models.DecimalField(max_digits=4, decimal_places=0, default=60)
	bonusWordsFile = models.FileField(upload_to='documents/',default='dummy.txt')
	stigmaWordsFile = models.FileField(upload_to='documents/',default='dummy.txt')

class Weight(models.Model):
	LR = models.FloatField()
	LU = models.FloatField()
	LS = models.FloatField()
	TR = models.FloatField()
