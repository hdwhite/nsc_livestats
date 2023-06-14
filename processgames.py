import os
import re
import json
import time
import random

#Functions to print each bracket/team
#Print the standings of each bracket
def print_standings(bracket):
	#Sort by wins, then by total points, then random. Note that this can put a 2-3 team over a 2-2 team
	sortedbracket = dict(sorted(list(bracket.items()), key=lambda x: x[1]['wins']*10000 + x[1]['score'] + random.random(), reverse=True))
	tablestr = ""
	for curteam in sortedbracket.values():
		ppg = '{:.2f}'.format(curteam['score'] / (curteam['wins'] + curteam['losses']) if curteam['score'] != 0 else 0)
		ppb = '{:.2f}'.format(curteam['bonuses'] / (curteam['powers'] + curteam['tens']) if curteam['bonuses'] != 0 else 0)
		tablestr += "<tr><td><a href=\"#" + curteam['name'].replace(" ", "_") + "\" class=\"jump\">" + curteam['name'] + "</a></td>"
		tablestr += "<td>" + str(curteam['wins']) + " - " + str(curteam['losses']) + "</td><td>" + ppg + "</td><td>" + ppb + "</td></tr>\n"
	return tablestr

#Print the team vs. team bracket with game scores
def print_bracket(bracket):
	sortedbracket = dict(sorted(list(bracket.items()), key=lambda x: x[1]['wins']*10000 + x[1]['score'], reverse=True))
	tablestr = "<div class=\"scrollable\"><table><thead><tr><th>Team</th>\n"
	for curteam in sortedbracket.values():
		#Adding in non-breaking spaces before a team's letter designation to avoid annoying line breaks
		tablestr += "<th><a href=\"#" + curteam['name'].replace(" ", "_") + "\" class=\"jump\">" + re.sub(" (.)$", "&nbsp;\\1", curteam['name']) + "</a></th>"
	tablestr += "<th>Record</th></tr></thead><tbody>\n"
	for curteam in sortedbracket.values():
		tablestr += "<tr><td><a href=\"#" + curteam['name'].replace(" ", "_") + "\" class=\"jump\">" + re.sub(" (.)$", "&nbsp;\\1", curteam['name']) + "</a></td>"
		for curopp in sortedbracket.values():
			if curteam['name'] == curopp['name']:
				tablestr += "<td>---</td>"
			elif curopp['name'] not in curteam:
				tablestr += "<td></td>"
			elif curteam[curopp['name']]['status'] == "Pregame":
				tablestr += "<td>Round&nbsp;" + str(curteam[curopp['name']]['round']) + "</td>"
			else:
				curgame = curteam[curopp['name']]
				#The JSONs are generated such that Team 1 is always the winning team. Should probably be changed.
				if curgame['status'] == "F" and curgame['team1']['name'] == curteam['name']:
					tablestr += "<td class=\"win\">" + str(curgame['team1']['score']) + "-" + str(curgame['team2']['score']) + "<br>Round&nbsp;" + str(curgame['round']) + "</td>"
				elif curgame['status'] == "F":
					tablestr += "<td class=\"loss\">" + str(curgame['team2']['score']) + "-" + str(curgame['team1']['score']) + "<br>Round&nbsp;" + str(curgame['round']) + "</td>"
				elif curgame['team1']['name'] == curteam['name']:
					tablestr += "<td class=\"ongoing\">" + str(curgame['team1']['score']) + "-" + str(curgame['team2']['score']) + "<br>" + curgame['statuspart'] + "&nbsp;" + str(curgame['status']) + "</td>"
				else:
					tablestr += "<td class=\"ongoing\">" + str(curgame['team2']['score']) + "-" + str(curgame['team1']['score']) + "<br>" + curgame['statuspart'] + "&nbsp;" + str(curgame['status']) + "</td>"
		tablestr += "<td>" + str(curteam['wins']) + " - " + str(curteam['losses']) + "</td></tr>\n"
	tablestr += "</tbody></table></div>\n"
	return tablestr

#Print a team's list of games
def print_detailed(teamname, teaminfo):
	tablestr = "<div class=\"scrollable\"><table><thead><tr><th>Round</th><th>Opponent</th><th>Result</th><th><abbr title='Tossups Powered'>20</abbr></th><th><abbr title='Tossups Answered'>10</abbr></th>"
	tablestr += "<th><abbr title='Bonuses Heard'>BHrd</abbr></th><th><abbr title='Bonus Points'>BPts</abbr></th><th><abbr title='Points Per Bonus'>PPB</abbr></th></tr></thead><tbody>\n"
	gamelist = dict(sorted(teaminfo['games'].items()))
	for curgame in gamelist.values():
		#Don't include tiebreakers (which have round numbers >50)
		if curgame['round'] > 50:
			continue
		if curgame['status'] == "Pregame":
			if curgame['team1']['name'] == teamname:
				tablestr += "<tr class=\"future\"><td>" + str(curgame['round']) + "</td><td><a href=\"#" + curgame['team2']['name'].replace(" ", "_") + "\" class=\"jump\">" + curgame['team2']['name'] + "</a></td>"
			else:
				tablestr += "<tr class=\"future\"><td>" + str(curgame['round']) + "</td><td><a href=\"#" + curgame['team1']['name'].replace(" ", "_") + "\" class=\"jump\">" + curgame['team1']['name'] + "</a></td>"
			tablestr += "<td>Round&nbsp;" + str(curgame['round']) + "</td><td></td><td></td><td></td><td></td><td></td></tr>"
		else:
			if curgame['team1']['name'] == teamname:
				score = str(curgame['team1']['score']) + "-" + str(curgame['team2']['score'])
				opponent = curgame['team2']['name']
				powers = curgame['team1']['powers']
				tens = curgame['team1']['tens']
				bonuses = curgame['team1']['bonuses']
				if curgame['status'] == "F":
					style = "win"
				else:
					style = "ongoing"
					score += "<br>" + curgame['statuspart'] + " " + str(curgame['status'])
			else:
				score = str(curgame['team2']['score']) + "-" + str(curgame['team1']['score'])
				opponent = curgame['team1']['name']
				powers = curgame['team2']['powers']
				tens = curgame['team2']['tens']
				bonuses = curgame['team2']['bonuses']
				if curgame['status'] == "F":
					style = "loss"
				else:
					style = "ongoing"
					score += "<br>" + str(curgame['statuspart']) + " " + str(curgame['status'])
			ppb = '{:.2f}'.format(bonuses / (powers + tens) if bonuses > 0 else 0)
			tablestr += "<tr class=\"" + style + "\"><td>" + str(curgame['round']) + "</td><td><a href=\"#" + opponent.replace(" ", "_") + "\" class=\"jump\">" + opponent + "</a></td><td>" + score + "</td>"
			tablestr += "<td>" + str(powers) + "</td><td>" + str(tens) + "</td><td>" + str(powers + tens) + "</td><td>" + str(bonuses) + "</td><td>" + ppb + "</td></tr>\n"
	totalppb = '{:.2f}'.format(teaminfo['bonuses'] / (teaminfo['powers'] + teaminfo['tens']) if teaminfo['bonuses'] != 0 else 0)
	tablestr += "</tbody><tfoot><tr><td colspan=\"3\">Total</td><td>" + str(teaminfo['powers']) + "</td><td>" + str(teaminfo['tens']) + "</td>"
	tablestr += "<td>" + str(teaminfo['powers'] + teaminfo['tens']) + "</td><td>" + str(teaminfo['bonuses']) + "</td><td>" + totalppb + "</td></tr></tfoot></table></div></div>\n"
	return tablestr

st = time.time()
random.seed(1337) #Just so the sort by random doesn't cause unnecessary shuffling of teams
isplayoffs = True #Manutally setting whether we've reached the playoff and superplayoff phases
issupers = True
#A list of games that carry over from playoffs to superplayoffs. They're of the form "Team A": "Team B", "Team B": "Team A"
carryover = {"Barrington A": "Thomas Jefferson A", "Thomas Jefferson A": "Barrington A", "Dallas County": "Detroit Catholic Central A", "Detroit Catholic Central A": "Dallas County", "Thomas Jefferson B": "Canyon Crest", "Canyon Crest": "Thomas Jefferson B", "Hunter A": "St. Mark's", "St. Mark's": "Hunter A", "University Lab": "Solon", "Solon": "University Lab", "Maggie Walker A": "Dunbar", "Dunbar": "Maggie Walker A", "Rockford Auburn A": "Detroit Country Day", "Detroit Country Day": "Rockford Auburn A", "Plymouth": "Richard Montgomery", "Richard Montgomery": "Plymouth", "Mira Loma": "Woodland", "Woodland": "Mira Loma", "Belmont": "Winston Churchill A", "Winston Churchill A": "Belmont", "Kinkaid": "Troy", "Troy": "Kinkaid", "William Fremd": "Johns Creek A", "Johns Creek A": "William Fremd", "Thomas Jefferson C": "Chattahoochee A", "Chattahoochee A": "Thomas Jefferson C", "Johns Creek B": "Thomas Jefferson D", "Thomas Jefferson D": "Johns Creek B", "Barrington B": "Lincoln-Way East", "Lincoln-Way East": "Barrington B", "Irvington A": "Mexico", "Mexico": "Irvington A", "Hinsdale Central": "Winston Churchill B", "Winston Churchill B": "Hinsdale Central", "Innovation Academy A": "Chattahoochee B", "Chattahoochee B": "Innovation Academy A", "Northmont A": "Choate Rosemary Hall", "Choate Rosemary Hall": "Northmont A", "Winnebago": "Walter Payton", "Walter Payton": "Winnebago", "Maggie Walker C": "Midtown", "Midtown": "Maggie Walker C", "Heights": "Parkway West", "Parkway West": "Heights", "New Brighton": "Stevenson A", "Stevenson A": "New Brighton", "Carl Sandburg": "Carbondale", "Carbondale": "Carl Sandburg", "Mercer County": "Detroit Catholic Central C", "Detroit Catholic Central C": "Mercer County", "Washington": "Cincinnati Hills Christian", "Cincinnati Hills Christian": "Washington", "Waukee": "Hoover A", "Hoover A": "Waukee", "West Point": "Rockford Auburn B", "Rockford Auburn B": "West Point", "Stevenson B": "Hunter B", "Hunter B": "Stevenson B", "John Adams A": "Norman", "Norman": "John Adams A", "Hoover B": "Detroit Catholic Central B", "Detroit Catholic Central B": "Hoover B", "Belvidere": "Lake Highland", "Lake Highland": "Belvidere", "Moberly": "Norris", "Norris": "Moberly", "Northmont B": "Maggie Walker B", "Maggie Walker B": "Northmont B", "Saint Joseph": "Elkhorn North", "Elkhorn North": "Saint Joseph", "Innovation Academy B": "John Adams B", "John Adams B": "Innovation Academy B"}

#A list of teams in each bracket, sorted by seed
prelimpools = {"Acadia": ["Plymouth", "Troy", "Thomas Jefferson C", "Hinsdale Central", "Innovation Academy B", "Waukee"],\
"Badlands": ["Rockford Auburn A", "Midtown", "Maggie Walker A", "Norris", "Carbondale", "John Adams A"],\
"Carlsbad Caverns": ["Richard Montgomery", "William Fremd", "Northmont A", "Chattahoochee B", "Hunter B", "Detroit Catholic Central C"],\
"Denali": ["Dallas County", "Winston Churchill A", "Johns Creek B", "New Brighton", "Rockford Auburn B", "Elkhorn North"],\
"Everglades": ["Hunter A", "Thomas Jefferson B", "Irvington A", "Barrington B", "Washington", "Norman"],\
"Fort McHenry": ["Detroit Country Day", "Johns Creek A", "Parkway West", "Hoover B", "Winnebago", "Saint Joseph"],\
"Grand Canyon": ["University Lab", "Mira Loma", "Heights", "Mercer County", "Thomas Jefferson D", "Stevenson B"],\
"Hot Springs": ["Kinkaid", "Solon", "Choate Rosemary Hall", "Stevenson A", "Maggie Walker B", "Moberly"],\
"Isle Royale": ["Thomas Jefferson A", "Mexico", "Woodland", "Detroit Catholic Central B", "Lincoln-Way East", "John Adams B"],\
"Joshua Tree": ["Belmont", "Hoover A", "Canyon Crest", "Carl Sandburg", "Lake Highland", "Maggie Walker C"],\
"Kings Canyon": ["Barrington A", "Chattahoochee A", "Dunbar", "Winston Churchill B", "West Point", "Cincinnati Hills Christian"],\
"Lake Clark": ["St. Mark's", "Detroit Catholic Central A", "Innovation Academy A", "Walter Payton", "Belvidere", "Northmont B"]}

playoffpools = {"Arches": ["Barrington A", "Thomas Jefferson A", "Dallas County", "Detroit Catholic Central A", "Thomas Jefferson B", "Canyon Crest"],\
"Big Bend": ["Hunter A", "University Lab", "St. Mark's", "Solon", "Dunbar", "Maggie Walker A"],\
"Capitol Reef": ["Rockford Auburn A", "Detroit Country Day", "Plymouth", "Richard Montgomery", "Woodland", "Mira Loma"],\
"Death Valley": ["Belmont", "Kinkaid", "William Fremd", "Winston Churchill A", "Johns Creek A", "Troy"],\
"Effigy Mounds": ["Thomas Jefferson C", "Chattahoochee A", "Johns Creek B", "Thomas Jefferson D", "Barrington B", "Lincoln-Way East"],\
"Fossil Butte": ["Irvington A", "Mexico", "Innovation Academy A", "Chattahoochee B", "Hinsdale Central", "Winston Churchill B"],\
"Glacier": ["Northmont A", "Choate Rosemary Hall", "Midtown", "Walter Payton", "Winnebago", "Maggie Walker C"],\
"Haleakala": ["Parkway West", "Heights", "Carl Sandburg", "New Brighton", "Stevenson A", "Carbondale"],\
"Indiana Dunes": ["Mercer County", "Waukee", "Washington", "Detroit Catholic Central C", "Cincinnati Hills Christian", "Hoover A"],\
"Jewel Cave": ["West Point", "Hunter B", "John Adams A", "Rockford Auburn B", "Stevenson B", "Norman"],\
"Katmai": ["Hoover B", "Detroit Catholic Central B", "Lake Highland", "Moberly", "Norris", "Belvidere"],\
"Lassen Volcanic": ["Northmont B", "Maggie Walker B", "Elkhorn North", "Saint Joseph", "John Adams B", "Innovation Academy B"]}

superpools = {"Championship": ["Barrington A", "Hunter A", "Rockford Auburn A", "Belmont", "Thomas Jefferson A", "St. Mark's", "Detroit Country Day", "Winston Churchill A"],\
"9-16": ["Dallas County", "University Lab", "Plymouth", "Kinkaid", "Detroit Catholic Central A", "Solon", "Richard Montgomery", "Troy"],\
"17-24": ["Thomas Jefferson B", "Maggie Walker A", "Mira Loma", "William Fremd", "Canyon Crest", "Dunbar", "Woodland", "Johns Creek A"],\
"25-32": ["Thomas Jefferson C", "Irvington A", "Northmont A", "Heights", "Chattahoochee A", "Mexico", "Choate Rosemary Hall", "Parkway West"],\
"33-40": ["Johns Creek B", "Hinsdale Central", "Winnebago", "New Brighton", "Thomas Jefferson D", "Winston Churchill B", "Walter Payton", "Stevenson A"],\
"41-48": ["Barrington B", "Innovation Academy A", "Maggie Walker C", "Carl Sandburg", "Lincoln-Way East", "Chattahoochee B", "Midtown", "Carbondale"],\
"49-56": ["Mercer County", "West Point", "Hoover B", "Northmont B", "Detroit Catholic Central C", "Rockford Auburn B", "Detroit Catholic Central B", "Maggie Walker B"],\
"57-64": ["Washington", "Stevenson B", "Belvidere", "Saint Joseph", "Cincinnati Hills Christian", "Hunter B", "Lake Highland", "Elkhorn North"],\
"65-72": ["Waukee", "John Adams A", "Moberly" ,"Innovation Academy B", "Hoover A", "Norman", "Norris", "John Adams B"]}

#The 6-team and 8-team round-robin schedules used for the NSC. sixrr[a][b] is seed b's opponent in round a, 0-indexed
sixrr = [[4, 3, 5, 1, 0, 2], [3, 5, 4, 0, 2, 1], [1, 0, 3, 2, 5, 4], [5, 2, 1, 4, 3, 0], [2, 4, 0, 5, 1, 3]]
eightrr = [[5, 4, 7, 6, 1, 0, 3, 2], [6, 7, 4, 5, 2, 3, 0, 1], [7, 6, 5, 4, 3, 2, 1, 0], [3, 2, 1, 0, 7, 6, 5, 4], [2, 3, 0, 1, 6, 7, 4, 5], [1, 0, 3, 2, 5, 4, 7, 6]]

teamnames = []
ongoing = []
prelims = {}
playoffs = {}
supers = {}
teamdetails = {}

#Filling in all the scheduled games of the prelims
#prelims is of the structure bracket->team->opponent->game details
#Would cause issues with double RRs
for bracketname, curbracket in prelimpools.items():
	prelims[bracketname] = {}
	for seed, curteam in enumerate(curbracket):
		teamnames.append(curteam)
		#Obviously this works with the PACE format only
		prelims[bracketname][curteam] = {'name': curteam, 'score': 0, 'powers': 0, 'tens': 0, 'bonuses': 0, 'wins': 0, 'losses': 0}
		teamdetails[curteam] = {'brackets': {'prelims': bracketname, 'playoffs': "", 'supers': ""}, 'games': {}, 'score': 0, 'powers': 0, 'tens': 0, 'bonuses':0, 'wins':0, 'losses': 0}
		for curround in range(1, 6):
			#Gets opponent from the round-robin schedules
			opponent = curbracket[sixrr[curround-1][seed]]
			newgame = {'round': curround, 'status': "Pregame", 'team1': {'name': curteam}, 'team2': {'name': opponent}}
			prelims[bracketname][curteam][opponent] = newgame
			teamdetails[curteam]['games'][curround] = newgame

if isplayoffs:
	for bracketname, curbracket in playoffpools.items():
		playoffs[bracketname] = {}
		for seed, curteam in enumerate(curbracket):
			playoffs[bracketname][curteam] = {'name': curteam, 'score': 0, 'powers': 0, 'tens': 0, 'bonuses': 0, 'wins': 0, 'losses': 0}
			teamdetails[curteam]['brackets']['playoffs'] = bracketname
			for curround in range(6, 11): #Offset for playoff rounds
				opponent = curbracket[sixrr[curround-6][seed]]
				newgame = {'round': curround, 'status': "Pregame", 'team1': {'name': curteam}, 'team2': {'name': opponent}}
				playoffs[bracketname][curteam][opponent] = newgame
				teamdetails[curteam]['games'][curround] = newgame

if issupers:
	for bracketname, curbracket in superpools.items():
		supers[bracketname] = {}
		for seed, curteam in enumerate(curbracket):
			supers[bracketname][curteam] = {'name': curteam, 'score': 0, 'powers': 0, 'tens': 0, 'bonuses': 0, 'wins': 0, 'losses': 0}
			teamdetails[curteam]['brackets']['supers'] = bracketname
			for curround in range(11, 17):
				opponent = curbracket[eightrr[curround-11][seed]]
				newgame = {'round': curround, 'status': "Pregame", 'team1': {'name': curteam}, 'team2': {'name': opponent}}
				supers[bracketname][curteam][opponent] = newgame
				teamdetails[curteam]['games'][curround] = newgame

#Process all the JSONs of the games
teamnames.sort()
filelist = os.listdir("json") #Get all the files in that folder
for curfile in filelist:
	curgame = json.load(open("json/" + curfile, "r")) #It might be worth it to ensure it only takes .json files
	name1 = curgame['team1']['name']
	name2 = curgame['team2']['name']
	if name1 not in teamdetails: #Make sure that, say, PACE isn't reading games involving Chicago A
		continue
	if curgame['round'] is None: #There should be a round associated with a game
		continue
	if curgame['round'] > 50: #Means it's a tiebreaker/finals
		prelimgame = False
		playoffgame = False
		supergame = False
	elif curgame['round'] > 10:
		prelimgame = False
		playoffgame = False
		supergame = True
		bracket3 = teamdetails[name1]['brackets']['supers'] #bracket1, bracket2, bracket3 should probably be renamed
		if bracket3 != teamdetails[name2]['brackets']['supers']: #Both teams should be in the same bracket
			continue
		if supers[bracket3][name1][name2]['round'] != curgame['round']: #The game should happen at the scheduled round
			continue
	elif issupers and carryover[name1] == name2 and curgame['round'] > 5: #Carryover game
		prelimgame = False
		playoffgame = True
		supergame = True
		bracket2 = teamdetails[name1]['brackets']['playoffs']
		bracket3 = teamdetails[name1]['brackets']['supers']
		if bracket2 != teamdetails[name2]['brackets']['playoffs']:
			continue
		if bracket3 != teamdetails[name2]['brackets']['supers']:
			continue
		if playoffs[bracket2][name1][name2]['round'] != curgame['round']:
			continue
	elif isplayoffs and curgame['round'] > 5: #Non-carryover playoff game
		prelimgame = False
		playoffgame = True
		supergame = False
		bracket2 = teamdetails[name1]['brackets']['playoffs']
		if bracket2 != teamdetails[name2]['brackets']['playoffs']:
			continue
		if playoffs[bracket2][name1][name2]['round'] != curgame['round']:
			continue
	else: #Prelim game
		prelimgame = True
		playoffgame = False
		supergame = False
		bracket1 = teamdetails[name1]['brackets']['prelims']
		if bracket1 != teamdetails[name2]['brackets']['prelims']:
			continue
		if prelims[bracket1][name1][name2]['round'] != curgame['round']:
			continue
	
	if curgame['status'] == "F":
#		if curgame['round'] > 80: #Uncomment and change values to display tiebreakers/finals in the ongoing games list
#			ongoing.append(curgame)
		if curgame['round'] == 0:
			continue
		if prelimgame:
			#Add the prelim stats to the total for that team
			prelims[bracket1][name1]['score'] += curgame['team1']['score']
			prelims[bracket1][name2]['score'] += curgame['team2']['score']
			prelims[bracket1][name1]['powers'] += curgame['team1']['powers']
			prelims[bracket1][name2]['powers'] += curgame['team2']['powers']
			prelims[bracket1][name1]['tens'] += curgame['team1']['tens']
			prelims[bracket1][name2]['tens'] += curgame['team2']['tens']
			prelims[bracket1][name1]['bonuses'] += curgame['team1']['bonuses']
			prelims[bracket1][name2]['bonuses'] += curgame['team2']['bonuses']
			prelims[bracket1][name1]['wins'] += 1 #We assume team 1 wins
			prelims[bracket1][name2]['losses'] += 1
		if playoffgame:
			playoffs[bracket2][name1]['score'] += curgame['team1']['score']
			playoffs[bracket2][name2]['score'] += curgame['team2']['score']
			playoffs[bracket2][name1]['powers'] += curgame['team1']['powers']
			playoffs[bracket2][name2]['powers'] += curgame['team2']['powers']
			playoffs[bracket2][name1]['tens'] += curgame['team1']['tens']
			playoffs[bracket2][name2]['tens'] += curgame['team2']['tens']
			playoffs[bracket2][name1]['bonuses'] += curgame['team1']['bonuses']
			playoffs[bracket2][name2]['bonuses'] += curgame['team2']['bonuses']
			playoffs[bracket2][name1]['wins'] += 1
			playoffs[bracket2][name2]['losses'] += 1
		if supergame:
			supers[bracket3][name1]['score'] += curgame['team1']['score']
			supers[bracket3][name2]['score'] += curgame['team2']['score']
			supers[bracket3][name1]['powers'] += curgame['team1']['powers']
			supers[bracket3][name2]['powers'] += curgame['team2']['powers']
			supers[bracket3][name1]['tens'] += curgame['team1']['tens']
			supers[bracket3][name2]['tens'] += curgame['team2']['tens']
			supers[bracket3][name1]['bonuses'] += curgame['team1']['bonuses']
			supers[bracket3][name2]['bonuses'] += curgame['team2']['bonuses']
			supers[bracket3][name1]['wins'] += 1
			supers[bracket3][name2]['losses'] += 1
		#And now do the same for the team for the entire tournament
		teamdetails[name1]['score'] += curgame['team1']['score']
		teamdetails[name2]['score'] += curgame['team2']['score']
		teamdetails[name1]['powers'] += curgame['team1']['powers']
		teamdetails[name2]['powers'] += curgame['team2']['powers']
		teamdetails[name1]['tens'] += curgame['team1']['tens']
		teamdetails[name2]['tens'] += curgame['team2']['tens']
		teamdetails[name1]['bonuses'] += curgame['team1']['bonuses']
		teamdetails[name2]['bonuses'] += curgame['team2']['bonuses']
		teamdetails[name1]['wins'] += 1
		teamdetails[name2]['losses'] += 1
	else:
		ongoing.append(curgame)
#		if curgame['round'] > 16: #If we're past a phase, we can tell games before a certain round to not show up on the Ongoing Games feed in case for some reason it's still showing up as ongoing
#			ongoing.append(curgame)
	
	#And now put the game in the appropriate bracket/team dict
	if prelimgame:
		prelims[bracket1][name1][name2] = curgame
		prelims[bracket1][name2][name1] = curgame
	if playoffgame:
		playoffs[bracket2][name1][name2] = curgame
		playoffs[bracket2][name2][name1] = curgame
	if supergame:
		supers[bracket3][name1][name2] = curgame
		supers[bracket3][name2][name1] = curgame
	
	teamdetails[name1]['games'][curgame['round']] = curgame
	teamdetails[name2]['games'][curgame['round']] = curgame

#Now to start printing out the HTML file
#First we do ongoing games, if there are any
outstr = ""
if len(ongoing) > 0:
	#Honestly the sorting can be done better, especially when games are jumping around
	ongoing = sorted(ongoing, key=lambda game: game['round']*100 + game['status'], reverse=True)
#	ongoing = sorted(ongoing, key=lambda game: game['round']*100, reverse=True) #Use this line instead if there are finished tiebreaker/placement games in the ongoing list
	outstr += "<div id=\"ongoing\"><h2 id=\"Ongoing\">Ongoing Games</h2><div class=\"flexy\">\n"
	for curgame in ongoing:
		if curgame['status'] == "F":
			outstr += "<div class=\"tableblock\"><table><thead><tr><th colspan=\"4\">Round " + str(curgame['round']) + ", Final</th></tr></thead><tbody>\n"
		else:
			outstr += "<div class=\"tableblock\"><table><thead><tr><th colspan=\"4\">Round " + str(curgame['round']) + ", " + curgame['statuspart'] + " " + str(curgame['status']) + "</th></tr></thead><tbody>\n"
		if curgame['team1']['score'] >= curgame['team2']['score']:
			outstr += "<tr><td colspan=\"2\">" + curgame['team1']['name'] + "</td><td colspan=\"2\">" + str(curgame['team1']['score']) + "</td></tr>\n"
			outstr += "<tr><td colspan=\"2\">" + curgame['team2']['name'] + "</td><td colspan=\"2\">" + str(curgame['team2']['score']) + "</td></tr>\n"
		else:
			outstr += "<tr><td colspan=\"2\">" + curgame['team2']['name'] + "</td><td colspan=\"2\">" + str(curgame['team2']['score']) + "</td></tr>\n"
			outstr += "<tr><td colspan=\"2\">" + curgame['team1']['name'] + "</td><td colspan=\"2\">" + str(curgame['team1']['score']) + "</td></tr>\n"
		#Get the last three bonuses and display them
		outstr += "<tr><th>#</th><th>Team</th><th>TU</th><th>Bonus</th></tr>\n"
		for i in range(22):
			tustr = str(i)
			if curgame['status'] != "F" and tustr in curgame['lastthree']:
				curtu = curgame['lastthree'][tustr]
				if curtu['team'] == 0:
					outstr += "<tr><td>" + tustr + "</td><td colspan=\"3\">Unanswered</td><tr>"
				else:
					outstr += "<tr><td>" + tustr + "</td><td>" + curtu['team'] + "</td><td>" + str(curtu['points']) + "</td><td>"
					for curbonus in curtu['bonus']:
						outstr += "\U00002705" if curbonus == 10 else "\U0000274C"
					outstr += "</td></tr>"
		outstr += "</tbody></table></div>\n"
	outstr += "</div><div class=\"return\"><a href=\"#\">Back to top</a></div></div>\n"

#Now print the bracket standings
bracketheader = "<thead><tr><th>Team</th><th>Record</th><th><abbr title=\"Points Per Game\">PPG</abbr></th><th><abbr title=\"Points Per Bonus\">PPB</abbr></th></tr></thead>\n"
outstr += "<div id=\"standings\">\n"
if issupers:
	outstr += "<h2 id=\"Superplayoffs\">Superplayoff Standings</h2><div class=\"flexy\">\n"
	for curbracket in superpools:
		outstr += "<div class=\"tableblock\"><h3><a href=\"#" + curbracket + "\" class=\"jump\">" + curbracket + "</a></h3><div class=\"scrollable\"><table>" + bracketheader + "<tbody>\n"
		outstr += print_standings(supers[curbracket])
		outstr += "</tbody></table></div></div>\n"
	outstr += "</div><div class=\"return\"><a href=\"#\">Back to top</a></div>\n"

if isplayoffs:
	outstr += "<h2 id=\"Playoffs\">Playoff Standings</h2><div class=\"flexy\">\n"
	for curbracket in playoffpools:
		outstr += "<div class=\"tableblock\"><h3><a href=\"#" + curbracket + "\" class=\"jump\">" + curbracket + "</a></h3><div class=\"scrollable\"><table>" + bracketheader + "<tbody>\n"
		outstr += print_standings(playoffs[curbracket])
		outstr += "</tbody></table></div></div>\n"
	outstr += "</div><div class=\"return\"><a href=\"#\">Back to top</a></div>\n"

outstr += "<h2 id=\"Prelims\">Prelim Standings</h2><div class=\"flexy\">\n"
for curbracket in prelimpools:
	outstr += "<div class=\"tableblock\"><h3><a href=\"#" + curbracket + "\" class=\"jump\">" + curbracket + "</a></h3><div class=\"scrollable\"><table>" + bracketheader + "<tbody>\n"
	outstr += print_standings(prelims[curbracket])
	outstr += "</tbody></table></div></div>\n"
outstr += "</div><div class=\"return\"><a href=\"#\">Back to top</a></div></div>\n"

#And now the detailed bracket grid
outstr += "<div id=\"bracket\">\n"
if issupers:
	outstr += "<h2>Superplayoff Brackets</h2><div class=\"flexy\">\n"
	for curbracket in superpools:
		outstr += "<div class=\"tableblock\" id=\"" + curbracket + "\"><h3>" + curbracket + "</h3>\n"
		outstr += print_bracket(supers[curbracket])
		outstr += "</div>"
	outstr += "</div><div class=\"return\"><a href=\"#\">Back to top</a></div>\n"

if isplayoffs:
	outstr += "<h2>Playoff Brackets</h2><div class=\"flexy\">\n"
	for curbracket in playoffpools:
		outstr += "<div class=\"tableblock\" id=\"" + curbracket + "\"><h3>" + curbracket + "</h3>\n"
		outstr += print_bracket(playoffs[curbracket])
		outstr += "</div>"
	outstr += "</div><div class=\"return\"><a href=\"#\">Back to top</a></div>\n"
	
outstr += "<h2>Prelim Brackets</h2><div class=\"flexy\">\n"
for curbracket in prelimpools:
	outstr += "<div class=\"tableblock\" id=\"" + curbracket + "\"><h3>" + curbracket + "</h3>\n"
	outstr += print_bracket(prelims[curbracket])
	outstr += "</div>"
outstr += "</div><div class=\"return\"><a href=\"#\">Back to top</a></div></div>\n"

#Finally, print team details
outstr += "<div id=\"team\"><h2>Detailed Team Info</h2><div class=\"flexy\">\n"
for curteam in teamnames:
	outstr += "<div class=\"tableblock\" id=\"" + curteam.replace(" ", "_") + "\" class=\"jump\"><h3>" + curteam + "</h3>\n"
	outstr += "<h4><a href=\"#" + teamdetails[curteam]['brackets']['prelims'] + "\" class=\"jump\">Prelim bracket: " + teamdetails[curteam]['brackets']['prelims'] + "</a></h4>"
	if isplayoffs:
		outstr += "<h4><a href=\"#" + teamdetails[curteam]['brackets']['playoffs'] + "\" class=\"jump\">Playoff bracket: " + teamdetails[curteam]['brackets']['playoffs'] + "</a></h4>"
	if issupers:
		outstr += "<h4><a href=\"#" + teamdetails[curteam]['brackets']['supers'] + "\" class=\"jump\">Superplayoff bracket: " + teamdetails[curteam]['brackets']['supers'] + "</a></h4>"
	outstr += print_detailed(curteam, teamdetails[curteam])
outstr += "</div><div class=\"return\"><a href=\"#\">Back to top</a></div></div>\n"

#This and the number in index.html can be incremented to force a refresh
outstr += "0"

with open("livestats.html", "w") as outfile:
	outfile.write(outstr)

#Making sure it doesn't take too much time
elapsed = time.time() - st
print("Success in", elapsed, "seconds")
