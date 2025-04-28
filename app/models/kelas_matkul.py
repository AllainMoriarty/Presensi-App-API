# app/models/kelas_matkul.py
from sqlalchemy import Table, Column, String, Integer, ForeignKey
from app.database import Base

kelas_matkul = Table(
    "kelas_matkul",
    Base.metadata,
    Column("kode_kelas", String, ForeignKey("kelas.kode_kelas", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column("id_matkul", Integer, ForeignKey("matakuliah.id_matkul", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
)
