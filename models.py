
from sqlalchemy import Column, Integer, LargeBinary
from database import Base


class ImageModel(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    image_data = Column(LargeBinary)