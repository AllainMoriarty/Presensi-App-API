from pydantic import BaseModel, Field
from typing import Optional
from typing import Optional, List
from app.schemas.kelas import KelasResponse

class MatakuliahBase(BaseModel):
    nama_matkul: str = Field(..., max_length=100)

class MatakuliahCreate(MatakuliahBase):
    pass

class MatakuliahUpdate(MatakuliahBase):
    pass

class MatakuliahResponse(MatakuliahBase):
    id_matkul: int
    id_dosen: Optional[int]
    #kelas: List[KelasResponse] = []

    class Config:
        orm_mode = True
