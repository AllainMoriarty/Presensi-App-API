from sqlalchemy.orm import Session
from app.models.user import User
from typing import List

def get_all_mahasiswa(db: Session) -> List[User]:
    """
    Mengambil semua user dari database yang memiliki role 'mahasiswa'.
    """
    return db.query(User).filter(User.role == 'mahasiswa').all()