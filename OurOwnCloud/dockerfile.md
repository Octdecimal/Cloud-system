computeNode:
    build:
    docker build -f ./Dockerfile.1 -t compute .

    run:
    docker run -it --name node1 compute
    docker run -it --name node2 compute


    