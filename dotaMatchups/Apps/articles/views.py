import ast
from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .models import Match, FullData
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
	"winrateLeft":round(winrate,1),
	"winrateRight":round(100-winrate,1)})


def update(request):
	maxMatchId=0
	matches_raw = requests.get('https://api.opendota.com/api/publicMatches?mmr_descending=10000').json()
	print("Recieved all")
	matchIds=[]
	for m in matches_raw[:30]:
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

			with open("dotaMatchups/Templates/json/heroes.json", "r") as file:
				heroNames=json.load(file)

			dire=[]
			radiant=[]
			for pickBan in match['pickBans']:
				if pickBan['isPick']:
					if pickBan['isRadiant']:
						radiant.append({"icon":"https://steamcdn-a.akamaihd.net"+heroNames[str(pickBan['heroId'])]['icon'],"name":heroNames[str(pickBan['heroId'])]['localized_name']})
					else:
						dire.append({"icon":"https://steamcdn-a.akamaihd.net"+heroNames[str(pickBan['heroId'])]['icon'],"name":heroNames[str(pickBan['heroId'])]['localized_name']})


			miders=midersFromStack(players)
			for i in range(0,2):
				if miders[i]['isRadiant']:
					miders[i]['team']=radiant
				else:
					miders[i]['team']=dire

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


def getForMain():
	result=[]
	mas=list(Match.objects.order_by("-matchId")[:30])
	for match in mas:
		evaled=ast.literal_eval(match.pair) #convert from string to [dict1,dict2]

		networthTiming1=networthForPlayer(0,evaled)
		networthTiming2=networthForPlayer(1,evaled)

		with open("dotaMatchups/Templates/json/heroes.json", "r") as file:
			heroNames=json.load(file)

		result.append( [
		{
		"heroIcon":"https://steamcdn-a.akamaihd.net"+heroNames[str(evaled[0]['heroId'])]['icon'],
		"kda":(evaled[0]['numKills']+evaled[0]['numAssists'])/(evaled[0]['numDeaths']+(1 if evaled[0]['numDeaths']==0 else 0)),
		"lastHits":evaled[0]['numLastHits'],
		"networthTiming":networthTiming1,
		"id":evaled[0]['heroId'],
		},
		{
		"heroIcon":"https://steamcdn-a.akamaihd.net"+heroNames[str(evaled[1]['heroId'])]['icon'],
		"kda":(evaled[1]['numKills']+evaled[1]['numAssists'])/(evaled[1]['numDeaths']+(1 if evaled[1]['numDeaths']==0 else 0)),
		"lastHits":evaled[1]['numLastHits'],
		"networthTiming":networthTiming2,
		"id":evaled[1]['heroId'],
		}
		])
	best=[0,0,0]
	maxnw=0
	maxlh=0
	maxkda=0
	for match in result:
		if match[0]["networthTiming"]['600']>maxnw:
			maxnw=match[0]["networthTiming"]['600']
			best[0]={"networth":maxnw,"player":match[0]["heroIcon"],"against":match[1]["heroIcon"],"id1":match[0]["id"],"id2":match[1]["id"]}
		elif match[1]["networthTiming"]['600']>maxnw:
			maxnw=match[1]["networthTiming"]['600']
			best[0]={"networth":maxnw,"player":match[1]["heroIcon"],"against":match[0]["heroIcon"],"id1":match[1]["id"],"id2":match[0]["id"]}

		if match[0]["kda"]>maxkda:
			maxkda=match[0]["kda"]
			best[1]={"kda":maxkda,"player":match[0]["heroIcon"],"against":match[1]["heroIcon"],"id1":match[0]["id"],"id2":match[1]["id"]}
		elif match[1]["kda"]>maxkda:
			maxkda=match[1]["kda"]
			best[1]={"kda":maxkda,"player":match[1]["heroIcon"],"against":match[0]["heroIcon"],"id1":match[1]["id"],"id2":match[0]["id"]}

		if match[0]["lastHits"]>maxlh:
			maxlh=match[0]["lastHits"]
			best[2]={"lastHits":maxlh,"player":match[0]["heroIcon"],"against":match[1]["heroIcon"],"id1":match[0]["id"],"id2":match[1]["id"]}
		elif match[1]["lastHits"]>maxlh:
			maxkda=match[1]["kda"]
			best[2]={"lastHits":maxlh,"player":match[1]["heroIcon"],"against":match[0]["heroIcon"],"id1":match[1]["id"],"id2":match[0]["id"]}



	return best



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
		"drawLane":abs(networthTiming1['600']-networthTiming2['600'])<=150,
		"team":evaled[0]['team']

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
		"drawLane":abs(networthTiming1['600']-networthTiming2['600'])<=150,
		"team":evaled[1]['team']
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

	data=getForMain()
	return render(request,"articles/main.html",{"data":data})
