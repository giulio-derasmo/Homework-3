# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from datetime import datetime
import re
import numpy as np
import heapq

# 1.3 Parse attributes 

def parse_time(dates):
# input: date >> a string of various format:
#            1)    Month day, Year to Month day, Year
#            2)    Month day, Year
#            3)    Year to Year

    # if we are in case 1 and 3 (there is a "to" in the string)
    if re.search("to", dates):
        # separate the start and the end date
        clean_date = [re.sub("\n","",date).strip() for date in dates.split("to")]
        # if we are in case 1 (Month day,Year)
        if re.search(",",clean_date[0]):
            # %b = for abbreviate month
            release = datetime.strptime(re.sub(",","",clean_date[0]), '%b %d %Y')
            # not everyone as end date (for example: still airing)
            # Month day, Year to ??
            try:
                end = datetime.strptime(re.sub(",","",clean_date[1]), '%b %d %Y')
            except:
                end = None
        # else we are in case 3
        else:
            release = datetime.strptime(clean_date[0], '%Y')
            end = datetime.strptime(clean_date[1], '%Y')
    # else we are in case 2 (for example film)
    else:
        clean_date = dates.replace(",","").strip()
        release = datetime.strptime(clean_date, '%b %d %Y')
        end = None
        
    return release, end


def scrabbing_anime1(soup, anime_info):
    # Anime Title
    # <h1 class="title-name h1_bold_none"><strong>Fullmetal Alchemist: Brotherhood</strong></h1>
    title = soup.find("h1", attrs = {"class": "title-name h1_bold_none"}).string
    # Taken Information
    # <h2>Information</h2> , there are a lot of h2 so i specify is written >>inside a div<<
    for h2 in soup.select('h2:has(+div)'):
        # I want the <h2> Information </h2> only
        if h2.text == "Information" :
            # iter over the next 4 <div> of Information, i go this way because
            # 1) i want to skip the "Status": is the 3th div
            # 2) more clear
            for inform in h2.find_all_next("div", attrs = {"class": "spaceit_pad"}, limit = 4):
                # Type
                if inform.contents[1].string == "Type:":
                    Type = inform.get_text(separator=" ", strip=True).split()[-1] 
                # nEpisodes
                try:
                    if inform.contents[1].string == "Episodes:":
                        nEpisodes = int(inform.get_text(separator=" ", strip=True).split()[-1])
                except:
                    nEpisodes = None
                # Relaese and end date
                if inform.contents[1].string == "Aired:":
                    # not always the date of start/end is store
                    # i can have NA value
                    try:
                        # take the string of where the data is store
                        date = inform.contents[2]
                        release_date, end_date = parse_time(date)
                    except:
                        release_date = None
                        end_date = None
    
    # save on anime info
    anime_info.extend((title,Type,nEpisodes,release_date,end_date))
    return anime_info



# Score, Ranked, Poplarity, Members
def scrabbing_anime2(soup, anime_info):
    #animeNumMembers
    members = soup.find("span",{"class":"numbers members"})
    members = int(members.find('strong').contents[0].replace(",",""))
    #animeScore
    score = soup.find("div", attrs = {"class": "fl-l score", "data-title": "score"})
    try:
        # is a number
        score = float(score.contents[0].string)
    except:
        # is N/A
        score = None
    # users
    try:
        users = soup.find("div", attrs = {"class": "fl-l score", "data-title": "score"}).get("data-user")
        users = int(users.replace(",","").split()[0])
    except:
        # is N/A
        users = None
    #animeRank
    rank = soup.find("span",{"class":"numbers ranked"})
    try:
        #rank is a number
        rank =  int(rank.find('strong').contents[0].replace(r"#", ' '))
    except:
        # anime have a rank of NA
        rank = None
    #animePopularity  
    popularity = soup.find("span",{"class":"numbers popularity"})
    popularity = int(popularity.find('strong').contents[0].replace(r"#", ' '))

    # save on anime info
    anime_info.extend((members, score, users, rank, popularity))
        
    return anime_info

# Anime characters and voices, synopsis, staff
def scrabbing_anime3(soup, anime_info):
    # Characters and voices doesn't exist always
    try:
        tag = soup.find_all("div", {"class": "detail-characters-list clearfix"})
        characters =  tag[0].find_all("h3", {"class": "h3_characters_voice_actors"})
        for i,char in enumerate(characters):
            characters[i] = char.get_text()
        voices = tag[0].find_all("td", {"class": "va-t ar pl4 pr4"})
        for i,voice in enumerate(voices):
            voices[i] = voice.get_text().replace("\n","")
    except:
        # there is some anime with empty attributes
        characters = None
        voices = None
    #synopsis (description)
    synopsis = str(soup.find("p", attrs = {"itemprop": "description"}).text)
    # related anime
    try:         
        related = soup.find_all("td", {"width": "100%",  "class": "borderClass"})
        for i,anime in enumerate(related):
            related[i] = anime.get_text()
        # only unique value
        related = list(set(related))
    except:
        related = None
    # Staff
    staff = []
    try:
        tag = soup.find_all("div", {"class": "detail-characters-list clearfix"})
        tag = tag[1].find_all("td")
        x = []
        y = []
        for i in range(1, len(tag), 2):
            x.append(tag[i].contents[1].contents[0])
            y.append(tag[i].find_all("small")[0].contents[0])
        staff.append([list(i) for i in list(zip(x,y))])
    except:
        staff = None
    
    # save on anime info
    anime_info.extend((synopsis,related,characters, voices, staff))
    return anime_info


# 2.0 PreProcessing documents
def replace_words(d, contractions):
    for key, value in contractions.items():
        d = d.replace(key, value)
    return d



# 2.2 Search Engine with ranked functions:

# function to create the cosine similiarity: using if we don't have
# enough k doc that match all the query
def cosine_sim(t,d,m):
    # t = sum of the tfidf match with the query
    # d = the documents d^i
    # m = the len of the query
    cosine = t/(np.linalg.norm(d)*np.sqrt(m))
    
    return cosine

# function to create the cosine similarity if enough document
# that match all the query
def cosine(q,d,m):
    # q = the query
    # d = the documents d^i
    # m = the length of the query
    cosine = np.dot(q,d)/(np.linalg.norm(d)*np.sqrt(m))
    return cosine
    
# function that return:
# bool True and a list "index" of the INTERSECTION of the query match list
# bool False and the original match_list if we don't have enough document to
# permorf the top k ranking
def intersection_all(k, match_list):
    # k: input for have the topk ranking
    # match_list: list of the matches
    find_all = []
    for query_match in match_list:
        tmp = []
        for tupla in query_match:
            tmp.append((tupla[0]))
        find_all.append(set(tmp))
        
    index = list(find_all[0].intersection(*find_all))
    if k <= len(index):
        yes = True
        return yes, index
    else:
        no = False
        return no, match_list


# function to output the minimum given a list of list of tuple, i.e the match list 
def minimum(lists, endlist):
    # lists = list of the query matches 
    # if a list is ended, than skip that list
    
    lis = []
    for i,idd in enumerate(lists):
        # be care to take the minimum for only the "still running" pointer
        if i in np.where(endlist == 0)[0]:
            lis.append(idd[0])
    minimum = min(lis)
    
    return minimum
    
# function to increase the pointer while compute the score 
def increase_pointer(match_list, pointer, minimum, lenMatch, endlist):
    # match_list = list of list of the matches
    # pointer = numpy array with the pointer position for each list
    # minimum = the minimum of the pointed element list
    # lenMatch = length of each list
    # endlist = numpy array of 0 and 1 which tell if a list is end or not
    
    # iter over the pointer
    for i in range(len(pointer)):
        # if a pointer reach the end of the list, increase endlist
        if  pointer[i] == lenMatch[i]-1:
            endlist[i] = 1
        # find the idd of the each list
        target = match_list[i][0]
        # if i compute the score (i.e target == min) and we don't reach the end
        # increase the pointer
        if  target == minimum and pointer[i] < lenMatch[i]-1:
            pointer[i] += 1
    return pointer, endlist
    
    
# function to compute the score of ALL the matches (at least a document match 1 query)
def scoresALL(match_list, tfIdf, m, lenMatch):
    pointer = np.zeros(m, dtype = "int")
    scores = []
    endlist = np.zeros(m, dtype = "int")
    # while loop untile escape the maximum list: I want all the score at least 1 match
    end = True
    while(end):
        # get the list of element pointed by the pointer
        lis = []
        for i in range(m):
            lis.append(match_list[i][pointer[i]])
        # get the minimum idd
        mini = minimum(lis,endlist)
        # get the tfIdf of the minimum
        tfIdf_match = np.sum([x[1] for x in lis if x[0] == mini])
        # compute the score:
        score = cosine_sim(tfIdf_match, tfIdf[mini],m)
        # heappush will heap by first element
        # !!! score<0 because I heap sort for min value
        heapq.heappush(scores,(-score, mini))
        # increase the pointer
        pointer, endlist = increase_pointer(lis, pointer, mini, lenMatch, endlist)  
        # when finishing the list, escape
        if endlist.all() == 1:
            end = False
            
    return scores

# function to compute the score of the document that match ALL the query
def scoresK(match_list, tfIdf, m, query_int):
    scores = []
    for doc in match_list:
        # compute the score
        score = cosine(query_int, tfIdf[doc], m)
        # push on the heap
        heapq.heappush(scores,(-score, doc))
    return scores

# function to get the top k document
def find_topK(k, scores):
    # search if i have k document that match ALL the query
    topscore = []
    topk = []
    for i in range(k):
        topscoretmp, topktmp = heapq.heappop(scores)
        topscore.append(abs(topscoretmp)), topk.append(topktmp)
    
    return topscore, topk