from sqlalchemy.orm import Session
from app.models.kelas import Kelas
from app.models.user import User
from app.models.matakuliah import Matakuliah
from app.schemas.kelas import KelasBase, KelasCreate, KelasUpdate, KelasResponse
from typing import List, Optional

def create_kelas(db: Session, kelas: KelasCreate) -> dict:
    # Buat instance kelas dengan data dasar
    new_kelas = Kelas(kode_kelas=kelas.kode_kelas, nama_kelas=kelas.nama_kelas)
    
    # Menambahkan data relasi mahasiswa jika disediakan
    if kelas.mahasiswa:
        # Ambil objek User berdasarkan nrp yang diberikan
        mahasiswa_list = db.query(User).filter(User.nrp.in_(kelas.mahasiswa)).all()
        # Tambahkan objek-objek mahasiswa ke relationship kelas
        new_kelas.mahasiswa.extend(mahasiswa_list)
    
    # Menambahkan data relasi matakuliah jika disediakan
    if kelas.matakuliah:
        # Ambil objek Matakuliah berdasarkan id_matkul yang diberikan
        matakuliah_list = db.query(Matakuliah).filter(Matakuliah.id_matkul.in_(kelas.matakuliah)).all()
        # Tambahkan objek-objek matakuliah ke relationship kelas
        new_kelas.matakuliah.extend(matakuliah_list)
    
    db.add(new_kelas)
    db.commit()
    db.refresh(new_kelas)
    
    return {
        "id_kelas": new_kelas.id_kelas,
        "kode_kelas": new_kelas.kode_kelas,
        "nama_kelas": new_kelas.nama_kelas,
        "mahasiswa": [m.nrp for m in new_kelas.mahasiswa],
        "matakuliah": [m.id_matkul for m in new_kelas.matakuliah],
    }

def get_all_kelas(db: Session) -> List[dict]:
    kelas_list = db.query(Kelas).all()
    return [
        {
            "id_kelas": k.id_kelas,
            "kode_kelas": k.kode_kelas,
            "nama_kelas": k.nama_kelas,
            "mahasiswa": [m.nrp for m in k.mahasiswa],       # Mengambil nrp dari objek User
            "matakuliah": [m.id_matkul for m in k.matakuliah],  # Mengambil id_matkul dari objek Matakuliah
        }
        for k in kelas_list
    ]


def get_kelas_by_kode(db: Session, kode_kelas: str) -> Optional[dict]:
    kelas_obj = db.query(Kelas).filter(Kelas.kode_kelas == kode_kelas).first()
    if kelas_obj is None:
        return None
    return {
        "id_kelas": kelas_obj.id_kelas,
        "kode_kelas": kelas_obj.kode_kelas,
        "nama_kelas": kelas_obj.nama_kelas,
        "mahasiswa": [m.nrp for m in kelas_obj.mahasiswa],
        "matakuliah": [m.id_matkul for m in kelas_obj.matakuliah],
    }

def get_kelas_by_matkul(db: Session, id_matkul: int) -> List[dict]:
    # Lakukan join ke relationship 'matakuliah' kemudian filter berdasarkan id_matkul
    kelas_list = (
        db.query(Kelas)
        .join(Kelas.matakuliah)
        .filter(Matakuliah.id_matkul == id_matkul)
        .all()
    )
    # Lakukan transformasi manual agar sesuai dengan schema jika diperlukan
    return [
        {
            "id_kelas": k.id_kelas,
            "kode_kelas": k.kode_kelas,
            "nama_kelas": k.nama_kelas,
            "mahasiswa": [m.nrp for m in k.mahasiswa],
            "matakuliah": [m.id_matkul for m in k.matakuliah],
        }
        for k in kelas_list
    ]


