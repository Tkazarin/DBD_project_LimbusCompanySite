from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from typing import Union
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/articles", response_class=HTMLResponse)
async def list_articles(request: Request):
    articles = [
        {"title": "Статья 1", "content": "Содержимое статьи 1"},
        {"title": "Статья 2", "content": "Содержимое статьи 2"},
        {"title": "Статья 3", "content": "Содержимое статьи 3"},
    ]
    return templates.TemplateResponse("articles.html", {"request": request, "articles": articles})

@app.get("/{name}", response_class=HTMLResponse)
async def read_item(request: Request, name: str):
    return templates.TemplateResponse("base.html", {"request": request, "name": name})

@app.post("/update", response_class=HTMLResponse)
async def update_item(request: Request, new_name: str = Form(...)):
    return templates.TemplateResponse("base.html", {"request": request, "name": new_name})



class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}


app.mount("/static", StaticFiles(directory="static"), name="static")