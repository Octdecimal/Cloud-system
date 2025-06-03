computeNode:  
    build:  
    `docker build -f ./Dockerfile.1 -t compute .`  

    run:  
    `docker run -it -v /uploads:/uploads --name node1 compute  
    docker run -it -v /uploads:/uploads --name node2 compute`  


webNode:  
    build:  
    `docker build -f ./Dockerfile.2 -t web .`  

    run:  
    `docker run -p 8000:8000 -p 5137:5137 -it -v /uploads:/uploads -v ./backend:/backend -v ./vue:/vue --name web --restart unless-stopped web`  

    restart:  
    `docker start -ai web`  
