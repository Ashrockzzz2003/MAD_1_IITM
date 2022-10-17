import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy import select

from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, autoincrement = True, primary_key = True)
    user_name = Column(String, unique = True)
    email = Column(String, unique = True)

class Article(Base):
    __tablename__ = 'article'
    article_id = Column(Integer, autoincrement = True, primary_key = True)
    title = Column(String)
    content = Column(String)
    authors = relationship("User", secondary = "article_authors")

class ArticleAuthors(Base):
    __tablename__ = 'article_authors'
    user_id = Column(Integer, ForeignKey("user.user_id"), primary_key = True, nullable = False)
    article_id = Column(Integer, ForeignKey("article.article_id"), primary_key = True, nullable = False)

engine = create_engine("sqlite:///./testdb.sqlite3")

if __name__ == "__main__":

    # Add Data Approach_2
    """
    with Session(engine, autoflush=False) as session:
        session.begin()
        try:
            author = session.query(User).filter(User.user_name == "Ananya R").one()
            article = Article(title = "Music", content="Music heals people. Music heals the world.")
            article.authors.append(author)
            session.add(article)
        except:
            print("Rolling Back...")
            session.rollback()
            raise
        else:
            print("Code is smooth as Butter! Commit")
            session.commit()
    """

    # Add Data Approach_1
    """
    with Session(engine, autoflush=False) as session:
        session.begin()
        try:
            article = Article(title = "Avengers Review", content="Great Film!")
            session.add(article)
            session.flush()

            # print(article.article_id)
            article_authors = ArticleAuthors(user_id = 5, article_id = article.article_id)
            session.add(article_authors)
        except:
            print("Rolling Back")
            session.rollback()
            raise
        else:
            print("Commit!")
            session.commit()
    """

    # View Data
    
    with Session(engine) as session:
        articles = session.query(Article).all()
        for article in articles:
            print("Article Title: ", article.title)
            count = 0
            for author in article.authors:
                count += 1
                print(f"Author_{count}: ", author.user_name)
            print(f"Content:\n{article.content}" )
            print("")
    
    
    # Execute Queries
    """
    stmt = select(User)
    print("---------- QUERY ----------")
    print(stmt)

    with engine.connect() as conn:
        print("---------- RESULT ----------")
        for row in conn.execute(stmt):
            print(row)
    """