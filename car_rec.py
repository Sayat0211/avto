import streamlit as st
import json
import os
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import subprocess

DATA_PATH = "car-config-sync/car_data_full.json"
FEEDBACK_PATH = "car-config-sync/user_feedback.json"
ADMIN_PASSWORD = "admin123"

# === Git Auto Push ===
def git_commit_and_push(message="Auto update"):
    try:
        subprocess.run(["git", "add", "."], cwd="car-config-sync", check=True)
        subprocess.run(["git", "commit", "-m", message], cwd="car-config-sync", check=True)
        subprocess.run(["git", "push"], cwd="car-config-sync", check=True)
    except Exception as e:
        print("Git push failed:", e)

# === Загрузка/сохранение данных ===
def load_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {
            "Кузов": {
                'пикап': "Пикап — это мощный автомобиль с открытым грузовым отсеком. Идеален для перевозки строительных материалов, сельскохозяйственной продукции и крупногабаритных грузов. Часто используется фермерами, строителями и любителями активного отдыха. Обладает высоким клиренсом, возможностью буксировки тяжелых прицепов и обычно оснащен полным приводом. Лучший выбор для бездорожья, тяжелых условий эксплуатации и работы в сельской местности.",
                'минивэн': "Минивэн — это просторный автомобиль, предназначенный для перевозки больших семей или групп людей. Оснащен тремя рядами сидений, комфортным салоном и большим багажным отделением. Идеален для дальних поездок, семейных путешествий и регулярных поездок в школу или на мероприятия. Главные плюсы: вместительность, высокий уровень комфорта, множество систем безопасности.",
                'кроссовер': "Кроссовер — это универсальный автомобиль, сочетающий черты внедорожника и легкового авто. Отличается высоким клиренсом, удобной посадкой, вместительным салоном и современными технологиями. Подходит как для городской езды, так и для поездок по неасфальтированным дорогам. Идеален для людей, ведущих активный образ жизни, семей с детьми, любителей путешествий.",
                'седан': "Седан — классический тип автомобиля с отдельным багажником и комфортным салоном. Лучший выбор для городской эксплуатации и дальних поездок по хорошим дорогам. Отличается высоким уровнем шумоизоляции, удобством посадки и устойчивостью на трассе. Плюсы: комфорт, управляемость, презентабельный внешний вид.",
                'хэтчбек': "Хэтчбек — компактный автомобиль с укороченной задней частью и поднимающейся вверх дверью багажника. Идеален для городской жизни: удобен в парковке, экономичен в расходе топлива, маневренен в пробках. Часто выбирается молодыми людьми, студентами, городскими жителями, которым важны мобильность и экономия.",
                'универсал': "Универсал — автомобиль с удлиненным кузовом и увеличенным багажным отделением. Оптимален для семейных поездок, перевозки большого количества багажа, домашних животных или спортивного инвентаря. Сочетает удобство седана с вместимостью кроссовера. Выбор для тех, кто ценит практичность и комфорт в путешествиях.",
                'внедорожник': "Внедорожник — крупный автомобиль с высокой проходимостью, усиленной подвеской и полным приводом. Способен преодолевать тяжелые дорожные условия: грязь, снег, камни, броды. Идеальный выбор для охотников, рыболовов, любителей экстремального отдыха, а также для проживания в сельской местности. Плюсы: мощность, безопасность, проходимость."
            },
            "Трансмиссия": {
                'автомат': "Автоматическая коробка передач обеспечивает плавную езду без необходимости вручную переключать передачи. Идеально подходит для городского движения, пробок и начинающих водителей. Повышает комфорт в повседневной эксплуатации, особенно в мегаполисах.",
                'механика': "Механическая коробка передач дает полный контроль над автомобилем. Любима опытными водителями и автолюбителями за возможность динамичного разгона и экономию топлива. Требует большего внимания и навыков вождения, особенно в пробках."
            },
            "Топливо": {
                'бензин': "Бензиновые двигатели обеспечивают хорошую динамику разгона, универсальность и тишину работы. Идеальны для городской езды и умеренных пробегов. Шире доступны и дешевле в ремонте по сравнению с дизельными и электрическими.",
                'дизель': "Дизельные двигатели отличаются высокой экономичностью на дальних расстояниях и повышенным крутящим моментом. Идеальны для тех, кто много ездит по трассам, перевозит грузы или живет в сельской местности. Дизельные автомобили имеют больший ресурс двигателя, но требуют регулярного обслуживания.",
                'электро': "Электромобили полностью работают на электричестве, не выбрасывая вредных веществ. Отличаются очень низкими эксплуатационными расходами и тишиной хода. Подходят для жителей городов с развитой инфраструктурой зарядных станций.",
                'гибрид': "Гибридные автомобили совмещают бензиновый двигатель и электромотор. Обеспечивают экономичность в городе, низкий уровень выбросов и комфорт. Подходят для тех, кто хочет снизить расход топлива без перехода на чистую электроэнергию."
            }
        }

def save_data(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    git_commit_and_push("Updated car config")

def save_feedback(entry):
    feedback = []
    feedback_dir = os.path.dirname(FEEDBACK_PATH)
    os.makedirs(feedback_dir, exist_ok=True)  # Создаём папку, если её нет

    if os.path.exists(FEEDBACK_PATH):
        with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
            feedback = json.load(f)

    feedback.append(entry)

    with open(FEEDBACK_PATH, "w", encoding="utf-8") as f:
        json.dump(feedback, f, ensure_ascii=False, indent=2)

    git_commit_and_push("New feedback entry")


def delete_feedback(index):
    if os.path.exists(FEEDBACK_PATH):
        with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
            fb_data = json.load(f)
        if 0 <= index < len(fb_data):
            del fb_data[index]
            with open(FEEDBACK_PATH, "w", encoding="utf-8") as f:
                json.dump(fb_data, f, ensure_ascii=False, indent=2)
            git_commit_and_push("Feedback deleted")

category_blocks = load_data()

# === TF-IDF поиск ===
def prepare_tfidf_data(keywords_dict):
    labels = list(keywords_dict.keys())
    texts = [keywords_dict[k] for k in labels]
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(texts)
    return labels, matrix, vectorizer

def find_best_match(query, labels, matrix, vectorizer, top_k=1):
    query_vec = vectorizer.transform([query])
    similarities = cosine_similarity(query_vec, matrix).flatten()
    top_indices = similarities.argsort()[::-1][:top_k]
    return [(labels[i], round(similarities[i], 3)) for i in top_indices]

def semantic_search_grouped(query, top_k=1):
    grouped_results = {}
    for cat_name, data in category_blocks.items():
        labels, matrix, vectorizer = prepare_tfidf_data(data)
        matches = find_best_match(query, labels, matrix, vectorizer, top_k)
        grouped_results[cat_name] = matches
    return grouped_results

def add_to_category(category, class_label, query):
    if class_label in category_blocks[category]:
        category_blocks[category][class_label] += f" {query}."
    else:
        category_blocks[category][class_label] = query
    save_data(category_blocks)

# === Интерфейс ===
st.set_page_config(page_title="АвтоПодбор", layout="centered")
st.title("🚘 Умный подбор автомобиля")

mode = st.sidebar.radio("Выберите режим:", ["Пользователь", "Админ"])
if mode == "Админ":
    password = st.sidebar.text_input("Введите пароль:", type="password")
    is_admin = password == ADMIN_PASSWORD
else:
    is_admin = False

if not is_admin:
    query = st.text_input("Введите описание запроса:")
    if query:
        st.subheader("🔍 Лучшие варианты:")
        results = semantic_search_grouped(query, top_k=1)
        feedback = {"query": query, "timestamp": str(datetime.now()), "results": {}, "rating": None, "comment": ""}

        for cat, matches in results.items():
            best_label = matches[0][0] if matches else "Не найдено"
            st.markdown(f"**{cat}:** {best_label}")
            feedback["results"][cat] = matches  # сохраняем с score для админа

        st.subheader("📝 Оцените результат")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍 Всё подошло"):
                feedback["rating"] = "like"
                save_feedback(feedback)
                st.success("Спасибо за положительную оценку!")
        with col2:
            if st.button("👎 Не подошло"):
                feedback["rating"] = "dislike"
                feedback["comment"] = st.text_input("Комментарий (по желанию)", key="comment")
                save_feedback(feedback)
                st.warning("Ваш отзыв сохранён. Спасибо!")
else:
    st.subheader("📋 Отчёты от пользователей")
    if os.path.exists(FEEDBACK_PATH):
        with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
            fb_data = json.load(f)

        sort_option = st.selectbox("Сортировка отзывов:", ["Все", "Только лайки", "Только дизлайки"])

        filtered_fb = fb_data
        if sort_option == "Только лайки":
            filtered_fb = [x for x in fb_data if x.get("rating") == "like"]
        elif sort_option == "Только дизлайки":
            filtered_fb = [x for x in fb_data if x.get("rating") == "dislike"]

        for i, entry in enumerate(reversed(filtered_fb)):
            feedback_index = len(fb_data) - 1 - i
            short = entry['query'][:40] + '...' if len(entry['query']) > 40 else entry['query']
            with st.expander(f"#{feedback_index + 1} — {short}"):
                st.markdown(f"**Полный запрос:** {entry['query']}")
                st.markdown(f"**Оценка:** {entry['rating']}")
                st.markdown(f"**Дата:** {entry['timestamp']}")
                for cat, matches in entry["results"].items():
                    st.markdown(f"**{cat}:**")
                    for label, score in matches:
                        st.write(f"- {label}: {score}")
                if entry.get("comment"):
                    st.markdown(f"**Комментарий:** {entry['comment']}")

                st.markdown("---")
                st.markdown("**➡️ Добавить этот запрос в категорию:**")
                fb_cat = st.selectbox("Категория:", list(category_blocks.keys()), key=f"fbcat_{i}")
                fb_cls = st.selectbox("Класс:", list(category_blocks[fb_cat].keys()), key=f"fbcls_{i}")

                if st.button("📥 Добавить запрос", key=f"addfb_{i}"):
                    add_to_category(fb_cat, fb_cls, entry['query'])

                    if "corrections" not in entry:
                        entry["corrections"] = []
                    entry["corrections"].append(f"Добавлено в {fb_cat} → {fb_cls}")
                    save_feedback(entry)

                    st.success("Добавлено в описание!")

                if entry.get("corrections"):
                    st.markdown("**🛠 Корректировки:**")
                    for c in entry["corrections"]:
                        st.write("-", c)

                if st.button("🗑 Удалить этот отзыв", key=f"delfb_{i}"):
                    delete_feedback(feedback_index)
                    st.warning("Отзыв удалён. Обновите страницу.")

    else:
        st.info("Пока нет отзывов от пользователей.")

    st.markdown("---")
    st.subheader("✍️ Ручная корректировка описаний")
    category = st.selectbox("Выберите категорию:", list(category_blocks.keys()))
    label = st.selectbox("Выберите класс:", list(category_blocks[category].keys()), key="admin_label")
    new_text = st.text_area("Изменить описание:", category_blocks[category][label], height=200)

    if st.button("💾 Сохранить изменения", key="save_edit"):
        category_blocks[category][label] = new_text
        save_data(category_blocks)
        st.success("Описание обновлено и сохранено!")

