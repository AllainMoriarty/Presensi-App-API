from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Path
from sqlalchemy.orm import Session
from typing import List
from app.schemas.absen import AbsenCreate, AbsenResponse, SessionOpenRequest, SessionCloseRequest, AbsenHistoryResponse
from app.services import absen_service
from app.config import get_db, get_current_user
from app.models.user import User
from scripts import face_recognition_integration 
import threading

router = APIRouter(prefix="/absen", tags=["Absensi"])

face_recognition_stop_events = {}

@router.post("/session/open", status_code=status.HTTP_200_OK)
def open_absen_session(
    background_tasks: BackgroundTasks,
    request: SessionOpenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "dosen":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Hanya dosen yang dapat membuka sesi absensi")

    absen_service.open_session(request.id_jadwal)

    # Buat event untuk penghentian
    stop_event = threading.Event()
    # Simpan event ke dictionary yang ada di dalam service
    absen_service.FACE_RECOGNITION_STOP_EVENTS[request.id_jadwal] = stop_event

    background_tasks.add_task(face_recognition_integration.run_face_recognition, request.id_jadwal, request.id_matkul, current_user, stop_event)
    return {"detail": f"Sesi absensi untuk id_jadwal {request.id_jadwal} telah dibuka dan face recognition dijalankan."}

@router.post("/session/close", status_code=status.HTTP_200_OK)
def close_absen_session(
    request: SessionCloseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "dosen":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Hanya dosen yang dapat menutup sesi absensi")
    
    # Cukup panggil service ini, logikanya sudah ada di dalam
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
