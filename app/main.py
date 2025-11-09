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
