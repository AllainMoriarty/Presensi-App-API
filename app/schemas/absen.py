from pydantic import BaseModel, Field
from typing import Optional

# Skema sederhana untuk detail mahasiswa di history
class MahasiswaInHistory(BaseModel):
    name: str
    nrp: int

    class Config:
        from_attributes = True

# Skema baru untuk respons history
class AbsenHistoryResponse(BaseModel):
    id_mahasiswa: int
    status: str
    mahasiswa: Optional[MahasiswaInHistory] = None

    class Config:
        from_attributes = True

class AbsenBase(BaseModel):
    id_mahasiswa: int
    status: str 

class AbsenCreate(AbsenBase):
    id_matkul: int
    id_jadwal: int

class SessionOpenRequest(BaseModel):
    id_jadwal: int
    id_matkul: int

class SessionCloseRequest(BaseModel):
    id_jadwal: int

class AbsenResponse(AbsenBase):
    id_absen: int
    id_matkul: int
    id_jadwal: int

    class Config:
        from_attributes = True
