from pydantic import BaseModel

class AbsenBase(BaseModel):
    id_mahasiswa: int
    status: str  # misalnya "hadir" atau "alpha"

class AbsenCreate(AbsenBase):
    pass

class AbsenResponse(AbsenBase):
    id_absen: int
    id_mahasiswa: int
    id_matkul: int
    id_jadwal: int
    status: str

    class Config:
        orm_mode = True
