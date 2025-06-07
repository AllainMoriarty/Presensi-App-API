# app/main.py (BARU & DIPERBAIKI)
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # 1. IMPORT INI
from app.routers import auth, matakuliah, kelas, jadwal, absen, mahasiswa, user
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

# 2. TAMBAHKAN BLOK KODE INI
origins = [
    "http://localhost",
    "http://localhost:5173", # Ganti dengan port frontend Vite kamu jika berbeda
    "http://127.0.0.1:5173",
    # Kamu bisa tambahkan origin lain jika ada, misal alamat frontend setelah di-deploy
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Izinkan semua method (GET, POST, dll)
    allow_headers=["*"], # Izinkan semua header
)
# SELESAI MENAMBAHKAN KODE

app.include_router(auth.router)
app.include_router(matakuliah.router)
app.include_router(kelas.router)
app.include_router(jadwal.router)
app.include_router(absen.router)
app.include_router(mahasiswa.router)
app.include_router(user.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)