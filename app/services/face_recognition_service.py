import cv2
import torch
import os
import numpy as np
from PIL import Image
from torchvision import transforms
from facenet_pytorch import MTCNN, InceptionResnetV1
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.models.user import User
from app.services import absen_service
from app.schemas.absen import AbsenCreate

# Inisialisasi model (dilakukan sekali saat aplikasi dimulai)
print("Initializing face recognition models...")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
mtcnn = MTCNN(keep_all=True, device=device)
face_encoder = InceptionResnetV1(pretrained='vggface2').eval().to(device)
transform = transforms.Compose([
    transforms.Resize((160, 160)),
    transforms.ToTensor()
])

# Memuat dataset wajah ke dalam memori
dataset_path = "scripts/dataset" # Pastikan path ini benar
known_face_encodings = []
known_face_names = []

def load_dataset():
    """Memuat semua wajah dari dataset ke memori."""
    print("Loading face dataset...")
    valid_extensions = ('.jpg', '.jpeg', '.png')
    for person_name in os.listdir(dataset_path):
        person_folder = os.path.join(dataset_path, person_name)
        if os.path.isdir(person_folder):
            for image_name in os.listdir(person_folder):
                image_path = os.path.join(person_folder, image_name)
                if not image_path.lower().endswith(valid_extensions):
                    continue
                try:
                    image = cv2.imread(image_path)
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(image_rgb)
                    face_locations, _ = mtcnn.detect(pil_image)
                    if face_locations is not None:
                        for box in face_locations:
                            x1, y1, x2, y2 = map(int, box)
                            face = pil_image.crop((x1, y1, x2, y2))
                            face_tensor = transform(face).unsqueeze(0).to(device)
                            with torch.no_grad():
                                embedding = face_encoder(face_tensor).cpu().numpy().flatten()
                                known_face_encodings.append(embedding)
                                known_face_names.append(person_name)
                except Exception as e:
                    print(f"Error processing image {image_path}: {e}")
    print(f"Dataset loaded. Found {len(known_face_names)} known faces.")

# Panggil fungsi ini saat modul diimpor untuk pertama kali
load_dataset()

def get_face_to_nrp_mapping():
    """Menghasilkan mapping nama folder ke nrp dari database."""
    mapping = {}
    db: Session = SessionLocal()
    try:
        mahasiswa_list = db.query(User).filter(User.role == "mahasiswa").all()
        for mhs in mahasiswa_list:
            mapping[mhs.name] = mhs.nrp # Asumsi nama folder di dataset = nama user di DB
    finally:
        db.close()
    return mapping

# --- FUNGSI UTAMA YANG AKAN DIPANGGIL API ---
def process_and_recognize_face(db: Session, image_bytes: bytes, id_jadwal: int, id_matkul: int):
    """Menerima gambar, mengenali wajah, dan mencatat absensi jika cocok."""
    
    # 1. Konversi gambar dari bytes ke format yang bisa diproses OpenCV
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # 2. Deteksi wajah dari gambar yang diterima
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)
    face_locations, _ = mtcnn.detect(pil_image)
    
    if face_locations is None:
        return {"status": "failed", "detail": "Wajah tidak terdeteksi."}

    face_to_nrp_map = get_face_to_nrp_mapping()
    
    for box in face_locations:
        # 3. Ekstrak embedding dari wajah yang terdeteksi
        x1, y1, x2, y2 = map(int, box)
        face = pil_image.crop((x1, y1, x2, y2))
        face_tensor = transform(face).unsqueeze(0).to(device)
        with torch.no_grad():
            embedding = face_encoder(face_tensor).cpu().numpy().flatten()

        # 4. Bandingkan dengan dataset yang sudah di-load
        if len(known_face_encodings) > 0:
            distances = np.linalg.norm(np.array(known_face_encodings) - embedding, axis=1)
            best_match_index = np.argmin(distances)
            THRESHOLD = 0.7 
            
            if distances[best_match_index] < THRESHOLD:
                recognized_name = known_face_names[best_match_index]
                
                if recognized_name in face_to_nrp_map:
                    nrp = face_to_nrp_map[recognized_name]
                    
                    # 5. Coba buat absensi (service `create_absen` akan menangani duplikasi)
                    try:
                        absen_data = AbsenCreate(
                            id_mahasiswa=nrp,
                            status="hadir",
                            id_jadwal=id_jadwal,
                            id_matkul=id_matkul
                        )
                        absen_service.create_absen(db, absen_data)
                        print(f"Absensi berhasil untuk {recognized_name} (NRP: {nrp})")
                        # Jika berhasil, langsung kembalikan respons
                        return {"status": "success", "detail": f"Absensi berhasil untuk {recognized_name}"}
                    except Exception as e:
                        # Ini terjadi jika mahasiswa sudah absen sebelumnya
                        print(f"Gagal mencatat absensi untuk {recognized_name}: {e}")
                        return {"status": "failed", "detail": f"{recognized_name} sudah melakukan absensi."}

    return {"status": "failed", "detail": "Wajah tidak dikenali atau tidak terdaftar."}
