"""
Dashboard wykresów - uruchom z katalogu głównego projektu:
    streamlit run gui/app.py
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

_APP_ROOT = Path(__file__).resolve().parent.parent
if str(_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(_APP_ROOT))

import streamlit as st

from config.settings import OUTPUT_DIR
from gui.services import (
    ANALYSIS_MODULES,
    fmt_size,
    list_analysis_dirs,
    list_pngs,
    resolve_csv_path,
    run_analysis,
    ROOT as PROJECT_ROOT,
)

st.set_page_config(
    page_title="Wykresy - War Impact Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("War Impact Analysis - wykresy")
st.caption(f"Katalog wyjściowy: `{OUTPUT_DIR}`")

with st.sidebar:
    st.header("Analizy i dane")
    csv_custom = st.text_input(
        "Ścieżka CSV (opcjonalnie)",
        value="",
        help="Puste = domyślny zbiór z projektu (dataset/).",
    )
    csv_path = resolve_csv_path(csv_custom)
    if csv_custom.strip() and csv_path is None:
        st.warning("Podany plik CSV nie istnieje - brak domyślnego zbioru.")
    elif csv_path is None:
        st.warning("Brak pliku datasetu - regeneracja może się nie powieść.")

    st.divider()
    st.subheader("Regeneracja wykresów")
    analysis_dirs = list_analysis_dirs()
    names = [p.name for p in analysis_dirs]
    regen_target = st.selectbox(
        "Wybierz analizę",
        options=["(wszystkie z listy)"] + names,
        index=0,
    )
    if st.button("Wygeneruj ponownie wykresy", type="primary"):
        targets = names if regen_target == "(wszystkie z listy)" else [regen_target]
        progress = st.progress(0.0, text="Start…")
        ok, err = [], []
        for i, name in enumerate(targets):
            progress.progress((i + 1) / max(len(targets), 1), text=f"Analiza: {name}…")
            mod_path = ANALYSIS_MODULES.get(name)
            if not mod_path:
                err.append(f"{name}: brak mapowania modułu (tylko podgląd plików).")
                continue
            try:
                paths = run_analysis(mod_path, csv_path)
                ok.append(f"{name}: {len(paths)} plików.")
            except Exception as e:
                err.append(f"{name}: {e}")
        progress.empty()
        for m in ok:
            st.success(m)
        for m in err:
            st.error(m)
        st.rerun()

analysis_dirs = list_analysis_dirs()
if not analysis_dirs:
    st.info("Brak podkatalogów w `output/`. Uruchom analizy (`python main.py`) lub przycisk regeneracji.")
    st.stop()

tab_browse, tab_manage = st.tabs(["Przegląd", "Zarządzanie plikami"])

with tab_browse:
    c1, c2 = st.columns([1, 2])
    with c1:
        folder_name = st.selectbox(
            "Katalog analizy",
            options=[p.name for p in analysis_dirs],
            index=0,
        )
    folder = OUTPUT_DIR / folder_name
    pngs = list_pngs(folder)

    with c2:
        if not pngs:
            st.warning("Brak plików PNG w tym katalogu.")
            st.stop()
        chart_name = st.selectbox("Wykres", options=[p.name for p in pngs], index=0)

    selected = folder / chart_name
    meta = selected.stat()
    st.markdown(
        f"**Plik:** `{selected.relative_to(PROJECT_ROOT)}` · {fmt_size(meta.st_size)} · "
        f"modyfikacja: {datetime.fromtimestamp(meta.st_mtime).strftime('%Y-%m-%d %H:%M')}"
    )

    st.image(str(selected), use_container_width=True)

    with open(selected, "rb") as f:
        st.download_button(
            "Pobierz PNG",
            data=f.read(),
            file_name=chart_name,
            mime="image/png",
        )

with tab_manage:
    st.markdown("Usuwanie plików jest nieodwracalne.")
    man_folder = st.selectbox(
        "Katalog",
        options=[p.name for p in analysis_dirs],
        key="manage_folder",
    )
    man_path = OUTPUT_DIR / man_folder
    man_pngs = list_pngs(man_path)
    if not man_pngs:
        st.info("Brak PNG.")
    else:
        to_delete = st.selectbox("Plik do usunięcia", options=[p.name for p in man_pngs], key="del_pick")
        confirm = st.checkbox("Potwierdzam usunięcie tego pliku", key="del_confirm")
        if st.button("Usuń plik", type="secondary", disabled=not confirm):
            target = man_path / to_delete
            try:
                target.unlink()
                st.success(f"Usunięto: {target.name}")
                st.rerun()
            except OSError as e:
                st.error(str(e))

    st.divider()
    st.markdown(f"Pełna ścieżka folderu: `{man_path.resolve()}`")
