from pydantic import BaseModel, Field
from typing import Optional, List

class KelasBase(BaseModel):
    kode_kelas: str = Field(..., max_length=10)
    nama_kelas: str = Field(..., max_length=100)

class KelasCreate(KelasBase):
    mahasiswa: Optional[List[int]] = []
    matakuliah: Optional[List[int]] = []

class KelasUpdate(KelasBase):
    mahasiswa: Optional[List[int]] = []
    matakuliah: Optional[List[int]] = []

class KelasResponse(KelasBase):
    id_kelas: int
    kode_kelas: str
    mahasiswa: Optional[List[int]]
    matakuliah: Optional[List[int]]

    class Config:
        orm_mode = True