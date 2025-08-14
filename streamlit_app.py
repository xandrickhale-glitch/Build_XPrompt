# streamlit_app.py — v3.1 (final: fixed session_state, dynamic style, better UX)
import os, json, re
from streamlit.components.v1 import html as st_html
import json as _json
from typing import Dict, List
import streamlit as st
from dotenv import load_dotenv
import re
from uuid import uuid4

FIELD_KEYS = [
    "Foreground", "Midground", "Background", "Floating Elements",
    "Central Banner", "Text & Effects", "Background Style", "Style & Lighting"
]

# -------------------------------
# Gemini API — robust import/fallback
# -------------------------------
def _call_gemini(prompt: str, model_name: str, api_key: str) -> str:
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        try:
            resp = client.models.generate_content(model=model_name, contents=prompt)
        except Exception:
            alt = model_name if model_name.startswith("models/") else f"models/{model_name}"
            resp = client.models.generate_content(model=alt, contents=prompt)
        return getattr(resp, "text", getattr(resp, "output_text", str(resp)))
    except Exception as e1:
        try:
            import google.generativeai as genai_old
            genai_old.configure(api_key=api_key)
            short = model_name.split("/", 1)[-1]
            model = genai_old.GenerativeModel(short)
            resp = model.generate_content(prompt)
            return getattr(resp, "text", str(resp))
        except Exception as e2:
            # 🔽 Jangan pernah gunakan RuntimeError di sini!
            error_msg = str(e2).lower()
            if "429" in str(e2) or "quota" in error_msg or "resource_exhausted" in error_msg:
                raise Exception(
                    "❌ **Kuota harian terlampaui!**\n\n"
                    "Anda telah melebihi batas permintaan gratis.\n\n"
                    "🔹 Solusi:\n"
                    "- Gunakan model `gemini-1.5-flash-8b` (kuota 500/hari)\n"
                    "- Hubungkan billing di [Google AI Studio](https://aistudio.google.com/) untuk upgrade\n"
                    "- Tunggu ~24 jam hingga kuota reset"
                )
            elif "401" in str(e2) or "unauthorized" in error_msg or "invalid key" in error_msg:
                raise Exception("❌ **API Key tidak valid.** Periksa kembali GEMINI_API_KEY Anda.")
            elif "network" in error_msg or "connection" in error_msg or "timeout" in error_msg:
                raise Exception("❌ **Gagal koneksi ke Gemini.** Periksa internet atau coba lagi nanti.")
            else:
                raise Exception(f"❌ **Gagal memanggil Gemini:**\n\n`{str(e2)}`")
        
# -------------------------------
# Presets — pack besar
# -------------------------------
PRESETS: Dict[str, Dict[str, str]] = {
    "Petualangan Luar Angkasa": {
        "Foreground": "Panda astronot berani melambaikan bendera di batu bulan (tengah-bawah), gurita alien kecil mengambang tanpa gravitasi di sampingnya.",
        "Midground": "Anjing robot biru melompat lambat (kiri), pesawat ruang angkasa berbentuk komet melintas; burung alien merah melayang dengan jejak debu bintang.",
        "Background": "Planet Saturnus bercincin bersinar (kiri-atas), UFO perak melayang (kanan-atas), sabuk asteroid berkilauan (bawah).",
        "Floating Elements": "Lencana neon ruang angkasa: 'PANDA','ALIEN','ROBOT','UFO','PLANET'.",
        "Central Banner": "Neon holografik “JELAJAHI GALAKSI!” di atas pita melayang.",
        "Text & Effects": "‘PELAJARAN ANTARIKSA GRATIS!’ pada bintang biru (kanan-atas). Jejak meteor.",
        "Background Style": "Angkasa gelap berbintang, awan kosmik seperti aurora.",
        "Style & Lighting": "3D Pixar, ekspresi besar, outline neon, palet biru-ungu, rim light dramatis kiri-bawah."
    },
    "Pesta Bawah Laut": {
        "Foreground": "Ikan badut ceria berputar dengan gelembung (tengah-bawah), bayi kura-kura menari membawa marakas karang.",
        "Midground": "Kuda laut kuning melayang (kiri), ubur-ubur bergoyang; kepiting biru berdansa menyamping.",
        "Background": "Ekor paus muncul (kiri-atas), lumba-lumba melompati cincin gelembung (kanan-atas), sinar matahari menembus permukaan.",
        "Floating Elements": "Balon gelembung bertuliskan: 'FISH','TURTLE','SEAHORSE','DOLPHIN','CRAB'.",
        "Central Banner": "Plakat karang neon “MENARI DI BAWAH LAUT!”.",
        "Text & Effects": "‘PELAJARAN LAUT GRATIS!’ dengan jejak gelembung.",
        "Background Style": "Laut biru jernih, terumbu karang, gerombolan ikan.",
        "Style & Lighting": "3D Pixar, aksen neon, caustic lembut, palet turquoise-koral."
    },
    "Pekan Kerajaan (Medieval)": {
        "Foreground": "Kucing ksatria gembul membawa piala emas (tengah-bawah), monyet badut menjuggling apel.",
        "Midground": "Anak naga hijau mengintip dari balik tenda (kiri), tupai berzirah memegang pedang mini; rubah pemusik memetik kecapi.",
        "Background": "Menara kastel berbanner (kiri-atas), roda putar kayu (kanan-atas), kembang api di langit.",
        "Floating Elements": "Perisai bertuliskan: 'KNIGHT','DRAGON','JESTER','FOX','CASTLE'.",
        "Central Banner": "Pita emas “SELAMAT DATANG DI PESTA KERAJAAN!”.",
        "Text & Effects": "‘PELAJARAN SEJARAH GRATIS!’ gaya gulungan.",
        "Background Style": "Padang hijau, tenda festival, tembok kastel.",
        "Style & Lighting": "3D Pixar, senja hangat kiri-bawah, aksen emas-merah."
    },
    "Festival Musik Rimba": {
        "Foreground": "Gorila DJ di turntable bambu (tengah-bawah), tukan bernyanyi di mikrofon.",
        "Midground": "Cheetah menari berkacamata neon (kiri), lemur berputar di ekor; kuda nil memantul mengikuti irama.",
        "Background": "Air terjun (kiri-atas), pelangi (kanan-atas), kawanan nuri terbang.",
        "Floating Elements": "Piringan vinyl neon: 'DJ','GORILLA','TOUCAN','HIPPO','CHEETAH'.",
        "Central Banner": "Papan berpijar “JUNGLE JAM!”.",
        "Text & Effects": "‘PELAJARAN MUSIK GRATIS!’ ikon nada neon.",
        "Background Style": "Kanopi rimba lebat berbunga warna-warni.",
        "Style & Lighting": "3D Pixar, tropis cerah, outline glow, spotlight panggung."
    },
    "Hari Seru Arktik": {
        "Foreground": "Beruang kutub meluncur di es (tengah-bawah), penguin melempar bola salju.",
        "Midground": "Narwhal berputar dengan kilau es (kiri), burung hantu salju melayang; anjing laut menyeimbangkan bola.",
        "Background": "Gunung es & iglo (kiri-atas), aurora (kanan-atas), pegunungan salju jauh.",
        "Floating Elements": "Lambang serpihan salju: 'BEAR','PENGUIN','SEAL','OWL','NARWHAL'.",
        "Central Banner": "Neon beku “AYO MAIN SALJU!”.",
        "Text & Effects": "‘PELAJARAN ARKTIK GRATIS!’ font kristal es.",
        "Background Style": "Bentang es berkilau, refleksi halus.",
        "Style & Lighting": "3D Pixar, palet biru-putih, soft sunlight."
    },
    "Kendaraan Kota Ceria": {
        "Foreground": "Bus sekolah tersenyum melaju (tengah-bawah), mobil pemadam melambai dengan tangga.",
        "Midground": "Ambulans menyalakan lampu hati (kiri), taksi kuning berputar; sepeda biru berkedip lampu.",
        "Background": "Gedung kota, lampu lalu lintas, jembatan jauh.",
        "Floating Elements": "Rambu lucu: 'BUS','FIRETRUCK','AMBULANCE','TAXI','BIKE'.",
        "Central Banner": "Neon “BELAJAR NAMA KENDARAAN!”.",
        "Text & Effects": "‘PELAJARAN KOTA GRATIS!’ bintang kuning.",
        "Background Style": "Kota cerah, awan lembut, jalan ramah anak.",
        "Style & Lighting": "3D Pixar, palet cerah, cahaya diagonal."
    },
    "Kebun Binatang Mini": {
        "Foreground": "Jerapah kuning meregangkan leher (kiri), penguin meluncur di perut ke arah jerapah.",
        "Midground": "Monyet hijau bergelayut di leher jerapah, zebra berjingkrak, rubah oranye melambai.",
        "Background": "Gajah teal menyemprot air (kiri-atas), burung hantu ungu di bulan sabit (kanan-atas), kanguru merah memantul; kupu pelangi, kura-kura mengintip (kanan-bawah).",
        "Floating Elements": "Balon huruf: 'LION','DOLPHIN','PENGUIN','GIRAFFE','MONKEY','ELEPHANT','OWL','KANGAROO','ZEBRA','TURTLE','FOX','BUTTERFLY'.",
        "Central Banner": "Neon “BELAJAR NAMA HEWAN!” + balok alfabet.",
        "Text & Effects": "‘PELAJARAN BAHASA INGGRIS GRATIS!’ bintang kuning, konfeti pelangi.",
        "Background Style": "Bokeh lembut: daun rimba, savana, ombak laut.",
        "Style & Lighting": "3D Pixar, ekspresi besar, outline neon, palet pelangi."
    },
    "Taman Dino Ramah": {
        "Foreground": "T-Rex kecil tersenyum (tengah-bawah) memegang balon tulang, Triceratops bayi melambai.",
        "Midground": "Pterodactyl warna pastel terbang rendah (kiri), Stegosaurus menari pelan.",
        "Background": "Gunung vulkanik damai (kiri-atas), hutan pakis (kanan-atas), jejak kaki dinosaurus.",
        "Floating Elements": "Balon: 'T-REX','TRI','PTERO','STEG','DINO'.",
        "Central Banner": "Papan kayu “SAHABAT DINO!”.",
        "Text & Effects": "‘PELAJARAN ZAMAN PURBA GRATIS!’ kilau oranye.",
        "Background Style": "Padang subur pastel, langit senja lembut.",
        "Style & Lighting": "Low-poly 3D pastel, shadow lembut."
    },
    "Kereta Api Ceria": {
        "Foreground": "Lokomotif tersenyum mengeluarkan asap hati (tengah-bawah), gerbong warna-warni bergoyang.",
        "Midground": "Kondektur beruang kecil melambaikan bendera (kiri), sinyal naik turun.",
        "Background": "Jembatan besi, bukit hijau, terowongan jauh.",
        "Floating Elements": "Plakat: 'TRAIN','ENGINE','CARRIAGE','STATION'.",
        "Central Banner": "Papan neon “ALL ABOARD!”.",
        "Text & Effects": "‘PELAJARAN TRANSPORTASI GRATIS!’ starburst kuning.",
        "Background Style": "Lembah cerah, awan kapas.",
        "Style & Lighting": "3D Pixar, rim light tipis, warna cerah."
    },
    "Karnaval Sirkus": {
        "Foreground": "Badut kucing melempar bola (tengah-bawah), singa ramah melompat melalui cincin.",
        "Midground": "Akrobat monyet di trapeze (kiri), gajah menari.",
        "Background": "Tenda sirkus merah-putih, roda bianglala mini.",
        "Floating Elements": "Balon huruf: 'CLOWN','LION','ELEPHANT','ACROBAT'.",
        "Central Banner": "Banner “CIRCUS CARNIVAL!”.",
        "Text & Effects": "‘FREE FUN LESSON!’ konfeti pelangi.",
        "Background Style": "Lampu panggung, bendera kecil warna-warni.",
        "Style & Lighting": "Neon playful, glitter halus."
    },
    "Pertanian Pagi": {
        "Foreground": "Sapi lucu menyapa (tengah-bawah), ayam jago bernyanyi di pagar.",
        "Midground": "Domba melompat (kiri), bebek berbaris; kelinci memegang wortel.",
        "Background": "Lumbung merah, kincir angin, matahari terbit.",
        "Floating Elements": "Papan: 'COW','CHICKEN','SHEEP','DUCK','RABBIT'.",
        "Central Banner": "Papan kayu “MORNING ON THE FARM!”.",
        "Text & Effects": "‘FREE FARM LESSON!’ bintang kuning.",
        "Background Style": "Padang rumput, bunga liar, awan lembut.",
        "Style & Lighting": "Gaya buku cerita pastel, cahaya pagi."
    },
    "Pesta Buah 3D (Hitam)": {
        "Foreground": "Apel tersenyum melompat (tengah-bawah), pisang meluncur spiral, jeruk berputar.",
        "Midground": "Stroberi jungkir balik (kiri), anggur memantul; semangka bergulir lucu.",
        "Background": "Latar hitam total untuk fokus karakter.",
        "Floating Elements": "Kata neon: 'JUMP','DANCE','BOUNCE','SPIN'.",
        "Central Banner": "Neon ‘DANCE & SENSORY FUN!’.",
        "Text & Effects": "Konfeti pelangi, jejak neon, bokeh halus.",
        "Background Style": "Hitam pekat, tanpa kabut.",
        "Style & Lighting": "3D Pixar, outline glow kuat, motion trails."
    },
    "Lab Sains Seru": {
        "Foreground": "Anak ilmuwan rubah memakai kacamata lab (tengah-bawah) memegang tabung reaksi berkilau.",
        "Midground": "Robot kecil membawa beaker (kiri), monster gelembung ramah melayang.",
        "Background": "Papan tulis rumus (kiri-atas), rak bahan kimia (kanan-atas), plasma globe mini.",
        "Floating Elements": "Ikon atom: 'ATOM','LAB','ROBOT','CHEM'.",
        "Central Banner": "Neon “SCIENCE IS FUN!”.",
        "Text & Effects": "Percikan neon hijau, asap lembut biru.",
        "Background Style": "Lab cerah ramah anak, permukaan putih bersih.",
        "Style & Lighting": "Plastic toy render, HDRI studio soft."
    },
    "Safari Malam": {
        "Foreground": "Singa kecil memakai senter kepala (tengah-bawah), hyena ramah tersenyum.",
        "Midground": "Zebra reflektif (kiri), jerapah melihat bintang.",
        "Background": "Langit malam, rasi bintang hewan, pohon akasia siluet.",
        "Floating Elements": "Ikon bintang: 'LION','ZEBRA','GIRAFFE','STARS'.",
        "Central Banner": "Papan kayu “NIGHT SAFARI!”.",
        "Text & Effects": "Fireflies, glow lembut kuning.",
        "Background Style": "Savana gelap biru, kabut tipis.",
        "Style & Lighting": "Neon rim subtle, moonlight cool."
    },
    "Festival Musim Dingin": {
        "Foreground": "Anak-anakan beruang dan rubah bermain salju (tengah-bawah), manusia salju tersenyum.",
        "Midground": "Rusa menarik kereta kecil (kiri), pinguin berseluncur.",
        "Background": "Pohon pinus bersalju, lampu string hangat.",
        "Floating Elements": "Keping salju: 'SNOW','FUN','WINTER','LIGHTS'.",
        "Central Banner": "Neon “WINTER FEST!”.",
        "Text & Effects": "Sparkle biru, nafas uap dingin.",
        "Background Style": "Lapangan salju berkilau.",
        "Style & Lighting": "Watercolor cartoon + glow putih."
    },
    "Pantai Tropis": {
        "Foreground": "Kepiting ceria melambai (tengah-bawah), anak penyu menuju laut.",
        "Midground": "Burung camar menukik (kiri), kelapa jatuh pelan.",
        "Background": "Matahari terbenam oranye, perahu kecil, ombak lembut.",
        "Floating Elements": "Cangkang & papan: 'SUN','SEA','SAND','FUN'.",
        "Central Banner": "Papan kayu “TROPICAL BEACH!”.",
        "Text & Effects": "Confetti daun, semburat pasir.",
        "Background Style": "Palem, payung warna-warni.",
        "Style & Lighting": "Gouache hangat, backlight lembut."
    },
    "Toko Mainan Ajaib": {
        "Foreground": "Beruang boneka hidup melambaikan pita (tengah-bawah), robot timah menari.",
        "Midground": "Kereta mini di rel (kiri), balok huruf melompat.",
        "Background": "Rak mainan tinggi, lampu peri.",
        "Floating Elements": "Tag: 'TOY','ROBOT','TRAIN','BLOCKS'.",
        "Central Banner": "Neon “MAGIC TOY SHOP!”.",
        "Text & Effects": "Glitter pastel, bokeh lampu.",
        "Background Style": "Interior kayu hangat.",
        "Style & Lighting": "Kawaii chibi + plastic toy."
    },
    "Taman Lalu Lintas Mini": {
        "Foreground": "Anak panda menyeberang zebra cross (tengah-bawah), polisi kucing memberi salam.",
        "Midground": "Lampu merah-kuning-hijau (kiri), rambu belok.",
        "Background": "Gedung rendah, taman kota mini.",
        "Floating Elements": "Rambu: 'STOP','GO','SLOW'.",
        "Central Banner": "Papan “LEARN TRAFFIC SIGNS!”.",
        "Text & Effects": "Arrow neon, icon klakson.",
        "Background Style": "Kota pastel aman.",
        "Style & Lighting": "Flat long-shadow, warna cerah."
    },
    "Kota Robot": {
        "Foreground": "Robot kubus lucu menyapa (tengah-bawah), drone kecil membawa paket.",
        "Midground": "Robot anjing (kiri), papan digital berkedip.",
        "Background": "Gedung futuristik, monorail.",
        "Floating Elements": "Badge: 'ROBO','DRONE','CITY'.",
        "Central Banner": "Hologram “ROBOT CITY!”.",
        "Text & Effects": "Glitch lembut, scanline tipis.",
        "Background Style": "Isometric city grid.",
        "Style & Lighting": "Isometric 3D, neon cyan-magenta."
    },
    "Pasar Buah Ceria": {
        "Foreground": "Pedagang apel dan jeruk berkedip (tengah-bawah), pisang menari.",
        "Midground": "Semangka bergulir (kiri), anggur jingkrak.",
        "Background": "Kios warna-warni, lampu gantung.",
        "Floating Elements": "Label: 'APPLE','ORANGE','BANANA','GRAPE','WATERMELON'.",
        "Central Banner": "Plakat “FRUIT MARKET!”.",
        "Text & Effects": "Konfeti warna buah.",
        "Background Style": "Jalan pasar pastel.",
        "Style & Lighting": "Papercraft 3D + rim light."
    },
    "Hari Olahraga Sekolah": {
        "Foreground": "Anak berlari membawa bendera (tengah-bawah), kucing kecil lompat jauh.",
        "Midground": "Tim bola mini latihan (kiri), peluit berbunyi.",
        "Background": "Lapangan sekolah, podium hadiah.",
        "Floating Elements": "Badge: 'RUN','JUMP','TEAM','WIN'.",
        "Central Banner": "Spanduk “SCHOOL SPORTS DAY!”.",
        "Text & Effects": "Konfeti warna tim.",
        "Background Style": "Rumput hijau, langit cerah.",
        "Style & Lighting": "Halftone comic + clean edges."
    },
    "Kelas Musik Ceria": {
        "Foreground": "Kelinci bermain piano mini (tengah-bawah), kucing meniup saksofon.",
        "Midground": "Bebek mengetuk drum (kiri), burung biru bernyanyi.",
        "Background": "Papan not musik, tirai panggung.",
        "Floating Elements": "Ikon nada: 'DO','RE','MI','FA'.",
        "Central Banner": "Neon “LET’S MAKE MUSIC!”.",
        "Text & Effects": "Sparkle emas, bokeh warna.",
        "Background Style": "Panggung kayu hangat.",
        "Style & Lighting": "Ghibli-soft + spotlight."
    }
}

STYLE_PRESETS: List[str] = [
    "3D Pixar (ekspresi besar, outline neon, ultra tajam)",
    "Claymation 3D (tekstur tanah liat, lighting studio)",
    "Low-poly 3D pastel (bentuk sederhana)",
    "Watercolor cartoon (aquarel lembut)",
    "Neon playful (glow rim light, warna cerah)",
    "Ghibli-soft (warna natural, ambient warm)",
    "Plastic toy render (material mengkilap, HDRI studio)",
    "Isometric 3D city (geometri rapi)",
    "Voxel art (blok piksel 3D)",
    "Gouache illustration (kuas tebal)",
    "Halftone comic (tekstur titik komik)",
    "Chalkboard school (tulisan kapur)",
    "Pastel gradient minimal (soft blend)",
    "Holographic chrome (reflective, iridescent)",
    "Retro vaporwave (grid, neon sunset)",
    "Kawaii chibi (proporsi imut)",
    "Line-art minimal (clean strokes)",
    "PBR realistic toy (material realistis)",
    "Papercraft layered 3D (kertas berlapis)",
]

# -------------------------------
# Utilities
# -------------------------------
def compose_prompt(fields: Dict[str, str], toggles: Dict[str, bool]) -> str:
    order = [
        "Foreground", "Midground", "Background", "Floating Elements",
        "Central Banner", "Text & Effects", "Background Style", "Style & Lighting"
    ]
    parts = []
    for key in order:
        val = (fields.get(key) or "").strip()
        if val:
            parts.append(f"{key}: {val}")
    if toggles.get("static_camera"):
        parts.append("Camera: perfectly static tripod; no pan, no zoom.")
    if toggles.get("black_bg"):
        parts.append("Background: pure solid black to isolate subjects; avoid ambient fog.")
    if toggles.get("ultra_sharp"):
        parts.append("Rendering: cinematic composition, ultra-sharp focus, clean edges, no blur.")
    if toggles.get("diag_lighting"):
        parts.append("Lighting: dramatic diagonal from bottom-left to top-right.")
    return " \n".join(parts)

def compose_prompt_localized(fields: Dict[str, str], toggles: Dict[str, bool], lang: str) -> str:
    map_id = {
        "Foreground": "Latar Depan",
        "Midground": "Lapisan Tengah",
        "Background": "Latar Belakang",
        "Floating Elements": "Elemen Mengambang",
        "Central Banner": "Papan Utama",
        "Text & Effects": "Teks & Efek",
        "Background Style": "Gaya Latar",
        "Style & Lighting": "Gaya & Pencahayaan"
    }
    order = [
        "Foreground", "Midground", "Background", "Floating Elements",
        "Central Banner", "Text & Effects", "Background Style", "Style & Lighting"
    ]
    parts = []
    for key in order:
        val = (fields.get(key) or "").strip()
        if not val:
            continue
        label = key if lang == "EN" else map_id[key]
        parts.append(f"{label}: {val}")
    if lang == "EN":
        if toggles.get("static_camera"): parts.append("Camera: perfectly static tripod; no pan, no zoom.")
        if toggles.get("black_bg"): parts.append("Background: pure solid black to isolate subjects; avoid ambient fog.")
        if toggles.get("ultra_sharp"): parts.append("Rendering: cinematic composition, ultra-sharp focus, clean edges, no blur.")
        if toggles.get("diag_lighting"): parts.append("Lighting: dramatic diagonal from bottom-left to top-right.")
    else:
        if toggles.get("static_camera"): parts.append("Kamera: statis sempurna dengan tripod; tanpa pan, tanpa zoom.")
        if toggles.get("black_bg"): parts.append("Latar: hitam pekat untuk fokus karakter; hindari kabut ambient.")
        if toggles.get("ultra_sharp"): parts.append("Rendering: komposisi sinematik, fokus sangat tajam, tepi bersih, tanpa blur.")
        if toggles.get("diag_lighting"): parts.append("Pencahayaan: diagonal dramatis dari kiri-bawah ke kanan-atas.")
    return " \n".join(parts)

def translate_to_english(text_id: str, api_key: str, model: str) -> str:
    try:
        if not api_key:
            return text_id
        instr = ("Translate the following structured prompt to natural English. "
                 "Convert section labels to EXACTLY these: Foreground, Midground, Background, Floating Elements, Central Banner, Text & Effects, Background Style, Style & Lighting. "
                 "Preserve order and details. Do not add commentary.")
        payload = f"{instr}\n{text_id}"
        return _call_gemini(payload, model, api_key)
    except Exception as e:
        st.warning(f"Terjemahan gagal: {e}")
        return text_id

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="Gemini Prompt Builder", page_icon="✨", layout="wide")
load_dotenv()
default_key = os.getenv("GEMINI_API_KEY", "")

st.markdown("""
<style>
main .block-container {max-width: 1050px; padding-top: 0.6rem; padding-bottom: 2rem;}
section[data-testid="stSidebar"] {width: 320px !important;}
.thin-outline { border: 1px solid rgba(0,0,0,0); border-radius: 0px; background: #ffffff; box-shadow: 0 0px 0px rgba(0,0,0,0); }
.dialog-card { border: 0px solid rgba(0,0,0,0.10); border-radius: 12px; background: #ffffff; padding: 12px; }
.stTextArea textarea { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Courier New", monospace; }
.stButton>button { border-radius: 8px; padding: 0.35rem 0.7rem; }
html, body { background: linear-gradient(180deg,#fbfcff 0%, #f6f8ff 100%); }
/* Hapus garis/outline tepat di bawah judul */
h1 + * { border: none !important; margin-top: 0.5rem; }
</style>
""", unsafe_allow_html=True)

st.title("✨ Build XPrompt (ID ➜ EN)")
st.caption("Bangun prompt terstruktur dengan UI Indonesia, otomatis hasilkan versi Inggris.")

with st.sidebar:
    st.header("⚙️ Settings")
    model = st.selectbox(
    "Model Gemini",
    [
        "gemini-1.5-flash-8b",      # ← Rekomendasi: 500 RPD
        "gemini-1.5-flash",         # 50 RPD — sangat terbatas
        "gemini-1.5-pro",           # Butuh Tier 1
    ],
    index=0,  # Default ke flash-8b
    help="gemini-1.5-flash-8b punya kuota lebih besar (500/hari) di tier gratis."
)
    api_key = st.text_input("GEMINI_API_KEY", type="password", value=default_key, help="isi dengan API dari https://aistudio.google.com/apikey")

    st.subheader("🎨 Tema Custom")
    custom_theme = st.text_input("Tema (contoh: Kartun buah 3D)")
    gen_custom_clicked = st.button("Generate dari Tema Custom", use_container_width=True)

    st.divider()
    st.subheader("Template")
    preset_options = ["— None (kosong) —"] + list(PRESETS.keys())
    preset_choice = st.selectbox("Pilih template", preset_options, index=0)
    apply_sidebar_template = st.button("Muat template", use_container_width=True)

    st.divider()
    st.subheader("Pengaturan Global")
    static_camera = st.checkbox("Kunci kamera (statis)", value=True)
    black_bg = st.checkbox("Paksa background hitam", value=False)
    ultra_sharp = st.checkbox("Fokus ultra-tajam", value=True)
    diag_lighting = st.checkbox("Pencahayaan diagonal dramatis (BL → TR)", value=True)

    st.divider()
    n_variations = st.number_input("Variasi (Gemini)", min_value=1, max_value=10, value=3, step=1)
    style_bias = st.selectbox("Bias gaya", STYLE_PRESETS, index=0)

# Handle custom theme generation
KEY_ALIASES = {
    "foreground": "Foreground", "latar depan": "Foreground",
    "midground": "Midground", "lapisan tengah": "Midground",
    "background": "Background", "latar belakang": "Background",
    "floating elements": "Floating Elements", "elemen mengambang": "Floating Elements",
    "central banner": "Central Banner", "papan utama": "Central Banner",
    "text & effects": "Text & Effects", "teks & efek": "Text & Effects",
    "background style": "Background Style", "gaya latar": "Background Style",
    "style & lighting": "Style & Lighting", "gaya & pencahayaan": "Style & Lighting",
}

def parse_sections(text: str) -> Dict[str, str]:
    """
    Parse teks prompt (ID/EN) menjadi bagian-bagian struktur.
    Mendukung format: "Foreground:", "Latar Depan:", "**Central Banner:**", dll.
    """
    # Mapping dari berbagai kemungkinan label ke kunci standar
    KEY_ALIASES = {
        "foreground": "Foreground",
        "latar depan": "Foreground",
        "latar depan:": "Foreground",
        "midground": "Midground",
        "lapisan tengah": "Midground",
        "lapisan tengah:": "Midground",
        "background": "Background",
        "latar belakang": "Background",
        "latar belakang:": "Background",
        "floating elements": "Floating Elements",
        "elemen mengambang": "Floating Elements",
        "elemen mengambang:": "Floating Elements",
        "central banner": "Central Banner",
        "papan utama": "Central Banner",
        "papan utama:": "Central Banner",
        "text & effects": "Text & Effects",
        "teks & efek": "Text & Effects",
        "teks & efek:": "Text & Effects",
        "background style": "Background Style",
        "gaya latar": "Background Style",
        "gaya latar:": "Background Style",
        "style & lighting": "Style & Lighting",
        "gaya & pencahayaan": "Style & Lighting",
        "gaya & pencahayaan:": "Style & Lighting",
    }

    parts = {}
    current_key = None

    for line in text.splitlines():
        line = line.strip()

        # Hilangkan **bold** atau format lain
        line = re.sub(r"^\*\*|\*\*$", "", line).strip()

        if not line:
            continue

        # Cek apakah baris mengandung kunci (dengan : atau tanpa)
        matched = False
        for alias, std_key in KEY_ALIASES.items():
            if line.lower().startswith(alias) and (len(alias) == len(line) or line[len(alias):len(alias)+1] in [":", " "]):
                # Ekstrak nilai setelah alias
                if ":" in line:
                    _, value = line.split(":", 1)
                    value = value.strip()
                else:
                    value = ""
                current_key = std_key
                parts[current_key] = value
                matched = True
                break

        # Jika tidak ada kunci baru, tambahkan ke bagian terakhir
        if not matched and current_key:
            parts[current_key] += " " + line

    # Bersihkan spasi awal/akhir
    for k in parts:
        parts[k] = parts[k].strip()

    return parts

if gen_custom_clicked:
    # Set flag bahwa tombol ditekan
    st.session_state["run_custom"] = True
    st.session_state["custom_theme_input"] = custom_theme
    st.session_state["style_bias_at_run"] = style_bias
    st.rerun()

# Cek apakah perlu generate (hanya sekali)
if st.session_state.get("run_custom", False):
    theme = st.session_state.get("custom_theme_input", "")
    bias = st.session_state.get("style_bias_at_run", STYLE_PRESETS[0])
    if not theme:
        st.error("Masukkan tema terlebih dahulu.")
    elif not (api_key or os.getenv("GEMINI_API_KEY")):
        st.error("Harap isi GEMINI_API_KEY.")
    else:
        try:
            prompt = f"""
Anda adalah seniman konsep sangat berpengalaman dan bersertifikat international. Buat prompt scene rinci berdasarkan tema: {theme}.
Gunakan STRUKTUR PERSIS BERIKUT (hanya gunakan label ini, satu per baris):

Foreground: [deskripsi karakter utama]
Midground: [elemen pendukung]
Background: [lingkungan jauh]
Floating Elements: [elemen mengambang seperti balon, neon]
Central Banner: [judul utama + gaya]
Text & Effects: [teks promosi + efek visual]
Background Style: [gaya latar belakang]
Style & Lighting: [gaya visual dan pencahayaan]

Gunakan bahasa Indonesia. Jangan gunakan bold, jangan tambahkan komentar.
Tambahkan detail visual yang menyenangkan anak-anak atau dewasa sesuai dengan tema yang di inginkan atau di tulis di tema custom.
{bias}
"""
            generated = _call_gemini(prompt, model, api_key or os.getenv("GEMINI_API_KEY"))
            sec = parse_sections(generated)
            for key in FIELD_KEYS:
                if key in sec:
                    st.session_state[key] = sec[key]
            st.success(f"✨ Template berhasil dibuat dari tema: {theme}")
        except Exception as e:
            st.error(str(e))  # Hanya tampilkan pesan yang sudah dibuat rapi
    st.session_state.pop("run_custom", None)
    st.session_state.pop("custom_theme_input", None)
    st.session_state.pop("style_bias_at_run", None)

# Apply template when clicked
if apply_sidebar_template:
    st.session_state["run_apply"] = True
    st.session_state["preset_choice"] = preset_choice
    st.rerun()

if st.session_state.get("run_apply", False):
    choice = st.session_state.get("preset_choice", "")
    if choice == "— None (kosong) —":
        for key in ["Foreground","Midground","Background","Floating Elements","Central Banner","Text & Effects","Background Style","Style & Lighting"]:
            st.session_state[key] = ""
        st.toast("Template kosong dimuat.")
    elif choice in PRESETS:
        for k,v in PRESETS[choice].items():
            st.session_state[k] = v
        st.toast(f"Template dimuat: {choice}")
    # Reset
    st.session_state.pop("run_apply", None)
    st.session_state.pop("preset_choice", None)

# Initialize fields as empty by default (CRITICAL: before any st.text_area)
FIELD_KEYS = [
    "Foreground", "Midground", "Background", "Floating Elements",
    "Central Banner", "Text & Effects", "Background Style", "Style & Lighting"
]
for key in FIELD_KEYS:
    if key not in st.session_state:
        st.session_state[key] = ""

# Builder (compact)
st.subheader("🧱 Builder Detail")
c1, c2 = st.columns(2)
with c1:
    fg = st.text_area("Foreground", value=st.session_state["Foreground"], height=110, help="Karakter/objek utama + pose + posisi.")
    mg = st.text_area("Midground", value=st.session_state["Midground"], height=110, help="Elemen pendukung + gerak.")
    bg = st.text_area("Background", value=st.session_state["Background"], height=110, help="Lingkungan jauh / langit.")
with c2:
    fl = st.text_area("Floating Elements", value=st.session_state["Floating Elements"], height=90, help="Balon, tulisan, ikon, gelembung.")
    cb = st.text_area("Central Banner", value=st.session_state["Central Banner"], height=80, help="Pesan utama + gaya.")
    te = st.text_area("Text & Effects", value=st.session_state["Text & Effects"], height=80, help="Starburst, konfeti, bokeh, glow.")
    bs = st.text_area("Background Style", value=st.session_state["Background Style"], height=80, help="Bokeh, gradien, pola.")
    sl = st.text_area("Style & Lighting", value=st.session_state["Style & Lighting"], height=110, placeholder=style_bias)

fields = {k: st.session_state[k] for k in FIELD_KEYS}
toggles = {
    "static_camera": static_camera,
    "black_bg": black_bg,
    "ultra_sharp": ultra_sharp,
    "diag_lighting": diag_lighting
}

# Compose
base_prompt_en = compose_prompt(fields, toggles)
base_prompt_id = compose_prompt_localized(fields, toggles, lang="ID")

# Buttons
st.divider()
b1, b2, b3 = st.columns(3)
with b1:
    gen_clicked = st.button("🧱 Buat Prompt", use_container_width=True, key="generate")
with b2:
    enh_clicked = st.button("✨ Tingkatkan Prompt", use_container_width=True, key="enhance")
with b3:
    var_clicked = st.button("🔁 Variasi Prompt", use_container_width=True, key="variations")

if gen_clicked:
    st.session_state["base_prompt_id"] = base_prompt_id
    st.session_state["base_prompt_en"] = base_prompt_en
    st.success("Prompt dibuat.")

if enh_clicked:
    if not (api_key or os.getenv("GEMINI_API_KEY")):
        st.error("Isi GEMINI_API_KEY terlebih dahulu.")
    else:
        try:
            enhanced = _call_gemini(
                f"Act as a senior prompt engineer. Polish the following prompt without changing structure:\n\n{base_prompt_en}",
                model,
                api_key or os.getenv("GEMINI_API_KEY"),
            )
            st.session_state["enhanced_prompt_en"] = enhanced
            st.success("✅ Enhanced EN siap.")
        except Exception as e:
            st.error(str(e))

if var_clicked:
    if not (api_key or os.getenv("GEMINI_API_KEY")):
        st.error("Isi GEMINI_API_KEY terlebih dahulu.")
    else:
        try:
            variations = _call_gemini(
                f"Produce {n_variations} alternative prompts following the same structure and kid-safe tone:\n\n{base_prompt_en}",
                model,
                api_key or os.getenv("GEMINI_API_KEY"),
            )
            st.session_state["variations_en"] = variations
            st.success("✅ Variasi EN dibuat.")
        except Exception as e:
            st.error(str(e))

# Auto English translation
auto_en = translate_to_english(base_prompt_id, api_key or os.getenv("GEMINI_API_KEY",""), model)

# Output
st.subheader("📄 Hasil Prompt ")
co1, co2 = st.columns(2)
with co1:
    st.markdown("#### 🇮🇩 Versi Indonesia")
    st.markdown('<div class="dialog-card">', unsafe_allow_html=True)
    text_id = st.session_state.get("base_prompt_id", base_prompt_id)
    st.code(text_id or "(kosong)", language="text")
    one_line_id = re.sub(r'\s+', ' ', text_id or '').strip()
    st.markdown("**One-line (ID):**")
    st.code(one_line_id or "(kosong)", language="text")
    st.markdown('</div>', unsafe_allow_html=True)

with co2:
    st.markdown("#### 🇬🇧 Versi Inggris")
    st.markdown('<div class="dialog-card">', unsafe_allow_html=True)
    text_en = st.session_state.get("base_prompt_en", auto_en)
    st.code(text_en or "(empty)", language="text")
    one_line_en = re.sub(r'\s+', ' ', text_en or '').strip()
    st.markdown("**One-line (EN):**")
    st.code(one_line_en or "(empty)", language="text")
    st.markdown('</div>', unsafe_allow_html=True)

# Enhanced & Variations
st.subheader("🌟 Enhanced Prompt (English)")
st.markdown('<div class="dialog-card">', unsafe_allow_html=True)
st.code(st.session_state.get("enhanced_prompt_en", "(Klik ‘Tingkatkan’ untuk menyempurnakan versi Inggris.)"), language="text")
st.markdown('</div>', unsafe_allow_html=True)

st.subheader("🔀 Variations (English)")
st.markdown('<div class="dialog-card">', unsafe_allow_html=True)
st.code(st.session_state.get("variations_en", "(Klik ‘Variasi’ untuk menghasilkan alternatif.)"), language="text")
st.markdown('</div>', unsafe_allow_html=True)

# Downloads
from io import StringIO
id_stream = StringIO(text_id or "")
en_stream = StringIO(text_en or "")
one_id_stream = StringIO(one_line_id or "")
one_en_stream = StringIO(one_line_en or "")
enh_stream = StringIO(st.session_state.get("enhanced_prompt_en", ""))
var_stream = StringIO(st.session_state.get("variations_en", ""))

d1, d2, d3, d4, d5, d6 = st.columns(6)
with d1: st.download_button("⬇️ ID.txt", data=id_stream.getvalue(), file_name="prompt_id.txt", use_container_width=True)
with d2: st.download_button("⬇️ EN.txt", data=en_stream.getvalue(), file_name="prompt_en.txt", use_container_width=True)
with d3: st.download_button("⬇️ One-line ID.txt", data=one_id_stream.getvalue(), file_name="prompt_id_oneline.txt", use_container_width=True)
with d4: st.download_button("⬇️ One-line EN.txt", data=one_en_stream.getvalue(), file_name="prompt_en_oneline.txt", use_container_width=True)
with d5:
    if enh_stream.getvalue().strip():
        st.download_button("⬇️ Enhanced EN.txt", data=enh_stream.getvalue(), file_name="prompt_enhanced.txt", use_container_width=True)
with d6:
    if var_stream.getvalue().strip():
        st.download_button("⬇️ Variations EN.txt", data=var_stream.getvalue(), file_name="prompts_variations.txt", use_container_width=True)

# Export JSON
export_payload = {
    "fields": fields,
    "toggles": toggles,
    "outputs": {
        "id": text_id or "",
        "en": text_en or "",
        "one_line_id": one_line_id or "",
        "one_line_en": one_line_en or "",
        "enhanced_en": st.session_state.get("enhanced_prompt_en", "") or "",
        "variations_en": st.session_state.get("variations_en", "") or "",
    }
}
st.download_button("⬇️ Export JSON", data=json.dumps(export_payload, ensure_ascii=False, indent=2), file_name="prompt_export.json", use_container_width=True, mime="application/json")

# Compact preset grid
st.divider()
st.subheader("🎨 Pilihan Template")
with st.container(height=400, border=True):
    keys = list(PRESETS.keys())
    for i in range(0, len(keys), 3):
        cols = st.columns(3)
        for j in range(3):
            idx = i + j
            if idx < len(keys):
                with cols[j]:
                    st.markdown('<div class="thin-outline" style="padding:10px;">', unsafe_allow_html=True)
                    st.markdown(f"**{keys[idx]}**")
                    st.caption(PRESETS[keys[idx]]['Foreground'][:110] + "…")
                    if st.button("Pilih", key=f"preset_{idx}", use_container_width=True):
                        for k,v in PRESETS[keys[idx]].items():
                            st.session_state[k] = v
                        st.toast(f"Template dimuat: {keys[idx]}")
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

st.caption("v3.1 • All fixes created @effands ft Ai | create August 2025  |  wa 0856 4990 5055")
st.caption("🙏 Terima Kasih")
st.caption("Dibuat dengan ❤️ untuk kreator Indonesia")
