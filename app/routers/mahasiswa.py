from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Path
from sqlalchemy.orm import Session
from typing import List
from app.schemas.absen import AbsenCreate, AbsenResponse
from app.services import absen_service
from app.config import get_db, get_current_user
from app.models.user import User
from scripts import face_recognition_integration 

router = APIRouter(prefix="/mahasiswa", tags=["Mahasiswa"])

@router.get("/rekap-absen", response_model=List[AbsenResponse])
def get_absen_by_mahasiswa(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "mahasiswa":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
    return absen_service.get_absen_by_mahasiswa(db, current_user.nrp)