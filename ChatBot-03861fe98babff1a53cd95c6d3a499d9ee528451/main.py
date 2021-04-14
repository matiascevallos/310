import json
import os
import requests
import smtplib
from trainer import *
from synonym import *
from BotActionChart import *
from google.cloud import translate
#from GuiControl import *

#author: Matias Cevallos



bot_name = "Thera-bot"
prevTag = 'None' #stores the previous input type from the user, used to handle the user saying yes or no
errorString = ["I couldn't understand that", "Please repeat that"]

#predict with model
def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1

    return numpy.array(bag)

# initiates the conversation and predicts passes the input to the model. It predicts which type of response to give
# and chooses one randomly from the selected words.
def chat():
    print("Start talking with the bot (type quit to exit)!")
    while True:
        inp = input("You: ")
        if inp.lower() == "quit":
            break
        if inp.lower() == "help":
            handleSuicide()
        #print("test1")
        results = model.predict([bag_of_words(inp, words)])[0]
        results_index = numpy.argmax(results)
        tag = labels[results_index]
        if isInputYesOrNo(tag):
            print(handleYesOrNoInput(tag, prevTag))
            prevTag = ''
        else:
            #print("test2")
            if results[results_index] > 0.7:
                for tg in data["intents"]:
                    #print("test3")
                    if tg['tag'] == tag:
                        responses = tg['responses']
                #print("test4")
                print(random.choice(responses))
                if isInputSuicide(tag):
                    handleSuicide()
                if isInputExplain(tag):
                    handleExplain()
                prevTag = tag
            else:
                print(getErrorString())

def isInputYesOrNo(tag):
    keyTags = ["confirmation", "decline"]
    if any(tag in s for s in keyTags):
        return True

def handleYesOrNoInput(tag, previousTag):
    global prevTag
    try:
        s = actionChart[previousTag][tag]
    except:
        s = getErrorString()
    prevTag = 'None'
    return s

def isInputExplain(tag):
    if tag == "explain":
        return True

def handleExplain():
    inp = input("You: ")
    return "Thanks for letting me know."

def getErrorString():
	return random.choice(errorString)

print("TEST")
def isInputSuicide(tag):
    if tag == "help":
        return True
def handleSuicide():
    #api key
    api_file=open("api-key.txt", "r")
    api_key=api_file.read()
    api_file.close()
    #temp1="Los Angeles Department of Water and Power"
    #temp2="L.A. Live"
    professionals="Los Angeles Convention Center"
    inp = input("You: ")

    url="https://maps.googleapis.com/maps/api/directions/json?"
    r = requests.get(url + "origin=" + professionals + "&destination=" + inp + "&key=" + api_key)
    routes=r.json()['routes']
    l=routes[0]['legs']
    time=l[0]['duration']['text']

    return "Help will be there in "+ time

def handleSpanish(text):
    if(text==""):
        return "Tambien hablo en español, que necesitas?"
    else:
        #api key
        api_file=open("api-key.txt", "r")
        api_key=api_file.read()
        api_file.close()
        translate_client=translate.Client()
        text="hello"
        target='en'
        output=translate_client.translate(
            text,
            target_language=target
        )
        return output

def get_response(inp):
    if(inp=='spanish'):
        f = open("Spanish.txt",'w')
        f.write("true") 
        f.close() 
        return handleSpanish("")
    f = open("Spanish.txt",'r') #Opens the file
    data = f.read() #reads the file into data
    if(data=="true"):
        inp=handleSpanish(inp)
    #find synonyms
    synonimousPhrases = findSynonyms(inp)
    synonimousPhrases.insert(0, inp)
    print(synonimousPhrases)
    for phrase in synonimousPhrases:
        print("phrase: ", phrase)
        global prevTag
        results = model.predict([bag_of_words(phrase, words)])[0]
        results_index = numpy.argmax(results)
        tag = labels[results_index]
        if results[results_index] > 0.7:
            if isInputYesOrNo(tag):
                print(prevTag)
                return handleYesOrNoInput(tag, prevTag)
            else:
                for tg in data["intents"]:
                    if tg['tag'] == tag:
                        responses = tg['responses']
                if isInputSuicide(tag):
                    random.choice(responses)
                    return "We have your location. " + handleSuicide()
                if isInputExplain(tag):
                    return handleExplain()
                prevTag = tag
                print(prevTag)
                return random.choice(responses)
    ## if we have iterated through all possible synonimous options we return error string
    return getErrorString()


#where the code starts
#chat()
#app = ChatApplication()
#app.run()