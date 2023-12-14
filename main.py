from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from pydantic import BaseModel
import uuid

DATABASE_URL = "postgresql://postgres:admin@localhost/test_task"
Base = declarative_base()


class VisitedLink(Base):
    __tablename__ = "visited_links"

    id = Column(String, primary_key=True, default=str(uuid.uuid4()))
    link = Column(String, index=True)
    timestamp = Column(DateTime, default=func.now())


app = FastAPI()

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)


class VisitedLinksRequest(BaseModel):
    links: List[str]


@app.post("/visited_links")
def visited_links_endpoint(data: VisitedLinksRequest):
    """
    Принимает список посещенных ссылок и сохраняет их в базе данных.

    :param data: Список ссылок для сохранения.
    :return: Словарь с полем "status" равным "ok" в случае успешного сохранения.
    """
    try:
        with Session(engine) as session:
            for link in data.links:
                db_link = VisitedLink(id=str(hash(link)), link=link)
                session.add(db_link)
            session.commit()

        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/visited_domains")
def visited_domains(from_time: int, to_time: int):
    """
    Возвращает список уникальных посещенных доменов за указанный временной интервал.

    :param from_time: Время начала интервала в формате числа секунд с начала эпохи.
    :param to_time: Время конца интервала в формате числа секунд с начала эпохи.
    :return: Словарь с полем "domains" содержащим список уникальных доменов или с подробным сообщением об ошибке.
    """
    try:
        with Session(engine) as session:
            from_datetime = datetime.utcfromtimestamp(from_time)
            to_datetime = datetime.utcfromtimestamp(to_time)
            domains = []
            for link in session.query(VisitedLink).filter(
                    VisitedLink.timestamp.between(from_datetime, to_datetime)).all():
                domain = link.link.split('/')[2]
                domains.append(domain)
            # Не знаю насколько читается этот генератор, но пусть будет :)
            # domains = [link.link.split('/')[2] for link in session.query(VisitedLink).filter(
            #     VisitedLink.timestamp.between(from_datetime, to_datetime)).all()]

        return {"domains": list(set(domains)), "status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
