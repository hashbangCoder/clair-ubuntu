import re
import operator
import pdb
import numpy
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer
from scipy.spatial.distance import euclidean


class Post(object):    
    # constructor
    def __init__(self, username, userid, message_words, message, timeid, dialogueid = None):
    	
    	# member variables
    	self.username = username
    	self.userid = userid
    	self.message_words = message_words
    	self.message = message
    	self.timeid = timeid
    	self.dialogueid = dialogueid;

    def __str__(self):
    	return 'Username: ' + self.username + ', User ID: ' + str(self.userid) + ', Time ID: ' + str(self.timeid) + ', Dialogue ID: ' + str(self.dialogueid) + '\nMessage: ' + self.message 

    def get_username(self):
    	return self.username

    def get_userid(self):
    	return self.userid

    def get_message_words(self):
    	return self.message_words

    def get_message(self):
    	return self.message      

    def get_timeid(self):
    	return self.timeid

    def set_dialogue_id(self, id_in):    	
    	self.dialogueid = id_in  
    	
    def get_dialogue_id(self):
    	return self.dialogueid

    
# create dictionary to hold mappings to user id's
user_aliases = {}
# list to store Post objects
entries = []

# file processing
def file_processing(file_in):

	global user_aliases
	global entries
	newuserid = 0
	timestamp = 0
	for line in myfile:	
		# if name is changed on line
		if (re.search(r'^===', line)):			
			
			# extract old and new name
			names = re.search(r'=== (.+?) is now known as (.*)\r?',line)
			old_name = names.group(1) 
			new_name = names.group(2)

			# if old name didn't exist in this file, 
			# add new one to user alias dictionary
			if not old_name in user_aliases:
				user_aliases[new_name] = newuserid
				newuserid += 1
			# otherwise, set the id of the new alias 
			# to the id of the old name
			else:
				user_aliases[new_name] = user_aliases[old_name]

		# if line contains a normal post, add username to dictionary
		else:
			current_line = re.search(r'\[.+?\]\s<(.+?)>', line)
			if current_line:

				username = current_line.group(1)
				# if user has not posted before, assign them a user id
				if not username in user_aliases:
					user_aliases[username] = newuserid
					newuserid += 1

				# tokenize post body and store strings in list
				current_entry = re.findall(r'\[.+?\]\s<.+?>\s(.*)', line)	
				split = current_entry[0].split()
				# add object storing current comment's information to data list
				bob = Post(username, user_aliases[username], split, current_entry[0], timestamp)
				entries.append(bob)
				timestamp += 1


def annotate(entries_list):
    num_messages = 10
    dialogueid = 0
    doAnnotation = True
    index = 0
    while ((doAnnotation == True) and (index < len(entries))):
    	num_entries_to_print = min(num_messages, index)
    	print ("PREVIOUS MESSAGES\n")
    	for j in range(num_entries_to_print):
    		print ('[',j,'] ', entries_list[index - num_entries_to_print + j])
    	
    	print ('\n')
    	valid_input = False
    	print ('CURRENT MESSAGE: ' + str(entries_list[index]) + '\n')
    	while (valid_input == False):
    		current_val = int(input("Please choose which dialogue current message pertains to. Enter -1 to create new dialogue. Enter -2 to exit annotation.\n"))
    		if (current_val == -2):
    			doAnnotation = False
    			valid_input = True
    		elif (current_val == -1):
    			print ("HELLLOOOO")
    			entries_list[index].set_dialogue_id(dialogueid)
    			dialogueid += 1
    			valid_input = True
    			print (valid_input)
    		elif ((current_val >= 0) and (current_val < num_entries_to_print)):
    			entries_list[index].set_dialogue_id(entries_list[index - num_entries_to_print + current_val].get_dialogue_id())
    			valid_input = True
    		else:
    			print ("Not a valid input. Please try again")

    	print ('_'*100)

    	index += 1


myfile = open('ubuntu_small_sample.txt', 'r')
file_processing(myfile)


annotate(entries)


message_list = []
for posts in entries:
	message_list.append(posts.get_message())

vectorizer = CountVectorizer(analyzer = "word", binary = True, tokenizer = None, preprocessor = None, stop_words = None, max_features = 5000) 
word_vec = vectorizer.fit_transform(message_list)

bin_matrix = word_vec.todense()
# print dimensions of binary frequency matrix
print (bin_matrix.shape)


vocab = vectorizer.get_feature_names()
#print (vocab)
num_clusters = 5
kmeans = KMeans(n_clusters = num_clusters)
kmeans.fit(bin_matrix)

bob = euclidean(bin_matrix[2,:], bin_matrix[3,:])
print (bob)

centroids = kmeans.cluster_centers_
labels = kmeans.labels_

#print (labels)
#print (centroids[2])

#print out like messages


for i in range(num_clusters):
	min_dist = 1000000000;
	min_index = 0;
	print ("Messages in cluster", i,':')
	for j in range(len(message_list)):
		if (labels[j] == i):
			if (euclidean(bin_matrix[j], centroids[i]) < min_dist):
				min_dist = euclidean(bin_matrix[j], centroids[i]) 
				min_index = j
			print (message_list[j])
	print ("\nCluster Medoid: ", message_list[min_index], '\n'*4)



