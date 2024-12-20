from sqlalchemy import create_engine, text, insert
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from fastapi import Depends

from auth import verify_password
from settings import get_database_url

DATABASE_URL = get_database_url()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def source_to_list_of_dic(source):
    list_of_dic = []
    titles = ('id', 'title', 'author', 'file')
    for s in source:
        list_of_dic.append(dict(zip(titles, s)))
    return list_of_dic


def select_from_source(db, title=None, author=None):
    statement = text("SELECT * FROM source")
    clauses = []
    params = {}
    if title:
        title_clauses = ["title = :title" + str(i) for i in range(len(title))]
        clauses.append("(" + " OR ".join(title_clauses) + ")")
        for i, t in enumerate(title):
            params[f"title{i}"] = t
    if author:
        author_clauses = ["author = :author" + str(i) for i in range(len(author))]
        if clauses:
            clauses.append("(" + " OR ".join(author_clauses) + ")")
        else:
            clauses.append("(" + " OR ".join(author_clauses) + ")")
        for i, a in enumerate(author):
            params[f"author{i}"] = a
    if clauses:
        statement = text(statement.text + " WHERE " + " AND ".join(clauses))
    result = db.execute(statement, params).fetchall()
    return result

"""
    A function that generates and executes a SQL statement to select data from the 'identity' table 
    based on the provided 'sinner' and 'rarity' parameters. The function returns a list of dictionaries 
    containing character data. Parameters:
    - db: Database connection object
    - sinner: A list of strings representing sinner names to filter the query by
    - rarity: A list of integers representing rarity values to filter the query by
    Return:
    - result: A list of dictionaries containing character data
"""
def select_from_identity(db, sinner=None, rarity=None):
    statement = text("SELECT * FROM identity JOIN sinners ON sinners.sinner_id = identity.sinner_id")
    clauses = []
    params = {}
    if sinner:
        sinner_clauses = ["name = :name" + str(i) for i in range(len(sinner))]
        clauses.append("(" + " OR ".join(sinner_clauses) + ")")
        for i, t in enumerate(sinner):
            params[f"name{i}"] = t
    if rarity:
        raity_clauses = ["rarity = :rarity" + str(i) for i in range(len(rarity))]
        if clauses:
            clauses.append("(" + " OR ".join(raity_clauses) + ")")
        else:
            clauses.append("(" + " OR ".join(raity_clauses) + ")")
        for i, a in enumerate(rarity):
            params[f"rarity{i}"] = a
    if clauses:
        statement = text(statement.text + " WHERE " + " AND ".join(clauses))
    curr_result = db.execute(statement, params).fetchall()
    result = []
    for rez in curr_result:
        print(rez)
        character_data = {
            "id_title": rez[1],
            "id_rarity": rez[4],
            "sinners_id": rez[3],
            "name": rez[6],
            "file": rez[2]
        }
        result.append(character_data)
    return result


def orm_select_sinner(db):
    from ORM_models import Source, Sinners
    sins = db.query(Sinners, Source) \
        .join(Source, Sinners.source_id == Source.source_id) \
        .all()
    result = []
    for sin, source in sins:
        character_data = {
            "sinners_id": sin.sinner_id,
            "name": sin.name,
            "nick": sin.nick,
            "source_title": source.title,
            "source_author": source.author,
            "file": sin.file
        }
        result.append(character_data)
    return result

def orm_select_characters(db):
    from ORM_models import Source, Characters
    chars = db.query(Characters, Source) \
        .join(Source, Characters.source_id == Source.source_id, isouter=True) \
        .all()
    result = []
    for char, source in chars:
        character_data = {
            "character_id": char.character_id,
            "name": char.name,
            "source_title": source.title if source else None,
            "source_author": source.author if source else None,
            "file": char.file
        }
        result.append(character_data)
    return result

def orm_select_identity(db):
    from ORM_models import Identity, Sinners
    sins = db.query(Sinners, Identity) \
        .join(Identity, Sinners.sinner_id == Identity.sinner_id) \
        .all()
    result = []
    for sin, id in sins:
        character_data = {
            "id_title": id.title,
            "id_rarity": id.rarity,
            "sinners_id": sin.sinner_id,
            "name": sin.name,
            "file": id.file
        }
        result.append(character_data)
    return result

def orm_select_last_identity(db):
    from ORM_models import Identity, Sinners
    sins = db.query(Sinners, Identity) \
        .join(Identity, Sinners.sinner_id == Identity.sinner_id) \
        .order_by(Identity.identity_id.desc()).limit(3)\
        .all()
    result = []
    for sin, id in sins:
        character_data = {
            "id_title": id.title,
            "id_rarity": id.rarity,
            "sinners_id": sin.sinner_id,
            "name": sin.name,
            "file": id.file
        }
        result.append(character_data)
    return result

def orm_select_ego(db):
    from ORM_models import EGO, Sinners, SinnerEgo
    query = db.query(EGO, Sinners, SinnerEgo).join(SinnerEgo, EGO.ego_id == SinnerEgo.ego_id)\
    .join(Sinners, Sinners.sinner_id == SinnerEgo.sinner_id).all()
    result = []
    for ego, sin, sinego in query:
        character_data = {
            "ego_title": ego.title,
            "ego_level": sinego.level,
            "sinners_id": sin.sinner_id,
            "name": sin.name,
            "file": ego.file
        }
        result.append(character_data)
    return result

def orm_select_last_ego(db):
    from ORM_models import EGO, Sinners, SinnerEgo
    query = db.query(EGO, Sinners, SinnerEgo).join(SinnerEgo, EGO.ego_id == SinnerEgo.ego_id)\
    .join(Sinners, Sinners.sinner_id == SinnerEgo.sinner_id)\
    .order_by(EGO.ego_id.desc()).limit(3)\
        .all()
    result = []
    for ego, sin, sinego in query:
        character_data = {
            "ego_title": ego.title,
            "ego_level": sinego.level,
            "sinners_id": sin.sinner_id,
            "name": sin.name,
            "file": ego.file
        }
        result.append(character_data)
    return result

def orm_get_user_by_login(db, user_login):
    from ORM_models import Users
    user = db.query(Users).filter(Users.login == user_login).first()
    return user


def orm_get_user_by_id(user_id):
    from ORM_models import Users
    db = SessionLocal()
    user = db.query(Users).filter(Users.id == user_id).first()
    return user

def add_new_user(db, user_data):
    from ORM_models import Users
    new_user = Users(**user_data)
    db.add(new_user)
    db.commit()

def authenticate_user(db, login, password):
    user = orm_get_user_by_login(db, login)
    if not user or verify_password(plain_password=password, hashed_password=user.password) is False:
        return None
    return user

def all_users(db):
    from ORM_models import Users
    users = db.query(Users).all()
    return users

def add_willing_book_into_reading_list(db, book, user_id):
    from ORM_models import ReadingList, Source
    new_book_id = db.query(Source).filter(Source.title == book).first().source_id
    if not new_book_id:
        return None
    new_book = ReadingList(user_id=user_id, source_id=new_book_id, status=False)
    db.add(new_book)
    db.commit()
    return new_book

def add_finished_book_into_reading_list(db, book):
    from ORM_models import ReadingList, Source
    book_id = db.query(Source).filter(Source.title == book).first().source_id
    reading_list = db.query(ReadingList).filter(ReadingList.source_id == book_id).first()
    if not reading_list:
        return None
    reading_list.status = True
    db.commit()
    return reading_list

def fast_add_finished_book_into_reading_list(db, book, user_id):
    from ORM_models import ReadingList, Source
    new_book_id = db.query(Source).filter(Source.title == book).first().source_id
    if not new_book_id:
        return None
    new_book = ReadingList(user_id=user_id, source_id=new_book_id, status=True)
    db.add(new_book)
    db.commit()
    return new_book

def get_source_by_id(db, source_id):
    from ORM_models import Source
    source = db.query(Source).filter(Source.source_id == source_id).first()
    return source

def reading_list_into_dic(db, list):
    result = []
    for source_id, date in list:
        source = get_source_by_id(db, source_id)
        data = {
            "title": source.title,
            "author": source.author,
            "adding_time": date.strftime('%d-%m-%Y'),
            "file": source.file
        }
        result.append(data)
    return result

def orm_select_reading_list(db, user_id):
    from ORM_models import Users, Source
    will_result = db.execute(text("CALL short_select_false_status(:user_id)"), {"user_id": user_id}).fetchall()
    read_result = db.execute(text("CALL short_select_true_status(:user_id)"), {"user_id": user_id}).fetchall()
    fin_will_result = reading_list_into_dic(db, will_result)
    fin_read_result = reading_list_into_dic(db, read_result)
    title_fin_will_result = {book['title'] for book in reading_list_into_dic(db, will_result)}
    title_fin_read_result = {book['title'] for book in reading_list_into_dic(db, read_result)}

    all_result = db.query(Source).all()
    fin_all_result = []
    for source in all_result:
        if source.title not in title_fin_will_result and source.title not in title_fin_read_result:
            character_data = {
                "title": source.title,
                "author": source.author,
                "file": source.file
            }
            fin_all_result.append(character_data)
    result = {
        "not_read": fin_all_result,
        "will": fin_will_result,
        "read": fin_read_result,
        "user_login": db.query(Users).filter(Users.id == user_id).first().login
    }
    return result


def add_new_id(db, id_data):
    from ORM_models import Identity, Sinners
    sinner_id = db.query(Sinners).filter(Sinners.name == id_data["sinner"]).first().sinner_id
    id = db.query(Identity).filter(Identity.title == id_data["title"]).filter(Identity.sinner_id == sinner_id).first()
    if id:
        return False
    new_id = Identity(title=id_data["title"], sinner_id=sinner_id, rarity=id_data["rarity"])
    if id_data["file"] is not None and id_data["file"] != "":
        new_id.file = id_data["file"]
    db.add(new_id)
    db.commit()
    return True

def delete_old_id(db, id_title, sinner):
    from ORM_models import Identity, Sinners
    sinner_id = db.query(Sinners).filter(Sinners.name == sinner).first().sinner_id
    id = db.query(Identity).filter(Identity.title == id_title).filter(Identity.sinner_id == sinner_id).first()
    if not id:
        return False
    db.delete(id)
    db.commit()
    return True