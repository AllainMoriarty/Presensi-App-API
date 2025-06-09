from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Path, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List
from app.schemas.absen import AbsenCreate, AbsenResponse, SessionOpenRequest, SessionCloseRequest, AbsenHistoryResponse, VerificationRequest
from app.services import absen_service
from app.services import face_recognition_service
from app.config import get_db, get_current_user
from app.models.user import User
# from scripts import face_recognition_integration 
import threading

router = APIRouter(prefix="/absen", tags=["Absensi"])

face_recognition_stop_events = {}

@router.post("/session/open", status_code=status.HTTP_200_OK)
def open_absen_session(
    request: SessionOpenRequest,
    current_user: User = Depends(get_current_user)
):
    """Hanya membuka flag bahwa sesi aktif."""
    if current_user.role != "dosen":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Hanya dosen yang dapat membuka sesi absensi")
    absen_service.open_session(request.id_jadwal)
    return {"detail": f"Sesi absensi untuk id_jadwal {request.id_jadwal} telah dibuka."}

@router.post("/session/close", status_code=status.HTTP_200_OK)
def close_absen_session(
    request: SessionCloseRequest,
    current_user: User = Depends(get_current_user)
):
    """Hanya menutup flag bahwa sesi aktif."""
    if current_user.role != "dosen":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Hanya dosen yang dapat menutup sesi absensi")
    absen_service.close_session(request.id_jadwal)
    return {"detail": f"Sesi absensi untuk id_jadwal {request.id_jadwal} telah ditutup."}

@router.post("/", response_model=AbsenResponse, status_code=status.HTTP_201_CREATED)
def create_absen(
    absen: AbsenCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not absen_service.is_session_open(absen.id_jadwal):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sesi absensi tidak aktif untuk jadwal ini.")
    if current_user.role == "dosen":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Anda tidak berhak mencatat absensi untuk orang lain.")
    new_absen = absen_service.create_absen(db, absen)
    return new_absen

@router.get("/", response_model=List[AbsenResponse])
def read_all_absen(
    db: Session = Depends(get_db)
):
    return absen_service.get_all_absen(db)

@router.get("/history/{id_jadwal}", response_model=List[AbsenHistoryResponse])
def get_history_absen_by_jadwal(
    id_jadwal: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "dosen":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Hanya dosen yang dapat melihat history absensi")
    
    history = absen_service.get_absen_by_jadwal(db, id_jadwal)
    return history

@router.post("/verifikasi-wajah")
async def verifikasi_wajah(
    db: Session = Depends(get_db),
    # Deklarasikan setiap field dari form secara eksplisit
    id_jadwal: int = Form(...),
    id_matkul: int = Form(...),
    image: UploadFile = File(...)
):
    """Menerima gambar dari frontend, memproses, dan mencatat absensi."""

    # 1. Pastikan sesi untuk jadwal ini sedang dibuka
    if not absen_service.is_session_open(id_jadwal):
        raise HTTPException(status_code=403, detail="Sesi absensi untuk jadwal ini sedang ditutup.")

    # 2. Baca gambar sebagai bytes
    image_bytes = await image.read()

    # 3. Panggil service untuk memproses gambar
    result = face_recognition_service.process_and_recognize_face(
        db=db,
        image_bytes=image_bytes,
        id_jadwal=id_jadwal, # Gunakan parameter langsung
        id_matkul=id_matkul  # Gunakan parameter langsung
    )

    if result.get("status") == "failed":
        raise HTTPException(status_code=400, detail=result.get("detail"))

    return result