from __future__ import unicode_literals
import re
import json
import string 
from abc import ABCMeta, abstractmethod
from six import add_metaclass
import os
from os import system
import platform
import datetime
import numpy as np
import time

@add_metaclass(ABCMeta)
class StemmerI(object):
    """A processing interface for removing morphological affixes from
    words. This process is known as stemming."""
    
    @abstractmethod
    def stem(self, token):
        """
        Strip affixes from the token and return the stem.

        :param token: The token that should be stemmed.
        :type token: str
        """
class liOS_Stemmer(StemmerI):
    
    # The rule list is static since it doesn't change between instances
    default_rule_tuple = (
        "ai*2.",  # -ia > -   if intact
        "a*1.",  # -a > -    if intact
        "bb1.",  # -bb > -b
        "city3s.",  # -ytic > -ys
        "ci2>",  # -ic > -
        "cn1t>",  # -nc > -nt
        "dd1.",  # -dd > -d
        "dei3y>",  # -ied > -y
        "deec2ss.",  # -ceed >", -cess
        "dee1.",  # -eed > -ee
        "de2>",  # -ed > -
        "dooh4>",  # -hood > -
        "e1>",  # -e > -
        "feil1v.",  # -lief > -liev
        "fi2>",  # -if > -
        "gni3>",  # -ing > -
        "gai3y.",  # -iag > -y
        "ga2>",  # -ag > -
        "gg1.",  # -gg > -g
        "ht*2.",  # -th > -   if intact
        "hsiug5ct.",  # -guish > -ct
        "hsi3>",  # -ish > -
        "i*1.",  # -i > -    if intact
        "i1y>",  # -i > -y
        "ji1d.",  # -ij > -id   --  see nois4j> & vis3j>
        "juf1s.",  # -fuj > -fus
        "ju1d.",  # -uj > -ud
        "jo1d.",  # -oj > -od
        "jeh1r.",  # -hej > -her
        "jrev1t.",  # -verj > -vert
        "jsim2t.",  # -misj > -mit
        "jn1d.",  # -nj > -nd
        "j1s.",  # -j > -s
        "lbaifi6.",  # -ifiabl > -
        "lbai4y.",  # -iabl > -y
        "lba3>",  # -abl > -
        "lbi3.",  # -ibl > -
        "lib2l>",  # -bil > -bl
        "lc1.",  # -cl > c
        "lufi4y.",  # -iful > -y
        "luf3>",  # -ful > -
        "lu2.",  # -ul > -
        "lai3>",  # -ial > -
        "lau3>",  # -ual > -
        "la2>",  # -al > -
        "ll1.",  # -ll > -l
        "mui3.",  # -ium > -
        "mu*2.",  # -um > -   if intact
        "msi3>",  # -ism > -
        "mm1.",  # -mm > -m
        "nois4j>",  # -sion > -j
        "noix4ct.",  # -xion > -ct
        "noi3>",  # -ion > -
        "nai3>",  # -ian > -
        "na2>",  # -an > -
        "nee0.",  # protect  -een
        "ne2>",  # -en > -
        "nn1.",  # -nn > -n
        "pihs4>",  # -ship > -
        "pp1.",  # -pp > -p
        "re2>",  # -er > -
        "rae0.",  # protect  -ear
        "ra2.",  # -ar > -
        "ro2>",  # -or > -
        "ru2>",  # -ur > -
        "rr1.",  # -rr > -r
        "rt1>",  # -tr > -t
        "rei3y>",  # -ier > -y
        "sei3y>",  # -ies > -y
        "sis2.",  # -sis > -s
        "si2>",  # -is > -
        "ssen4>",  # -ness > -
        "ss0.",  # protect  -ss
        "suo3>",  # -ous > -
        "su*2.",  # -us > -   if intact
        "s*1>",  # -s > -    if intact
        "s0.",  # -s > -s
        "tacilp4y.",  # -plicat > -ply
        "ta2>",  # -at > -
        "tnem4>",  # -ment > -
        "tne3>",  # -ent > -
        "tna3>",  # -ant > -
        "tpir2b.",  # -ript > -rib
        "tpro2b.",  # -orpt > -orb
        "tcud1.",  # -duct > -duc
        "tpmus2.",  # -sumpt > -sum
        "tpec2iv.",  # -cept > -ceiv
        "tulo2v.",  # -olut > -olv
        "tsis0.",  # protect  -sist
        "tsi3>",  # -ist > -
        "tt1.",  # -tt > -t
        "uqi3.",  # -iqu > -
        "ugo1.",  # -ogu > -og
        "vis3j>",  # -siv > -j
        "vie0.",  # protect  -eiv
        "vi2>",  # -iv > -
        "ylb1>",  # -bly > -bl
        "yli3y>",  # -ily > -y
        "ylp0.",  # protect  -ply
        "yl2>",  # -ly > -
        "ygo1.",  # -ogy > -og
        "yhp1.",  # -phy > -ph
        "ymo1.",  # -omy > -om
        "ypo1.",  # -opy > -op
        "yti3>",  # -ity > -
        "yte3>",  # -ety > -
        "ytl2.",  # -lty > -l
        "yrtsi5.",  # -istry > -
        "yra3>",  # -ary > -
        "yro3>",  # -ory > -
        "yfi3.",  # -ify > -
        "ycn2t>",  # -ncy > -nt
        "yca3>",  # -acy > -
        "zi2>",  # -iz > -
        "zy1s.",  # -yz > -ys
    )
    
    def __init__(self, rule_tuple=None, strip_prefix_flag=False):
        """Create an instance of the Lancaster stemmer."""
        # Setup an empty rule dictionary - this will be filled in later
        self.rule_dictionary = {}
        # Check if a user wants to strip prefix
        self._strip_prefix = strip_prefix_flag
        # Check if a user wants to use his/her own rule tuples.
        self._rule_tuple = rule_tuple if rule_tuple else self.default_rule_tuple
    
    def parseRules(self, rule_tuple=None):
        """Validate the set of rules used in this stemmer.

        If this function is called as an individual method, without using stem
        method, rule_tuple argument will be compiled into self.rule_dictionary.
        If this function is called within stem, self._rule_tuple will be used.
        """
        # If there is no argument for the function, use class' own rule tuple.
        rule_tuple = rule_tuple if rule_tuple else self._rule_tuple
        valid_rule = re.compile("^[a-z]+\*?\d[a-z]*[>\.]?$")
        # Empty any old rules from the rule set before adding new ones
        self.rule_dictionary = {}

        for rule in rule_tuple:
            if not valid_rule.match(rule):
                raise ValueError("The rule {0} is invalid".format(rule))
            first_letter = rule[0:1]
            if first_letter in self.rule_dictionary:
                self.rule_dictionary[first_letter].append(rule)
            else:
                self.rule_dictionary[first_letter] = [rule]
    def stem(self, word):
        """Stem a word using the Lancaster stemmer."""
        # Lower-case the word, since all the rules are lower-cased
        word = word.lower()
        word = self.__stripPrefix(word) if self._strip_prefix else word

        # Save a copy of the original word
        intact_word = word

        # If rule dictionary is empty, parse rule tuple.
        if not self.rule_dictionary:
            self.parseRules()

        return self.__start_stemming(word, intact_word)
    
    def __start_stemming(self, word, intact_word):
        """Perform the actual word stemming"""

        valid_rule = re.compile("^([a-z]+)(\*?)(\d)([a-z]*)([>\.]?)$")
        proceed = True
        while proceed:
            # Find the position of the last letter of the word to be stemmed
            last_letter_position = self.__getLastLetter(word)

            # Only stem the word if it has a last letter and a rule matching that last letter
            if (
                last_letter_position < 0
                or word[last_letter_position] not in self.rule_dictionary
            ):
                proceed = False
            else:
                rule_was_applied = False

                # Go through each rule that matches the word's final letter
                for rule in self.rule_dictionary[word[last_letter_position]]:
                    rule_match = valid_rule.match(rule)
                    if rule_match:
                        (
                            ending_string,
                            intact_flag,
                            remove_total,
                            append_string,
                            cont_flag,
                        ) = rule_match.groups()

                        # Convert the number of chars to remove when stemming
                        # from a string to an integer
                        remove_total = int(remove_total)

                        # Proceed if word's ending matches rule's word ending
                        if word.endswith(ending_string[::-1]):
                            if intact_flag:
                                if word == intact_word and self.__isAcceptable(
                                    word, remove_total
                                ):
                                    word = self.__applyRule(
                                        word, remove_total, append_string
                                    )
                                    rule_was_applied = True
                                    if cont_flag == '.':
                                        proceed = False
                                    break
                            elif self.__isAcceptable(word, remove_total):
                                word = self.__applyRule(
                                    word, remove_total, append_string
                                )
                                rule_was_applied = True
                                if cont_flag == '.':
                                    proceed = False
                                break
                # If no rules apply, the word doesn't need any more stemming
                if rule_was_applied == False:
                    proceed = False
        return word
    
    def __isAcceptable(self, word, remove_total):
        """Determine if the word is acceptable for stemming."""
        word_is_acceptable = False
        # If the word starts with a vowel, it must be at least 2
        # characters long to be stemmed
        if word[0] in "aeiouy":
            if len(word) - remove_total >= 2:
                word_is_acceptable = True
        # If the word starts with a consonant, it must be at least 3
        # characters long (including one vowel) to be stemmed
        elif len(word) - remove_total >= 3:
            if word[1] in "aeiouy":
                word_is_acceptable = True
            elif word[2] in "aeiouy":
                word_is_acceptable = True
        return word_is_acceptable

    def __getLastLetter(self, word):
        """Get the zero-based index of the last alphabetic character in this string."""
        last_letter = -1
        for position in range(len(word)):
            if word[position].isalpha():
                last_letter = position
            else:
                break
        return last_letter
    
    def __applyRule(self, word, remove_total, append_string):
        """Apply the stemming rule to the given word."""
        # Remove letters from the end of the word
        new_word_length = len(word) - remove_total
        word = word[0:new_word_length]

        # And add new letters to the end of the truncated word
        if append_string:
            word += append_string
        return word
    
    def __stripPrefix(self, word):
        """Remove prefix from a word."""
        for prefix in (
            "kilo",
            "micro",
            "milli",
            "intra",
            "ultra",
            "mega",
            "nano",
            "pico",
            "pseudo",
            "anti",
            "dis",
            "ex",
            "hyper",
        ):
            if word.startswith(prefix):
                return word[len(prefix) :]
        return word

    def __repr__(self):
        return '<liOS_Stemmer>'

stemmer = liOS_Stemmer()

def tokenize(content_type, content):
	'''takes in list of word, returns a dictionary with words as key, and frequency of word as value'''
	if content_type is 'file':
		frequency = {}
		frequency_v = list(frequency.values())
		frequency_k = list(frequency.keys())
		word_list = open(content, 'r')
		for word in word_list.readlines():
			if word not in frequency:
				frequency[word] = 0
				frequency_v = list(frequency.values())
				frequency_k = list(frequency.keys())
			frequency[word] += 1
		return frequency_v
	elif content_type is 'string':
		final_content = content.split(' ')
		for words in content:
			words.replace(string.punctuation,'')
		
		#[re.sub(r'[^\w\s]','',word) for word in content.split(' ')]
		#[word.strip(string.punctuation) for word in content.split(' ')]
		
		return final_content
	else:
		print('please set the content type as ”file” or ”string”.')
		return 0

# classes of training data
class json_utils():
	def __init__(self):
		return
	
	def get_training_data(self, file):
		with open(file) as training_data:
			training_dataJSON = json.load(training_data)
			# set the data id helper to 1, unlike common arrays
			d_id_helper = 1
			
			# define the final training data to return
			final_training_data = []
			
			# loop through training_dataJSON to create an list object
			for data in training_dataJSON['dataObjects']:
				# retrive the variables from the dataObjects
				d_id, d_class, d_content = data['id'], data['class'], data['sentence']
				
				# if the id is not defined, define it
				if d_id == '': 
					d_id = d_id_helper
				d_id_helper += 1
				
				# put all the retrived variables into an array
				tmp_data_array = {"id":d_id, "class":d_class, "sentence":d_content}
				final_training_data.append(tmp_data_array)
			return final_training_data
		
json_utils = json_utils()
training_data = json_utils.get_training_data('training_data.json')
print("%s sentences in training data" % len(training_data))

words = []
classes = []
documents = []
ignore_words = ['?']
# loop through each sentence in our training data
for pattern in training_data:
    # tokenize each word in the sentence
    w = tokenize('string', pattern['sentence'])
    words.extend(w)
    
    # add to documents in our corpus
    documents.append((w, pattern['class']))
    if pattern['class'] not in classes:
        classes.append(pattern['class'])

# stem and lower each word and remove duplicates
words = [stemmer.stem(w.lower()) for w in words if w not in ignore_words]
words = list(set(words))

# remove duplicates
classes = list(set(classes))

print("Documents:", str(len(documents)))
print("Classes:", str(len(classes)), classes)
print("USW:", str(len(words)), words)

# create our training data
training = []
output = []
# create an empty array for our output
output_empty = [0] * len(classes)

# training set, bag of words for each sentence
for doc in documents:
    # initialize our bag of words
    bag = []
    
    # list of tokenized words for the pattern
    pattern_words = doc[0]
    
    # stem each word
    pattern_words = [stemmer.stem(word.lower()) for word in pattern_words]
    # create our bag of words array
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)

    training.append(bag)
    
    # output is a '0' for each tag and '1' for current tag
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1
    output.append(output_row)
    
# sample training/output
i = 0
w = documents[i][0]
print("\nSample Training/output")
print([stemmer.stem(word.lower()) for word in w])
print(training[i])
print(output[i])


# compute sigmoid nonlinearity
def sigmoid(x):
    output = 1/(1+np.exp(-x))
    return output

# convert output of sigmoid function to its derivative
def sigmoid_output_to_derivative(output):
    return output*(1-output)
 
def clean_up_sentence(sentence):
    # tokenize the pattern
    sentence_words = tokenize("string", sentence)
    
    # stem each word
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    return sentence_words

# return BagOfWords array: 0 or 1 for each word in the bag that‘s in the sentence
def bow(sentence, words, show_details=False):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)

    return(np.array(bag))

def think(sentence, show_details=False):
    x = bow(sentence.lower(), words, show_details)
    if show_details:
        print ("sentence:", sentence, "\n bow:", x)
    # input layer is our bag of words
    l0 = x
    
    # matrix multiplication of input and hidden layer
    l1 = sigmoid(np.dot(l0, synapse_0))
    
    # output layer
    l2 = sigmoid(np.dot(l1, synapse_1))
    return l2
    
# Artaficial Neuaral Network (ANN) and Gradient Descent
def train(X, y, hidden_neurons=10, alpha=1, epochs=50000, dropout=False, dropout_percent=0.5):

    print ("Training with %s neurons, alpha:%s, dropout:%s %s" % (hidden_neurons, str(alpha), dropout, dropout_percent if dropout else ''))
    print ("Input matrix: %sx%s    Output matrix: %sx%s" % (len(X),len(X[0]),1, len(classes)))
    
    np.random.seed(1)

    last_mean_error = 1
    # randomly initialize our weights with mean 0
    synapse_0 = 2*np.random.random((len(X[0]), hidden_neurons)) - 1
    synapse_1 = 2*np.random.random((hidden_neurons, len(classes))) - 1

    prev_synapse_0_weight_update = np.zeros_like(synapse_0)
    prev_synapse_1_weight_update = np.zeros_like(synapse_1)

    synapse_0_direction_count = np.zeros_like(synapse_0)
    synapse_1_direction_count = np.zeros_like(synapse_1)
        
    for j in iter(range(epochs+1)):

        # Feed forward through layers 0, 1, and 2
        layer_0 = X
        layer_1 = sigmoid(np.dot(layer_0, synapse_0))
                
        if(dropout):
            layer_1 *= np.random.binomial([np.ones((len(X),hidden_neurons))],1-dropout_percent)[0] * (1.0/(1-dropout_percent))

        layer_2 = sigmoid(np.dot(layer_1, synapse_1))

        # how much did we miss the target value?
        layer_2_error = y - layer_2

        if (j% 10000) == 0 and j > 5000:
            # if this 10k iteration's error is greater than the last iteration, break out
            if np.mean(np.abs(layer_2_error)) < last_mean_error:
                print ("delta after "+str(j)+" iterations:" + str(np.mean(np.abs(layer_2_error))) )
                last_mean_error = np.mean(np.abs(layer_2_error))
            else:
                print ("break:", np.mean(np.abs(layer_2_error)), ">", last_mean_error )
                break
                
        # in what direction is the target value?
        # were we really sure? if so, don't change too much.
        layer_2_delta = layer_2_error * sigmoid_output_to_derivative(layer_2)

        # how much did each l1 value contribute to the l2 error (according to the weights)?
        layer_1_error = layer_2_delta.dot(synapse_1.T)

        # in what direction is the target l1?
        # were we really sure? if so, don't change too much.
        layer_1_delta = layer_1_error * sigmoid_output_to_derivative(layer_1)
        
        synapse_1_weight_update = (layer_1.T.dot(layer_2_delta))
        synapse_0_weight_update = (layer_0.T.dot(layer_1_delta))
        
        if(j > 0):
            synapse_0_direction_count += np.abs(((synapse_0_weight_update > 0)+0) - ((prev_synapse_0_weight_update > 0) + 0))
            synapse_1_direction_count += np.abs(((synapse_1_weight_update > 0)+0) - ((prev_synapse_1_weight_update > 0) + 0))        
        
        synapse_1 += alpha * synapse_1_weight_update
        synapse_0 += alpha * synapse_0_weight_update
        
        prev_synapse_0_weight_update = synapse_0_weight_update
        prev_synapse_1_weight_update = synapse_1_weight_update

    now = datetime.datetime.now()

    # persist synapses
    synapse = {'datetime': now.strftime("%Y-%m-%d %H:%M"),
               'words': words,
               'classes': classes,
               'synapse0': synapse_0.tolist(), 'synapse1': synapse_1.tolist()
               
              }
    synapse_file = "synapses.json"

    with open(synapse_file, 'w') as outfile:
        json.dump(synapse, outfile, indent=4, sort_keys=True)
    print ("saved synapses to:", synapse_file)

######################################################
# Training
X = np.array(training)
y = np.array(output)

start_time = time.time()

#train(X, y, hidden_neurons=20, alpha=0.1, epochs=100000, dropout=False, dropout_percent=0.2)

elapsed_time = time.time() - start_time
print("\nTraining results")
print ("processing time:", elapsed_time, "seconds")
######################################################


######################################################
# Probability and Guessing

# probability threshold
ERROR_THRESHOLD = 0.2

# load our calculated synapse values
synapse_file = 'synapses.json' 
with open(synapse_file) as data_file: 
    synapse = json.load(data_file) 
    synapse_0 = np.asarray(synapse['synapse0']) 
    synapse_1 = np.asarray(synapse['synapse1'])

def classify(sentence, show_details=False, show_classifications=True):
    results = think(sentence, show_details)

    results = [[i,r] for i,r in enumerate(results) if r>ERROR_THRESHOLD ] 
    results.sort(key=lambda x: x[1], reverse=True) 
    return_results =[[classes[r[0]],r[1]] for r in results]
    if show_classifications: print("%s \n classification: %s" % (sentence, return_results))
    return return_results

classify("sudo make me a sandwich", show_classifications=False)
classify("how are you today?", show_classifications=False)
classify("talk to you tomorrow", show_classifications=False)
classify("who are you?", show_classifications=False)
classify("make me some lunch", show_classifications=False)
classify("how was your lunch today?", show_classifications=False)
print()
classify("who are you?", show_classifications=False)
classify("have a good day! idiot")
######################################################

"""Clears the console"""
def clean():
	os_name = platform.system().lower()
	if 'windows' in os_name:
		system('cls')
	else:
		system('clear')

######################################################
# Getting input from the user

# Create a while loop to keep the program running
while True:
	user_input = input(">>> ")
	classified_input = classify(user_input, show_classifications=True)
	
	while len(classified_input) == 0:
		classified_input = classify(user_input, show_classifications=True)
	print(classified_input[0][0])
