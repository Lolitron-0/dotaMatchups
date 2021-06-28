import ast
from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .models import Article, Comment, Match, FullData
from .defs import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
import requests
from bs4 import BeautifulSoup
import json



def temp(request):
	all=Match.objects.all()
	for obj in all:
		print(obj.matchId)
		pair=ast.literal_eval(obj.pair)
		print('evaled')
		fullData=FullData(data=str(pair),match=obj)
		fullData.save()
		result={}
		for key in pair[1]:
			if key!='heroAverage':
				result[key]=pair[1][key]
		pair[1]=result
		result={}
		for key in pair[0]:
			if key!='heroAverage':
				result[key]=pair[0][key]
		pair[0]=result
		for player in pair:
			result={}
			for key in player['playbackData']:
				if key=='playerUpdateGoldEvents':
					networthTiming=[]
					for event in player['playbackData']['playerUpdateGoldEvents']:
						if event['time']%15==0:
							networthTiming.append(event)
					player['playbackData']['playerUpdateGoldEvents']=networthTiming
				if key!='abilityUsedEvents' and \
				key!='abilityActiveLists' and \
				key!='itemUsedEvents' and \
				key!='playerUpdatePositionEvents' and \
				key!='playerUpdateAttributeEvents' and \
				key!='playerUpdateLevelEvents' and \
				key!='playerUpdateHealthEvents' and \
				key!='playerUpdateBattleEvents' and \
				key!='killEvents' and \
				key!='deathEvents' and \
				key!='assistEvents' and \
				key!='csEvents' and \
				key!='goldEvents' and \
				key!='experienceEvents' and \
				key!='healEvents' and \
				key!='heroDamageEvents' and \
				key!='towerDamageEvents' and \
				key!='inventoryEvent' and \
				key!='buyBackEvents' and \
				key!='streakEvents' and \
				key!='spiritBearInventoryEvents':
					result[key]=player['playbackData'][key]
			player['playbackData']=result
		obj.pair=str(pair)
		obj.save()

def index(request,id1,id2):
	data=get(id1,id2)
	sum=0.0
	winrate=0
	try:
		for matchUp in data:
			sum+=(1 if matchUp[0]['isVictory'] else 0)
			winrate=sum/len(data)
			winrate=winrate*100
	except:
		winrate=0
	return render(request,'articles/list.html',{'data':data,
	"isEmpty": len(data)==0,
	"winrateLeft":winrate,
	"winrateRight":100-winrate})


def update(request):
	maxMatchId=0
	matches_raw = requests.get('https://api.opendota.com/api/publicMatches?mmr_descending=10000').json()
	print("Recieved all")
	matchIds=[]
	for m in matches_raw:
		if dbContainsSuchId(m['match_id']): #checking unique
			print("contains")
		else:
			matchIds.append(m['match_id']) #Getting matches by descending mmr in json (OPENDOTA)
			print("OK")

	for id in matchIds:
		try:
			print("-------")
			print(id)
			r=requests.get('https://api.stratz.com/api/v1/match/'+str(id)) #Requesting more information about evety match (STRATZ)
			print("Remaining requests: "+str(r.headers['X-RateLimit-Remaining-Hour']))
			match=r.json()
			print(str(id)+" <-Rendered")
			players=match['players']   #Extracting players


			miders=midersFromStack(players)

			temp = Match()
			temp.heroId1=miders[0]['heroId']
			temp.heroId2=miders[1]['heroId']
			temp.matchId=miders[0]['matchId']
			temp.pair=normalize(miders)
			temp.save()  #Saving miders to DB  -- Pair->list of two miders  heroId1&heroId2 ids for extracting relevant matches
			fullData=FullData(data=str(miders),match=temp) #
			fullData.save()
			print("saved")
		except:
			print("oui")
	return HttpResponseRedirect(reverse("articles:main"))


#[get] but by match id
def moreInfo(match):
	evaled=ast.literal_eval(match.pair) #convert from string to [dict1,dict2]
	networthTiming1={}
	networthTiming2={}
	for event in evaled[0]['playbackData']['playerUpdateGoldEvents']:
		if (event['time'] % 15 )==0:
			networthTiming1[str(event['time'])]=event['networth']
	for event in evaled[1]['playbackData']['playerUpdateGoldEvents']:
		if (event['time'] % 15 )==0:
			networthTiming2[str(event['time'])]=event['networth']


#All info scanning from cascade of json files
	#Abilities for each
	abilitiesTiming1=[]
	abilitiesTiming2=[]
	with open("dotaMatchups/Templates/json/abilities.json", "r") as file:
		abilitiesInfo=json.load(file)
	with open("dotaMatchups/Templates/json/ability_ids.json", "r") as file:
		abilitiesNames=json.load(file)

	def addToAbilities(mas,event):
		try:
			img="https://steamcdn-a.akamaihd.net"+abilitiesInfo[abilitiesNames[str(event['abilityId'])]]['img']
		except:
			img="https://ru.dotabuff.com/assets/skills/talent-a12822c609ce0c17b85811b1b3c1bb882de6f0b9f67b7fdc19800e8db2c28ae3.jpg"
		min=str(event['time']//60)
		sec=("0" if abs(event['time'])%60<10 else "")+str(abs(event['time'])%60)
		try:
			name=abilitiesInfo[abilitiesNames[str(event['abilityId'])]]['dname']
		except:
			name="+ all stats"
		mas.append({
		"name":name,
		"time":min+":"+sec,
		"timeInMin":int(min),
		'icon':img})

	for event in evaled[0]['playbackData']['abilityLearnEvents']:
		addToAbilities(abilitiesTiming1,event)
	for event in evaled[1]['playbackData']['abilityLearnEvents']:
		addToAbilities(abilitiesTiming2,event)



	#Items for each
	purchaseEvents1=[]
	purchaseEvents2=[]
	with open("dotaMatchups/Templates/json/item_ids.json", "r") as file:
		itemNames=json.load(file)
	with open("dotaMatchups/Templates/json/items.json", "r") as file:
		itemInfo=json.load(file)

	def addToPurchased(mas,event):
		min=str(event['time']//60)
		sec=("0" if abs(event['time'])%60<10 else "")+str(abs(event['time'])%60)
		core=itemInfo[itemNames[str(event['item'])]]['cost']>2000
		if event['time']//60<=10 :
			mas.append({
			"name":itemInfo[itemNames[str(event['item'])]]['dname'],
			"core":core,
			"time":min+":"+sec,
			"timeInMin":int(min),
			'icon':"https://steamcdn-a.akamaihd.net"+itemInfo[itemNames[str(event['item'])]]['img']})
		elif itemInfo[itemNames[str(event['item'])]]['dname'].find("Recipe") == -1 and (itemInfo[itemNames[str(event['item'])]]['created'] or itemInfo[itemNames[str(event['item'])]]['cost']>=1400 ):
			mas.append({
			"name":itemInfo[itemNames[str(event['item'])]]['dname'],
			"core":core,
			"time":min+":"+sec,
			"timeInMin":int(min),
			'icon':"https://steamcdn-a.akamaihd.net"+itemInfo[itemNames[str(event['item'])]]['img']})

	for event in evaled[0]['playbackData']['purchaseEvents']:
		addToPurchased(purchaseEvents1,event)
	for event in evaled[1]['playbackData']['purchaseEvents']:
		addToPurchased(purchaseEvents2,event)

	with open("dotaMatchups/Templates/json/heroes.json", "r") as file:
		heroNames=json.load(file)
	return ( [
	{
	"matchId":evaled[0]['matchId'],
	"heroName":heroNames[str(evaled[0]['heroId'])]['localized_name'],
	"heroId":evaled[0]['heroId'],
	"heroIcon":"https://steamcdn-a.akamaihd.net"+heroNames[str(evaled[0]['heroId'])]['icon'],
	"abilityIcon":"https://steamcdn-a.akamaihd.net"+heroNames[str(evaled[0]['heroId'])]['icon'],
	"isVictory":evaled[0]['isVictory'],
	"kills":evaled[0]['numKills'],
	"deaths":evaled[0]['numDeaths'],
	"assists":evaled[0]['numAssists'],
	"goldPerMinute":evaled[0]['goldPerMinute'],
	"lastHits":evaled[0]['numLastHits'],
	"denies":evaled[0]['numDenies'],
	'abilitiesTiming':abilitiesTiming1,
	"purchase":purchaseEvents1,
	"networthTiming":networthTiming1,
	"networth":evaled[0]['networth'],
	"winLane":networthTiming1['600']>networthTiming2['600'],
	"drawLane":abs(networthTiming1['600']-networthTiming2['600'])<=150

	},
	{
	"matchId":evaled[1]['matchId'],
	"heroName":heroNames[str(evaled[1]['heroId'])]['localized_name'],
	"heroId":evaled[1]['heroId'],
	"heroIcon":"https://steamcdn-a.akamaihd.net"+heroNames[str(evaled[1]['heroId'])]['icon'],
	"abilityIcon":"https://steamcdn-a.akamaihd.net"+heroNames[str(evaled[1]['heroId'])]['icon'],
	"isVictory":evaled[1]['isVictory'],
	"kills":evaled[1]['numKills'],
	"deaths":evaled[1]['numDeaths'],
	"assists":evaled[1]['numAssists'],
	"goldPerMinute":evaled[1]['goldPerMinute'],
	"lastHits":evaled[1]['numLastHits'],
	"denies":evaled[1]['numDenies'],
	'abilitiesTiming':abilitiesTiming2,
	"purchase":purchaseEvents2,
	"networthTiming":networthTiming2,
	"networth":evaled[1]['networth'],
	"winLane":networthTiming2['600']>networthTiming1['600'],
	"drawLane":abs(networthTiming1['600']-networthTiming2['600'])<=150
	}
	])

#get all relevant matches in correct form
def get(id1,id2):
	result=[]
	mas=selectFromDB(id1,id2)
	for match in mas:

		evaled=ast.literal_eval(match.pair) #convert from string to [dict1,dict2]
		swapByIds(evaled,id1,id2)

		networthTiming1=networthForPlayer(0,evaled)
		networthTiming2=networthForPlayer(1,evaled)


		abilitiesTiming1=[]
		abilitiesTiming2=[]
		extractAbilities(abilitiesTiming1,abilitiesTiming2,evaled)

		#Items for each
		purchaseEvents1=[]
		purchaseEvents2=[]
		extractItems(purchaseEvents1,purchaseEvents2,evaled)

		with open("dotaMatchups/Templates/json/heroes.json", "r") as file:
			heroNames=json.load(file)

		result.append( [
		{
		"matchId":evaled[0]['matchId'],
		"heroName":heroNames[str(evaled[0]['heroId'])]['localized_name'],
		"heroId":evaled[0]['heroId'],
		"heroIcon":"https://steamcdn-a.akamaihd.net"+heroNames[str(evaled[0]['heroId'])]['icon'],
		"abilityIcon":"https://steamcdn-a.akamaihd.net"+heroNames[str(evaled[0]['heroId'])]['icon'],
		"isVictory":evaled[0]['isVictory'],
		"kills":evaled[0]['numKills'],
	 	"deaths":evaled[0]['numDeaths'],
		"assists":evaled[0]['numAssists'],
		"goldPerMinute":evaled[0]['goldPerMinute'],
		"lastHits":evaled[0]['numLastHits'],
		"denies":evaled[0]['numDenies'],
		'abilitiesTiming':abilitiesTiming1,
		"purchase":purchaseEvents1,
		"networthTiming":networthTiming1,
		"networth":evaled[0]['networth'],
		"winLane":networthTiming1['600']>networthTiming2['600'],
		"drawLane":abs(networthTiming1['600']-networthTiming2['600'])<=150

		},
		{
		"matchId":evaled[1]['matchId'],
		"heroName":heroNames[str(evaled[1]['heroId'])]['localized_name'],
		"heroId":evaled[1]['heroId'],
		"heroIcon":"https://steamcdn-a.akamaihd.net"+heroNames[str(evaled[1]['heroId'])]['icon'],
		"abilityIcon":"https://steamcdn-a.akamaihd.net"+heroNames[str(evaled[1]['heroId'])]['icon'],
		"isVictory":evaled[1]['isVictory'],
		"kills":evaled[1]['numKills'],
	 	"deaths":evaled[1]['numDeaths'],
		"assists":evaled[1]['numAssists'],
		"goldPerMinute":evaled[1]['goldPerMinute'],
		"lastHits":evaled[1]['numLastHits'],
		"denies":evaled[1]['numDenies'],
		'abilitiesTiming':abilitiesTiming2,
		"purchase":purchaseEvents2,
		"networthTiming":networthTiming2,
		"networth":evaled[1]['networth'],
		"winLane":networthTiming2['600']>networthTiming1['600'],
		"drawLane":abs(networthTiming1['600']-networthTiming2['600'])<=150
		}
		])
	return result


def main(request): #Choosing heroes
	if request.method=="POST":
		try:
			id1=int(request.POST['choice1'])
			id2=int(request.POST['choice2'])
		except:
			id1=0
			id2=0
		return HttpResponseRedirect(reverse('articles:index', args=(id1,id2,)))

	data=[]
	for match in Match.objects.order_by('-matchId')[:5]:
		data.append(moreInfo(match))
	return render(request,"articles/main.html",{"latest":data})
