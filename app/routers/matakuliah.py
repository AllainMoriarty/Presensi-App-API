from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from typing import List
from app.services import matakuliah_service
from app.schemas.matakuliah import MatakuliahCreate, MatakuliahUpdate, MatakuliahResponse
from app.models.user import User
from app.config import get_db, get_current_user
from app.routers import kelas

router = APIRouter(prefix="/matakuliah", tags=["Matakuliah"])

@router.post("/", response_model=MatakuliahResponse)
def create_matkul(
    matkul: MatakuliahCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "dosen":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
    
    return matakuliah_service.create_matakuliah(db, matkul, current_user.nip)

@router.get("/", response_model=List[MatakuliahResponse])
def get_all_matkul(
    db: Session = Depends(get_db),
):
    return matakuliah_service.get_all_matakuliah(db)

@router.get("/{id_matkul}", response_model=MatakuliahResponse)
def get_matkul_by_id(
    id_matkul: int,
    db: Session = Depends(get_db),
):
    matkul = matakuliah_service.get_matakuliah_by_id(db, id_matkul)
    if not matkul:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mata kuliah tidak ditemukan")
    
    return matkul

@router.get("/dosen", response_model=List[MatakuliahResponse])
def get_matkul_by_dosen(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    matkul = matakuliah_service.get_matakuliah_by_dosen(db, current_user.nip)
    
    return matkul

@router.put("/{id_matkul}", response_model=MatakuliahResponse)
def update_matkul(
    id_matkul: int,
    matkul: MatakuliahUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "dosen":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
    
    updated = matakuliah_service.update_matakuliah(db, id_matkul, matkul, current_user.nip)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mata kuliah tidak ditemukan atau bukan milik dosen")
    return updated

@router.delete("/{id_matkul}")
def delete_matkul(
    id_matkul: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "dosen":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
    
    success = matakuliah_service.delete_matakuliah(db, id_matkul, current_user.nip)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mata kuliah tidak ditemukan atau bukan milik dosen")
    
    return {"message": "Mata kuliah berhasil dihapus"}

router.include_router(kelas.router, prefix="/{id_matkul}/kelas")