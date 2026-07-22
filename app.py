"""
FiloTech Edu - Plataforma de Aprendizaje Gamificada
---------------------------------------------------
Este archivo contiene la aplicación completa. En un entorno de producción tradicional,
estas clases estarían divididas en: database.py, auth.py, gamification.py, models.py, app.py.
Para garantizar la ejecución en este entorno interactivo, se presenta de forma consolidada,
modularizada mediante Programación Orientada a Objetos.

Tecnologías: Streamlit (Python), SQLite3, HTML5/CSS3 (Glassmorphism)
Tema: Filosofía y Ética en la Ingeniería de Sistemas (UNDC)
"""

import streamlit as st
import sqlite3
import hashlib
import time
from datetime import date, timedelta
import pandas as pd
import json

# ==========================================
# 1. CONFIGURACIÓN Y ESTILOS (UX/UI)
# ==========================================
st.set_page_config(page_title="FiloTech Edu | Aprende Jugando", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

def inject_custom_css():
    """Inyecta CSS para lograr un diseño moderno (Apple, Notion, Duolingo, Glassmorphism)"""
    st.markdown("""
        
    """, unsafe_allow_html=True)


# ==========================================
# 2. BASE DE DATOS Y MODELOS
# ==========================================
class DatabaseManager:
    def __init__(self, db_name="filotech.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        password TEXT,
                        xp INTEGER DEFAULT 0,
                        level INTEGER DEFAULT 1,
                        streak INTEGER DEFAULT 0,
                        last_login DATE,
                        badges TEXT DEFAULT '[]'
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS progress (
                        username TEXT,
                        module_id TEXT,
                        score INTEGER,
                        completed BOOLEAN,
                        PRIMARY KEY (username, module_id)
                    )''')
        self.conn.commit()

db = DatabaseManager()

# ==========================================
# 3. AUTENTICACIÓN Y ESTADO DE SESIÓN
# ==========================================
class AuthManager:
    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def login(username, password):
        c = db.conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, AuthManager.hash_password(password)))
        user = c.fetchone()
        if user:
            # Update streak
            today = date.today().isoformat()
            last_login = user[5]
            streak = user[4]
            if last_login:
                last_date = date.fromisoformat(last_login)
                if last_date == date.today() - timedelta(days=1):
                    streak += 1
                elif last_date < date.today() - timedelta(days=1):
                    streak = 1 # Reset streak
            else:
                streak = 1

            c.execute("UPDATE users SET last_login=?, streak=? WHERE username=?", (today, streak, username))
            db.conn.commit()
            return True
        return False

    @staticmethod
    def register(username, password):
        c = db.conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password, last_login, streak) VALUES (?, ?, ?, ?)",
                      (username, AuthManager.hash_password(password), date.today().isoformat(), 1))
            db.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def init_session():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"
    if 'current_module' not in st.session_state:
        st.session_state.current_module = None

# ==========================================
# 4. MOTOR DE GAMIFICACIÓN
# ==========================================
class GamificationEngine:
    @staticmethod
    def get_user_stats(username):
        c = db.conn.cursor()
        c.execute("SELECT xp, level, streak, badges FROM users WHERE username=?", (username,))
        return c.fetchone()

    @staticmethod
    def add_xp(username, amount):
        stats = GamificationEngine.get_user_stats(username)
        if stats:
            new_xp = stats[0] + amount
            new_level = (new_xp // 100) + 1  # 100 XP por nivel
            c = db.conn.cursor()
            c.execute("UPDATE users SET xp=?, level=? WHERE username=?", (new_xp, new_level, username))
            db.conn.commit()

            if new_level > stats[1]:
                st.balloons()
                st.success(f"🎉 ¡Súper! Has alcanzado el Nivel {new_level}")

    @staticmethod
    def unlock_badge(username, badge_name):
        stats = GamificationEngine.get_user_stats(username)
        if stats:
            badges = json.loads(stats[3])
            if badge_name not in badges:
                badges.append(badge_name)
                c = db.conn.cursor()
                c.execute("UPDATE users SET badges=? WHERE username=?", (json.dumps(badges), username))
                db.conn.commit()
                st.toast(f"🏅 ¡Insignia desbloqueada: {badge_name}!")

# ==========================================
# 5. CONTENIDO DEL CURSO (UNDC)
# ==========================================
COURSE_DATA = {
    "MOD-01": {
        "title": "Las 4 Disciplinas Fundamentales",
        "description": "Epistemología, Lógica, Ética y Ontología en la Ingeniería.",
        "content": """
        ### La Filosofía no es una abstracción aislada
        Como sostuvo Aristóteles, es una estructura integral. Cada disciplina responde a una dimensión de la realidad en la Ingeniería de Sistemas:

        1. **Epistemología:** Estudia el origen y validación del conocimiento (Descartes, Popper).
           *Aplicación:* Validación de datos e hipótesis en modelos formales.
        2. **Lógica:** Estructura del razonamiento correcto.
           *Aplicación:* Construcción de algoritmos y diseño de bases de datos.
        3. **Ética:** Principios normativos de conducta (Adela Cortina).
           *Aplicación:* Ciberseguridad, privacidad e Inteligencia Artificial responsable.
        4. **Ontología:** Estudio del ser y lo "real" (Heidegger).
           *Aplicación:* Modelado de entidades (físicas vs digitales), el Metaverso.
        """,
        "quiz": [
            {
                "question": "¿Qué disciplina filosófica es la base para la construcción de algoritmos y programación?",
                "options": ["Epistemología", "Lógica", "Ontología", "Ética"],
                "answer": "Lógica",
                "feedback": "¡Correcto! La Lógica define las reglas del razonamiento, pilar de los algoritmos."
            },
            {
                "question": "Según Karl Popper, ¿cómo avanza el conocimiento?",
                "options": ["Cuando es absoluto", "Cuando funciona", "Cuando puede ser refutado (falsación)", "Por intuición"],
                "answer": "Cuando puede ser refutado (falsación)",
                "feedback": "¡Excelente! Popper es el padre del falsacionismo en la Epistemología."
            }
        ]
    },
    "MOD-02": {
        "title": "Caso de Estudio: IA y Decisiones Automáticas",
        "description": "Sesgos, caja negra y la ética de la responsabilidad.",
        "content": """
        ### El Dilema Contemporáneo
        Imagina un sistema de Inteligencia Artificial que evalúa créditos bancarios. Funciona con alta precisión estadística, pero tiene dos problemas graves:

        * **Falta de explicabilidad (Caja Negra):** No se puede desglosar el razonamiento lógico que justifica un rechazo.
        * **Sesgo sistémico:** Desaprobación desproporcionada de ciertos grupos demográficos.

        **Pregunta Filosófica:** ¿Es verdadero un conocimiento solo porque "funciona" en números?
        * Desde la **Epistemología**: Un algoritmo opaco no genera conocimiento, genera automatismos propensos a errores ciegos.
        * Desde la **Ética**: Delegar decisiones sin poder explicarlas transgrede la justicia y la equidad. ¡La responsabilidad no se puede delegar a un algoritmo!
        """,
        "quiz": [
            {
                "question": "¿A qué se refiere el término 'Caja Negra' en IA?",
                "options": ["A un servidor apagado", "A la imposibilidad de explicar el razonamiento lógico del algoritmo", "A la base de datos de deudores", "Al diseño físico del hardware"],
                "answer": "A la imposibilidad de explicar el razonamiento lógico del algoritmo",
                "feedback": "¡Exacto! Es cuando sabemos qué entra y qué sale, pero no CÓMO se tomó la decisión."
            }
        ]
    }
}

# ==========================================
# 6. INTERFAZ GRÁFICA (VISTAS)
# ==========================================
def render_sidebar():
    with st.sidebar:
        st.markdown("🧠 FiloTech Edu", unsafe_allow_html=True)
        st.write("---")

        stats = GamificationEngine.get_user_stats(st.session_state.username)
        if stats:
            xp, level, streak, badges = stats
            st.markdown(f"""
            
                
                    🔥 {streak}
                    Racha
                
                
                    ⭐ {level}
                    Nivel
                
            
            """, unsafe_allow_html=True)
            st.progress(xp % 100 / 100, text=f"XP: {xp} / {(level)*100}")

        st.write("---")
        if st.button("📊 Dashboard principal", use_container_width=True):
            st.session_state.current_page = "Dashboard"
        if st.button("🤖 Asistente IA (Tutor)", use_container_width=True):
            st.session_state.current_page = "Tutor"
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

def view_login():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        
            FiloTech Edu
            La plataforma gamificada para aprender Filosofía y Ética en la Ingeniería de Sistemas.
        
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🚀 Iniciar Sesión", "✨ Registrarse"])

        with tab1:
            with st.form("login_form"):
                user = st.text_input("Usuario")
                pwd = st.text_input("Contraseña", type="password")
                if st.form_submit_button("Entrar", use_container_width=True):
                    if AuthManager.login(user, pwd):
                        st.session_state.logged_in = True
                        st.session_state.username = user
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas.")

        with tab2:
            with st.form("register_form"):
                new_user = st.text_input("Nuevo Usuario")
                new_pwd = st.text_input("Nueva Contraseña", type="password")
                if st.form_submit_button("Crear cuenta", use_container_width=True):
                    if AuthManager.register(new_user, new_pwd):
                        st.success("Cuenta creada. ¡Ahora puedes iniciar sesión!")
                    else:
                        st.error("El usuario ya existe.")

def view_dashboard():
    st.markdown(f"👋 Hola, {st.session_state.username}", unsafe_allow_html=True)
    st.write("Continúa tu aprendizaje para no perder tu racha.")

    # Obtener progreso
    c = db.conn.cursor()
    c.execute("SELECT module_id, completed FROM progress WHERE username=?", (st.session_state.username,))
    progress_data = {row[0]: row[1] for row in c.fetchall()}

    st.markdown("📚 Rutas de Aprendizaje", unsafe_allow_html=True)

    for mod_id, mod_info in COURSE_DATA.items():
        is_completed = progress_data.get(mod_id, False)
        status_icon = "✅ Completado" if is_completed else "🚀 Empezar"
        bg_color = "rgba(16, 185, 129, 0.1)" if is_completed else "rgba(255,255,255,0.05)"
        border_color = "rgba(16, 185, 129, 0.5)" if is_completed else "rgba(255,255,255,0.1)"

        st.markdown(f"""
        
            {mod_info['title']}
            {mod_info['description']}
        
        """, unsafe_allow_html=True)
        if st.button(f"{status_icon} :: {mod_id}", key=f"btn_{mod_id}"):
            st.session_state.current_page = "Lesson"
            st.session_state.current_module = mod_id
            st.rerun()

    # Mostrar Insignias
    st.markdown("🏅 Tus Logros", unsafe_allow_html=True)
    stats = GamificationEngine.get_user_stats(st.session_state.username)
    if stats and stats[3]:
        badges = json.loads(stats[3])
        badges_html = "".join([f"{b}" for b in badges])
        if badges_html:
            st.markdown(f"{badges_html}", unsafe_allow_html=True)
        else:
            st.info("Aún no tienes insignias. ¡Completa módulos para ganarlas!")

def view_lesson():
    mod_id = st.session_state.current_module
    module = COURSE_DATA[mod_id]

    if st.button("← Volver al Dashboard"):
        st.session_state.current_page = "Dashboard"
        st.rerun()

    st.markdown(f"{module['title']}{module['content']}", unsafe_allow_html=True)

    st.markdown("⚔️ Reto de Conocimiento", unsafe_allow_html=True)

    # Evaluación Interactiva
    with st.container():
        score = 0
        total = len(module["quiz"])

        with st.form(f"quiz_{mod_id}"):
            user_answers = {}
            for i, q in enumerate(module["quiz"]):
                st.markdown(f"**Pregunta {i+1}:** {q['question']}")
                user_answers[i] = st.radio("Selecciona una opción:", q["options"], key=f"q_{i}")
                st.write("---")

            submitted = st.form_submit_button("Evaluar respuestas", use_container_width=True)

            if submitted:
                for i, q in enumerate(module["quiz"]):
                    if user_answers[i] == q["answer"]:
                        score += 1
                        st.success(f"✅ Correcto: {q['feedback']}")
                    else:
                        st.error(f"❌ Incorrecto. La respuesta era: {q['answer']}")

                # Gamificación post-evaluación
                if score == total:
                    st.balloons()
                    xp_earned = 50
                    GamificationEngine.add_xp(st.session_state.username, xp_earned)
                    GamificationEngine.unlock_badge(st.session_state.username, f"Maestro {mod_id}")

                    # Guardar progreso
                    c = db.conn.cursor()
                    c.execute("INSERT OR REPLACE INTO progress (username, module_id, score, completed) VALUES (?, ?, ?, ?)",
                              (st.session_state.username, mod_id, score, True))
                    db.conn.commit()

                    st.markdown(f"""
                    
                        ¡Módulo Completado! 🏆
                        Has ganado +{xp_earned} XP
                    
                    """, unsafe_allow_html=True)
                else:
                    st.warning("Necesitas todas las respuestas correctas para completar el módulo y ganar XP. ¡Inténtalo de nuevo!")

def view_tutor():
    st.markdown("🤖 Asistente Virtual Socrático", unsafe_allow_html=True)
    st.markdown("¡Hola! Soy tu tutor de inteligencia artificial (simulado). Puedo ayudarte a repasar conceptos sobre Filosofía y Ética en Sistemas. Hazme una pregunta rápida.", unsafe_allow_html=True)

    # Simulación de chat IA
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ej: ¿Qué dijo Peter Drucker sobre la ingeniería?")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Respuestas pre-programadas basadas en el documento
        response = "Interesante pregunta. Recuerda analizarlo desde el punto de vista ético y tecnológico."
        p_lower = prompt.lower()
        if "drucker" in p_lower:
            response = "Peter Drucker dijo: 'Hacer lo correcto es más importante que hacer las cosas bien'. En ingeniería, esto significa que el pensamiento crítico garantiza que el imperativo técnico ('saber cómo hacer') esté siempre supeditado al juicio ético ('saber si se debe hacer')."
        elif "ontolog" in p_lower or "metaverso" in p_lower:
            response = "La Ontología estudia el ser y lo 'real' (su referente es Heidegger). En Ingeniería de Sistemas, se aplica para modelar entidades físicas vs digitales, arquitectura de datos y la redefinición de la identidad en el Metaverso."
        elif "epistemolog" in p_lower or "popper" in p_lower:
            response = "La Epistemología estudia la naturaleza y validación del conocimiento verdadero. Karl Popper introdujo la 'falsación': el conocimiento avanza cuando puede ser refutado. En sistemas, esto se aplica al verificar hipótesis en modelos formales y validar datos."
        elif "caja negra" in p_lower or "ia" in p_lower:
            response = "La 'Caja Negra' en IA ocurre cuando un algoritmo funciona bien estadísticamente, pero no podemos desglosar su razonamiento lógico. Desde la ética de la responsabilidad, atribuir decisiones cruciales a estos sistemas transgrede los principios de justicia y explicabilidad."

        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# ==========================================
# 7. CONTROLADOR PRINCIPAL (MAIN)
# ==========================================
def main():
    inject_custom_css()
    init_session()

    if not st.session_state.logged_in:
        view_login()
    else:
        render_sidebar()

        # Enrutador simple
        if st.session_state.current_page == "Dashboard":
            view_dashboard()
        elif st.session_state.current_page == "Lesson":
            view_lesson()
        elif st.session_state.current_page == "Tutor":
            view_tutor()

if __name__ == "__main__":
    main()
