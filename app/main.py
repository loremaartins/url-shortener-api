import secrets
import string
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener & Analytics API",
    description="API REST para encurtamento de URLs com persistência em banco de dados e contagem de cliques.",
    version="1.0.0",
)


def generate_short_code(length: int = 6) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


@app.post("/shorten", response_model=schemas.URLInfo, status_code=status.HTTP_201_CREATED)
def create_short_url(url_data: schemas.URLCreate, db: Session = Depends(get_db)):
    short_code = generate_short_code()
    while db.query(models.URLItem).filter(models.URLItem.short_code == short_code).first():
        short_code = generate_short_code()

    db_url = models.URLItem(
        target_url=str(url_data.target_url),
        short_code=short_code,
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url


@app.get("/stats/{short_code}", response_model=schemas.URLInfo)
def get_url_stats(short_code: str, db: Session = Depends(get_db)):
    db_url = db.query(models.URLItem).filter(models.URLItem.short_code == short_code).first()
    if not db_url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return db_url


@app.delete("/urls/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_short_url(short_code: str, db: Session = Depends(get_db)):
    db_url = db.query(models.URLItem).filter(models.URLItem.short_code == short_code).first()
    if not db_url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    db.delete(db_url)
    db.commit()
    return None


@app.get("/{short_code}")
def redirect_to_target(short_code: str, db: Session = Depends(get_db)):
    db_url = db.query(models.URLItem).filter(models.URLItem.short_code == short_code).first()
    if not db_url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    db_url.clicks += 1
    db.commit()
    return RedirectResponse(url=db_url.target_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
