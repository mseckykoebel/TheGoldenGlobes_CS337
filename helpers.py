import json


def comment_extract_file(path):
    """ 
	Helper function to extract comments from JSON tweets.
	Arguments : JSON file directory (Tweets)
	Output	  : List of comments strings
	"""

    with open(path, "r") as read_file:
        data = json.load(read_file)

    comments = comment_extract(data)

    return comments


def comment_extract(json_obj):
    """ 
	Helper function to extract comments from JSON obj.
	Arguments : JSON Obj of tweets
	Output	  : List of comments strings
	"""
    comment_list = []
    #for comment in json_obj:
    #    text = comment if type(comment) is str else comment["text"]
    #    comment_list.append(text)

    return comment_list