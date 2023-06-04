from sqlalchemy.orm import Session




class CRUDBase:
    def __init__(self, model):
        self.model = model
    
    def create(self, db: Session, commit: bool = False, **kwargs):
        instance = self.model(**kwargs)
        db.add(instance)
        if commit:
            db.commit()
            db.refresh(instance)
        return instance
    
    def read(self, db: Session, **kwargs):
        return db.query(self.model).filter_by(**kwargs).all()
    
    def update(self, db: Session, instance, commit: bool = False, **kwargs):
        for key, value in kwargs.items():
            setattr(instance, key, value)
        db.add(instance)
        if commit:
            db.commit()
            db.refresh(instance)
        
        return instance
    
    def delete(self, db: Session, instance, commit: bool = False):
        
        db.delete(instance)
        if commit:
            db.commit()

    def get_all(self, db: Session):
        return db.query(self.model).all()

