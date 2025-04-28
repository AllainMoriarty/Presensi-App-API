from sqlalchemy.orm import Session
from app.models.absen import Absen
from app.schemas.absen import AbsenCreate
from typing import List
from fastapi import HTTPException
from app.models.kelas import Kelas
from app.models.jadwal import Jadwal

# Global dictionary untuk status sesi absensi; key = id_jadwal, value = bool (True jika open)
SESSION_STATUS = {}

def open_session(id_jadwal: int):
    SESSION_STATUS[id_jadwal] = True

def close_session(id_jadwal: int):
    SESSION_STATUS[id_jadwal] = False

def is_session_open(id_jadwal: int) -> bool:
    return SESSION_STATUS.get(id_jadwal, False)

def create_absen(db: Session, absen_data: AbsenCreate, id_matkul: int, id_jadwal: int) -> Absen:
    # Validasi agar sesi terbuka
    if not is_session_open(id_jadwal):
        raise HTTPException(status_code=403, detail="Sesi absensi tidak dibuka.")

    # Validasi: Mahasiswa tidak boleh absen lebih dari sekali
    existing = db.query(Absen).filter(
        Absen.id_mahasiswa == absen_data.id_mahasiswa,
        Absen.id_jadwal == id_jadwal
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Mahasiswa sudah melakukan absensi pada jadwal ini.")

    # Dapatkan informasi jadwal
    jadwal = db.query(Jadwal).filter(Jadwal.id_jadwal == id_jadwal).first()
    if not jadwal:
        raise HTTPException(status_code=404, detail="Jadwal tidak ditemukan.")

    # Ambil kelas dari jadwal
    kelas = db.query(Kelas).filter(Kelas.kode_kelas == jadwal.kode_kelas).first()
    if not kelas:
        raise HTTPException(status_code=404, detail="Kelas tidak ditemukan.")

    # Validasi bahwa matakuliah dari kelas sesuai dengan id_matkul
    matkul_ids = [mk.id_matkul for mk in kelas.matakuliah]
    if id_matkul not in matkul_ids:
        raise HTTPException(status_code=400, detail="Matakuliah tidak sesuai dengan kelas ini.")

    # Validasi: Mahasiswa harus terdaftar di kelas ini (via association table)
    mahasiswa_ids = [mhs.nrp for mhs in kelas.mahasiswa]
    if absen_data.id_mahasiswa not in mahasiswa_ids:
        raise HTTPException(status_code=403, detail="Mahasiswa tidak terdaftar dalam kelas ini.")

    # Buat absen
    new_absen = Absen(
        id_mahasiswa=absen_data.id_mahasiswa,
        id_matkul=id_matkul,
        id_jadwal=id_jadwal,
        status=absen_data.status,
    )
    db.add(new_absen)
    db.commit()
    db.refresh(new_absen)
    return new_absen


def get_all_absen(db: Session) -> List[Absen]:
    return db.query(Absen).all()

def get_absen_by_id(db: Session, id_absen: int) -> Absen:
    return db.query(Absen).filter(Absen.id_absen == id_absen).first()

def get_absen_by_mahasiswa(db: Session, id_mahasiswa: int) -> Absen:
    return db.query(Absen).filter(Absen.id_mahasiswa == id_mahasiswa).all()

def update_absen(db: Session, id_absen: int, absen_data: AbsenCreate) -> Absen:
    absen_record = get_absen_by_id(db, id_absen)
    if absen_record:
        absen_record.id_jadwal = absen_data.id_jadwal
        absen_record.status = absen_data.status
        db.commit()
        db.refresh(absen_record)
    return absen_record

def delete_absen(db: Session, id_absen: int) -> bool:
    absen_record = get_absen_by_id(db, id_absen)
    if not absen_record:
        return False
    db.delete(absen_record)
    db.commit()
    return True
