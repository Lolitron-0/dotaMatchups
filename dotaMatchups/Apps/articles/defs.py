import ast
from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .models import Match, FullData
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
import requests
from bs4 import BeautifulSoup
import json



#deletion all unuseful headers from player
def normalize(pair):
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
		return str(pair)

def selectFromDB(id1,id2):
	if id1==0 and id2==0:
		mas=list(Match.objects.all())
		temp=[]
	elif id1==0:
		mas=list(Match.objects.filter(heroId2=id2))
		temp=list(Match.objects.filter(heroId1=id2))
	elif id2==0:
		mas=list(Match.objects.filter(heroId1=id1))
		temp=list(Match.objects.filter(heroId2=id1))
	else:
		mas=list(Match.objects.filter(heroId1=id1,heroId2=id2))
		temp=Match.objects.filter(heroId1=id2,heroId2=id1)
	for obj in temp:
		mas.append(obj)
	return mas

def swapByIds(evaled,id1,id2):
    if id1!=0 and id2!=0:
        if evaled[0]['heroId']!=id1:
            evaled[0],evaled[1]=evaled[1],evaled[0]
    elif id1==0:
        if evaled[0]['heroId']!=id2:
            evaled[0],evaled[1]=evaled[1],evaled[0]
    elif id2==0:
        if evaled[0]['heroId']!=id1:
            evaled[0],evaled[1]=evaled[1],evaled[0]

def networthForPlayer(player,evaled):
    networthTiming={}
    for event in evaled[player]['playbackData']['playerUpdateGoldEvents']:
        networthTiming[str(event['time'])]=event['networth']
    return networthTiming

def extractAbilities(abilitiesTiming1, abilitiesTiming2 ,evaled):
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

def extractItems(purchaseEvents1, purchaseEvents2 ,evaled):
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

def midersFromStack(players):
    miders=[]
    p1=''
    p2=''
    for player in players:
        try:
            if player['lane']==2:
                if p1!='':
                    p2=player
                else:
                    p1=player
        except:
            print('nolane')
    if p1!='' and p2!='':
        if(p1['heroId']<p2['heroId']): #Creating  mid pair [dict1,dict2]
            miders=[p1,p2]
        else:
            miders=[p2,p1]
    p1=''
    p2=''
    return miders

def dbContainsSuchId(id):
	mas=list(Match.objects.filter(matchId=id))
	return len(mas)>0
