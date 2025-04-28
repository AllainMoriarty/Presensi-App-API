# app/models/matakuliah.py
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.kelas_matkul import kelas_matkul  # Import association table kelas_matkul

class Matakuliah(Base):
    __tablename__ = "matakuliah"
    
    id_matkul = Column(Integer, primary_key=True, index=True)
    nama_matkul = Column(String, nullable=False)
    id_dosen = Column(BigInteger, ForeignKey("users.nip", onupdate="CASCADE", ondelete="SET NULL"), nullable=True)
    
    # Relasi ke dosen
    dosen = relationship("User", foreign_keys=[id_dosen])
    
    # Many-to-many dengan Kelas melalui association table kelas_matkul
    kelas = relationship("Kelas", secondary=kelas_matkul, back_populates="matakuliah")
