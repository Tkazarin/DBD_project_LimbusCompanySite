from fastapi import FastAPI, Request, Form, File, UploadFile, Depends, HTTPException
from fastapi.responses import HTMLResponse
from typing import Union
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database import SessionLocal, engine
from models import ImageModel, Base
from fastapi import FastAPI, File, UploadFile, Depends
from sqlalchemy.orm import Session
import base64

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root():
    return {"message": "Hello World"}

Base.metadata.create_all(bind=engine)

# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
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

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    image = ImageModel(image_data=contents)
    db.add(image)
    db.commit()
    db.refresh(image)
    return {"filename": file.filename, "id": image.id}

@app.get("/images/{image_id}", response_class=HTMLResponse)
async def get_image(image_id: int, db: Session = Depends(get_db)):
    image = db.query(ImageModel).filter(ImageModel.id == image_id).first()

    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")

    # Извлеките бинарные данные изображения
    image_data = image.image_data  # Это должно быть корректным бинарным содержимым

    if image_data is None:
        raise HTTPException(status_code=404, detail="Image data not found")

    # Кодирование изображения в base64
    image_data_base64 = base64.b64encode(image_data).decode("utf-8")

    # Формирование HTML-страницы с изображением
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Изображение {image_id}</title>
    </head>
    <body>
        <h1>Изображение {image_id}</h1>
        <img src="data:image/jpeg;base64,{image_data_base64}" alt="Image {image_id}">
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)




class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}


app.mount("/static", StaticFiles(directory="static"), name="static")