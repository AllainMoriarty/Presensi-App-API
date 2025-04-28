from sqlalchemy.orm import Session
from app.models.jadwal import Jadwal
from app.schemas.jadwal import JadwalBase, JadwalCreate, JadwalUpdate, JadwalResponse
from typing import List

def create_jadwal(db: Session, jadwal: JadwalCreate, kode_kelas: str) -> Jadwal:
    new_jadwal = Jadwal(kode_kelas=kode_kelas, week=jadwal.week, tanggal=jadwal.tanggal)
    db.add(new_jadwal)
    db.commit()
    db.refresh(new_jadwal)
    return new_jadwal

def get_all_jadwal(db: Session) -> list[Jadwal]:
    return db.query(Jadwal).all()

def get_jadwal_by_id(db: Session, id_jadwal: int) -> Jadwal:
    return db.query(Jadwal).filter(Jadwal.id_jadwal == id_jadwal).first()

def get_jadwal_by_kelas(db: Session, kode_kelas: str) -> List[Jadwal]:
    return db.query(Jadwal).filter(Jadwal.kode_kelas == kode_kelas).all()