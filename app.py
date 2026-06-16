# =============================================================================
#  APEXDRIVE PRO — PROJE & GÖREV YÖNETİM SİSTEMİ
#  Üniversite Proje Yönetimi Dersi Ödevi
#  Teknolojiler: Python · Streamlit · SQLite · Plotly · Pandas
# =============================================================================
#  Modüller: Dashboard · Görev Panosu (Kanban) · Görev Listesi · Ekip Yönetimi
#            Bütçe Takibi · Risk Kaydı · Gantt / Zaman Çizelgesi · Toplantılar
#            Raporlar
# =============================================================================

import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date

DB_ADI = "proje_yonetim.db"

# ----------------------------------------------------------------- RENK PALETİ
# Açık ve koyu tema renkleri. Aktif tema RENK sözlüğüne kopyalanır.
TEMA_ACIK = {
    "primary":   "#4f46e5",   # indigo
    "primary2":  "#6366f1",
    "accent":    "#06b6d4",   # cyan
    "success":   "#10b981",
    "warning":   "#f59e0b",
    "danger":    "#ef4444",
    "review":    "#8b5cf6",
    "bg":        "#f1f5f9",
    "card":      "#ffffff",
    "ink":       "#0f172a",
    "muted":     "#64748b",
    "border":    "#eef0f6",
    "shadow":    "rgba(15,23,42,.06)",
}
TEMA_KOYU = {
    "primary":   "#818cf8",
    "primary2":  "#a5b4fc",
    "accent":    "#22d3ee",
    "success":   "#34d399",
    "warning":   "#fbbf24",
    "danger":    "#f87171",
    "review":    "#c4b5fd",
    "bg":        "#0f172a",
    "card":      "#1e293b",
    "ink":       "#f1f5f9",
    "muted":     "#94a3b8",
    "border":    "#334155",
    "shadow":    "rgba(0,0,0,.4)",
}
RENK = dict(TEMA_ACIK)

def tema_uygula():
    """Aktif temayı session_state'e göre RENK sözlüğüne yükler."""
    koyu = st.session_state.get("dark_mode", False)
    RENK.clear()
    RENK.update(TEMA_KOYU if koyu else TEMA_ACIK)
DURUM_RENK = {
    "Yapılacak": "#f59e0b", "Devam Ediyor": "#3b82f6",
    "İncelemede": "#8b5cf6", "Tamamlandı": "#10b981",
}
ONCELIK_RENK = {
    "Düşük": "#10b981", "Orta": "#3b82f6", "Yüksek": "#f59e0b", "Kritik": "#ef4444",
}

# =============================================================================
#  VERİTABANI KATMANI
# =============================================================================
def db():
    return sqlite3.connect(DB_ADI, check_same_thread=False)

def sifre_hashle(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def sorgu_df(sql, params=()):
    con = db(); df = pd.read_sql_query(sql, con, params=params); con.close(); return df

def calistir(sql, params=()):
    con = db(); cur = con.cursor(); cur.execute(sql, params)
    con.commit(); con.close()

def kullanici_dogrula(kadi, sifre):
    con = db(); cur = con.cursor()
    cur.execute("""SELECT id,kullanici_adi,ad_soyad,rol,unvan,departman,avatar
                   FROM kullanicilar WHERE kullanici_adi=? AND sifre_hash=?""",
                (kadi, sifre_hashle(sifre)))
    r = cur.fetchone(); con.close()
    if r:
        return {"id": r[0], "kullanici_adi": r[1], "ad_soyad": r[2], "rol": r[3],
                "unvan": r[4], "departman": r[5], "avatar": r[6]}
    return None

def aktif_proje():
    df = sorgu_df("SELECT * FROM projeler ORDER BY id LIMIT 1")
    return df.iloc[0] if not df.empty else None

# =============================================================================
#  GLOBAL STİL (PREMIUM TASARIM)
# =============================================================================
def stil_yukle():
    koyu = st.session_state.get("dark_mode", False)
    app_bg = ("linear-gradient(160deg,#0f172a 0%, #111827 45%, #0b1220 100%)"
              if koyu else
              "linear-gradient(160deg,#eef2ff 0%, #f1f5f9 45%, #f8fafc 100%)")
    kanban_col_bg = "#172033" if koyu else "#f8fafc"
    tab_list_bg = RENK["card"]
    input_bg = "#0f172a" if koyu else "#ffffff"
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {{ font-family:'Inter',sans-serif; }}
    .stApp {{ background:{app_bg}; }}
    #MainMenu, footer, header {{ visibility:hidden; }}
    .block-container {{ padding-top:1.5rem; padding-bottom:3rem; max-width:1300px; }}

    .app-title {{ font-size:1.9rem; font-weight:800; color:{RENK['ink']};
        letter-spacing:-.5px; margin:0; }}
    .app-sub {{ color:{RENK['muted']}; font-size:.95rem; margin:.2rem 0 1.2rem; }}

    .metric-card {{ background:{RENK['card']}; border-radius:18px; padding:1.2rem 1.3rem;
        box-shadow:0 6px 24px {RENK['shadow']}; border:1px solid {RENK['border']};
        transition:.25s; height:100%; }}
    .metric-card:hover {{ transform:translateY(-3px); box-shadow:0 12px 30px {RENK['shadow']}; }}
    .metric-ico {{ width:42px;height:42px;border-radius:12px;display:flex;
        align-items:center;justify-content:center;font-size:1.3rem;margin-bottom:.6rem; }}
    .metric-label {{ color:{RENK['muted']}; font-size:.72rem; font-weight:600;
        text-transform:uppercase; letter-spacing:.6px; }}
    .metric-value {{ font-size:1.7rem; font-weight:800; color:{RENK['ink']};
        line-height:1.1; margin:.15rem 0; }}
    .metric-foot {{ font-size:.78rem; color:{RENK['muted']}; }}

    .kanban-col {{ background:{kanban_col_bg}; border-radius:16px; padding:.7rem;
        border:1px solid {RENK['border']}; min-height:140px; }}
    .kanban-head {{ font-weight:700; font-size:.9rem; padding:.4rem .6rem;
        border-radius:10px; color:#fff; margin-bottom:.6rem; text-align:center; }}
    .kanban-card {{ background:{RENK['card']}; border-radius:12px; padding:.7rem .8rem;
        margin-bottom:.55rem; box-shadow:0 2px 8px {RENK['shadow']};
        border-left:4px solid {RENK['border']}; }}
    .kc-title {{ font-weight:600; font-size:.86rem; color:{RENK['ink']}; }}
    .kc-meta {{ font-size:.72rem; color:{RENK['muted']}; margin-top:.3rem; }}
    .badge {{ display:inline-block; padding:.12rem .5rem; border-radius:20px;
        font-size:.68rem; font-weight:700; color:#fff; }}
    .sec-title {{ font-size:1.15rem; font-weight:700; color:{RENK['ink']};
        margin:.4rem 0 .8rem; }}

    .stTabs [data-baseweb="tab-list"] {{ gap:6px; background:{tab_list_bg}; padding:6px;
        border-radius:14px; box-shadow:0 4px 16px {RENK['shadow']}; }}
    .stTabs [data-baseweb="tab"] {{ border-radius:10px; padding:8px 14px;
        font-weight:600; color:{RENK['muted']}; }}
    .stTabs [aria-selected="true"] {{ background:{RENK['primary']}; color:#fff !important; }}

    div.stButton > button {{ border-radius:10px; font-weight:600; }}
    section[data-testid="stSidebar"] {{ background:linear-gradient(180deg,#1e1b4b,#312e81); }}
    section[data-testid="stSidebar"] * {{ color:#e0e7ff; }}
    .sb-logo {{ font-size:1.25rem; font-weight:800; color:#fff;
        display:flex; align-items:center; gap:.5rem; }}
    .sb-user {{ background:rgba(255,255,255,.08); border-radius:14px; padding:.9rem;
        margin:.4rem 0 1rem; }}
    .pill {{ display:inline-block; background:rgba(255,255,255,.15);
        padding:.15rem .6rem; border-radius:20px; font-size:.72rem; }}

    /* --- Genel metin & başlıklar --- */
    .stApp, .stApp p, .stApp span, .stApp label, .stApp li,
    h1,h2,h3,h4,h5,h6 {{ color:{RENK['ink']}; }}
    .stMarkdown {{ color:{RENK['ink']}; }}

    /* --- Form alanları (dark mode için) --- */
    .stTextInput input, .stTextArea textarea, .stNumberInput input,
    div[data-baseweb="select"] > div {{
        background:{input_bg} !important; color:{RENK['ink']} !important;
        border-color:{RENK['border']} !important; }}
    .stTextInput label, .stTextArea label, .stSelectbox label,
    .stNumberInput label, .stRadio label, .stSlider label,
    .stMultiSelect label, .stDateInput label {{ color:{RENK['ink']} !important; }}

    /* --- Dataframe / tablolar --- */
    [data-testid="stDataFrame"] {{ background:{RENK['card']};
        border-radius:12px; border:1px solid {RENK['border']}; }}

    /* --- Expander --- */
    [data-testid="stExpander"] {{ background:{RENK['card']};
        border:1px solid {RENK['border']}; border-radius:12px; }}
    [data-testid="stExpander"] summary {{ color:{RENK['ink']}; }}

    /* --- Metric (yerleşik) --- */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{ color:{RENK['ink']}; }}
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
#  YARDIMCI BİLEŞENLER
# =============================================================================
def metric_card(ico, bg, label, value, foot=""):
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-ico" style="background:{bg}22;color:{bg};">{ico}</div>
      <div class="metric-label">{label}</div>
      <div class="metric-value">{value}</div>
      <div class="metric-foot">{foot}</div>
    </div>""", unsafe_allow_html=True)

def tl(x):
    return f"₺{x:,.0f}".replace(",", ".")

def grafik_tema(fig, yukseklik=300):
    """Plotly figürünü aktif temaya (açık/koyu) uydurur."""
    koyu = st.session_state.get("dark_mode", False)
    fig.update_layout(
        height=yukseklik,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=RENK["ink"],
        legend_font_color=RENK["ink"],
    )
    fig.update_xaxes(gridcolor=RENK["border"], zerolinecolor=RENK["border"])
    fig.update_yaxes(gridcolor=RENK["border"], zerolinecolor=RENK["border"])
    return fig

# =============================================================================
#  GİRİŞ SAYFASI
# =============================================================================
def giris_sayfasi():
    c1, c2, c3 = st.columns([1, 1.3, 1])
    with c2:
        st.markdown(f"""
        <div style='text-align:center;padding:2.5rem 0 1rem;'>
          <div style='font-size:3.2rem;'>🧠</div>
          <h1 style='margin:.2rem 0;color:{RENK['ink']};font-weight:800;'>MindDeckCard</h1>
          <p style='color:{RENK['muted']};margin-top:0;'>Proje & Görev Yönetim Portalı</p>
        </div>""", unsafe_allow_html=True)
        with st.form("giris"):
            ka = st.text_input("👤 Kullanıcı Adı")
            sf = st.text_input("🔒 Şifre", type="password")
            if st.form_submit_button("Giriş Yap →", use_container_width=True):
                u = kullanici_dogrula(ka, sf)
                if u:
                    st.session_state["kullanici"] = u
                    st.rerun()
                else:
                    st.error("Kullanıcı adı veya şifre hatalı.")
        with st.expander("🔑 Test Kullanıcıları"):
            st.code("Yönetici  → admin       / 1234\n"
                    "Yazılımcı → yazilimci1  / 1234\n"
                    "Tasarımcı → tasarimci1  / 1234\n"
                    "Analist   → analist1    / 1234\n"
                    "Test Müh. → test1       / 1234\n"
                    "Mobil Gel. → donanim1    / 1234")

# =============================================================================
#  SIDEBAR
# =============================================================================
def sidebar(menu):
    u = st.session_state["kullanici"]
    with st.sidebar:
        st.markdown('<div class="sb-logo">🧠 MindDeckCard</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:.72rem;letter-spacing:1px;opacity:.6;">PROJE YÖNETİMİ</div>',
                    unsafe_allow_html=True)
        st.markdown(f"""
        <div class="sb-user">
          <div style="display:flex;align-items:center;gap:.6rem;">
            <div style="width:40px;height:40px;border-radius:50%;background:#6366f1;
                 display:flex;align-items:center;justify-content:center;font-weight:700;">{u['avatar']}</div>
            <div><div style="font-weight:700;">{u['ad_soyad']}</div>
            <div style="font-size:.74rem;opacity:.8;">{u['unvan']}</div></div>
          </div>
          <div style="margin-top:.6rem;"><span class="pill">{u['rol']}</span>
          <span class="pill">{u['departman']}</span></div>
        </div>""", unsafe_allow_html=True)
        secim = st.radio("Menü", menu, label_visibility="collapsed")
        st.divider()
        if st.button("🚪 Çıkış Yap", use_container_width=True):
            del st.session_state["kullanici"]; st.rerun()
    return secim

# =============================================================================
#  MODÜL: DASHBOARD
# =============================================================================
def m_dashboard():
    p = aktif_proje()
    st.markdown(f'<div class="app-title">📊 {p["ad"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="app-sub">{p["aciklama"]}</div>', unsafe_allow_html=True)

    gd = sorgu_df("SELECT * FROM gorevler WHERE proje_id=?", (int(p["id"]),))
    bd = sorgu_df("SELECT * FROM butce_kalemleri WHERE proje_id=?", (int(p["id"]),))
    rd = sorgu_df("SELECT * FROM riskler WHERE proje_id=?", (int(p["id"]),))
    fd = sorgu_df("SELECT * FROM fazlar WHERE proje_id=? ORDER BY sira", (int(p["id"]),))

    toplam = len(gd); biten = (gd["durum"] == "Tamamlandı").sum()
    ilerleme = round((gd["ilerleme"].mean()) if toplam else 0)
    harcanan = bd["harcanan"].sum(); planlanan = bd["planlanan"].sum()
    acik_risk = (rd["durum"] != "Kapandı").sum()

    c = st.columns(4)
    with c[0]: metric_card("📋", RENK["primary"], "Toplam Görev", toplam,
                           f"{biten} tamamlandı · {toplam-biten} açık")
    with c[1]: metric_card("📈", RENK["success"], "İlerleme", f"%{ilerleme}",
                           "Ağırlıklı tamamlanma")
    with c[2]: metric_card("💰", RENK["warning"], "Bütçe", tl(p["butce"]),
                           f"Harcanan: {tl(harcanan)} (%{round(harcanan/planlanan*100)})")
    with c[3]: metric_card("⚠️", RENK["danger"], "Açık Risk", acik_risk,
                           f"Toplam {len(rd)} risk kaydı")

    st.write("")
    # Genel ilerleme barı
    st.markdown(f'<div class="sec-title">Genel Proje İlerlemesi</div>', unsafe_allow_html=True)
    st.progress(ilerleme / 100, text=f"%{ilerleme} tamamlandı")

    st.write("")
    g1, g2 = st.columns(2)
    with g1:
        st.markdown('<div class="sec-title">Görev Durum Dağılımı</div>', unsafe_allow_html=True)
        ds = gd["durum"].value_counts().reindex(
            ["Yapılacak", "Devam Ediyor", "İncelemede", "Tamamlandı"], fill_value=0)
        fig = go.Figure(go.Pie(labels=ds.index, values=ds.values, hole=.6,
            marker=dict(colors=[DURUM_RENK[x] for x in ds.index]),
            textinfo="value"))
        fig.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10),
            showlegend=True, legend=dict(orientation="h", y=-.1),
            annotations=[dict(text=f"{toplam}<br>görev", x=.5, y=.5,
                              font_size=16, showarrow=False)])
        grafik_tema(fig)
        st.plotly_chart(fig, use_container_width=True)
    with g2:
        st.markdown('<div class="sec-title">Faz Bazlı İlerleme</div>', unsafe_allow_html=True)
        faz_ler = []
        for _, f in fd.iterrows():
            fg = gd[gd["faz_id"] == f["id"]]
            faz_ler.append({"Faz": f["ad"].split(". ")[-1],
                            "İlerleme": round(fg["ilerleme"].mean()) if len(fg) else 0})
        ff = pd.DataFrame(faz_ler)
        fig = px.bar(ff, x="İlerleme", y="Faz", orientation="h", text="İlerleme",
                     color="İlerleme", color_continuous_scale=["#fca5a5", "#fcd34d", "#86efac"])
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10),
            coloraxis_showscale=False, xaxis_range=[0, 110], yaxis_title="", xaxis_title="")
        grafik_tema(fig)
        st.plotly_chart(fig, use_container_width=True)

    # Bütçe ve ekip yükü
    g3, g4 = st.columns(2)
    with g3:
        st.markdown('<div class="sec-title">Bütçe: Planlanan vs Harcanan</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_bar(name="Planlanan", x=bd["kategori"], y=bd["planlanan"], marker_color="#c7d2fe")
        fig.add_bar(name="Harcanan", x=bd["kategori"], y=bd["harcanan"], marker_color=RENK["primary"])
        fig.update_layout(height=300, barmode="group", margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation="h", y=1.1))
        grafik_tema(fig)
        st.plotly_chart(fig, use_container_width=True)
    with g4:
        st.markdown('<div class="sec-title">Yaklaşan Kilometre Taşları</div>', unsafe_allow_html=True)
        kt = sorgu_df("SELECT * FROM kilometre_taslari WHERE proje_id=? ORDER BY tarih",
                      (int(p["id"]),))
        ikon = {"Tamamlandı": "✅", "Beklemede": "🕒", "Gecikti": "🔴"}
        for _, k in kt.iterrows():
            st.markdown(f"""
            <div style="background:#fff;border-radius:12px;padding:.7rem .9rem;
                 margin-bottom:.5rem;box-shadow:0 2px 8px rgba(15,23,42,.05);
                 display:flex;justify-content:space-between;align-items:center;">
              <div><b>{ikon.get(k['durum'],'')} {k['ad']}</b>
                <div style="font-size:.74rem;color:{RENK['muted']};">{k['aciklama']}</div></div>
              <div style="font-size:.78rem;color:{RENK['muted']};text-align:right;">{k['tarih']}</div>
            </div>""", unsafe_allow_html=True)

# =============================================================================
#  MODÜL: KANBAN GÖREV PANOSU
# =============================================================================
def m_kanban():
    p = aktif_proje()
    st.markdown('<div class="app-title">🗂️ Görev Panosu (Kanban)</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-sub">Görevleri durumlarına göre sürükleyip yönetin.</div>',
                unsafe_allow_html=True)

    df = sorgu_df("""SELECT g.*, k.ad_soyad, k.avatar FROM gorevler g
        LEFT JOIN kullanicilar k ON g.atanan_id=k.id WHERE g.proje_id=?""", (int(p["id"]),))

    kolonlar = ["Yapılacak", "Devam Ediyor", "İncelemede", "Tamamlandı"]
    cols = st.columns(4)
    for i, durum in enumerate(kolonlar):
        with cols[i]:
            grup = df[df["durum"] == durum]
            st.markdown(f'<div class="kanban-head" style="background:{DURUM_RENK[durum]};">'
                        f'{durum} · {len(grup)}</div>', unsafe_allow_html=True)
            for _, g in grup.iterrows():
                oc = ONCELIK_RENK[g["oncelik"]]
                st.markdown(f"""
                <div class="kanban-card" style="border-left-color:{oc};">
                  <div class="kc-title">{g['baslik']}</div>
                  <div class="kc-meta">👤 {g['ad_soyad'] or '—'}</div>
                  <div style="margin-top:.4rem;">
                    <span class="badge" style="background:{oc};">{g['oncelik']}</span>
                    <span style="font-size:.7rem;color:{RENK['muted']};">%{g['ilerleme']}</span>
                  </div>
                </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="sec-title">🔄 Görev Durumu Güncelle</div>', unsafe_allow_html=True)
    if not df.empty:
        with st.form("kanban_guncelle"):
            c1, c2, c3 = st.columns([2, 1.5, 1])
            sec = c1.selectbox("Görev", df.apply(
                lambda r: f"#{r['id']} — {r['baslik']}", axis=1))
            yeni = c2.selectbox("Yeni Durum", kolonlar)
            ilerleme = c3.slider("İlerleme %", 0, 100, 50, 5)
            if st.form_submit_button("💾 Güncelle", use_container_width=True):
                gid = int(sec.split(" — ")[0].replace("#", ""))
                calistir("UPDATE gorevler SET durum=?, ilerleme=? WHERE id=?",
                         (yeni, ilerleme, gid))
                st.success("Görev güncellendi."); st.rerun()

# =============================================================================
#  MODÜL: GÖREV LİSTESİ
# =============================================================================
def m_gorev_listesi():
    p = aktif_proje()
    st.markdown('<div class="app-title">📋 Görev Listesi</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-sub">Tüm görevleri filtreleyin, yönetin ve yeni görev ekleyin.</div>',
                unsafe_allow_html=True)

    df = sorgu_df("""SELECT g.id "ID", g.baslik "Başlık", g.durum "Durum",
        g.oncelik "Öncelik", k.ad_soyad "Atanan", g.tahmini_saat "Tahmini (s)",
        g.harcanan_saat "Harcanan (s)", g.ilerleme "İlerleme %", g.bitis "Bitiş"
        FROM gorevler g LEFT JOIN kullanicilar k ON g.atanan_id=k.id
        WHERE g.proje_id=? ORDER BY g.id""", (int(p["id"]),))

    f1, f2 = st.columns(2)
    fd = f1.multiselect("Durum filtrele", list(DURUM_RENK.keys()))
    fo = f2.multiselect("Öncelik filtrele", list(ONCELIK_RENK.keys()))
    view = df.copy()
    if fd: view = view[view["Durum"].isin(fd)]
    if fo: view = view[view["Öncelik"].isin(fo)]

    st.dataframe(view, use_container_width=True, hide_index=True,
        column_config={"İlerleme %": st.column_config.ProgressColumn(
            "İlerleme", min_value=0, max_value=100, format="%d%%")})

    if st.session_state["kullanici"]["rol"] == "Yönetici":
        st.divider()
        with st.expander("➕ Yeni Görev Ekle"):
            calisanlar = sorgu_df("SELECT id,ad_soyad FROM kullanicilar WHERE rol='Çalışan'")
            fazlar = sorgu_df("SELECT id,ad FROM fazlar WHERE proje_id=? ORDER BY sira",
                              (int(p["id"]),))
            with st.form("yeni_gorev"):
                c1, c2 = st.columns(2)
                baslik = c1.text_input("Başlık")
                faz = c2.selectbox("Faz", fazlar["ad"])
                acik = st.text_area("Açıklama", height=80)
                c3, c4, c5 = st.columns(3)
                atan = c3.selectbox("Atanan", calisanlar["ad_soyad"])
                onc = c4.selectbox("Öncelik", list(ONCELIK_RENK.keys()), index=1)
                tah = c5.number_input("Tahmini saat", 0, 500, 20)
                if st.form_submit_button("✅ Görevi Ekle", use_container_width=True):
                    if baslik.strip():
                        aid = int(calisanlar[calisanlar["ad_soyad"] == atan]["id"].iloc[0])
                        fid = int(fazlar[fazlar["ad"] == faz]["id"].iloc[0])
                        calistir("""INSERT INTO gorevler
                            (proje_id,faz_id,baslik,aciklama,durum,oncelik,atanan_id,
                             tahmini_saat,harcanan_saat,ilerleme,olusturma_tar)
                            VALUES (?,?,?,?,'Yapılacak',?,?,?,0,0,?)""",
                            (int(p["id"]), fid, baslik.strip(), acik.strip(), onc, aid,
                             tah, datetime.now().strftime("%Y-%m-%d %H:%M")))
                        st.success(f"'{baslik}' eklendi."); st.rerun()
                    else:
                        st.error("Başlık boş olamaz.")

# =============================================================================
#  MODÜL: EKİP YÖNETİMİ
# =============================================================================
def m_ekip():
    p = aktif_proje()
    st.markdown('<div class="app-title">👥 Ekip Yönetimi</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-sub">Ekip üyeleri, iş yükü ve performans dağılımı.</div>',
                unsafe_allow_html=True)

    ek = sorgu_df("SELECT * FROM kullanicilar")
    gd = sorgu_df("SELECT * FROM gorevler WHERE proje_id=?", (int(p["id"]),))

    # Üye kartları
    cols = st.columns(3)
    for i, (_, u) in enumerate(ek.iterrows()):
        g = gd[gd["atanan_id"] == u["id"]]
        biten = (g["durum"] == "Tamamlandı").sum()
        with cols[i % 3]:
            st.markdown(f"""
            <div class="metric-card" style="margin-bottom:1rem;">
              <div style="display:flex;align-items:center;gap:.7rem;">
                <div style="width:46px;height:46px;border-radius:50%;
                     background:{RENK['primary']};color:#fff;display:flex;
                     align-items:center;justify-content:center;font-weight:700;">{u['avatar']}</div>
                <div><div style="font-weight:700;">{u['ad_soyad']}</div>
                <div style="font-size:.76rem;color:{RENK['muted']};">{u['unvan']}</div></div>
              </div>
              <div style="margin-top:.7rem;font-size:.78rem;color:{RENK['muted']};">
                🏢 {u['departman']} · 📧 {u['eposta']}<br>
                📋 {len(g)} görev · ✅ {biten} tamamlandı · ⏱️ {g['harcanan_saat'].sum():.0f} saat
              </div>
            </div>""", unsafe_allow_html=True)

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sec-title">Üye Başına İş Yükü</div>', unsafe_allow_html=True)
        yuk = []
        for _, u in ek.iterrows():
            g = gd[gd["atanan_id"] == u["id"]]
            if len(g):
                yuk.append({"Üye": u["ad_soyad"], "Görev": len(g),
                            "Saat": g["harcanan_saat"].sum()})
        yf = pd.DataFrame(yuk)
        fig = px.bar(yf, x="Üye", y="Görev", text="Görev", color="Görev",
                     color_continuous_scale=["#c7d2fe", RENK["primary"]])
        fig.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10),
            coloraxis_showscale=False, xaxis_title="")
        grafik_tema(fig)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown('<div class="sec-title">Departman Dağılımı</div>', unsafe_allow_html=True)
        dd = ek["departman"].value_counts()
        fig = go.Figure(go.Pie(labels=dd.index, values=dd.values, hole=.5))
        fig.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation="h", y=-.1))
        grafik_tema(fig)
        st.plotly_chart(fig, use_container_width=True)

# =============================================================================
#  MODÜL: BÜTÇE TAKİBİ
# =============================================================================
def m_butce():
    p = aktif_proje()
    st.markdown('<div class="app-title">💰 Bütçe Takibi</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-sub">Kategori bazlı bütçe planlama ve gider takibi.</div>',
                unsafe_allow_html=True)

    bd = sorgu_df("SELECT * FROM butce_kalemleri WHERE proje_id=?", (int(p["id"]),))
    plan = bd["planlanan"].sum(); harc = bd["harcanan"].sum()
    kalan = float(p["butce"]) - harc

    c = st.columns(4)
    with c[0]: metric_card("🏦", RENK["primary"], "Toplam Bütçe", tl(p["butce"]), "Onaylı bütçe")
    with c[1]: metric_card("📤", RENK["danger"], "Harcanan", tl(harc),
                           f"%{round(harc/plan*100)} kullanıldı")
    with c[2]: metric_card("💵", RENK["success"], "Kalan", tl(kalan), "Mevcut bakiye")
    with c[3]: metric_card("📊", RENK["warning"], "Planlanan", tl(plan), "Kategoriler toplamı")

    st.write("")
    c1, c2 = st.columns([1.3, 1])
    with c1:
        st.markdown('<div class="sec-title">Kategori Bazlı Bütçe</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_bar(name="Planlanan", y=bd["kategori"], x=bd["planlanan"],
                    orientation="h", marker_color="#c7d2fe")
        fig.add_bar(name="Harcanan", y=bd["kategori"], x=bd["harcanan"],
                    orientation="h", marker_color=RENK["primary"])
        fig.update_layout(height=340, barmode="group", margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation="h", y=1.12))
        grafik_tema(fig)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown('<div class="sec-title">Harcama Dağılımı</div>', unsafe_allow_html=True)
        fig = go.Figure(go.Pie(labels=bd["kategori"], values=bd["harcanan"], hole=.5))
        fig.update_layout(height=340, margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation="h", y=-.2))
        grafik_tema(fig)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="sec-title">Bütçe Kalemleri</div>', unsafe_allow_html=True)
    tab = bd[["kategori", "aciklama", "planlanan", "harcanan"]].copy()
    tab["kalan"] = tab["planlanan"] - tab["harcanan"]
    tab["kullanım %"] = (tab["harcanan"] / tab["planlanan"] * 100).round()
    tab.columns = ["Kategori", "Açıklama", "Planlanan", "Harcanan", "Kalan", "Kullanım %"]
    st.dataframe(tab, use_container_width=True, hide_index=True,
        column_config={
            "Planlanan": st.column_config.NumberColumn(format="₺%d"),
            "Harcanan": st.column_config.NumberColumn(format="₺%d"),
            "Kalan": st.column_config.NumberColumn(format="₺%d"),
            "Kullanım %": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d%%")})

    if st.session_state["kullanici"]["rol"] == "Yönetici":
        with st.expander("➕ Yeni Bütçe Kalemi / Gider Ekle"):
            with st.form("yeni_butce"):
                c1, c2 = st.columns(2)
                kat = c1.text_input("Kategori")
                ac = c2.text_input("Açıklama")
                c3, c4 = st.columns(2)
                pl = c3.number_input("Planlanan (₺)", 0, 1000000, 10000, 1000)
                ha = c4.number_input("Harcanan (₺)", 0, 1000000, 0, 1000)
                if st.form_submit_button("✅ Ekle", use_container_width=True):
                    if kat.strip():
                        calistir("""INSERT INTO butce_kalemleri
                            (proje_id,kategori,aciklama,planlanan,harcanan,tarih)
                            VALUES (?,?,?,?,?,?)""",
                            (int(p["id"]), kat, ac, pl, ha,
                             datetime.now().strftime("%Y-%m-%d")))
                        st.success("Bütçe kalemi eklendi."); st.rerun()

# =============================================================================
#  MODÜL: RİSK KAYDI
# =============================================================================
def m_risk():
    p = aktif_proje()
    st.markdown('<div class="app-title">⚠️ Risk Kaydı</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-sub">Risk matrisi, skorlama ve azaltma planları.</div>',
                unsafe_allow_html=True)

    rd = sorgu_df("""SELECT r.*, k.ad_soyad FROM riskler r
        LEFT JOIN kullanicilar k ON r.sahibi_id=k.id WHERE r.proje_id=?""", (int(p["id"]),))
    rd["skor"] = rd["olasilik"] * rd["etki"]

    c = st.columns(4)
    with c[0]: metric_card("📑", RENK["primary"], "Toplam Risk", len(rd), "Tüm kayıtlar")
    with c[1]: metric_card("🔴", RENK["danger"], "Yüksek Risk",
                           (rd["skor"] >= 12).sum(), "Skor ≥ 12")
    with c[2]: metric_card("👁️", RENK["warning"], "İzlenen",
                           (rd["durum"] == "İzleniyor").sum(), "Aktif takip")
    with c[3]: metric_card("✅", RENK["success"], "Kapanan",
                           (rd["durum"] == "Kapandı").sum(), "Çözüldü")

    st.write("")
    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.markdown('<div class="sec-title">Risk Matrisi (Olasılık × Etki)</div>',
                    unsafe_allow_html=True)
        renk_skor = rd["skor"].apply(lambda s: RENK["danger"] if s >= 12
                    else RENK["warning"] if s >= 6 else RENK["success"])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=rd["olasilik"], y=rd["etki"], mode="markers+text",
            text=rd["id"], textposition="middle center", textfont=dict(color="#fff", size=10),
            marker=dict(size=rd["skor"] * 3 + 14, color=renk_skor,
                        line=dict(width=1, color="#fff")),
            hovertext=rd["baslik"], hoverinfo="text"))
        fig.update_layout(height=340, margin=dict(t=10, b=10, l=10, r=10),
            xaxis=dict(title="Olasılık", range=[0.5, 5.5], dtick=1),
            yaxis=dict(title="Etki", range=[0.5, 5.5], dtick=1),
            plot_bgcolor="#f8fafc")
        grafik_tema(fig)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown('<div class="sec-title">Risk Listesi</div>', unsafe_allow_html=True)
        for _, r in rd.sort_values("skor", ascending=False).iterrows():
            sk = r["skor"]
            renk = RENK["danger"] if sk >= 12 else RENK["warning"] if sk >= 6 else RENK["success"]
            st.markdown(f"""
            <div style="background:#fff;border-radius:12px;padding:.7rem .9rem;
                 margin-bottom:.5rem;box-shadow:0 2px 8px rgba(15,23,42,.05);
                 border-left:4px solid {renk};">
              <div style="display:flex;justify-content:space-between;">
                <b>#{r['id']} {r['baslik']}</b>
                <span class="badge" style="background:{renk};">Skor {sk}</span></div>
              <div style="font-size:.76rem;color:{RENK['muted']};margin-top:.3rem;">{r['aciklama']}</div>
              <div style="font-size:.74rem;color:{RENK['muted']};margin-top:.3rem;">
                🛡️ {r['onlem']} · 👤 {r['ad_soyad']} · <b>{r['durum']}</b></div>
            </div>""", unsafe_allow_html=True)

    if st.session_state["kullanici"]["rol"] == "Yönetici":
        with st.expander("➕ Yeni Risk Ekle"):
            sahipler = sorgu_df("SELECT id,ad_soyad FROM kullanicilar")
            with st.form("yeni_risk"):
                ba = st.text_input("Risk Başlığı")
                ac = st.text_area("Açıklama", height=70)
                c1, c2, c3 = st.columns(3)
                ol = c1.slider("Olasılık", 1, 5, 3)
                et = c2.slider("Etki", 1, 5, 3)
                sa = c3.selectbox("Sahibi", sahipler["ad_soyad"])
                on = st.text_input("Azaltma / Önlem")
                if st.form_submit_button("✅ Ekle", use_container_width=True):
                    if ba.strip():
                        sid = int(sahipler[sahipler["ad_soyad"] == sa]["id"].iloc[0])
                        calistir("""INSERT INTO riskler
                            (proje_id,baslik,aciklama,olasilik,etki,durum,sahibi_id,onlem)
                            VALUES (?,?,?,?,?,'Açık',?,?)""",
                            (int(p["id"]), ba, ac, ol, et, sid, on))
                        st.success("Risk eklendi."); st.rerun()

# =============================================================================
#  MODÜL: GANTT / ZAMAN ÇİZELGESİ
# =============================================================================
def m_gantt():
    p = aktif_proje()
    st.markdown('<div class="app-title">📅 Gantt Şeması & Zaman Çizelgesi</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="app-sub">Görev ve fazların zaman içindeki dağılımı.</div>',
                unsafe_allow_html=True)

    gd = sorgu_df("""SELECT g.*, k.ad_soyad, f.ad faz_ad FROM gorevler g
        LEFT JOIN kullanicilar k ON g.atanan_id=k.id
        LEFT JOIN fazlar f ON g.faz_id=f.id
        WHERE g.proje_id=? AND g.baslangic IS NOT NULL ORDER BY g.baslangic""",
        (int(p["id"]),))

    gd2 = gd.dropna(subset=["baslangic", "bitis"]).copy()
    fig = px.timeline(gd2, x_start="baslangic", x_end="bitis", y="baslik",
                      color="durum", color_discrete_map=DURUM_RENK,
                      hover_data=["ad_soyad", "oncelik", "ilerleme"])
    fig.update_yaxes(autorange="reversed", title="")
    fig.add_vline(x=datetime.now(), line_dash="dash", line_color=RENK["danger"],
                  annotation_text="Bugün")
    fig.update_layout(height=560, margin=dict(t=20, b=10, l=10, r=10),
                      legend=dict(orientation="h", y=1.05))
    grafik_tema(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="sec-title">Proje Fazları</div>', unsafe_allow_html=True)
    fd = sorgu_df("SELECT * FROM fazlar WHERE proje_id=? ORDER BY sira", (int(p["id"]),))
    cols = st.columns(len(fd))
    for i, (_, f) in enumerate(fd.iterrows()):
        fg = gd[gd["faz_id"] == f["id"]]
        ilrl = round(fg["ilerleme"].mean()) if len(fg) else 0
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
              <div style="font-weight:700;font-size:.85rem;">{f['ad']}</div>
              <div style="font-size:.72rem;color:{RENK['muted']};margin:.3rem 0;">
                {f['baslangic']} → {f['bitis']}</div>
              <div style="font-size:1.4rem;font-weight:800;color:{RENK['primary']};">%{ilrl}</div>
              <div style="font-size:.72rem;color:{RENK['muted']};">{len(fg)} görev</div>
            </div>""", unsafe_allow_html=True)

# =============================================================================
#  MODÜL: TOPLANTILAR
# =============================================================================
def m_toplanti():
    p = aktif_proje()
    st.markdown('<div class="app-title">🗓️ Toplantılar & Notlar</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-sub">Toplantı kayıtları, kararlar ve katılımcılar.</div>',
                unsafe_allow_html=True)

    td = sorgu_df("SELECT * FROM toplantilar WHERE proje_id=? ORDER BY tarih DESC",
                  (int(p["id"]),))
    for _, t in td.iterrows():
        st.markdown(f"""
        <div style="background:#fff;border-radius:14px;padding:1rem 1.1rem;
             margin-bottom:.7rem;box-shadow:0 3px 12px rgba(15,23,42,.05);
             border-left:4px solid {RENK['accent']};">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <b style="font-size:1rem;">📌 {t['baslik']}</b>
            <span style="font-size:.78rem;color:{RENK['muted']};">📅 {t['tarih']}</span></div>
          <div style="font-size:.86rem;color:#334155;margin:.5rem 0;">{t['notlar']}</div>
          <div style="font-size:.74rem;color:{RENK['muted']};">👥 {t['katilimcilar']}</div>
        </div>""", unsafe_allow_html=True)

    if st.session_state["kullanici"]["rol"] == "Yönetici":
        with st.expander("➕ Yeni Toplantı Kaydı"):
            with st.form("yeni_toplanti"):
                ba = st.text_input("Başlık")
                c1, c2 = st.columns(2)
                tar = c1.date_input("Tarih", date.today())
                kat = c2.text_input("Katılımcılar")
                no = st.text_area("Notlar / Kararlar", height=90)
                if st.form_submit_button("✅ Kaydet", use_container_width=True):
                    if ba.strip():
                        calistir("""INSERT INTO toplantilar
                            (proje_id,baslik,tarih,notlar,katilimcilar) VALUES (?,?,?,?,?)""",
                            (int(p["id"]), ba, tar.strftime("%Y-%m-%d"), no, kat))
                        st.success("Toplantı kaydedildi."); st.rerun()

# =============================================================================
#  MODÜL: RAPORLAR
# =============================================================================
def m_rapor():
    p = aktif_proje()
    st.markdown('<div class="app-title">📑 Raporlar & Dışa Aktarım</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-sub">Proje özet raporu ve CSV dışa aktarımı.</div>',
                unsafe_allow_html=True)

    gd = sorgu_df("SELECT * FROM gorevler WHERE proje_id=?", (int(p["id"]),))
    bd = sorgu_df("SELECT * FROM butce_kalemleri WHERE proje_id=?", (int(p["id"]),))
    rd = sorgu_df("SELECT * FROM riskler WHERE proje_id=?", (int(p["id"]),))

    biten = (gd["durum"] == "Tamamlandı").sum()
    ilerleme = round(gd["ilerleme"].mean())
    harc = bd["harcanan"].sum(); plan = bd["planlanan"].sum()

    st.markdown(f"""
    <div class="metric-card" style="padding:1.6rem;">
      <h3 style="margin-top:0;color:{RENK['ink']};">📋 Proje Özet Raporu</h3>
      <p style="color:{RENK['muted']};">{p['ad']}</p>
      <table style="width:100%;font-size:.9rem;border-collapse:collapse;">
        <tr style="border-bottom:1px solid #eee;"><td style="padding:.5rem 0;">Durum</td>
            <td style="text-align:right;"><b>{p['durum']}</b></td></tr>
        <tr style="border-bottom:1px solid #eee;"><td style="padding:.5rem 0;">Süre</td>
            <td style="text-align:right;"><b>{p['baslangic']} → {p['bitis']}</b></td></tr>
        <tr style="border-bottom:1px solid #eee;"><td style="padding:.5rem 0;">Genel İlerleme</td>
            <td style="text-align:right;"><b>%{ilerleme}</b></td></tr>
        <tr style="border-bottom:1px solid #eee;"><td style="padding:.5rem 0;">Görevler</td>
            <td style="text-align:right;"><b>{biten}/{len(gd)} tamamlandı</b></td></tr>
        <tr style="border-bottom:1px solid #eee;"><td style="padding:.5rem 0;">Bütçe Kullanımı</td>
            <td style="text-align:right;"><b>{tl(harc)} / {tl(plan)} (%{round(harc/plan*100)})</b></td></tr>
        <tr><td style="padding:.5rem 0;">Açık Riskler</td>
            <td style="text-align:right;"><b>{(rd['durum']!='Kapandı').sum()}</b></td></tr>
      </table>
    </div>""", unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="sec-title">📥 Veri Dışa Aktarım (CSV)</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.download_button("⬇️ Görevler", gd.to_csv(index=False).encode("utf-8-sig"),
                       "gorevler.csv", "text/csv", use_container_width=True)
    c2.download_button("⬇️ Bütçe", bd.to_csv(index=False).encode("utf-8-sig"),
                       "butce.csv", "text/csv", use_container_width=True)
    c3.download_button("⬇️ Riskler", rd.to_csv(index=False).encode("utf-8-sig"),
                       "riskler.csv", "text/csv", use_container_width=True)

# =============================================================================
#  ANA AKIŞ
# =============================================================================
def ustbar():
    """Sağ üstte canlı veri etiketi ve dark mode geçiş butonu."""
    koyu = st.session_state.get("dark_mode", False)
    bos, sag1, sag2 = st.columns([6, 1.1, 1.1])
    with sag1:
        st.markdown(
            f"<div style='text-align:right;padding-top:.4rem;font-size:.8rem;"
            f"color:{RENK['muted']};'>🟢 Canlı Veri</div>",
            unsafe_allow_html=True)
    with sag2:
        etiket = "☀️ Açık Tema" if koyu else "🌙 Koyu Tema"
        if st.button(etiket, use_container_width=True, key="tema_btn"):
            st.session_state["dark_mode"] = not koyu
            st.rerun()

def main():
    st.set_page_config(page_title="MindDeckCard — Proje Yönetimi",
                       page_icon="🧠", layout="wide", initial_sidebar_state="expanded")
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = False
    tema_uygula()      # RENK sözlüğünü aktif temaya göre ayarla
    stil_yukle()       # CSS'i aktif temaya göre uygula
    veritabani_kontrol()

    if "kullanici" not in st.session_state:
        giris_sayfasi(); return

    menu = ["📊 Dashboard", "🗂️ Görev Panosu", "📋 Görev Listesi", "👥 Ekip Yönetimi",
            "💰 Bütçe Takibi", "⚠️ Risk Kaydı", "📅 Gantt Şeması",
            "🗓️ Toplantılar", "📑 Raporlar"]
    secim = sidebar(menu)
    ustbar()           # sağ üst kontrol çubuğu (dark mode butonu)

    yonlendirme = {
        "📊 Dashboard": m_dashboard, "🗂️ Görev Panosu": m_kanban,
        "📋 Görev Listesi": m_gorev_listesi, "👥 Ekip Yönetimi": m_ekip,
        "💰 Bütçe Takibi": m_butce, "⚠️ Risk Kaydı": m_risk,
        "📅 Gantt Şeması": m_gantt, "🗓️ Toplantılar": m_toplanti,
        "📑 Raporlar": m_rapor,
    }
    yonlendirme[secim]()

def veritabani_kontrol():
    """DB yoksa ilk çalıştırmada build_db.py'yi çalıştırarak otomatik oluşturur."""
    import os, runpy
    if not os.path.exists(DB_ADI) and os.path.exists("build_db.py"):
        runpy.run_path("build_db.py")

if __name__ == "__main__":
    main()
