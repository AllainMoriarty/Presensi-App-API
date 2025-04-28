from sqlalchemy import Column, Integer, BigInteger, ForeignKey, CheckConstraint, Date, String
from sqlalchemy.orm import relationship
from app.database import Base

class Jadwal(Base):
    __tablename__ = "jadwal"

    id_jadwal = Column(Integer, primary_key=True, index=True)
    kode_kelas = Column(String, ForeignKey("kelas.kode_kelas", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    week = Column(Integer, nullable=False)
    tanggal = Column(Date, nullable=False)


    # Relationship
    kelas = relationship("Kelas", foreign_keys=[kode_kelas])  