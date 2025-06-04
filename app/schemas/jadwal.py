from pydantic import BaseModel
from datetime import date
from typing import Optional

class JadwalBase(BaseModel):
    week: int
    tanggal: date

class JadwalCreate(JadwalBase):
    pass

class JadwalUpdate(JadwalBase):
    week: Optional[int] = None
    tanggal: Optional[date] = None

class JadwalResponse(JadwalBase):
    id_jadwal: int
    kode_kelas: str
    week: int
    tanggal: date

    class Config:
        orm_mode = True