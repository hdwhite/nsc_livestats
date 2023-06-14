<?php
header('Access-Control-Allow-Headers: Origin, X-Requested-With, Content-Type, Accept'); //CORS stuff can probably be done better
$qbjtext = file_get_contents('php://input');
$gameinfo = json_decode($qbjtext);
$gamestats = new stdClass();

//In this case, packets are of the form [text]##.json, though tiebreakers cause packet number and round number not to match
//Numbers greater than 60 mean tiebreakers/finals
//Note that by getting round number from packet number, we don't care what round number MODAQ says
if(!preg_match('/\d+\w?/', $gameinfo->packets, $match)) exit();
$packets = ["01" => 1, "02" => 2, "03" => 3, "04" => 4, "05" => 5, "06" => 61, "06A" => 61, "06B" => 62,
			"07" => 6, "08" => 7, "09" => 8, "10" => 9, "11" => 10, "12" => 71, "12A" => 71, "12B" => 72,
			"13" => 11, "14" => 12, "15" => 13, "16" => 14, "17" => 15, "18" => 16, "19" => 81, "19A" => 81, "19B" => 82,
			"20" => 91, "21" => 92];
if(!array_key_exists($match[0], $packets)) exit();
$curround = $packets[$match[0]];

$team1 = $gameinfo->match_teams[0]->team->name;
$team2 = $gameinfo->match_teams[1]->team->name;
$filename = $curround . "_" . str_replace(" ", "-", $team1) . "_" . str_replace(" ", "-", $team2);
if(empty($team1) || empty($team2)) exit(); //Make sure there are two teams playing

if($gameinfo->isFinished)
{
	$status = "F";
	$lastthree = null; //If the game's finished, don't track last three bonuses (but we probably could)
}
else
{
	//tossups_read is based on what tossup the moderator is on right now, but we need to catch the case where they're looking back for some reason
	$status = $gameinfo->tossups_read - 1; //0-indexed vs. 1-indexed
	for($i = count($gameinfo->match_questions) - 1; $i > $status; $i--)
	{
		if(count($gameinfo->match_questions[$i]->buzzes)) //If there's a buzz it means that TU had to have been read
		{
			$status = $i;
			break;
		}
	}

	//Figure out if a tossup or a bonus is being read
	if(property_exists($gameinfo->match_questions[$status], "bonus"))
	{
		$statuspart = "Bonus";
		$lasttu = $status;
	}
	else
	{
		$statuspart = "Tossup";
		$lasttu = $status - 1;
	}

	//Get the status of the last three tossups
	$lastthree = array();
	for($curtu = $lasttu; $curtu > $lasttu - 3 && $curtu >= 0; $curtu--)
	{
		$lastthree[$curtu+1] = ["team" => 0];
		foreach($gameinfo->match_questions[$curtu]->buzzes as $curbuzz)
			if($curbuzz->result->value > 0)
			{
				$lastthree[$curtu+1] = ["team" => $curbuzz->team->name, "points" => $curbuzz->result->value, "bonus" => []];
				for($i = 0; $i < 3; $i++)
					$lastthree[$curtu+1]["bonus"][$i] = $gameinfo->match_questions[$curtu]->bonus->parts[$i]->controlled_points;
			}
	}
	$status++;
}

//Now we're going to populate the stats for each team that will go in the smaller .json file
$team1stats = $gameinfo->match_teams[0];
$team2stats = $gameinfo->match_teams[1];
$bonus1 = $team1stats->bonus_points;
$bonus2 = $team2stats->bonus_points;
$buzzes1 = [20 => 0, 10 => 0];
$buzzes2 = [20 => 0, 10 => 0];
//I guess here we could get and display individual stats as well
foreach($team1stats->match_players as $curplayer)
	foreach($curplayer->answer_counts as $curbuzz)
		$buzzes1[$curbuzz->answer->value] += $curbuzz->number;
foreach($team2stats->match_players as $curplayer)
	foreach($curplayer->answer_counts as $curbuzz)
		$buzzes2[$curbuzz->answer->value] += $curbuzz->number;
$score1 = $bonus1 + $buzzes1[20]*20 + $buzzes1[10]*10;
$score2 = $bonus2 + $buzzes2[20]*20 + $buzzes2[10]*10;
//If it's a 0-0 game, there's a decent chance it's a phantom game, so ignore it
if($score1 == 0 && $score2 == 0)
	exit();
$team1obj = new stdClass();
$team2obj = new stdClass();
$team1obj->name = $team1;
$team2obj->name = $team2;
$team1obj->score = $score1;
$team2obj->score = $score2;
$team1obj->powers = $buzzes1[20]; //Should be 15 for mACF, and negs would need to be included
$team2obj->powers = $buzzes2[20];
$team1obj->tens = $buzzes1[10];
$team2obj->tens = $buzzes2[10];
$team1obj->bonuses = $bonus1;
$team2obj->bonuses = $bonus2;

$gamestats->round = $curround;
$gamestats->status = $status;
$gamestats->statuspart = $statuspart;
if($score1 >= $score2)
{
	$gamestats->team1 = $team1obj;
	$gamestats->team2 = $team2obj;
}
else
{
	$gamestats->team1 = $team2obj;
	$gamestats->team2 = $team1obj;
}
$gamestats->lastthree = $lastthree;

//Print the files. Obviously uncomment the lines when ready, but it could probably use with some more security
$file = fopen("json/$filename.json", "w");
//fwrite($file, json_encode($gamestats));
fclose($file);

$file = fopen("qbj/$filename.json", "w");
//fwrite($file, $qbjtext);
fclose($file);
?>
