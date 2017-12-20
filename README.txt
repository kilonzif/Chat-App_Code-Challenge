-----<BACKEND CHALLENGE>-----

This application currently supports 5 endpoints for a chat app:

	-Create a user
	-Log in
	-Log out
	-Send a message
	-Fetch messages between two users

-----<SETUP>-----

1. unzip backend-python.zip
2. cd backend-python
3. docker build -t challenge .
4. docker run -d -p 9000:5000 challenge

-----<INSTRUCTIONS>-----

This app has an authentication framework. In order to test its functionality, the following steps should be completed in sequence. CURL requests are provided to simulate behavior for both a logged in and a logged out user. Request parameters may be substituted but are provided for your use.

1. Create user

	a. Failed constraints:

		curl -k -H "Content-Type: application/json" -X POST -d '{"username":"foobar","password":""}' http://localhost:9000/users

			{
			  "msg": "Bad Request: http://localhost:9000/users",
			  "status": 400
			}

	b. Correct (user 1):

		curl -k -H "Content-Type: application/json" -X POST -d '{"username":"foo","password":"bar"}' http://localhost:9000/users

			{
			  "msg": "Account successfully registered",
			  "status": "OK"
			}

	c. Correct (user 2):

		curl -k -H "Content-Type: application/json" -X POST -d '{"username":"ada","password":"lovelace"}' http://localhost:9000/users

			{
			  "msg": "Account successfully registered",
			  "status": "OK"
			}

2. Log in the user
	*Note: In practice and to optimize UX, creating a user would also log in the user.*

	a. Incorrect credentials:

		curl -k -H "Content-Type: application/json" -X POST -d '{"username":"bar","password":"foo"}' -c cookie-jar.txt http://localhost:9000/log_in

			{
			  "msg": "Unauthorized: http://localhost:9000/log_in",
			  "status": 401
			}

	b. Correct credentials:

		curl -k -H "Content-Type: application/json" -X POST -d '{"username":"foo","password":"bar"}' -c cookie-jar.txt http://localhost:9000/log_in

			{
			  "msg": "Successfully logged in",
			  "status": "OK"
			}

-----<User now logged in>-----

3. Send a message

	a. Text:

		curl -k -H "Content-Type: application/json" -X POST -d '{"sender_id":"1","recipient_id":"2","message_content":"hello world"}' -b cookie-jar.txt http://localhost:9000/messages

			{
			  "msg": {
			    "content": "hello world",
			    "timestamp": "Sun, 17 Dec 2017 23:53:00 GMT",
			    "type": "text"
			  },
			  "status": "OK"
			}

	b. Image:

		curl -k -H "Content-Type: application/json" -X POST -d '{"sender_id":"1","recipient_id":"2","message_content":"http://www.smashbros.com/images/og/link.jpg"}' -b cookie-jar.txt http://localhost:9000/messages

			{
			  "msg": {
			    "content": "http://www.smashbros.com/images/og/link.jpg",
			    "timestamp": "Sun, 17 Dec 2017 23:53:23 GMT",
			    "type": "image_link"
			  },
			  "status": "OK"
			}

	c. Video:

		curl -k -H "Content-Type: application/json" -X POST -d '{"sender_id":"1","recipient_id":"2","message_content":"https://player.vimeo.com/external/158148793.hd.mp4?s=8e8741dbee251d5c35a759718d4b0976fbf38b6f&profile_id=119&oauth2_token_id=57447761"}' -b cookie-jar.txt http://localhost:9000/messages

			{
			  "msg": {
			    "content": "https://player.vimeo.com/external/158148793.hd.mp4?s=8e8741dbee251d5c35a759718d4b0976fbf38b6f&profile_id=119&oauth2_token_id=57447761",
			    "timestamp": "Sun, 17 Dec 2017 23:53:46 GMT",
			    "type": "video_link"
			  },
			  "status": "OK"
			}

	d. Incorrect / broken link:

		curl -k -H "Content-Type: application/json" -X POST -d '{"sender_id":"1","recipient_id":"2","message_content":"http://wwww."}' -b cookie-jar.txt http://localhost:9000/messages

			{
			  "msg": "Unsupported Media Type: http://localhost:9000/messages",
			  "status": 415
			}

	e. Incorrect / user not registered

		curl -k -H "Content-Type: application/json" -X POST -d '{"sender_id":"1","recipient_id":"3","message_content":"hello world"}' -b cookie-jar.txt http://localhost:9000/messages

			{
			  "msg": "Bad Request: http://localhost:9000/messages",
			  "status": 400
			}

4. Fetch messages

	a. With page parameters:

		curl -k -X GET -b cookie-jar.txt 'http://localhost:9000/messages?user_id_1=1&user_id_2=2&page=1&messages_per_page=20'

			{
			  "msg": {...messages...},
			    "has_next": false,
			    "has_prev": false,
			    "page": 1,
			    "pages": 1,
			    "per_page": 20
			  },
			  "status": "OK"
			}

	b. Without page parameters:

		curl -k -X GET -b cookie-jar.txt 'http://localhost:9000/messages?user_id_1=1&user_id_2=2'

			{
			  "msg": {...messages...},
			    "has_next": false,
			    "has_prev": false,
			    "page": 1,
			    "pages": 1,
			    "per_page": 20
			  },
			  "status": "OK"
			}


	c. Incorrect / attempt to messages fetch from an unregistered user:

		curl -k -X GET -b cookie-jar.txt 'http://localhost:9000/messages?user_id_1=1&user_id_2=3'

			{
			  "msg": "Bad Request: http://localhost:9000/messages?user_id_1=1&user_id_2=3",
			  "status": 400
			}

5. Log out

	curl -k -i -H "Accept: application/json" -H "Content-Type: application/json" -X GET -b cookie-jar.txt http://localhost:9000/log_out

			{
			  "msg": "User successfully logged out",
			  "status": "OK"
			}

-----<User now logged out>-----

6. Log out

	curl -k -i -H "Accept: application/json" -H "Content-Type: application/json" -X GET -b cookie-jar.txt http://localhost:9000/log_out

			{
			  "msg": "Bad Request: http://localhost:9000/log_out",
			  "status": 400
			}

7. Send a message

	curl -k -H "Content-Type: application/json" -X POST -d '{"sender_id":"1","recipient_id":"2","message_content":"hello world"}' -b cookie-jar.txt http://localhost:9000/messages

			{
			  "msg": "Bad Request: http://localhost:9000/messages",
			  "status": 400
			}

8. Fetch messages

	curl -k -X GET -b cookie-jar.txt 'http://localhost:9000/messages?user_id_1=1&user_id_2=2&page=1&messages_per_page=20'

			{
			  "msg": "Bad Request: http://localhost:9000/messages?user_id_1=1&user_id_2=2&page=1&messages_per_page=20",
			  "status": 400
			}
