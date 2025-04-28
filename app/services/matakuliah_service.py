from sqlalchemy.orm import Session
from app.models.matakuliah import Matakuliah
from app.schemas.matakuliah import MatakuliahCreate, MatakuliahUpdate
from typing import List, Optional

def create_matakuliah(db: Session, matkul: MatakuliahCreate, id_dosen: int) -> Matakuliah:
    new_matkul = Matakuliah(nama_matkul=matkul.nama_matkul, id_dosen=id_dosen)
    db.add(new_matkul)
    db.commit()
    db.refresh(new_matkul)
    return new_matkul

def get_all_matakuliah(db: Session) -> List[Matakuliah]:
    return db.query(Matakuliah).all()

def get_matakuliah_by_id(db: Session, id_matkul: int) -> Optional[Matakuliah]:
    return db.query(Matakuliah).filter(Matakuliah.id_matkul == id_matkul).first()

def get_matakuliah_by_dosen(db: Session, id_dosen: int) -> Optional[Matakuliah]:
    return db.query(Matakuliah).filter(Matakuliah.id_dosen == id_dosen).all()

def update_matakuliah(db: Session, id_matkul: int, matkul: MatakuliahUpdate, id_dosen: int) -> Optional[Matakuliah]:
    db_matkul = get_matakuliah_by_id(db, id_matkul)
    if db_matkul is None or db_matkul.id_dosen != id_dosen:
        return None
    db_matkul.nama_matkul = matkul.nama_matkul
    db.commit()
    db.refresh(db_matkul)
    return db_matkul

def delete_matakuliah(db: Session, id_matkul: int, id_dosen: int) -> bool:
    db_matkul = get_matakuliah_by_id(db, id_matkul)
    if db_matkul is None or db_matkul.id_dosen != id_dosen:
        return False
    db.delete(db_matkul)
    db.commit()
    return True
