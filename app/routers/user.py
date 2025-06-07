from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.services import user_service # Service yang baru kita buat
from app.schemas.user import UserOut # Schema untuk output, agar password tidak ikut terkirim
from app.config import get_db, get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(get_current_user)] # Melindungi semua rute di sini, harus login
)

@router.get("/mahasiswa", response_model=List[UserOut])
def read_all_mahasiswa(db: Session = Depends(get_db)):
    """
    Endpoint untuk mengambil daftar semua user dengan role mahasiswa.
    Ini dibutuhkan untuk mengisi pilihan pada form "Tambah Kelas".
    """
    mahasiswa_list = user_service.get_all_mahasiswa(db)
    return mahasiswa_list