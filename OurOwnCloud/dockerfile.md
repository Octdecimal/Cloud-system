computeNode:
    build:
    docker build -f ./Dockerfile.1 -t compute .

    run:
    docker run -it -v /uploads --name node1 compute
    docker run -it -v /uploads --name node2 compute


webNode:
    build:
    docker build -f ./Dockerfile.2 -t web .

    run:
    docker run -p 5137:5137 -it -v /uploads --name web web
