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