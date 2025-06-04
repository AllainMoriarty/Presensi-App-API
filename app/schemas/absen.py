from pydantic import BaseModel

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
