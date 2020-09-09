react_container:
	docker run -v $(shell pwd)/react.quizzer.app:/appx -it node:10 /bin/bash -c "cd /appx ; ls -al ; npm install ; npm run start-all"
