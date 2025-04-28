from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from typing import List
from app.models.user import User
from app.config import get_db, get_current_user
from app.services import kelas_service
from app.schemas.kelas import KelasBase, KelasCreate, KelasUpdate, KelasResponse
from app.routers import jadwal

router = APIRouter(tags=["Kelas"])

@router.post("/", response_model=KelasResponse)
def create_kelas(
    kelas: KelasCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "dosen":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    return kelas_service.create_kelas(db, kelas)
@router.get("/", response_model=List[KelasResponse])
def get_all_kelas(db: Session = Depends(get_db)):
    return kelas_service.get_all_kelas(db)

@router.get("/{kode_kelas}", response_model=KelasResponse)
def get_kelas_by_kode(kode_kelas: str, db: Session = Depends(get_db)):
    kelas = kelas_service.get_kelas_by_kode(db, kode_kelas)
    if not kelas:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kelas tidak ditemukan")
    
    return kelas

@router.get("/by-matkul", response_model=List[KelasResponse])
def get_kelas_by_matkul(id_matkul: int = Path(...),  db: Session = Depends(get_db)):
    results = kelas_service.get_kelas_by_matkul(db, id_matkul)
    return [{"kode_kelas": kode, "nama_kelas": nama} for kode, nama in results]

router.include_router(jadwal.router, prefix="/{kode_kelas}/jadwal")