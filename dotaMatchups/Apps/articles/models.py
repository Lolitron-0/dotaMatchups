from django.db import models
import datetime
from django.utils import timezone

class Article(models.Model):
	title = models.CharField('название статьи', max_length = 200)
	text = models.TextField('текст статьи');
	pub_date = models.DateTimeField('дата публикации')

	def __str__(self):
		return self.title

	def was_published_recently(self):
		return self.pub_date >= (timezone.now()-datetime.timedelta(days = 7))

	class Meta:
		verbose_name="Статья"
		verbose_name_plural="Статьи"

class Comment(models.Model):
	article = models.ForeignKey(Article, on_delete = models.CASCADE)
	author_name = models.CharField('имя автора', max_length = 50)
	comment_text = models.CharField('текст комментария', max_length = 200);

	def __str__(self):
		return self.author_name +"->"+ self.article.title

	class Meta:
		verbose_name="Комментарий"
		verbose_name_plural="Комментарии"

class Match(models.Model):

	heroId1 = models.IntegerField("heroId1")
	#isVictory=models.BooleanField()
	#kills1 = models.IntegerField("kills1")
	#deaths1= models.IntegerField("deaths1")
	#assists1= models.IntegerField("assists1")
	#lastHits1= models.IntegerField("//'lastHits1")
	#denies1= models.IntegerField("denies1")
	#networth1= models.IntegerField("networth1")

	heroId2 = models.IntegerField("heroId2")
	#kills2 = models.IntegerField("kills2")
	#deaths2= models.IntegerField("deaths2")
	#assists2= models.IntegerField("assists2")
	#lastHits2= models.IntegerField("lastHits2")
	#denies2= models.IntegerField("denies2")
	#networth2= models.IntegerField("networth2")


	matchId = models.BigIntegerField("matchId")
	pair = models.TextField("pair")
	def __str__(self):
		return str(self.heroId1) + " -- " +  str(self.heroId2) +"   <-- "+ str(self.matchId)

class FullData(models.Model):
	data = models.TextField("data")
	match=models.OneToOneField(Match,on_delete=models.CASCADE,primary_key=True)
