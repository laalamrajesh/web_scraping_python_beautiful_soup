import requests
import bs4


def getYearBodyIndex(career_summary_table):
    index=0
    for body in career_summary_table:
        tr = body.find_all('tr')[1]
        td = tr.find_all('td')[0]
        if str(td).find("year")!=-1:
            return index
        index+=1
    return -1
players_file = open("players.txt","w+")
players_year_file = open("players_year_by_runs.txt","w+")
players_cumulative_year_file = open("players_cumulative_year_runs.txt","w+")


result = requests.get("http://stats.espncricinfo.com/ci/content/records/83548.html")

soup  = bs4.BeautifulSoup(result.text,'lxml')

tables = soup.select('.engineTable')

players_table = tables[0]

players = [] # players list

for tr in players_table.find_all('tr')[1:]:

    player = {}

    td_all = tr.find_all('td')

    a = str(td_all[0].select('a')[0]) #name and id td
    f_index = a.find(">")
    l_index = a.rfind("<")
    name = a[f_index+1  : l_index]

    f_index = a.find("player/")
    l_index = a.find(".html")
    id = a[f_index+len("player/")  : l_index]

    runs_td = str(td_all[5])  #runs td
    f_index = runs_td.find("<b>")
    l_index = runs_td.find("</b>")
    total_runs = runs_td[f_index+len("<b>") : l_index]

    country_td = str(td_all[0]) #country td
    f_index = country_td.find("(")
    l_index = country_td.find(")")
    country = country_td[f_index+1 : l_index]

    #player details
    player["name"]=name
    player["id"] = id
    player["total_runs"]=total_runs
    player["country"]=country


    players.append(player)


#print (players)



#calculating player year wise runs list

player_year_runs = {}
player_year_cumulative_runs = {}

for player in players:
    #print(player["id"])
    player_details = requests.get("http://stats.espncricinfo.com/ci/engine/player/"+player["id"]+".html?class=2;template=results;type=batting")
    soup  = bs4.BeautifulSoup(player_details.text,'lxml')
    tables = soup.select('.engineTable')
    career_summary_table = tables[3]

    year_body_index = getYearBodyIndex(career_summary_table.find_all('tbody'))
    year_wise_body = career_summary_table.find_all('tbody')[year_body_index]


    year_runs = {}
    cumulative_year_runs = {}
    cumulative_runs = 0

    for tr in year_wise_body.find_all('tr')[1:]:
        td_all = tr.find_all('td')

        year_td = str(td_all[0])  #year td
        f_index = year_td.find("<b>")
        l_index = year_td.find("</b>")
        year = year_td[f_index+len("<b>") : l_index].split(" ")[1]
        #print(year)

        runs_td = td_all[5]  #runs td
        runs_in_year = runs_td.text

        year_runs[year]=runs_in_year
        try:
            cumulative_runs+=int(runs_in_year)
            cumulative_year_runs[year]=cumulative_runs
        except:
            cumulative_year_runs[year]=cumulative_runs



    player_year_runs[player["id"]]= year_runs
    player_year_cumulative_runs[player["id"]] = cumulative_year_runs



#print(players)   #Dictionary list having Playername, total_runs, country , id(primary key)
#print(player_year_runs) #Dictionary list having id(primary key), year by runs
#print(player_year_cumulative_runs) #Dictionary list having id(primary key), cumulative year by runs

#file operations

players_file.write("Name\tCountry\tTotalRuns\n")
year_head = "Name\t"
for year in range(1971,2019+1):
    year_head+= str(year)+"\t"
year_head+="\n"
players_year_file.write(year_head)
players_cumulative_year_file.write(year_head)



for player in players:
    players_file.write(player["name"]+"\t\t"+player["country"]+"\t"+player["total_runs"]+"\n")

    year_by_runs = player["name"]+""
    cumulative_year_by_runs = player["name"]+""

    total_year_runs = player_year_runs[player["id"]]
    total_cumulative_runs = player_year_cumulative_runs[player["id"]]

    
    for year in range(1971,2019+1):
        try:
            year_by_runs += total_year_runs[str(year)]+" \t"
            cumulative_year_by_runs += str(total_cumulative_runs[str(year)])+"\t"
        except:
            year_by_runs += "  -  "+"\t"
            cumulative_year_by_runs += " - "+"\t"
    players_year_file.write(year_by_runs+"\n")
    players_cumulative_year_file.write(cumulative_year_by_runs+"\n")


players_file.close()
players_cumulative_year_file.close()
players_year_file.close()
