from sqlalchemy import Column, Integer, BigInteger, ForeignKey, CheckConstraint, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class StatusEnum(str, enum.Enum):
    hadir = "hadir",
    alpha = "alpha"

class Absen(Base):
    __tablename__ = "absen"
    
    id_absen = Column(Integer, primary_key=True, index=True)
    # Mereferensikan users.nrp (mahasiswa)
    id_mahasiswa = Column(BigInteger, ForeignKey("users.nrp", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    # Mereferensikan kelas.id_kelas
    id_matkul = Column(Integer, ForeignKey("matakuliah.id_matkul", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    id_jadwal = Column(Integer, ForeignKey("jadwal.id_jadwal", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(StatusEnum), nullable=False)
    
    # Relationship
    matakuliah = relationship("Matakuliah", foreign_keys=[id_matkul])
    mahasiswa = relationship("User", foreign_keys=[id_mahasiswa])
    jadwal = relationship("Jadwal", foreign_keys=[id_jadwal])
