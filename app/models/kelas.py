# app/models/kelas.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.kelas_mahasiswa import kelas_mahasiswa  # Import association table mahasiswa
from app.models.kelas_matkul import kelas_matkul        # Import association table matakuliah

class Kelas(Base):
    __tablename__ = "kelas"
    
    id_kelas = Column(Integer, primary_key=True, index=True)
    kode_kelas = Column(String, unique=True, nullable=True)
    nama_kelas = Column(String, nullable=False)
    
    # Many-to-many dengan Matakuliah melalui association table kelas_matkul
    matakuliah = relationship("Matakuliah", secondary=kelas_matkul, back_populates="kelas")
    
    # Many-to-many dengan Mahasiswa melalui association table kelas_mahasiswa
    mahasiswa = relationship("User", secondary=kelas_mahasiswa, back_populates="kelas")
