import json

from fastapi import FastAPI, Request, Form, File, UploadFile, Depends, HTTPException
from fastapi.responses import HTMLResponse
from typing import Union, Optional
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from starlette import status
from starlette.responses import Response

from ORM_models import Users
from auth import get_password_hash, create_access_token, get_current_user, type_of_curr_user
from database import SessionLocal, engine, source_to_list_of_dic, select_from_source, Base, orm_select_sinner, \
    orm_select_characters, orm_select_identity, orm_select_last_identity, orm_select_ego, orm_select_last_ego, \
    orm_get_user_by_login, add_new_user, authenticate_user, all_users, add_willing_book_into_reading_list, \
    add_finished_book_into_reading_list, fast_add_finished_book_into_reading_list, select_from_identity, \
    orm_select_reading_list, add_new_id, delete_old_id
from database import get_db, Base
from fastapi import FastAPI, File, UploadFile, Depends
from sqlalchemy.orm import Session
import base64

from pydantic_models import UserLoginRegister, Identity

app = FastAPI()
templates = Jinja2Templates(directory="templates")


#Base.metadata.create_all(bind=engine)

def list_of_models_to_list_of_dic(models):
    return [model.to_dic() for model in models]

async def get_current_admin_user(current_user: Users = Depends(get_current_user)):
    if current_user.is_superuser:
        return current_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав!')


"""
    This function handles the root route of the application.

    Parameters:
    - request (Request): The request object.
    - user_info (bool): A boolean indicating user information.
    - db (Session): The database session.

    Returns:
    - TemplateResponse: A response with the main page template.
    """
@app.get('/', response_class=HTMLResponse)
async def root(request: Request, user_info: bool = Depends(type_of_curr_user), db: Session = Depends(get_db)):
    result_ego = orm_select_last_ego(db)
    result_identity = orm_select_last_identity(db)
    result_chars = orm_select_characters(db)
    result_sinner = orm_select_sinner(db)
    result = {
              "request": request,
              "user_type": 1 if user_info is None else 2 if user_info is True else 3,
              "ego": result_ego,
              "identity": result_identity,
              "sinners": result_sinner,
              "characters": result_chars,

    }
    print(result)
    return templates.TemplateResponse("main_page.html", result)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/ego_list", response_class=HTMLResponse)
async def root(request: Request, user_info: bool = Depends(type_of_curr_user), db: Session = Depends(get_db)):
    result_ego = orm_select_ego(db)
    result = {
        "request": request,
        "user_type": 1 if user_info is None else 2 if user_info is True else 3,
        "ego": result_ego,
    }
    return templates.TemplateResponse("ego.html", result)

@app.get("/reading_list_new", response_class=HTMLResponse)
async def root(request: Request, user_data: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    result = orm_select_reading_list(db, user_data.id)
    result["request"] = request
    result["user_type"] = 2
    return templates.TemplateResponse("reading_list.html", result)

@app.get("/id_list", response_class=HTMLResponse)
async def root(request: Request, user_info: bool = Depends(type_of_curr_user), db: Session = Depends(get_db)):
    result = {
        "request": request,
        "user_type": 1 if user_info is None else 2 if user_info is True else 3,
    }
    print(result["user_type"])
    return templates.TemplateResponse("identities.html", result)


@app.get("/id_list/edit", response_class=HTMLResponse)
def edit_page(request: Request, db: Session = Depends(get_db), user_data: Users = Depends(get_current_admin_user)):
    result = select_from_identity(db)
    print(result)
    context = {
        "request": request,
        "identity": result
    }
    print(context)
    return templates.TemplateResponse("add_id.html", context)


@app.get("/source")
async def source(db: Session = Depends(get_db), title: Optional[str] = None, author: Optional[str] = None):
    list_title = []
    list_author = []
    if title:
        list_title = title.split(',')
    if author:
        list_author = author.split(',')
    result = select_from_source(db, list_title, list_author)
    list_of_source = source_to_list_of_dic(result)
    return list_of_source

@app.get("/sinners")
async def sinners(db: Session = Depends(get_db), rarity: Optional[str] = None, sinner: Optional[str] = None):
    list_rarity = []
    list_sinner = []
    if rarity:
        list_rarity = rarity.split(',')
    if sinner:
        list_sinner = sinner.split(',')
    result = select_from_identity(db, rarity=list_rarity, sinner=list_sinner)
    return result

@app.get("/characters")
async def characters(db: Session = Depends(get_db)):
    result = orm_select_characters(db)
    return result

@app.get("/identity")
async def characters(db: Session = Depends(get_db)):
    result = orm_select_identity(db)
    return result

@app.get("/recent_identity")
async def characters(db: Session = Depends(get_db)):
    result = orm_select_last_identity(db)
    return result

@app.get("/ego")
async def characters(db: Session = Depends(get_db)):
    result = orm_select_ego(db)
    return result

@app.get("/recent_ego")
async def characters(db: Session = Depends(get_db)):
    result = orm_select_last_ego(db)
    return result

@app.get("/recent")
async def characters(db: Session = Depends(get_db)):
    result_ego = orm_select_last_ego(db)
    result_identity = orm_select_last_identity(db)
    result = {"ego": result_ego,
              "identity": result_identity}
    return result

@app.post("/register_user/")
async def register_user(response: Response,user_data: UserLoginRegister, db: Session = Depends(get_db)) -> dict:
    user = orm_get_user_by_login(db, user_data.login)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь уже существует'
        )
    user_dict = user_data.dict()
    user_dict['password'] = get_password_hash(user_data.password)
    add_new_user(db, user_dict)
    check = authenticate_user(db, login=user_data.login, password=user_data.password)
    print(check)
    if check is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверная почта или пароль')
    access_token = create_access_token({"sub": str(check.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {'message': 'Вы успешно зарегистрированы!'}

@app.post("/login_user/")
async def auth_user(response: Response, user_data: UserLoginRegister, db: Session = Depends(get_db)):
    check = authenticate_user(db, login=user_data.login, password=user_data.password)
    print(check)
    if check is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверная почта или пароль')
    access_token = create_access_token({"sub": str(check.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {'access_token': access_token, 'refresh_token': None}

@app.get("/me/")
async def get_me(user_data: Users = Depends(get_current_user)):
    return user_data

@app.get("/me_without_mistake/")
async def get_me(user_info: bool = Depends(type_of_curr_user)):
    return user_info

@app.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    return {'message': 'Пользователь успешно вышел из системы'}


@app.get("/all_users/")
async def get_all_users(user_data: Users = Depends(get_current_admin_user),  db: Session = Depends(get_db)):
    result = all_users(db)
    return result

@app.post("/add_into_reading_list")
async def add_into_reading_list(title: str = Form(...),
                                user_data: Users = Depends(get_current_user),  db: Session = Depends(get_db)):
    if add_willing_book_into_reading_list(db, title, user_data.id):
        return {"Книга успешно добавлена!"}
    return {"Книга не найдена!"}

@app.post("/add_into_finished_reading_list")
async def add_into_finished_reading_list(title: str = Form(...),
                                         user_data: Users = Depends(get_current_user),  db: Session = Depends(get_db)):
    if add_finished_book_into_reading_list(db, title):
        return {"Прочитанная книга успешно добавлена!"}
    return {"Книга не найдена в списке чтения!"}

@app.post("/fast_add_into_finished_reading_list")
async def fast_add_into_finished_reading_list(title: str = Form(...),
                                              user_data: Users = Depends(get_current_user),  db: Session = Depends(get_db)):
    if fast_add_finished_book_into_reading_list(db, title, user_data.id):
        return {"Прочитанная книга успешно добавлена!"}
    return {"Книга не найдена в списке чтения!"}
@app.get("/reading_list")
async def get_all_users(user_data: Users = Depends(get_current_user),  db: Session = Depends(get_db)):
    result = orm_select_reading_list(db, user_data.id)
    return result

@app.post("/add_id")
def add_id(identity: Identity, db: Session = Depends(get_db), user_data: Users = Depends(get_current_admin_user)):
    id_dict = identity.dict()
    check = add_new_id(db, id_dict)
    if check:
        return {"message": "Идентичность успешно добавлена"}
    else:
        return {"message": "Ошибка при добавлении идентичности"}

@app.delete("/delete_id")
def delete_id(identity: Identity, db: Session = Depends(get_db), user_data: Users = Depends(get_current_admin_user)):
    check = delete_old_id(db, identity.title, identity.sinner)
    if check:
        return {"message": "Идентичность успешно удалена!"}
    else:
        raise HTTPException(status_code=400, detail="Ошибка при удалении идентичности")

@app.put("/update_id")
def update_id(identity_old: Identity, identity_new: Identity, db: Session = Depends(get_db), user_data: Users = Depends(get_current_admin_user)):
    check = delete_old_id(db, identity_old.title, identity_old.sinner)
    print(identity_new.file)
    id_dict = identity_new.dict()
    check = add_new_id(db, id_dict)
    if check:
        return {"message": "Идентичность успешно обновлена!"}
    else:
        raise HTTPException(status_code=400, detail="Ошибка при обновлении идентичности")
'''

    for char, source in chars:
        if source:
            result.append({
                "character_id": char.character_id,
                "name": char.name,
                "source_title": source.title,
                "source_author": source.author
            })
        else:
            result.append({
                "character_id": char.character_id,
                "name": char.name
            })
    
    
@app.get("/", response_class=HTMLResponse)
async def root(request: Request, db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM source")).fetchall()
    print(result)
    list_of_source = source_to_list_of_dic(result)
    return templates.TemplateResponse("articles.html", {"request": request, "source": list_of_source})


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

'''
'''

class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}

'''
app.mount("/static", StaticFiles(directory="static"), name="static")