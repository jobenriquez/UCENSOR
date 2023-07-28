from flask import Flask, render_template, request, jsonify

import re
PUNCTUATIONS_AND_SPACE = ['.', ',', '!', '?', ';', ' ', '\n', '\'', '\"']

app = Flask(__name__, static_folder='static', static_url_path='/static')
    
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        
        # Get the user input from the input text box
        input_text = request.json.get('text', '')
        
        sentence_in_array = []
    
        sentence_in_array = re.findall(r"[\w']+|[.,!?; \n\'\"]", input_text) 
        
        # Load up the patterns
        bad_dictionary = load_bad_dictionary()
        good_dictionary = load_good_dictionary()
        
        # Call function 'censor' to start censoring
        censored_sentence = censor(sentence_in_array, good_dictionary, bad_dictionary)
        
        # Print out processed text to the output text box
        return jsonify({'censored_sentence': censored_sentence})
    
    else:
        return render_template('index.html')
    
# To process censor...
def load_bad_dictionary():
    
    bad_words = []

    with open('bad_words_list.txt', 'rt') as string:
        for line in string:
            bad_words.append(line.strip())

    bad_words.sort(reverse=True)
    
    return bad_words

def load_good_dictionary():
    
    good_words = []

    with open('good_words_list.txt', 'rt') as string:
        for line in string:
            good_words.append(line.strip())

    good_words.sort(reverse=True)
    
    return good_words

def shift_table(pattern, length):
    
    # Store values in a shift table
    skip = []

    # 256 is the no. of characters in ASCII-8
    # Initialize each characters the value of the pattern's length
    for i in range(256):
        skip.append(length)
    
    # Calculate skip value of the pattern (exluding the last character of the pattern)
    for i in range(length - 1):
        skip[ord(pattern[i])] = length - 1 - i 
    
    return skip

def horspool_search(text, pattern):
    
    # Get text and pattern length
    text_length = len(text)
    pattern_length = len(pattern)
    
    # Call function shift_table
    skip = shift_table(pattern, pattern_length)
    
    # Points at the index of the text
    current_index = 0
    
    # Search 
    while (current_index <= text_length - pattern_length):
        
        # Points at the last index of the pattern        
        rightmost_index = pattern_length - 1
        
        # Compare text character and pattern character from rightmost of the pattern       
        while (rightmost_index >= 0 and pattern[rightmost_index] == text[current_index + rightmost_index]):
            # If it matches, proceed going to the left until rightmost_index = -1
            rightmost_index = rightmost_index - 1 
        
        # If a match is found...            
        if (rightmost_index == -1):
            # Convert text to list of characters
            # ex. choco = ['c', 'h', 'o', 'c', 'o']
            censor = list(text)
            
            # Starting from current_index
            # replace text with '*' 
            for i in range(pattern_length):
                 censor[current_index + i] = '*'
            
            # Merge the censored text '*' with the text itself
            text = "".join(censor)
            
            # After censoring text, pattern will skip by its length
            current_index = current_index + pattern_length
            
        # No match is found, then skip based on the shift table     
        else:
                    
            current_index = current_index + skip[ord(text[current_index + rightmost_index])]
    
    # Once the text has been completely searched, return text with censorship
    return text

def censor (text, good_words, bad_words):
    
    original_text = text
    temporary_text = original_text
    
    # Convert the text to lowercase for case-insensitive matching
    # Iterate through each word and censor it in the text
    # Check first if the text word belong to the good word dictionary
    for i in range(len(original_text)):
        if temporary_text[i].lower() in good_words or temporary_text[i].lower() in PUNCTUATIONS_AND_SPACE:
            continue
        
        # If the text word is unknown (ex. hdjkahdjhad) or does not belong to the dictionary,
        # then proceed checking it within the bad word dictionary and censor     
        for word in bad_words:
            # If the text word was already censored, just proceed to the next word
            # ex. "shit fuck", if the word 'shit' has searched through the text then "**** fuck"
            # when its the pattern 'fuck' turn to search, it will skip the text "****"
            asterisk = temporary_text[i].count('*') 
            if asterisk == len(temporary_text[i]):
                break
            
            # Search for bad words in the text to censor by calling function horspool_search
            original_text[i] = horspool_search(temporary_text[i].lower(), word)  

    # Convert the list of words back to a string
    censored_text = "".join(original_text)
    
    return censored_text 
    
if __name__ == '__main__':
    app.run(debug=True)
