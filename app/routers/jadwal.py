from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from app.models.user import User
from app.config import get_db, get_current_user
from app.services import jadwal_service
from app.schemas.jadwal import JadwalBase, JadwalCreate, JadwalUpdate, JadwalResponse
from app.routers import absen
from typing import List

router = APIRouter(tags=["Jadwal"])

@router.post("/", response_model=JadwalResponse)
def create_jadwal(jadwal: JadwalCreate, kode_kelas: str = Path(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "dosen":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
    
    return jadwal_service.create_jadwal(db, jadwal, kode_kelas)

@router.get("/{id_jadwal}", response_model=JadwalResponse)
def get_jadwal_by_id(id_jadwal: int = Path(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return jadwal_service.get_jadwal_by_id(db, id_jadwal)

@router.get("/", response_model=List[JadwalResponse])
def get_jadwal_by_kelas(kode_kelas: str = Path(...), db: Session = Depends(get_db)):
    return jadwal_service.get_jadwal_by_kelas(db, kode_kelas)

router.include_router(absen.router, prefix="/{id_jadwal}/absen")