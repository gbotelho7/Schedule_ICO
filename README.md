# ICO

Para poder correr a aplicação localmente, basta entrar na pasta source e abri-la com um IDE (por exemplo, VSCODE).
De seguida, basta correr o ficheiro index.html.


Correr o algoritmo em docker:

docker build -t room-assignment-app .       
docker run --name room-assignment-OS -p 5000:5000 room-assignment-app

Aceder ao ficheiros:
docker container ls
docker exec -it room-assignment-OS /bin/bash

ou utilizado o Docker Desktop
