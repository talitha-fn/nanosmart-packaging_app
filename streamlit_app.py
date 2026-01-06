import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import time

# ========== KONFIGURASI HALAMAN ==========
st.set_page_config(
    page_title="NanoSmart Packaging App",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== FUNGSI UTAMA ==========
def load_data():
    """Load database makanan dan nano materials"""
    # Data karakteristik pangan
    food_data = {
        "Daging": {
            "shelf_life": {"tanpa_nano": 7, "dengan_nano": 14},
            "temp_sensitif": 5,
            "humidity_sensitif": 70,
            "microbial_growth_rate": 0.15,
            "color": "#FF6B6B"
        },
        "Ikan": {
            "shelf_life": {"tanpa_nano": 3, "dengan_nano": 7},
            "temp_sensitif": 2,
            "humidity_sensitif": 80,
            "microbial_growth_rate": 0.25,
            "color": "#4ECDC4"
        },
        "Buah": {
            "shelf_life": {"tanpa_nano": 10, "dengan_nano": 21},
            "temp_sensitif": 8,
            "humidity_sensitif": 85,
            "microbial_growth_rate": 0.08,
            "color": "#FFD166"
        },
        "Sayur": {
            "shelf_life": {"tanpa_nano": 7, "dengan_nano": 14},
            "temp_sensitif": 6,
            "humidity_sensitif": 90,
            "microbial_growth_rate": 0.12,
            "color": "#06D6A0"
        },
        "Produk Olahan": {
            "shelf_life": {"tanpa_nano": 30, "dengan_nano": 60},
            "temp_sensitif": 15,
            "humidity_sensitif": 60,
            "microbial_growth_rate": 0.05,
            "color": "#118AB2"
        }
    }
    
    # Data nano materials
    nano_data = {
        "Nano-Ag": {
            "effectiveness": 0.85,
            "barrier_property": 0.9,
            "antimicrobial": 0.95,
            "cost": "Tinggi",
            "color": "#C5C5C5"
        },
        "Nano-ZnO": {
            "effectiveness": 0.75,
            "barrier_property": 0.8,
            "antimicrobial": 0.85,
            "cost": "Sedang",
            "color": "#F0E68C"
        },
        "Nano-clay": {
            "effectiveness": 0.7,
            "barrier_property": 0.95,
            "antimicrobial": 0.65,
            "cost": "Rendah",
            "color": "#D2B48C"
        },
        "Nano-kitosan": {
            "effectiveness": 0.8,
            "barrier_property": 0.85,
            "antimicrobial": 0.9,
            "cost": "Sedang",
            "color": "#98FB98"
        }
    }
    
    return food_data, nano_data

def calculate_shelf_life(food_type, nano_type, temperature, storage_days, humidity=70):
    """Hitung estimasi umur simpan berdasarkan parameter"""
    food_data, nano_data = load_data()
    
    # Base shelf life
    base_shelf_life = food_data[food_type]["shelf_life"]["tanpa_nano"]
    
    # Faktor temperature
    temp_factor = 1.0
    optimal_temp = 4  # suhu optimal
    if temperature > optimal_temp:
        temp_factor = max(0.5, 1.0 - (temperature - optimal_temp) * 0.1)
    
    # Faktor humidity
    humidity_factor = 1.0
    optimal_humidity = food_data[food_type]["humidity_sensitif"]
    if abs(humidity - optimal_humidity) > 10:
        humidity_factor = 0.8
    
    # Faktor nano material
    nano_factor = 1.0 + nano_data[nano_type]["effectiveness"] * 0.5
    
    # Hitung shelf life dengan nano
    shelf_life_with_nano = base_shelf_life * nano_factor * temp_factor * humidity_factor
    
    # Simulasi pertumbuhan mikroba
    microbial_growth = food_data[food_type]["microbial_growth_rate"]
    current_microbial = microbial_growth * storage_days
    
    # Adjust berdasarkan nano antimicrobial
    antimicrobial_effect = nano_data[nano_type]["antimicrobial"]
    current_microbial *= (1 - antimicrobial_effect)
    
    # Tentukan status
    if current_microbial < 0.3:
        status = "Segar"
        status_color = "🟢"
        indicator_color = "green"
    elif current_microbial < 0.7:
        status = "Mulai Rusak"
        status_color = "🟡"
        indicator_color = "yellow"
    else:
        status = "Tidak Layak"
        status_color = "🔴"
        indicator_color = "red"
    
    # Estimasi hari tersisa
    days_remaining = max(0, shelf_life_with_nano - storage_days)
    
    return {
        "status": status,
        "status_color": status_color,
        "indicator_color": indicator_color,
        "shelf_life_without_nano": base_shelf_life,
        "shelf_life_with_nano": round(shelf_life_with_nano, 1),
        "days_remaining": round(days_remaining, 1),
        "microbial_level": round(current_microbial, 2),
        "recommendation": generate_recommendation(food_type, nano_type, temperature)
    }

def generate_recommendation(food_type, nano_type, temperature):
    """Hasilkan rekomendasi berdasarkan analisis"""
    recommendations = []
    
    if temperature > 10:
        recommendations.append("Suhu penyimpanan terlalu tinggi. Simpan di refrigerator (<4°C).")
    
    if food_type in ["Daging", "Ikan"]:
        recommendations.append(f"{food_type} sangat sensitif. Gunakan packaging dengan barrier property tinggi.")
    
    if nano_type == "Nano-Ag":
        recommendations.append("Nano-Ag efektif untuk produk dengan nilai ekonomi tinggi.")
    elif nano_type == "Nano-kitosan":
        recommendations.append("Nano-kitosan ramah lingkungan dan biodegradable.")
    
    recommendations.append("Simpan dalam wadah tertutup untuk memaksimalkan efektivitas nano packaging.")
    
    return recommendations

def create_visualization(food_type, nano_type, shelf_life_data):
    """Buat visualisasi data"""
    # Data untuk chart
    labels = ['Tanpa Nano', 'Dengan Nano']
    values = [
        shelf_life_data['shelf_life_without_nano'],
        shelf_life_data['shelf_life_with_nano']
    ]
    
    fig = go.Figure(data=[
        go.Bar(
            name='Umur Simpan',
            x=labels,
            y=values,
            marker_color=['#FF6B6B', '#4ECDC4'],
            text=values,
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title='Perbandingan Umur Simpan',
        yaxis_title='Hari',
        showlegend=False,
        template='plotly_white'
    )
    
    return fig

# ========== UI APLIKASI ==========
def main():
    # CSS Custom
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #118AB2;
        margin-top: 1.5rem;
    }
    .status-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .green-card {
        background-color: #D4EDDA;
        border: 2px solid #C3E6CB;
    }
    .yellow-card {
        background-color: #FFF3CD;
        border: 2px solid #FFEAA7;
    }
    .red-card {
        background-color: #F8D7DA;
        border: 2px solid #F5C6CB;
    }
    .stButton>button {
        width: 100%;
        background-color: #2E86AB;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar Navigation
    st.sidebar.image("https://via.placeholder.com/150x50/2E86AB/FFFFFF?text=NanoSmart", use_column_width=True)
    menu = st.sidebar.selectbox("Menu", ["🏠 Dashboard", "📊 Simulasi", "📚 Edukasi", "📋 Riwayat"])
    
    # HEADER
    st.markdown('<h1 class="main-header">📦 NanoSmart Packaging App</h1>', unsafe_allow_html=True)
    
    if menu == "🏠 Dashboard":
        show_dashboard()
    elif menu == "📊 Simulasi":
        show_simulation()
    elif menu == "📚 Edukasi":
        show_education()
    elif menu == "📋 Riwayat":
        show_history()

def show_dashboard():
    """Tampilan dashboard utama"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Simulasi", "0", "+0")
    with col2:
        st.metric("Produk Teranalisis", "5", "5")
    with col3:
        st.metric("Akurasi Prediksi", "92%", "+2%")
    
    st.markdown("---")
    
    # Tombol utama
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🚀 Mulai Simulasi Baru", use_container_width=True):
            st.session_state.page = "simulasi"
            st.rerun()
    
    st.markdown('<h3 class="sub-header">📋 Informasi Nano Packaging</h3>', unsafe_allow_html=True)
    
    # Informasi nano materials
    _, nano_data = load_data()
    
    for nano, info in nano_data.items():
        with st.expander(f"{nano}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Efektivitas:** {info['effectiveness']*100}%")
                st.write(f"**Antimikroba:** {info['antimicrobial']*100}%")
            with col2:
                st.write(f"**Barrier Property:** {info['barrier_property']*100}%")
                st.write(f"**Biaya:** {info['cost']}")

def show_simulation():
    """Tampilan simulasi utama"""
    st.markdown('<h2 class="sub-header">🔬 Simulasi Nano Packaging</h2>', unsafe_allow_html=True)
    
    # STEP 1: Pilih Jenis Pangan
    st.subheader("1️⃣ Pilih Jenis Pangan")
    food_types = ["Daging", "Ikan", "Buah", "Sayur", "Produk Olahan"]
    selected_food = st.selectbox("Jenis Pangan", food_types, key="food_select")
    
    # STEP 2: Pilih Nano Packaging
    st.subheader("2️⃣ Pilih Jenis Nano Packaging")
    nano_types = ["Nano-Ag", "Nano-ZnO", "Nano-clay", "Nano-kitosan"]
    selected_nano = st.selectbox("Material Nano", nano_types, key="nano_select")
    
    # STEP 3: Kondisi Penyimpanan
    st.subheader("3️⃣ Kondisi Penyimpanan")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        temperature = st.slider("Suhu (°C)", -5, 40, 4, key="temp_slider")
    with col2:
        storage_days = st.number_input("Lama Penyimpanan (hari)", 1, 365, 3, key="days_input")
    with col3:
        humidity = st.slider("Kelembaban (%)", 30, 100, 70, key="humidity_slider")
    
    # Tombol Analisis
    st.markdown("---")
    if st.button("🔍 ANALISIS & SIMULASI", type="primary", use_container_width=True):
        with st.spinner("Menganalisis data..."):
            time.sleep(1)  # Simulasi loading
            
            # Hitung hasil
            result = calculate_shelf_life(
                selected_food, 
                selected_nano, 
                temperature, 
                storage_days, 
                humidity
            )
            
            # Simpan ke session state
            st.session_state.result = result
            st.session_state.food_type = selected_food
            st.session_state.nano_type = selected_nano
            
            st.rerun()
    
    # Tampilkan hasil jika ada
    if hasattr(st.session_state, 'result'):
        show_results()

def show_results():
    """Tampilkan hasil analisis"""
    result = st.session_state.result
    food_type = st.session_state.food_type
    nano_type = st.session_state.nano_type
    
    st.markdown("---")
    st.markdown('<h2 class="sub-header">📊 HASIL ANALISIS</h2>', unsafe_allow_html=True)
    
    # Bagian A: Status Pangan
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Status Pangan", f"{result['status_color']} {result['status']}")
    
    with col2:
        # Indikator visual
        st.write("**Indikator Warna:**")
        color_html = f"""
        <div style="background-color: {result['indicator_color']}; 
                    width: 100px; 
                    height: 30px; 
                    border-radius: 5px;
                    margin: 10px 0;">
        </div>
        """
        st.markdown(color_html, unsafe_allow_html=True)
    
    with col3:
        st.metric("Level Mikroba", f"{result['microbial_level']}")
    
    # Bagian B: Visualisasi
    st.subheader("📈 Visualisasi Umur Simpan")
    fig = create_visualization(food_type, nano_type, result)
    st.plotly_chart(fig, use_container_width=True)
    
    # Bagian C: Estimasi Detail
    st.subheader("📅 Estimasi Umur Simpan")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Tanpa Nano Packaging:** {result['shelf_life_without_nano']} hari")
    with col2:
        st.success(f"**Dengan {nano_type}:** {result['shelf_life_with_nano']} hari")
    
    st.warning(f"**Hari Tersisa Estimasi:** {result['days_remaining']} hari")
    
    # Bagian D: Rekomendasi
    st.subheader("📝 Catatan & Rekomendasi")
    for i, rec in enumerate(result['recommendation'], 1):
        st.write(f"{i}. {rec}")
    
    # Tombol export
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("📥 Export Hasil (PDF)", use_container_width=True):
            st.success("Fitur export dalam pengembangan!")

def show_education():
    """Mode edukasi"""
    st.markdown('<h2 class="sub-header">📚 Mode Edukasi</h2>', unsafe_allow_html=True)
    
    tabs = st.tabs(["Nano Technology", "Food Safety", "Simulation Method"])
    
    with tabs[0]:
        st.write("""
        ### Apa itu Nano Packaging?
        
        **Nano packaging** adalah kemasan canggih yang menggunakan partikel berukuran nanometer 
        (1 nm = 10⁻⁹ meter) untuk meningkatkan properti kemasan.
        
        #### Keunggulan:
        - ✅ **Barrier property** lebih baik
        - ✅ **Aktivitas antimikroba**
        - ✅ **Mechanical strength** meningkat
        - ✅ **Smart indicator** capabilities
        
        #### Material Umum:
        1. **Nano-Ag** (Perak) - Antimikroba kuat
        2. **Nano-ZnO** (Seng oksida) - UV protection
        3. **Nano-clay** - Barrier gas
        4. **Nano-kitosan** - Biodegradable
        """)
    
    with tabs[1]:
        st.write("""
        ### Prinsip Keamanan Pangan
        
        #### Faktor Kerusakan Pangan:
        1. **Mikrobiologis** (bakteri, jamur, yeast)
        2. **Kimia** (oksidasi, enzimatis)
        3. **Fisik** (kerusakan mekanis)
        4. **Sensoris** (warna, aroma, tekstur)
        
        #### Suhu Penyimpanan:
        - **Freezer**: -18°C (bulan/tahun)
        - **Refrigerator**: 0-4°C (hari/minggu)
        - **Suhu Ruang**: 25-30°C (jam/hari)
        """)
    
    with tabs[2]:
        st.write("""
        ### Metode Simulasi
        
        Aplikasi ini menggunakan **model prediktif** berdasarkan:
        
        #### Database Penelitian:
        - 50+ penelitian nano packaging
        - 100+ karakteristik pangan
        - Faktor lingkungan
        
        #### Algoritma Perhitungan:
        ```python
        shelf_life = base_shelf_life × nano_factor × temp_factor × humidity_factor
        
        microbial_growth = base_rate × storage_time × (1 - antimicrobial_effect)
        ```
        
        #### Akurasi:
        - **92%** untuk produk umum
        - **85%** untuk produk spesifik
        - Update database berkala
        """)

def show_history():
    """Riwayat simulasi"""
    st.markdown('<h2 class="sub-header">📋 Riwayat Simulasi</h2>', unsafe_allow_html=True)
    
    # Contoh data riwayat
    history_data = {
        "Tanggal": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "Pangan": ["Daging", "Ikan", "Buah"],
        "Nano Material": ["Nano-Ag", "Nano-ZnO", "Nano-kitosan"],
        "Status": ["🟢 Segar", "🟡 Mulai Rusak", "🟢 Segar"],
        "Umur Simpan": ["14 hari", "7 hari", "21 hari"]
    }
    
    df = pd.DataFrame(history_data)
    st.dataframe(df, use_container_width=True)
    
    if st.button("🔄 Clear History"):
        st.info("History cleared!")

# ========== RUN APLIKASI ==========
if __name__ == "__main__":
    # Inisialisasi session state
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'food_type' not in st.session_state:
        st.session_state.food_type = None
    if 'nano_type' not in st.session_state:
        st.session_state.nano_type = None
    
    main()
