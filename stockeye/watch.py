from requests  import get
from time      import sleep
from random    import randint
from newspaper import Article
from bs4       import BeautifulSoup
from re        import search, sub  
from datetime  import datetime, timedelta
from math      import log10 

from smtplib              import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from nltk                 import sent_tokenize, word_tokenize
from nltk.corpus          import stopwords
stopWords = set(stopwords.words('english'))

# --- Textrank Methods ---------------------------------------------------------

class vertex:
    order = 0
    def __init__(self, sentence_raw, sentence_processed, words):
        self.order              = vertex.order
        self.score              = None
        self.scores             = []
        self.sentence_raw       = sentence_raw
        self.sentence_processed = sentence_processed
        self.words              = words
        vertex.order += 1
        
    def averageScores(self):
        try: self.score = sum(self.scores)/len(self.scores)
        except ZeroDivisionError: self.score = 0

def overlap(w1, w2):
    s1 = []
    for w in w1:
        if w not in stopWords:
            s1.append(w)
    s2 = []
    for w in w2:
        if w not in stopWords:
            s2.append(w)
            
    try: return len([w for w in s1 if w in s2])/(log10(len(s1))+log10(len(s2)))
    except ZeroDivisionError: return 0
    
def buildGraph(text):
    vertices = [] 
    sentences = sent_tokenize(text, language='english')
    for sentence_raw in sentences:  
        sentence_processed = sub("[^a-zA-Z ]+", '', sentence_raw).lower()          
        words = word_tokenize(sentence_processed, language='english')
        vertices.append(vertex(sentence_raw, sentence_processed, words))
    
    for v1 in vertices:
        for v2 in vertices:
            if v1.order != v2.order:                
                v1.scores.append(overlap(v1.words, v2.words))
        v1.averageScores()
    return vertices

def summarize(text, sentences, firstlast = False):
    vertices = buildGraph(text)
    all_ord = sorted(vertices, key=lambda v: v.order)
    mos_sig = sorted(vertices, key=lambda v: v.score, reverse=True)[0:sentences]
    mos_sig_ord = sorted(mos_sig, key=lambda v: v.order)
        
    if firstlast:
        if all_ord[0] not in mos_sig_ord: 
            mos_sig_ord.insert(0, all_ord[0])
        if all_ord[len(all_ord)-1] not in mos_sig_ord:
            mos_sig_ord.append(all_ord[len(all_ord)-1])
    
    summary = []
    for v in mos_sig_ord:
        summary.append(v.sentence_raw)
    return summary

# --- Yahoo Methods -----------------------------------------------------------

def loadSymbols():
    afile = open('symbols/alpha.txt', 'r')
    cfile = open('symbols/clean.txt', 'r') 
    alpha, clean = [], [] 
    for a in afile:
        alpha.append(a.strip('\n'))
    for c in cfile:
        clean.append(c.strip('\n'))
    symbols = {}
    for i in xrange(len(alpha)):
        symbols[alpha[i]] = clean[i]
    return symbols

def yahooURL(ticks):
    query = ''
    for i,t in enumerate(ticks):
        if i == len(ticks)-1: query += '%22'+t+'%22'
        else: query += '%22'+t+'%22%2C'
    return "https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.quotes%20where%20symbol%20in%20("+query+")%0A%09%09&format=json&diagnostics=true&env=http%3A%2F%2Fdatatables.org%2Falltables.env&callback="

def yahooRequest(url, moreProperties = []):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
    r = get(url, headers=headers)
    j = r.json()
    try: 
        quotes = j['query']['results']['quote']      
    except KeyError:                         
        print "No Stocks Found!"             # If zero stocks found
        return 
    stocks = {}
    properties = ['Name'] + moreProperties       
    if type(quotes) == dict:                 # If one stock found
        stocks[quotes['Symbol']] = {}
        for p in properties:
            try:
                stocks[quotes['Symbol']][p] = quotes[p]
            except KeyError:
                stocks[quotes['Symbol']][p] = "None"        
    else:
        for q in quotes:                     # If multiple stocks found
            stocks[q['Symbol']] = {}
            for p in properties:
                try:
                    stocks[q['Symbol']][p] = q[p]
                except KeyError:
                    stocks[q['Symbol']][p] = "None"
    return stocks

# --- Email Methods ------------------------------------------------------------

def stats_HTML(symbol, statistics, properties):
    symbols = loadSymbols()
    stats = '<center><b>'+symbol+'</b><br><br><table>'
    for p in properties:
        try:
            stats += '<tr><td style="padding-right:30px">'+symbols[p]+'</td>'
        except:
            stats += '<tr><td>'+p+'</td>'
        stats += '<td>'+str(statistics[symbol][p])+'</td></tr>'
    return stats+'</table><br><hr><br></center>'

def outline_HTML(i, title, link, time, summary):
    title_HTML = '<br>'+str(i+1)+'. <b><a href="'+link+'">'+title+'</a></b><br>' 
    time_HTML = 'Posted '+time+'<br>'
    summary_HTML = ''    
    for sentence in summary:
        summary_HTML += '<br><i>'+sentence+'<br></i>'
    return title_HTML+time_HTML+summary_HTML

def subject_HTML(symbol):
    subject = 'Recent News Activity for '+symbol
    return subject

def body_HTML(symbol, statistics, properties, articles):
    body = ''
    body += stats_HTML(symbol, statistics, properties)
    for i, a in enumerate(articles):
        body += outline_HTML(i, a.title, a.link, a.time, a.summary)
    return body    

def sendEmail(subject, body, credentials):    
    self = credentials[0]
    password = credentials[1]    
    fromAddr = credentials[2]
    toAddr = credentials[3]   
    msg = MIMEMultipart()
    msg['From'] = fromAddr
    msg['To'] = toAddr
    msg['Subject'] = subject   
    msgText = MIMEText(body, 'html', 'UTF-8')
    msg.attach(msgText)
    server = SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(self, password)
    text = msg.as_string()
    server.sendmail(fromAddr, toAddr, text)
    server.quit()

# --- Scraping Methods ---------------------------------------------------------

class article:    
    def __init__(self, title, link, time):   
        self.title   = title
        self.link    = link
        self.time    = time
        self.order   = None
        self.body    = []
        self.summary = []
        
    def printTitle(self):
        print self.title
        
    def printBody(self):
        for s in self.body:
            print '  ',
            print s
            print
        
    def printSummary(self):
        for s in self.summary:
            print s
            print

def similarity(s1, s2):
    if len(s1) == 0: return len(s2)
    elif len(s2) == 0: return len(s1)
    v0 = [None]*(len(s2) + 1)
    v1 = [None]*(len(s2) + 1)
    for i in range(len(v0)):
        v0[i] = i
    for i in range(len(s1)):
        v1[0] = i + 1
        for j in range(len(s2)):
            cost = 0 if s1[i] == s2[j] else 1
            v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
        for j in range(len(v0)):
            v0[j] = v1[j]
    return 100-((float(v1[len(s2)])/(len(s1)+len(s2)))*100)

def unique(title, articles):
    for article in articles:
        if similarity(title, article.title) >= 95:
            return False
    return True

def createURLs(query, pages):
    pages = (10 * x for x in xrange(0, pages))
    lower = query.lower().replace(' ', '+')
    urls = ['https://www.google.com/search?q="%s"&tbm=nws&tbs=qdr:y#q="%s"&safe=active&tbs=qdr:y,sbd:1&tbm=nws&start=%s' % (lower, lower, x) for i, x in enumerate(pages)]
    return urls
  
def grabArticles(query, pages, rest = 0):
    urls = createURLs(query, pages)
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
    articles = []
    for url in urls:
        response = get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        objects_HId = soup.find_all("a", class_="_HId")
        objects_sQb = soup.find_all("a", class_="_sQb")
        
        for a in objects_HId:
            title = a.get_text()
            link = a['href']
            try:
                time = a.parent.find("span", class_="_uQb").text
            except AttributeError: 
                time = a.parent.parent.find("span", class_="_uQb").text
            if unique(title, articles):
                articles.append(article(title, link, time))

        for a in objects_sQb:
            title =  a.get_text()
            link = a['href']
            try:
                time = a.parent.find("span", class_="_uQb").text
            except AttributeError:
                time = a.parent.parent.find("span", class_="_uQb").text
            if unique(title, articles):
                articles.append(article(title, link, time))
               
        sleep(randint(float(rest)/2, rest))
    return articles   

# ----- Analytical Methods -----------------------------------------------------

def summarizeArticles(articles, sentences, firstlast = False):
    summedArticles = []
    for a in articles:
        try: 
            A = Article(a.link)
            A.download()
            A.parse()
            text = ""
            paragraphs = A.text.split('\n')
            for p in paragraphs:
                if len(p) > 100:
                    a.body.append(p)
                    text += p + ' ' 
            sentences = summarize(text, sentences, firstlast)
            for s in sentences:
                a.summary.append(s) 
            summedArticles.append(a)    
        except: pass
    return summedArticles

def sortArticles(articles):
    for a in articles:    
        time = a.time  
        if search("second", time):
            seconds = int(time.split(' ')[0])
            order = datetime.now()-timedelta(seconds=seconds)        
        elif search("minute", time):
            minutes = int(time.split(' ')[0])
            order = datetime.now()-timedelta(minutes=minutes)           
        elif search("hour", time):
            hours = int(time.split(' ')[0])
            order = datetime.now()-timedelta(hours=hours)        
        else:
            order = datetime.strptime(time, '%b %d, %Y') 
        a.order = order
    return sorted(articles, key=lambda a: a.order, reverse=True)     

# ----- The Mastermind ---------------------------------------------------------

def watch(credentials, ticks, properties = [], threshold = 5, hourspast = 18, sentences = 3, firstlast = False):
    if threshold <= 0:
        print "Please choose a threshold greater than 0."
        return         
    if hourspast < 0:
        print "This program is not capable of scraping news from the future."
        return  
    if len(ticks) > 100:
        print "API calls are limited to 100 individual stocks."
        return   
    
    estimate = len(ticks)*15*2
    if estimate < 60: print "This run will take approximately %s seconds" % (str(estimate))
    else: print "This run will take approximately %s minutes" % (str(estimate/60))    
    
    url = yahooURL(ticks)
    stats = yahooRequest(url, properties)
    remove = ['class', 'common', 'stock']
    for symbol in stats:
        name = stats[symbol]['Name']
        if name:
            print "Finding news for %s" % (symbol)
            query = (' '.join([w for w in name.split() if w.lower() not in remove]))+' '+symbol
            print query
            articles = grabArticles(query+' '+symbol, 2, 20)
            articles = summarizeArticles(articles, sentences, firstlast)  
            articles = sortArticles(articles) 
            recentArticles = []
            for a in articles:
                hoursago = float((datetime.now()-a.order).total_seconds())/3600
                if hoursago <= hourspast:
                    recentArticles.append(a)    
            if len(recentArticles) >= threshold:
                subject = subject_HTML(symbol)
                body = body_HTML(symbol, stats, properties, recentArticles)
                sendEmail(subject, body, credentials)
        else:
            print "Coudn't find any company for %s" % (symbol)