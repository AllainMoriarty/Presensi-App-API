import cv2
import torch
import os
import numpy as np
from PIL import Image
from torchvision import transforms
from facenet_pytorch import MTCNN, InceptionResnetV1
import time
import requests
import threading
from sqlalchemy.orm import Session
from app.config import SessionLocal

# Inisialisasi device, model, dan transformasi wajah
device = torch.device("cuda" if torch.cuda.is_available() 
                      else ("mps" if torch.backends.mps.is_available() else "cpu"))
print("Device:", device)

mtcnn = MTCNN(keep_all=True, device=device)
face_encoder = InceptionResnetV1(pretrained='vggface2').eval().to(device)

transform = transforms.Compose([
    transforms.Resize((160, 160)),
    transforms.ToTensor()
])

def get_face_embeddings(image):
    """
    Mendeteksi wajah dan mengembalikan list tuple (embedding, (x1, y1, x2, y2)).
    """
    if image is None:
        return []
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)
    face_locations, _ = mtcnn.detect(pil_image)
    results = []
    if face_locations is not None:
        for box in face_locations:
            x1, y1, x2, y2 = map(int, box)
            face = pil_image.crop((x1, y1, x2, y2))
            face_tensor = transform(face).unsqueeze(0).to(device)
            with torch.no_grad():
                embedding = face_encoder(face_tensor).cpu().numpy().flatten()
            results.append((embedding, (x1, y1, x2, y2)))
    return results

def load_dataset(dataset_path):
    """
    Memuat dataset wajah, mengembalikan (encodings, names).
    """
    known_face_encodings = []
    known_face_names = []
    valid_extensions = ('.jpg', '.jpeg', '.png')
    for person_name in os.listdir(dataset_path):
        person_folder = os.path.join(dataset_path, person_name)
        if os.path.isdir(person_folder):
            for image_name in os.listdir(person_folder):
                image_path = os.path.join(person_folder, image_name)
                if not image_path.lower().endswith(valid_extensions):
                    continue
                image = cv2.imread(image_path)
                if image is None:
                    print(f"Error: Tidak bisa membaca {image_path}")
                    continue
                face_data = get_face_embeddings(image)
                for (embedding, _) in face_data:
                    known_face_encodings.append(embedding)
                    known_face_names.append(person_name)
    return np.array(known_face_encodings), np.array(known_face_names)

def get_face_to_nrp_mapping():
    """
    Menghasilkan mapping nama ke nrp dengan query ke database.
    Diasumsikan tabel users memiliki field 'nama' dan 'nrp' untuk mahasiswa.
    """
    mapping = {}
    db: Session = SessionLocal()
    try:
        from app.models.user import User  # pastikan model User tersedia
        mahasiswa = db.query(User).filter(User.role == "mahasiswa").all()
        for mhs in mahasiswa:
            mapping[mhs.name] = mhs.nrp
    finally:
        db.close()
    return mapping

def run_face_recognition(id_jadwal: int, id_matkul: int, dosen, stop_event: threading.Event):
    dataset_path = "scripts/dataset"
    known_face_encodings, known_face_names = load_dataset(dataset_path)
    print(f"Jumlah wajah yang diketahui: {len(known_face_encodings)}")

    face_to_nrp = get_face_to_nrp_mapping()
    
    THRESHOLD = 0.7
    start_time = time.time()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Kamera tidak dapat dibuka.")
        return

    detection_start_times = {}
    absensi_sent = set()

    from app.config import SessionLocal
    from app.services import absen_service
    from app.schemas.absen import AbsenCreate

    while time.time() - start_time < 3600 and not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)
        face_data = get_face_embeddings(frame)
        
        detected_nrp_current = set()
        
        for (face_embedding, (x1, y1, x2, y2)) in face_data:
            recognized_name = "Unknown"
            if len(known_face_encodings) > 0:
                distances = np.linalg.norm(known_face_encodings - face_embedding, axis=1)
                best_match_index = np.argmin(distances)
                if distances[best_match_index] < THRESHOLD:
                    recognized_name = known_face_names[best_match_index]
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, recognized_name, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            if recognized_name != "Unknown" and recognized_name in face_to_nrp:
                nrp = face_to_nrp[recognized_name]
                detected_nrp_current.add(nrp)
                now = time.time()
                if nrp not in detection_start_times:
                    detection_start_times[nrp] = now
                else:
                    duration = now - detection_start_times[nrp]
                    if duration >= 3 and nrp not in absensi_sent:
                        absen_data = AbsenCreate(
                            id_mahasiswa=nrp,
                            status="hadir",
                            detection_duration=int(duration)
                        )
                        db = SessionLocal()
                        try:
                            absen_service.create_absen(db, absen_data, id_matkul, id_jadwal)
                            absensi_sent.add(nrp)
                            print(f"Absensi terkirim untuk nrp {nrp} setelah terdeteksi selama {int(duration)} detik.")
                        except Exception as e:
                            print(f"Gagal mengirim absensi untuk nrp {nrp}: {e}")
                        finally:
                            db.close()
        
        nrp_yang_tidak_terdeteksi = set(detection_start_times.keys()) - detected_nrp_current
        for nrp in nrp_yang_tidak_terdeteksi:
            detection_start_times.pop(nrp)
        
        cv2.imshow('Face Recognition', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Proses face recognition selesai.")

# Pastikan tidak ada kode eksekusi langsung di level modul.
if __name__ == '__main__':
    # Jika file dijalankan langsung, contoh eksekusi:
    # Pastikan untuk mengganti parameter sesuai kondisi yang valid.
    run_face_recognition(1, 1, None)
