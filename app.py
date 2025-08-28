import streamlit as st
from itertools import combinations, permutations
from unidecode import unidecode

st.set_page_config(page_title="Generator Hashtagów", page_icon="✅")

st.title("#Generator")
st.caption("Podaj jakieś dane")

col1, col2 = st.columns(2)
with col1:
    item_type = st.text_input("Typ (np. koszulka, spodnie)", placeholder="koszulka")
    color = st.text_input("Kolor", placeholder="biala")
with col2:
    brand = st.text_input("Marka", placeholder="zara")
    size = st.text_input("Rozmiar (opcjonalnie)", placeholder="M")

st.subheader("Ustawienia")
c1, c2, c3, c4 = st.columns(4)
with c1:
    max_len = st.number_input("Maks. długość taga", min_value=0, max_value=60, value=30, step=1)
with c2:
    include_size = st.checkbox("Uwzględniaj rozmiar", value=True)
with c3:
    unique_only = st.checkbox("Usuwaj duplikaty", value=True)
with c4:
    prefer_order = st.checkbox("Preferuj kolejność: kolor → typ → cecha/marka", value=True)

extra_feature = st.text_input("Dodatkowa cecha/wzór (opcjonalnie)", placeholder="kropki / oversize / basic")

def normalize_token(s: str) -> str:
    s = (s or "").strip().lower()
    s = unidecode(s)  # żółta -> zolta
    return "".join(s.split())

def generate_hashtags(color, item_type, brand, size, extra, max_len=30, include_size=True, unique_only=True, prefer_order=True):

    color = normalize_token(color)
    item_type = normalize_token(item_type)
    brand = normalize_token(brand)
    size = normalize_token(size) if include_size else ""
    extra = normalize_token(extra)

    # Lista słów (pomijamy puste)
    words = [w for w in [color, item_type, brand, size, extra] if w]

    if not words:
        return []

    hashtags = []
    seen = set()

    for r in range(1, len(words) + 1):
        for combo in combinations(words, r):
            for perm in permutations(combo):
                if prefer_order and len(perm) > 1:
                    # prosty trik: ułóż perm według priorytetu (ale zachowaj też oryginalne permutacje)
                    priority = {color: 1, item_type: 2, extra: 3, brand: 4, size: 5}
                    perm_sorted = tuple(sorted(perm, key=lambda x: priority.get(x, 99)))
                    variants = {perm, perm_sorted}
                else:
                    variants = {perm}

                for variant in variants:
                    tag = "#" + "".join(variant)
                    if len(tag) > max_len:
                        continue
                    if unique_only:
                        if tag in seen:
                            continue
                        seen.add(tag)
                    hashtags.append(tag)

    def score(t):
        pts = 0
        if item_type and item_type in t: pts += 2
        if color and color in t: pts += 1
        if brand and brand in t: pts += 1
        if extra and extra in t: pts += 1
        pts -= max(0, len(t) - 20) * 0.05  # lekkie minusy za długość
        return -pts  # sort ascending → odwracamy znaki

    hashtags = sorted(dict.fromkeys(hashtags), key=score)  # dedupe + sort wg score
    return hashtags

if st.button("Generuj hashtagi"):
    tags = generate_hashtags(
        color=color,
        item_type=item_type,
        brand=brand,
        size=size,
        extra=extra_feature,
        max_len=int(max_len),
        include_size=include_size,
        unique_only=unique_only,
        prefer_order=prefer_order
    )

    st.subheader(f"Wynik ({len(tags)})")
    if tags:
        # lista
        for t in tags:
            st.write(t)

        # w jednej linii do szybkiego kopiowania
        joined = " ".join(tags)
        st.text_area("Kopiuj do ogłoszenia", value=joined, height=120)
        st.download_button("Pobierz jako TXT", data=joined, file_name="hashtags.txt")
    else:
        st.info("???")

