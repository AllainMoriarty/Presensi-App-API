# app/models/kelas_mahasiswa.py
from sqlalchemy import Table, Column, String, BigInteger, ForeignKey
from app.database import Base

kelas_mahasiswa = Table(
    "kelas_mahasiswa",
    Base.metadata,
    Column("kode_kelas", String, ForeignKey("kelas.kode_kelas", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column("nrp_mahasiswa", BigInteger, ForeignKey("users.nrp", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
)
