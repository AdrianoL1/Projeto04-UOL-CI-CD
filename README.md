![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/fastapi-%23009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%232496ED.svg?style=for-the-badge&logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/kubernetes-%23326CE5.svg?style=for-the-badge&logo=kubernetes&logoColor=white)
![Rancher](https://img.shields.io/badge/rancher-%230075A8.svg?style=for-the-badge&logo=rancher&logoColor=white)
![ArgoCD](https://img.shields.io/badge/ArgoCD-%23EF7422.svg?style=for-the-badge&logo=argo&logoColor=white)

# CI/CD com Github Actions e GitOps - Books API

### Objetivo: Automatizar o ciclo completo de desenvolvimento, build, deploy e execução de uma aplicação FastAPI simples, usando GitHub Actions para CI/CD, Docker Hub como registry, e ArgoCD para entrega contínua em Kubernetes local com Rancher Desktop.

## Índice

1. [Pré-requisitos](#1-pré-requisitos)
2. [Criar um app com FastAPI](#2-criar-um-app-com-fastapi)
    - 2.1 [Criando um repositório no GitHub para o projeto](#21-criando-um-repositório-no-github-para-o-projeto)
    - 2.2 [Criando um Dockerfile para executar o aplicativo](#22-criando-um-dockerfile-para-executar-o-aplicativo)
3. [Criar um Workflow com Github Actions](#3-criar-um-workflow-com-github-)
4. [Criar repositório com manifests do ArgoCD](#4-criar-um-repositório-com-manifests-do-argocd)
5. [Instalando ArgoCD no Cluster local](#5-instalando-argocd-no-cluster-local)
    - 5.1 [Acessar o ArgoCD localmente](#51-acessar-o-argocd-localmente)
6. [Criar o App no ArgoCD](#6-criar-o-app-no-argocd)
7. [Acessar e testar a aplicação](#7-acessar-e-testar-a-aplicação)

## 1. Pré-requisitos

- Conta no GitHub.
- Conta no DockerHub.
- Rancher Desktop com Kubernetes habilitado.
- Git, Python 3 e Docker instalados.

## 2. Criar um app com FastAPI

### Criaremos uma API de livros, simulando um banco de dados como e uma arquitetura de Controller e Service.

### 2.1. Criando um repositório no GitHub para o projeto
- Vá até seu perfil no GitHub, clique em **_Repositories_** e **_New_**.
- Preencha os campos e clique em **_Create repository_**

![Exemplo repositorio](https://github.com/user-attachments/assets/932c3e21-aae7-41aa-af34-5c12f2def217)

> [!IMPORTANT]
> Não esqueça de adicionar o .gitignore para o Python, assim, evitaremos o commit de pastas e arquivos desnecessários.

- Abra o Git bash em sua máquina, clone e abra o repositório criado.
- Para clonar clique em **_Code_** no repositório criado, copie a URL e rode o comando:

```
   git clone https://github.com/<SEU-USUARIO>/<SEU-REPOSITÓRIO>.git
```

- Com o repositório aberto em um editor de texto ou IDE de sua preferência, crie a seguinte estrutura de pastas e arquivos:

```
seu-repositório/
├── app/
     ├── main.py
     ├── fake_db.py
```

![Estrutura pastas](https://github.com/user-attachments/assets/c6b191da-d92b-4e56-a687-5d46caf6dd9f)

- Após isso, abra o terminal e instale o FastAPI com o comando:

```
pip install fastapi[standard]
```

- E crie o arquivo **_requirements.txt_** com o seguinte comando:

```
pip freeze > requirements.txt
```

> [!TIP]
> Podemos criar um **_ambiente virtual_** em Python, assim podemos separar todas as dependências, evitando conflitos e organizando melhor a aplicação.
> 
> Para isso, rode o comando: ``` python -m venv venv ```
> E em seguida, ative o ambiente com ``` .\venv\Scripts\Activate.ps1 ``` para Windows, ou, ``` .\venv\Scripts\activate ``` para distros Linux.

> [!IMPORTANT]
> Talvez seja necessário permitir a execução de comandos no Windows, para isso, utilize: ``` Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass ```.

### Vamos criar nossa simulação de um banco de dados, utilizando uma classe Python, um dicionário e funções que atuam como o Service da aplicação, validando erros e realizando operações CRUD no dicionário.

- Abra o arquivo **_fake_db.py_**, copie e cole o seguinte código:

```
class Books:
    def __init__(self):
        self.books_db = {
            1: {"name": "Marina", "author": "Carlos Ruiz Zafón", "date": "1999"},
            2: {"name": "Neuromancer", "author": "William Gibson", "date": "1984"},
            3: {"name": "O Fantasma de Canterville", "author": "Oscar Wilde", "date": "1887"}
        }

    def list_all(self):
        return self.books_db
    
    def get_book_or_exception(self, id):
        if int(id) not in self.books_db:
            raise ValueError(f"Livro com ID {id} não encontrado")
    
    def create(self, name, author, date):
        if any(book["name"].lower() == name.lower() for book in self.books_db.values()):
            raise ValueError("Livro já cadastrado")
        
        book_id = max(self.books_db.keys()) + 1
        new_book = self.books_db[book_id] = {"name": name, "author": author, "date": date}
        return new_book
    
    def delete(self, id):
        self.get_book_or_exception(id)
        self.books_db.pop(int(id))
        return f"Livro com ID {id} removido com sucesso"
    
    def update(self, id, name, author, date):
        self.get_book_or_exception(id)
        if name:
            self.books_db[int(id)]["name"] = name
        if author:
            self.books_db[int(id)]["author"] = author
        if date:
            self.books_db[int(id)]["date"] = date

        return f"Livro com ID {id} atualizado com sucesso"
```

### Agora vamos criar nosso Controller da aplicação, para mapear e atender as requisições REST, devolvendo as respostas e status codes adequedos.

- Abra o arquivo **_main.py_**, copie e cole o seguinte código:

```
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from fake_db import Books

app = FastAPI()
books = Books()

@app.get("/")
def redirect():
    return RedirectResponse(url="/docs")

@app.get("/books")
def list_all():
    return JSONResponse(content=books.list_all(), status_code=200)

@app.post("/books")
async def create_book(name, author, date):
    try:
        new_book = books.create(name=name, author=author, date=date)
        return JSONResponse(content=new_book, status_code=201)
    except ValueError as e:
        raise HTTPException(status_code=300, detail=str(e))

@app.put("/books/{book_id}")
async def update_book(book_id, name, author, date):
    try:
        return JSONResponse(
            content=books.update(id=book_id, name=name, author=author, date=date),
            status_code=200
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/books/{book_id}")
def delete_book(book_id):
    try:
        JSONResponse(content=books.delete(book_id), status_code=204)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

```

> ![IMPORTANT]
> Salve seus arquivos para não perder as alterações realizadas.

### 2.2 Criando um Dockerfile para executar o aplicativo

- Na sua IDE crie um arquivo Dockerfile, copie e cole o seguinte código:

```
FROM python:3.13.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["fastapi", "dev", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
```

O código acima serve para copiarmos todo o conteúdo do nosso diretório, instalar todas as dependências necessáias, e rodarmos o servidor local na porta 8000.


- Após isso basta enviar as alterações para o Git com os seguintes comandos:

```
git add .
```

```
git commit -m "feat: add API app and Dockerfile"
```

```
git push origin main
```

## 3. Criar um Workflow com Github 

- No diretório principal da sua aplicação, crie as seguintes pastas e arquivo:
```
├── .github/
     ├── workflows/
         ├── build-and-deploy.yml
```

![Workflows](https://github.com/user-attachments/assets/b7ea8787-9d5f-4a41-a754-b8d71a64e747)

- Agora, vamos criar as chaves secretas no GitHub, para podermos logar no Docker Hub e fazer o deploy da imagem automaticamente.
- No seu repositório, vá até **_Settings_** > **_Actions_** > **_New repository secret_**.
- Crieremos 4 chaves, **_DOCKER_ACCESS_TOKEN_**, **_DOCKER_USERNAME_**, **_REPOSITORY_** e **_REPO_ACCESS_TOKEN_**.
- Para **_DOCKER_USERNAME_**, copie e cole seu nome de usuário do Docker Hub.
- Para **_REPOSITORY_**, copie e cole o nome do seu repositório criado anteriormente no GitHub.
- Já para **_DOCKER_ACCESS_TOKEN_**, iremos criar um Token no Docker Hub. Para isso vá até o Docker Hub, clique no ícone do seu perfil, **_My profile_** > **_Personal access tokens_** > **_Generate new token_**, e crie um token com data de expiração **_None_** e com permissões de **_Read, Write, Delete_**.

![Token](https://github.com/user-attachments/assets/284fe356-fba6-4f2f-91ed-978b383240f0)

- Para **_REPO_ACCESS_TOKEN_**, acesse o GitHub e vá até **_Settings_** > **_Developer Settings_** > **_Fine-grained tokens_** > **_Generate new token_**.
- Crie um token com as seguintes configurações:

| Expiration    | Repository access | Permissions                                                                           |
|---------------|-----------|---------------------------------------------------------------------------------------|
| No expiration | All repositories       | Contents (Read and write)<br/>Metadata (Read only)<br/>Pull requests (Read and write) |             

- Clique em _**Generate token**_.

![Repo token](https://github.com/user-attachments/assets/d2928b02-4d30-4ddf-bba1-0dd407dd8190)

- No arquivo .yml, cole o seguinte código:

```
name: Build and Deploy to Docker Hub
on:
  workflow_dispatch:
  push:
    branches:
      - "main"
jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_ACCESS_TOKEN }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.DOCKER_USERNAME }}/books-api:latest
            ${{ secrets.DOCKER_USERNAME }}/books-api:v${{ github.run_number }}

  update-manifests:
    needs: docker
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - name: Checkout Manifests Repo
        uses: actions/checkout@v4
        with:
          repository: ${{ secrets.REPOSITORY }}
          token: ${{ secrets.REPO_ACCESS_TOKEN }}
          path: projeto-cicd

      - name: Update Docker image tag
        run: |
          cd projeto-cicd
          sed -i 's|image: .*/books-api:.*|image: ${{ secrets.DOCKER_USERNAME }}/books-api:v${{ github.run_number }}|' k8s/api-deployment.yml
      
      - name: Create Pull Request
        id: create-pr
        uses: peter-evans/create-pull-request@v6
        with:
          token: ${{ secrets.REPO_ACCESS_TOKEN }}
          path: projeto-cicd
          commit-message: "chore: update Docker image to version v${{ github.run_number }}"
          branch: update-image-${{ github.run_number }}
          title: "Update image to version ${{ github.run_number }}"
          base: main
          delete-branch: false

      - name: Enable Pull Request Automerge
        run: |
          cd projeto-cicd
          gh pr merge --merge --auto --delete-branch "${{ steps.create-pr.outputs.pull-request-number }}"
        env:
          GH_TOKEN: ${{ secrets.REPO_ACCESS_TOKEN }}
```

- Após isso basta enviar as alterações para o Git com os seguintes comandos:

```
git add .
```

```
git commit -m "chore: build and push image to docker hub registry and auto merge"
```

```
git push origin main
```

## 4. Criar um repositório com manifests do ArgoCD
- Vá até seu perfil no GitHub, clique em **_Repositories_** e **_New_**.
- Preencha os campos e clique em **_Create repository_**

![Repo 2](https://github.com/user-attachments/assets/d2520f20-5119-4e4d-9645-75625d107fdc)

- Com o repositório aberto em um editor de texto ou IDE de sua preferência, crie a seguinte estrutura de pastas e arquivos:

```
seu-repositório/
├── k8s/
     ├── api-deployment.yml
     ├── api-service.yml
```

![Estrutura pastas](https://github.com/user-attachments/assets/d6664bc9-b435-4e89-92bf-d64a4efdc616)

- No arquivo **_api-deployment.yml_**, cole o seguinte código:

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: books-api-deployment
  labels:
    app: books-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: books-api
  template:
    metadata:
      labels:
        app: books-api
    spec:
      containers:
      - name: books-api
        image: <SEU-USERNAME>/books-api:v1
        ports:
        - containerPort: 8000
```

>![IMPORTANT]
> Substitua a variável <SEU-USERNAME>, com o seu nome de usuário do Docker Hub.

- No arquivo **_api-service.yml_**, cole o seguinte código:

```
apiVersion: v1
kind: Service
metadata:
  name: books-service
  labels:
    app: books-api
spec:
  type: ClusterIP
  selector:
    app: books-api
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8000
```

- Após isso basta enviar as alterações para o Git com os seguintes comandos:

```
git add .
```

```
git commit -m "chore: add service and deployment files"
```

```
git push origin main
```

## 5. Instalando ArgoCD no Cluster local
- Com o Rancher Desktop devidamente instalado e rodando, abra o Git bash e digite os seguintes comandos:
```
kubectl create namespace argocd
``` 

```
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
``` 

### 5.1. Acessar o ArgoCD localmente
- Para acessarmos o ArgoCD, devemos fazer um port-forward para a interface web.
- Rode o seguinte comando para realizar o port-forward:
```
kubectl port-forward svc/argocd-server -n argocd 8080:443
```
- Agora, ao acessar o [localhost:8080](http://localhost:8080), aparecerá a tela inicial do ArgoCD.

![Tela ArgoCD](https://github.com/user-attachments/assets/1a07c4b7-b6e8-4a8f-8c18-c32fa7bf6dc7)

- Para logar, devemos utilizar o usuário e senha padrões:
- Usuário: admin
- Para obter a senha, rode o seguinte comando e copie a saída:
```
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 --decode
```

![Dashboard ArgoCD](https://github.com/user-attachments/assets/269417ca-7235-4938-a363-ffa16c0c1247)

## 6. Criar o App no ArgoCD

- Acesse a página do ArgoCD, e clique em **_New App_**.
- Clique em **_Edit as YAML_** e cole o seguinte código:

```
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: projeto-cicd
spec:
  destination:
    namespace: argocd
    server: https://kubernetes.default.svc
  source:
    path: k8s/
    repoURL: <SEU-REPOSITÓRIO>.git
    targetRevision: HEAD
  sources: []
  project: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
      enabled: true
    syncOptions:
      - CreateNamespace=true
```
> [!IMPORTANT]
> Substitua "SEU-REPOSITÓRIO" com a URL do seu repositório, caso contrário, não funcionará.

![Argo App](https://github.com/user-attachments/assets/83cd6bfe-fa16-4011-9ad0-0706598acb98)

## 7. Acessar e testar a aplicação
- Para acessarmos o front-end da aplicação, devemos fazer um port-forward para o site.
- Rode o seguinte comando para realizar o port-forward:
```
kubectl port-forward -n argocd svc/books-service 8081:8080
```
- Após isso, basta ir até o [localhost:8081](http:localhost:8081) e poderemos ver a página inicial da aplicação.

![Tela app](https://github.com/user-attachments/assets/81bfad73-f1a5-48aa-b838-fa52ab4dc0c5)

- Também é possível testar a API através do Swagger.

![GET exemplo](https://github.com/user-attachments/assets/576b3c8f-ac14-4d7e-bdff-4eac545c9233)

- Agora, vá até o **_fake_db.py_** e faça uma alteração no código (ex: mude os dados de um livro no dicionário) e faça um push para a branch main.

### GitHub Actions: O push irá rodar o workflow.

### docker: O job "docker" constrói uma nova imagem e publica no Docker Hub com uma nova tag (ex: v2, v3).

### update-manifests: Faz o checkout do repositório dos manifests, altera a tag da imagem no arquivo api-deployment.yml, cria uma PR e faz o merge automaticamente.

![Pipeline GH](https://github.com/user-attachments/assets/261f3cf8-15ad-4914-82ec-3e3d9d583d76)

### Docker Hub: A imagem atualizada aparece no Docker Hub.

![Docker Hub img](https://github.com/user-attachments/assets/e6ec842c-2eb4-4782-ba38-c2725aaf82a5)

### Manifests: O repositório de manifests é atualizado automaticamente com a nova imagem.

![Repo atualizado](https://github.com/user-attachments/assets/2efeb5df-a3a3-4d3d-9d8b-d1de2834b3bb)

### ArgoCD: Detecta a mudança no repositório e aplica as alterações no cluster Kubernetes, atualizando para a nova versão da imagem.

![Argo Nova img](https://github.com/user-attachments/assets/2a9576a3-a91b-49e9-b725-b2102e48ae78)

- Podemos verificar o número de pods no terminal com o seguinte comando:

```
kubectl get pods -n argocd
```

![Pods](https://github.com/user-attachments/assets/cf46abbb-fc91-4e7e-877a-39f59c8812ef)