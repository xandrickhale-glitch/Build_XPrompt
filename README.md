**# ✨ Pembuat Prompt Gemini (ID ➜ EN)

Sebuah aplikasi web interaktif untuk **membangun prompt gambar terstruktur dalam bahasa Indonesia**, lalu **mengonversinya ke bahasa Inggris secara otomatis** menggunakan Gemini API. Aplikasi ini dirancang untuk **pengguna non-teknis, pendidik, dan kreator konten anak**, dengan antarmuka sederhana dan hasil siap pakai untuk AI image generator seperti Midjourney, Leonardo, atau DALL·E.

🔗 [Lihat Demo (jika di-deploy)](https://xpromp.streamlit.app) *(ganti dengan link Anda)*

---
## ✅ Fitur Utama

- **🌐 UI Bahasa Indonesia** — Mudah digunakan oleh pengguna lokal.
- **🔄 Otomatis Terjemahkan ke Inggris** — Prompt dikonversi ke bahasa Inggris menggunakan Gemini.
- **🧱 Template Siap Pakai** — 20+ tema seperti "Petualangan Luar Angkasa", "Pesta Bawah Laut", "Karnaval Sirkus", dll.
- **🎨 Buat Tema Custom** — Masukkan ide bebas (misal: "mobil balapan kartun"), aplikasi akan menghasilkan prompt lengkap.
- **✂️ One-line Prompt (ID & EN)** — Format siap salin untuk input ke AI image generator.
- **📋 Copy to Clipboard** — Tombol salin yang andal (dengan fallback manual).
- **📤 Export JSON** — Simpan seluruh konfigurasi (field, toggle, hasil) untuk backup atau berbagi.
- **💾 Default Kosong + Preset "None"** — Mulai dari awal tanpa isi.
- **🔄 Update Langsung Saat Custom Theme** — Hasil langsung muncul di form.
- **🎨 Banyak Pilihan Gaya** — 19+ gaya visual (3D Pixar, Watercolor, Claymation, dll).

---

## 🛠️ Teknologi yang Digunakan

- **Streamlit** — Framework Python untuk aplikasi web interaktif.
- **Gemini API (Google AI Studio)** — Untuk terjemahan, penyempurnaan prompt, dan pembuatan tema custom.
- **Python** — Logika aplikasi, parsing, dan manajemen state.
- **JavaScript (opsional)** — Untuk fitur copy to clipboard (dinonaktifkan jika gagal).
- **dotenv** — Manajemen API key secara aman.

---

## 🚀 Cara Menjalankan di Lokal

### 1. Instal dependensi
```bash
pip install streamlit google-genai python-dotenv**

🤝 Kontribusi ( boleh traktir kopi | 0856 4990 5055)
Ingin menambahkan fitur?

Mode gelap
Simpan template ke lokal
Ekspor ke format Midjourney/Discord
Login pengguna
Silakan buka Pull Request atau Issue di repo ini!

📄 Lisensi
Distribusikan secara bebas. Cocok untuk proyek edukasi, non-profit, atau komersial.

🙏 Terima Kasih
Dibuat dengan ❤️ untuk kreator Indonesia.


