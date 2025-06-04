from pydantic import BaseModel, Field
from typing import Optional, List

class KelasBase(BaseModel):
    kode_kelas: str = Field(..., max_length=10)
    nama_kelas: str = Field(..., max_length=100)
    mahasiswa: Optional[List[int]] = None
    matakuliah: Optional[List[int]] = None

class KelasCreate(KelasBase):
    pass

class KelasUpdate(BaseModel):
    kode_kelas: Optional[str] = None
    nama_kelas: Optional[str] = None
    mahasiswa: Optional[List[int]] = None
    matakuliah: Optional[List[int]] = None

class KelasResponse(KelasBase):
    id: int

    class Config:
        from_attributes = True