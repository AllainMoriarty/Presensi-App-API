# app/models/user.py
from sqlalchemy import Column, BigInteger, String, Enum, CheckConstraint, Integer
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class RoleEnum(str, enum.Enum):
    mahasiswa = "mahasiswa"
    dosen = "dosen"

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    nrp = Column(BigInteger, unique=True, nullable=True)  # Hanya untuk mahasiswa
    nip = Column(BigInteger, unique=True, nullable=True)  # Hanya untuk dosen

    __table_args__ = (
        CheckConstraint(
            "(role = 'mahasiswa' AND nrp IS NOT NULL AND nip IS NULL) OR (role = 'dosen' AND nip IS NOT NULL AND nrp IS NULL)",
            name="chk_role_nrp_nip"
        ),
    )

    # Many-to-many dengan Kelas (mahasiswa)
    kelas = relationship("Kelas", secondary="kelas_mahasiswa", back_populates="mahasiswa")
