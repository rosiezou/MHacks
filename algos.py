import math
import json
from firebase import firebase
# MUST FIRST LOAD USER DATA FROM CAPITAL ONE DEMO ACCOUNTS

# A user is going to be a dictof industry: [[frequency, total amt], [freq, amt]]

# This is a sample code to demo the math formulae and I/O format & file types
#    replace all strings and numbers with queried results & firebase data

# Note that the user info would be a GLOBAL CONSTANT within the analysis context

# get user info from Capital One API:
fireBase = firebase.FirebaseApplication('https://flickering-torch-8936.firebaseio.com/', None)


userJson = fireBase.get("/data", None)
sectors = ["Energy", "Materials", "Industrials", "Consumer Discretionary", "Consumer Staples",
	"Health Care", "Financials", "Information Technology", "Telecommunication Services", "Utilities"]
sectors2 = [["Energy0", "Energy1", "Energy2", "Energy3", "Energy4"], ["Materials0", "Materials1", "Materials2",
    "Materials3", "Materials4"], ["Industrials0", "Industrials1", "Industrials2", "Industrials3", "Industrials4"],
    ["Consumer Discretionary0", "Consumer Discretionary1", "Consumer Discretionary2", "Consumer Discretionary3",
    "Consumer Discretionary4"], ["Consumer Staples0", "Consumer Staples1", "Consumer Staples2",
    "Consumer Staples3", "Consumer Staples4"], ["Health Care0", "Health Care1", "Health Care2",
    "Health Care3", "Health Care4"], ["Financials0", "Financials1", "Financials2", "Financials3",
    "Financials4"], ["Information Technology0", "Information Technology1", "Information Technology2",
    "Information Technology3", "Information Technology4"], ["Telecommunication Services0",
    "Telecommunication Services1", "Telecommunication Services2", "Telecommunication Services3",
    "Telecommunication Services4"], ["Utilities0", "Utilities1", "Utilities2", "Utilities3", "Utilities4"]]

def getOrganizedResult(userJson):
    count1 = 0
    user = {}
    while count1 < 10:
        results = []
        count2 = 0
        while count2 < 5:
            freq = len(list(filter(lambda x: x["description"] == sectors2[count1][count2], userJson)))
            amt = sum(list(map(lambda x: x["amount"], list(filter(lambda x: x["description"] == sectors2[count1][count2], userJson)))))
            results += [[freq, amt]]
            count2 += 1
        industry = sectors[count1]
        user[industry] = results
        count1 += 1
    return user

user = getOrganizedResult(userJson)

# (listof (listof Num)) -> Num
def avg_freq(listofnum):
    return sum(list(map(lambda x: x[0], listofnum)))/len(list(map(lambda x: x[0], listofnum)))

#(listof (listof Num)) -> Num
def avg_amt(listofnum):
    return sum(list(map(lambda x: x[1], listofnum)))/len(list(map(lambda x: x[1], listofnum)))

#(listof (listof Num)) -> Num
def sigmamle_freq(listofnum):
    n = len(listofnum)
    count = 0
    sumofdiffsq = 0
    while count < n:
        diff = listofnum[count][0] - avg_freq(listofnum)
        sumofdiffsq += diff * diff
        count += 1
    return math.sqrt(sumofdiffsq / n)

#(listof (listof Num)) -> Num
def sigmamle_amt(listofnum):
    n = len(listofnum)
    count = 0
    sumofdiffsq = 0
    while count < n:
        diff = listofnum[count][1] - avg_freq(listofnum)
        sumofdiffsq += diff * diff
        count += 1
    return math.sqrt(sumofdiffsq / n)

def erfcc(x):
    z = abs(x)
    t = 1. / (1. + 0.5*z)
    r = t * math.exp(-z*z-1.26551223+t*(1.00002368+t*(.37409196+
    	t*(.09678418+t*(-.18628806+t*(.27886807+
    	t*(-1.13520398+t*(1.48851587+t*(-.82215223+
    	t*.17087277)))))))))
    if (x >= 0.):
    	return r
    else:
    	return 2. - r

def ncdf(x):
    return 1 - 0.5*erfcc(x/(2**0.5))

def normcdf(x, mu, sigma):
    t = x-mu;
    y = 0.5*erfcc(-t/(sigma*math.sqrt(2.0)));
    if y>1.0:
        y = 1.0;
    return y

def normpdf(x, mu, sigma):
    u = (x-mu)/math.fabs(sigma)
    y = (1/(sqrt(2*pi)*math.fabs(sigma)))*math.exp(-u*u/2)
    return y

def normdist(x, mu, sigma, f):
    if f:
        y = normcdf(x,mu,sigma)
    else:
        y = normpdf(x,mu,sigma)
    return y

# (dictof industry: vals) -> (listof industry)
def all_industries(auser):
    return list(auser.keys())
# eg. of return result: ["Information Technology", "Materials", "Financials"]

#(listof Str) -> (listof (listof Str Num))
def weight_freq(listofindustry):
    count = 0
    n = len(listofindustry)
    freq_result = []
    # for each industry
    while count < n:
        lolonum = user[listofindustry[count]]
        mu = avg_freq(lolonum)
        sigma = sigmamle_freq(lolonum)
        listofnorm = []
        count2 = 0
        m = len(lolonum)
        while count2 < m:
            listofnorm = listofnorm + [normcdf(lolonum[count2][0], mu, sigma)]
            count2 += 1
        freq_result = freq_result + [[listofindustry[count], sum(listofnorm)/len(listofnorm)]]
        count += 1
    return freq_result

#(listof Str) -> (listof (listof Str Num))
def weight_amt(listofindustry):
    count = 0
    n = len(listofindustry)
    amt_result = []
    # for each industry
    while count < n:
        lolonum = user[listofindustry[count]]
        mu = avg_amt(lolonum)
        sigma = sigmamle_amt(lolonum)
        listofnorm = []
        count2 = 0
        m = len(lolonum)
        while count2 < m:
            listofnorm = listofnorm + [normcdf(lolonum[count2][0], mu, sigma)]
            count2 += 1
        amt_result = amt_result + [[listofindustry[count], sum(listofnorm)/len(listofnorm)]]
        count += 1
    return amt_result

#(listof (listof Str Num)) (listof (listof Str Num)) -> (listof (listof Str Num))
def overall_weight(l1, l2):
    n = len(l1)
    count = 0
    result = []
    while count < n:
        product = l1[count][1] * l2[count][1]
        result = result + [[l1[count][0], product]]
        count += 1
    return sorted(result, key = lambda weights: weights[1])[-1]

def getRecommendations(marketSector):
    myFile = open(marketSector + "Rankings.txt", "r").read().split("\n")
    toReturn = []
    for line in myFile:
        toReturn.append(line)
    return toReturn[0:len(toReturn)-1]

def conductAnalysis():
    [sector, confidence] = overall_weight(weight_freq(all_industries(user)), weight_amt(all_industries(user)))
    return [getRecommendations(sector), confidence]
