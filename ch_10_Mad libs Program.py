# TODO 1: Read the file 

parts_of_speech = ['ADJECTIVE', 'NOUN', 'ADVERB', 'VERB']

def madLibs(madlibs_txt):
    foundedList = []
    userInput = []
    with open(madlibs_txt, encoding='UTF-8') as text:
        content = text.read()


    # Check if ADJECTIVE, NOUN, ADVERB, VERB is in the text 
    # Fist split it into characters
    content_split = content.split()
    #print(content_split)

    # Founded -> add to the foundedList
    for word in content_split:
        # Need to remove . , ! ? 
        word = word.strip('.,!?')
        #print(word)

        if word in parts_of_speech:
            foundedList.append(word)

    #user input
    for context in foundedList:
        print(f'Enter an {context}:') 
        userInput.append(input())
    #print(userInput)

    new_words= []
    #Output
    #define the file
    madlibs_txt_modified = 'D:/0_YG Project/0_Python Practice/madlibs_output.txt'

    with open(madlibs_txt_modified, 'w', encoding='UTF-8') as output:
        for word in content_split:
            word = word.strip('.,!?')
            if word in parts_of_speech:
                new_words.append(userInput.pop(0))
            else:
                new_words.append(word)

        print(' '.join(new_words))
        output.write(' '.join(new_words))
   

madLibs('D:/0_YG Project/0_Python Practice/madlibs_txt.txt')
    

    
    
    
