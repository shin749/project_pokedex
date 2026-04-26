import streamlit as st
import requests

# perintah run code di terminal
# streamlit run pokedex.py

# 1. Setting Halaman
st.set_page_config(page_title="Pokedex by Irza a.k.a. Kenshin", layout="wide")

# CSS Custom
st.markdown("""
    <style>
    .stApp { background-color: #A3B3FF; }
    .pokemon-card {
        background-color: #f2f2f2;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        color: #313131;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .pokemon-id { color: #919191; font-weight: bold; font-size: 14px; }
    .pokemon-name { color: #313131; font-size: 20px; font-weight: bold; margin-bottom: 10px; }
    .info-box {
        background-color: #30a7d7;
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .header-pokedex {
        background-color: #FFF085;
        padding: 20px;
        text-align: center;
        border-bottom: 4px solid #ff4b4b;
    }
    [data-testid="stImage"] img {
        transition: transform 0.3s;
    }
    [data-testid="stImage"] img:hover {
        transform: scale(1.1);
    }
    /* Efek biar tombol evolusi kelihatan interaktif */
.stButton button {
    border-radius: 10px;
    transition: all 0.3s ease;
}

.stButton button:hover {
    background-color: #30a7d7 !important;
    color: white !important;
    transform: translateY(-3px);
}
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI AMBIL DATA ---
@st.cache_data
def get_pokemon(name_or_id):
    url = f"https://pokeapi.co/api/v2/pokemon/{name_or_id}"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else None

@st.cache_data
def get_all_pokemon_names():
    url = "https://pokeapi.co/api/v2/pokemon?limit=1300"
    res = requests.get(url)
    return [p['name'] for p in res.json()['results']] if res.status_code == 200 else []

@st.cache_data
def get_weaknesses(pokemon_types):
    weaknesses = set()
    for t_info in pokemon_types:
        res = requests.get(t_info['type']['url'])
        if res.status_code == 200:
            for w in res.json()['damage_relations']['double_damage_from']:
                weaknesses.add(w['name'].capitalize())
    return list(weaknesses)

@st.cache_data
def get_pokemon_description(pokemon_id):
    url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}/"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        # Mencari deskripsi dalam bahasa Inggris
        for entry in data['flavor_text_entries']:
            if entry['language']['name'] == 'en':
                # Bersihkan teks dari karakter aneh seperti baris baru (\n atau \f)
                return entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
    return "Deskripsi tidak tersedia."

@st.cache_data
def get_evolution_chain(pokemon_id):
    species_url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}/"
    res = requests.get(species_url)
    evo_data = []
    
    if res.status_code == 200:
        evo_url = res.json()['evolution_chain']['url']
        res_evo = requests.get(evo_url)
        
        if res_evo.status_code == 200:
            current = res_evo.json()['chain']
            while current:
                name = current['species']['name']
                # Ambil detail untuk dapat gambar
                detail = get_pokemon(name)
                if detail:
                    img = detail['sprites']['other']['official-artwork']['front_default']
                    evo_data.append({"name": name.capitalize(), "image": img})
                
                if current['evolves_to']:
                    current = current['evolves_to'][0]
                else:
                    current = None
    return evo_data

# --- FUNGSI LAYER DETAIL (POP-UP) ---
@st.dialog("Pokemon Detail", width="large")
def show_details(data):
    st.markdown(f"<h1 style='text-align: center; color: white;'>{data['name'].upper()} #{data['id']:03}</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image(data['sprites']['other']['official-artwork']['front_default'], use_container_width=True)
    with col2:
        types_list = [t['type']['name'].capitalize() for t in data['types']]
        weak_list = get_weaknesses(data['types'])
        description = get_pokemon_description(data['id'])
        
        st.markdown(f"""
            <div class="info-box">
                <div style="margin-bottom: 15px;">
                    <h2 style="color: white; margin-bottom: 5px;">{data['name'].capitalize()}</h2>
                    <p style="font-style: italic; font-size: 15px; line-height: 1.4; opacity: 0.9;">
                        "{description}"
                    </p>
                </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="info-box">
                <div style="margin-top: 10px "><b>Tinggi:</b> {data['height']/10} m</div>
                <div style="margin-top: 10px"><b>Berat:</b> {data['weight']/10} kg</div>
                <div style="margin-top: 10px;"><b>Ability:</b> {', '.join([a['ability']['name'].capitalize() for a in data['abilities']])}</div>
                <div style="margin-top: 10px;"><b>Tipe:</b> {', '.join(types_list)}</div>
                <div style="margin-top: 10px;"><b>Kelemahan:</b> {', '.join(weak_list)}</div>
            </div>
        """, unsafe_allow_html=True)
        st.subheader("Stats")
        for s in data['stats']:
            st.write(f"{s['stat']['name'].replace('-', ' ').upper()}: {s['base_stat']}")
            st.progress(min(s['base_stat']/150, 1.0))
            
            # --- BAGIAN EVOLUSI DENGAN GAMBAR ---
        st.write("---")
        st.subheader("Evolution Chain")
        evolutions = get_evolution_chain(data['id'])
        
        if evolutions:
            cols_evo = st.columns(len(evolutions))
            for i, evo in enumerate(evolutions):
                with cols_evo[i]:
                    st.image(evo['image'], use_container_width=True)
                    
                    # Ganti logika tombolnya jadi begini:
                    if st.button(f"{evo['name']}", key=f"evo_btn_{evo['name']}_{i}", use_container_width=True):
                        # 1. Ambil data baru
                        new_data = get_pokemon(evo['name'].lower())
                        if new_data:
                            # 2. Simpan ke session state biar bisa dipanggil ulang
                            st.session_state.selected_pokemon = new_data
                            # 3. Paksa aplikasi buat refresh
                            st.rerun()
        else:
            st.write("Tidak memiliki evolusi.")

# --- HEADER ---
st.markdown('<div class="header-pokedex"><h1>🔴 Pokédex</h1></div>', unsafe_allow_html=True)
st.write("##")

# --- INPUT SEARCH ---
all_names = get_all_pokemon_names()
search = st.text_input("", placeholder="Cari nama atau nomor Pokemon...").lower()

# --- FIX BUG: RESET PAGE JIKA SEARCH BERUBAH ---
# Kita simpan search sebelumnya di session_state untuk pengecekan
if 'last_search' not in st.session_state:
    st.session_state.last_search = ""

# Jika teks search sekarang beda sama yang tadi, balikkan ke halaman 1 (0)
if search != st.session_state.last_search:
    st.session_state.current_page = 0
    st.session_state.last_search = search

# --- LOGIKA TAMPILAN DINAMIS ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0

limit = 9
offset = st.session_state.current_page * limit

# Tentukan list data (all_results)
if search:
    if search.isdigit():
        all_results = [search]
    else:
        all_results = [name for name in all_names if search in name]
    title_text = f"Hasil Pencarian: '{search}'"
else:
    all_results = list(range(1, 1026))
    title_text = f"Halaman {st.session_state.current_page + 1}"

# Potong list untuk ditampilkan
display_items = all_results[offset : offset + limit]

st.write(f"### {title_text}")

if not display_items:
    st.warning("Tidak ada data di halaman ini.")
else:
    # Bungkus bagian ini dengan spinner
    with st.spinner('Sedang memanggil Pokemon...'):
        cols = st.columns(3)
        for idx, item in enumerate(display_items):
            p = get_pokemon(item)
            if p:
                with cols[idx % 3]:
                    st.markdown(f"""
                        <div class="pokemon-card">
                            <img src="{p['sprites']['other']['official-artwork']['front_default']}" width="180">
                            <p class="pokemon-id">#{p['id']:03}</p>
                            <div class="pokemon-name">{p['name'].capitalize()}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Lihat Detail {p['name'].capitalize()}", key=f"btn_{p['id']}_{idx}", use_container_width=True):
                        show_details(p)
# --- NAVIGASI HALAMAN ---
st.write("---")
c1, c2, c3 = st.columns([1, 2, 1])

with c1:
    if st.session_state.current_page > 0:
        if st.button("⬅️ Sebelumnya", use_container_width=True):
            st.session_state.current_page -= 1
            st.rerun()

with c3:
    if offset + limit < len(all_results):
        if st.button("Selanjutnya ➡️", use_container_width=True):
            st.session_state.current_page += 1
            st.rerun()
            
# Cek apakah ada pokemon yang baru saja diklik dari evolusi
if 'selected_pokemon' in st.session_state and st.session_state.selected_pokemon:
    pokemon_to_show = st.session_state.selected_pokemon
    # Hapus dari memori biar nggak muncul terus tiap refresh
    st.session_state.selected_pokemon = None 
    # Tampilkan detailnya
    show_details(pokemon_to_show)