from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import IntegrityError
from typing import Optional, List

# Define the base for declarative models
Base = declarative_base()

# Define the Category model
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String, nullable=False) # e.g., "Food", "Subscription", "Shopping"

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', type='{self.type}')>"

class TransactionClassifier:
    def __init__(self, db_url: str = "sqlite:///./categories.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Populate default categories if they don't exist
        self._populate_default_categories()

    def _populate_default_categories(self):
        db = self.SessionLocal()
        try:
            default_categories = [
                {"name": "Starbucks", "type": "Food"},
                {"name": "McDonalds", "type": "Food"},
                {"name": "Netflix", "type": "Subscription"},
                {"name": "Spotify", "type": "Subscription"},
                {"name": "Amazon", "type": "Shopping"},
                {"name": "Walmart", "type": "Shopping"},
            ]
            
            for cat_data in default_categories:
                # Check if category already exists to avoid duplicates
                if not db.query(Category).filter_by(name=cat_data["name"]).first():
                    category = Category(name=cat_data["name"], type=cat_data["type"])
                    db.add(category)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error populating default categories: {e}")
        finally:
            db.close()

    def create_category(self, name: str, category_type: str, description: Optional[str] = None) -> Optional[Category]:
        db = self.SessionLocal()
        try:
            new_category = Category(name=name, type=category_type, description=description)
            db.add(new_category)
            db.commit()
            db.refresh(new_category)
            return new_category
        except IntegrityError:
            db.rollback()
            print(f"Category with name '{name}' already exists.")
            return None
        except Exception as e:
            db.rollback()
            print(f"Error creating category: {e}")
            return None
        finally:
            db.close()

    def get_category(self, category_id: int) -> Optional[Category]:
        db = self.SessionLocal()
        try:
            return db.query(Category).filter(Category.id == category_id).first()
        finally:
            db.close()

    def get_all_categories(self) -> List[Category]:
        db = self.SessionLocal()
        try:
            return db.query(Category).all()
        finally:
            db.close()

    def update_category(self, category_id: int, new_name: Optional[str] = None, 
                        new_category_type: Optional[str] = None, new_description: Optional[str] = None) -> Optional[Category]:
        db = self.SessionLocal()
        try:
            category = db.query(Category).filter(Category.id == category_id).first()
            if not category:
                return None
            if new_name:
                category.name = new_name
            if new_category_type:
                category.type = new_category_type
            if new_description is not None: # Allow setting to None
                category.description = new_description
            db.commit()
            db.refresh(category)
            return category
        except IntegrityError:
            db.rollback()
            print(f"Cannot update category to name '{new_name}', it already exists.")
            return None
        except Exception as e:
            db.rollback()
            print(f"Error updating category: {e}")
            return None
        finally:
            db.close()

    def delete_category(self, category_id: int) -> bool:
        db = self.SessionLocal()
        try:
            category = db.query(Category).filter(Category.id == category_id).first()
            if category:
                db.delete(category)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            print(f"Error deleting category: {e}")
            return False
        finally:
            db.close()

    def classify_transaction(self, description: str) -> str:
        db = self.SessionLocal()
        try:
            # Check against stored categories first
            for category_rule in db.query(Category).all():
                if category_rule.name.lower() in description.lower():
                    return category_rule.type
            return "Uncategorized"
        finally:
            db.close()

def get_classifier() -> TransactionClassifier:
    return TransactionClassifier()
