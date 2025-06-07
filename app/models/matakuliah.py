# app/models/matakuliah.py
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.kelas_matkul import kelas_matkul  # Import association table kelas_matkul

# app/models/matakuliah.py (BARU & DIPERBAIKI)
class Matakuliah(Base):
    __tablename__ = "matakuliah"
    
    id_matkul = Column(Integer, primary_key=True, index=True)
    nama_matkul = Column(String, nullable=False)
    id_dosen = Column(BigInteger, ForeignKey("users.nip", onupdate="CASCADE", ondelete="SET NULL"), nullable=True)
    
    # Relasi ke dosen
    dosen = relationship("User", back_populates="matakuliah", foreign_keys=[id_dosen]) # <-- TAMBAHKAN back_populates="matakuliah"
    
    # Many-to-many dengan Kelas
    kelas = relationship("Kelas", secondary=kelas_matkul, back_populates="matakuliah")