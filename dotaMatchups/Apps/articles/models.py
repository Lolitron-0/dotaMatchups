from django.db import models
import datetime
from django.utils import timezone

class Match(models.Model):

	heroId1 = models.IntegerField("heroId1")
	heroId2 = models.IntegerField("heroId2")

	matchId = models.BigIntegerField("matchId")
	pair = models.TextField("pair")
	def __str__(self):
		return str(self.heroId1) + " -- " +  str(self.heroId2) +"   <-- "+ str(self.matchId)

class FullData(models.Model):
	data = models.TextField("data")
	match=models.OneToOneField(Match,on_delete=models.CASCADE,primary_key=True)
