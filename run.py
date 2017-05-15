# -*- coding: utf-8 -*-
import codecs, requests, urllib, webbrowser, json, os, math, time, logger, sys
from threading import Thread


# Application settings
client_id = "3998121"
client_secret = "AlVXZFMUqyrnABp8ncuU"
runThread = 10

# API call function
def api_call(method, param):
	api_url = "https://api.vk.com/method/" + method + "?" + urllib.urlencode(param)
	s = requests.Session()
	r = s.get(api_url)

	response = json.loads(r.text)

	return response["response"]

# Simple errors display
def error():
	logger.fail("Пусто!")

def downloadPhoto(threadID, url, path):
	urllib.urlretrieve(url, path)

# Creating users folder if not exists
if not os.path.exists("./users/"):
	os.makedirs("./users/")

# Checking access_token file for exists
if os.path.isfile("./access_token.txt"):
	file = open("./access_token.txt", "r")
	access_token = file.read()
	file.close()

	logger.success("Authorized!")
else:
	data = {
		"client_id": client_id,
		"redirect_uri": "https://oauth.vk.com/blank.html",
		"display": "page",
		"scope": "photos,offline",
		"response_type": "token",
		"v": "5.0"
	}

	url = "https://oauth.vk.com/authorize?" + urllib.urlencode(data)

	webbrowser.open(url, new=2)

	logger.info("In browser, you need to allow access to get access token");
	logger.info("After that, copy value of parameter access_token from browser url")

	access_token = raw_input("[~] Enter access_token: ")

	if len(access_token) > 0:
		logger.success("Authorized!")

		file = open("./access_token.txt", "w")
		file.write(access_token)
		file.close()
	else:
		error()

# Saving user
user_id = raw_input("[~] Enter user id: ")

if len(user_id) > 0:
	user_id = user_id.replace("id","")

	user = api_call('users.get', {
		'user_ids': user_id,
		'fields': 'photo_max_orig,bdate,city,country,home_town,counters',
		'access_token': access_token
	})

	user_counters = user[0]['counters']

	user_name = str("%s %s" % (user[0]['first_name'], user[0]['last_name']))

	logger.success("Saving user: %s [id%s]" % (user_name, user_id))

	# Creating user folder if not exists
	user_path = "./users/%s [%s]" % (user_name, user_id)
	if not os.path.exists(user_path):
		os.makedirs(user_path)

	# Download user's avatar
	try:
		if not os.path.isfile("%s/avatar.jpg" % user_path):
			logger.info("Download user's avatar")
			urllib.urlretrieve(user[0]['photo_max_orig'], "%s/avatar.jpg" % user_path)
	except: 
		pass

	# Download user's albums
	photos_path = str("%s/albums/" % user_path)
	if not os.path.exists(photos_path):
		os.makedirs(photos_path)

	albums = api_call('photos.getAlbums', {
		'owner_id': user_id,
		'access_token': access_token
	})

	for album in albums:
		# Creating album folder if not exists
		album_path = str("%s/%s" % (photos_path, album['title'].encode('utf-8')))
		if not os.path.exists(album_path):
			os.makedirs(album_path)

		photos = api_call('photos.get', {
			'owner_id': user_id,
			'album_id': album['aid'],
			'access_token': access_token
		})

		tId = 1

		for photo in photos:
			photo_name = str("%s.jpg" % photo['pid'])

			# Download photo
			try:
				if not os.path.isfile("%s/%s" % (album_path, photo_name)):
					logger.info("Download photo %s" % photo_name)
					thread = Thread(target = downloadPhoto, args = (tId, photo['src_big'], "%s/%s" % (album_path, photo_name),))
					thread.start()
					tId += 1
			except: 
				pass

	# Saving user's friend list
	logger.info("Saving user's friend list")

	friends_path = "%s/friends.txt" % user_path
	os.remove(friends_path) if os.path.exists(friends_path) else None
	file = open(friends_path, "w")

	for x in xrange(0, (user_counters['friends']/100)+1):
		friends = api_call('friends.get', {
			'user_id': user_id,
			'order': 'name',
			'count': 100,
			'offset': (x * 100),
			'fields': 'uid, first_name, last_name, nickname, sex',
			'name_case': 'nom',
			'access_token': access_token
		})

		for friend in friends:
			file.write("Id: %s\n" % friend['uid'])
			file.write("Name: %s %s\n" % (friend['first_name'],friend['last_name']))
			file.write("URL: https://vk.com/id%s\n" % friend['uid'])
			file.write("===============\n")

	file.close()

logger.success("Done!")
sys.exit()