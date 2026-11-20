import argparse
import json
from html import escape
from pathlib import Path
from datetime import date, timedelta

cli = argparse.ArgumentParser()
cli.add_argument("--stats", type=Path, default=Path(__file__).with_name("stats.json"))
cli.add_argument("--output", type=Path, default=Path("."))
options = cli.parse_args()
stats = json.loads(options.stats.read_text(encoding="utf-8"))
root = options.output
assets = root / "dashboard"
assets.mkdir(exist_ok=True)

def text(x, y, label, size=22, color="#e6ddf8", weight=400, extra=""):
    size = min(size, max(15, round(size * .88, 1)))
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}" {extra}>{escape(label)}</text>'

def eyebrow(x,y,label):
    return text(x,y,label,15,"#d6baff",700,'letter-spacing="2.2"')

def panel(x,y,w,h, radius=25):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="url(#glass)" stroke="url(#edge)"/><path d="M{x+radius} {y+1}h{w-2*radius}" stroke="url(#shine)"/>'

def scan_sweep(x, y, width, height, radius=20, phase=0, period=6.4):
    clip = f"sweep-{x}-{y}"
    return f'''<g transform="translate({x} {y})" aria-hidden="true">
  <clipPath id="{clip}"><rect width="{width}" height="{height}" rx="{radius}"/></clipPath>
  <g clip-path="url(#{clip})">
    <g class="motion-decoration" transform="translate(-114 0)">
      <animateTransform attributeName="transform" type="translate"
        values="-114 0;{width} 0;{width} 0" keyTimes="0;.78;1"
        begin="{phase:.2f}s" dur="{period}s" repeatCount="indefinite"/>
      <rect width="112" height="{height}" fill="url(#scanner-glow)"/>
      <path d="M110 0v{height}" stroke="#f4cdff" stroke-width="2" stroke-opacity=".63"/>
    </g>
  </g>
</g>'''

def flow_line(path, color, width):
    return f'''<path class="motion-decoration" d="{path}" fill="none" stroke="{color}"
  stroke-width="{width}" stroke-dasharray="8 11">
  <animate attributeName="stroke-dashoffset" from="0" to="-38" dur="2.8s" repeatCount="indefinite"/>
</path>'''

def section(kicker, heading, subtitle):
    centered = 'text-anchor="middle"'
    return (
        text(500,49,kicker,15,"#d6baff",700,'text-anchor="middle" letter-spacing="2.7"')
        + text(500,104,heading,48,"#fff6ff",750,centered)
        + text(500,143,subtitle,20.5,"#e6ddf8",480,centered)
        + '<path d="M231 161H769" stroke="url(#shine)" stroke-width="1.5"/>'
    )

def svg(name, title, description, h, body, hero=False):
    document = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 {h}" role="img" aria-labelledby="title desc" font-family="system-ui, -apple-system, Segoe UI, sans-serif">
<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>
<defs>
  <linearGradient id="background" x2="1" y2="1" gradientUnits="objectBoundingBox"><stop stop-color="#140b26"/><stop offset=".52" stop-color="#24143d"/><stop offset="1" stop-color="#10091d"/></linearGradient>
  <radialGradient id="aura"><stop stop-color="#a758ed" stop-opacity=".38"/><stop offset="1" stop-color="#a758ed" stop-opacity="0"/></radialGradient>
  <linearGradient id="glass" x2=".3" y2="1" gradientUnits="objectBoundingBox"><stop stop-color="#eacaff" stop-opacity=".18"/><stop offset=".37" stop-color="#9975ca" stop-opacity=".095"/><stop offset="1" stop-color="#130b26" stop-opacity=".56"/></linearGradient>
  <linearGradient id="edge" x2=".85" y2="1" gradientUnits="objectBoundingBox"><stop stop-color="#efd9ff" stop-opacity=".65"/><stop offset=".45" stop-color="#c3a0fc" stop-opacity=".24"/><stop offset="1" stop-color="#ad72ed" stop-opacity=".34"/></linearGradient>
  <linearGradient id="shine"><stop stop-color="#e5ceff" stop-opacity="0"/><stop offset=".32" stop-color="#f8e7ff" stop-opacity=".8"/><stop offset="1" stop-color="#e5ceff" stop-opacity="0"/></linearGradient>
  <linearGradient id="accent"><stop stop-color="#f0bfff"/><stop offset="1" stop-color="#a088ff"/></linearGradient>
  <linearGradient id="scanner-glow">
    <stop stop-color="#bd77ff" stop-opacity="0"/>
    <stop offset=".55" stop-color="#bd77ff" stop-opacity=".06"/>
    <stop offset=".95" stop-color="#d79cff" stop-opacity=".29"/>
    <stop offset="1" stop-color="#edbeff" stop-opacity=".09"/>
  </linearGradient>
  <linearGradient id="metal" x2=".35" y2="1" gradientUnits="objectBoundingBox"><stop stop-color="#ffedff"/><stop offset=".22" stop-color="#d7a0ff"/><stop offset=".47" stop-color="#6242af" stop-opacity=".12"/><stop offset=".72" stop-color="#9c61f6" stop-opacity=".46"/><stop offset="1" stop-color="#f9d7ff"/></linearGradient>
  <radialGradient id="orb" cx=".37" cy=".26" r=".71"><stop stop-color="#eedaff" stop-opacity=".71"/><stop offset=".35" stop-color="#a758ed" stop-opacity=".34"/><stop offset=".69" stop-color="#38236e" stop-opacity=".11"/><stop offset="1" stop-color="#e4b3ff" stop-opacity=".5"/></radialGradient>
  <pattern id="dots" width="25" height="25" patternUnits="userSpaceOnUse"><path d="M0 25V0H25" stroke="#bc94ed" stroke-opacity=".11" fill="none"/><circle cx="3" cy="3" r="1" fill="#e0c8ff" opacity=".18"/></pattern>
  <clipPath id="frame"><rect width="1000" height="{h}" rx="31"/></clipPath>
  <clipPath id="counter-window"><rect width="253" height="70"/></clipPath>
</defs>
<style>
  .counter-static {{display:none}}
  @media (prefers-reduced-motion: reduce) {{
    .counter-motion,.motion-decoration {{display:none}}
    .counter-static {{display:inline}}
    .chart-reveal {{clip-path:none}}
  }}
</style>
<g clip-path="url(#frame)">
<rect width="1000" height="{h}" fill="url(#background)"/>
<ellipse cx="880" cy="{85 if hero else 15}" rx="480" ry="255" fill="url(#aura)"/>
<ellipse cx="230" cy="{h}" rx="470" ry="169" fill="url(#aura)" opacity=".56"/>
<rect width="1000" height="{h}" fill="url(#dots)"/>
<rect x="1" y="1" width="998" height="{h-2}" rx="30" fill="none" stroke="url(#edge)"/>
<path d="M45 21H22V45M955 21h23v24M22 {h-45}v24h23M978 {h-45}v24h-23" stroke="#d5a4fc" stroke-opacity=".72" fill="none" stroke-width="1.25"/>
{body}
</g></svg>'''
    (assets / f"{name}.svg").write_text(document, encoding="utf-8")

orbital = '''
<g transform="translate(785 191)">
  <circle r="185" fill="url(#aura)"/>
  <circle r="147" fill="none" stroke="#cdaaee" stroke-opacity=".25" stroke-dasharray="2 8"/>
  <g class="motion-decoration" aria-hidden="true">
    <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="9s" repeatCount="indefinite"/>
    <path d="M-105 -102 A147 147 0 0 1 0 -147" fill="none" stroke="#d8a2ff" stroke-opacity=".6" stroke-width="2"/>
    <circle cy="-147" r="7" fill="#da96ff" opacity=".25"/>
    <circle cy="-147" r="3.3" fill="#fff0ff"/>
  </g>
  <circle r="118" fill="url(#orb)" stroke="url(#metal)" stroke-width="2"/>
  <g transform="rotate(-27)" fill="none">
    <ellipse rx="165" ry="72" stroke="#a56af6" stroke-width="18" opacity=".17"/>
    <ellipse rx="165" ry="72" stroke="url(#metal)" stroke-width="11"/>
    <ellipse rx="169" ry="77" stroke="#f2daff" stroke-width="1.1" opacity=".67"/>
    <ellipse rx="159" ry="67" stroke="#d9bbff" opacity=".71"/>
    <ellipse rx="133" ry="37" stroke="url(#metal)" stroke-width="2" opacity=".64" transform="rotate(70)"/>
    <circle cx="149" cy="31" r="6" fill="#ffefff"/>
    <circle cx="149" cy="31" r="13" stroke="#eab9ff" opacity=".63"/>
  </g>
  <path d="M-87 -66Q-29 -132 52 -103" fill="none" stroke="#fff1ff" stroke-width="2" opacity=".8"/>
  <circle cx="-100" cy="-96" r="3" fill="#f5ddff"/>
  <circle cx="98" cy="103" r="4" fill="#dfb9ff"/>
</g>
'''
hero = orbital + eyebrow(43,62,"PORTAFOLIO DE DESARROLLO") + text(39,149,"Benjamín Díaz",70,"#fff6ff",775) + text(39,225,"Donoso",70,"#ead4ff",775)
hero += text(45,278,"Full Stack · Ciencia de Datos",28,"#fff2ff",650) + text(45,313,"Machine Learning · Ciberseguridad",26,"#e4d5f6",520)
hero += '<path d="M45 348H955" stroke="#c9a4fd" opacity=".34"/>' + text(45,389,"@benjadiaz112",21,"#f0d9ff",650) + text(955,389,"CHILE",15,"#dfc5f3",700,'text-anchor="end" letter-spacing="2"')
hero += panel(43,429,914,235)
hero += scan_sweep(43,429,914,235,25,phase=-2,period=13)
hero += eyebrow(66,466,"SOBRE MÍ")
hero += text(66,507,"Desarrollo aplicaciones web y proyectos de análisis de datos.",28,"#fff4ff",700)
hero += text(66,543,"Conecto la interfaz, el backend y los datos para construir herramientas",24)
hero += text(66,574,"que ayuden a gestionar procesos y tomar decisiones.",24)
hero += '<path d="M66 597H932" stroke="url(#edge)"/>'
hero += text(66,627,"Duoc UC · Ingeniería en Informática, mención Ciencia de Datos",22,"#e9caff",640)
svg("portada","Benjamín Díaz Donoso",
    "Desarrollo Full Stack, Ciencia de Datos, Machine Learning y Ciberseguridad en Chile. "
    "Desarrollo aplicaciones web y proyectos de análisis de datos. Conecto la interfaz, el backend y los datos para construir herramientas que ayuden a gestionar procesos y tomar decisiones. "
    "Estudio Ingeniería en Informática, mención Ciencia de Datos, en Duoc UC.",
    699,hero,True)

icons = {
    "screen":"M3 5h34v23H3z M14 34h12 M20 28v6 M9 11h22 M9 17h11",
    "api":"M20 3 35 11v17L20 36 5 28V11z M13 20h14 M20 13v14",
    "database":"M5 10c0-7 30-7 30 0s-30 7-30 0z M5 10v20c0 7 30 7 30 0V10 M5 20c0 7 30 7 30 0",
    "chart":"M5 5v30h30 M9 26l7-9 6 4 11-13 M27 8h6v6",
    "phone":"M11 3h18v34H11z M17 7h6 M18 32h4",
    "cloud":"M11 29a7 7 0 0 1 0-14 10 10 0 0 1 19 1 6.6 6.6 0 0 1 0 13z M20 33v4",
    "nodes":"M8 12 21 6 32 16 27 31 11 29z M8 12l19 19 M21 6 11 29 M32 16 8 12 M21 6l6 25",
    "shield":"M20 4 34 10v9c0 8-7 14-14 17-7-3-14-9-14-17v-9z M13 21l5 5 9-10",
}


def icon(x,y,name,scale=1):
    return (
        f'<g transform="translate({x} {y}) scale({scale})" fill="none" stroke="#edcaff" '
        f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="{icons[name]}"/></g>'
    )


def chip(x,y,label):
    width = 25 + 10*len(label)
    badge = f'<rect x="{x}" y="{y}" width="{width}" height="30" rx="9" fill="#5c3487" fill-opacity=".6" stroke="#c494eb" stroke-opacity=".46"/>'
    return badge + text(x+12,y+21,label,16,"#f6deff",700),width


def card(x,y,w,h,title,descriptor,glyph,tools,lines):
    block = panel(x,y,w,h,20)
    block += scan_sweep(x,y,w,h,phase=-(x+y)/190,period=9.5)
    block += f'<path d="M{x+7} {y+2}h{w-14}" stroke="url(#accent)" stroke-width="2.2" opacity=".8"/>'
    block += icon(x+w-49,y+22,glyph,.73)
    block += text(x+21,y+43,title,24 if w<320 else 27,"#fff4ff",735)
    block += text(x+21,y+70,descriptor,17.5,"#e9caff",560)
    px=x+21
    for label in tools:
        badge, width = chip(px,y+91,label)
        block += badge
        px += width+8
    for i,line in enumerate(lines):
        block += text(x+21,y+151+24*i,line,18.5)
    block += f'<path d="M{x+21} {y+h-18}h{w-42}" stroke="#a776d3" stroke-opacity=".28"/>'
    block += f'<circle cx="{x+w-24}" cy="{y+h-18}" r="3.6" fill="#f9cfff"/>'
    return block


tech = [
    ("Frontend","Interfaces y componentes","screen",("React","Next.js","Tailwind"),("TypeScript · JavaScript","Vite · HTML · CSS")),
    ("Backend y APIs","Servicios e integración","api",("Node.js","Spring Boot","FastAPI"),("Python · Java","Diseño de APIs REST")),
    ("Datos","Persistencia y búsqueda","database",("PostgreSQL","MongoDB","Pinecone"),("SQL · Supabase · Firestore","Databricks")),
    ("Cloud y CI","Contenedores y colaboración","cloud",("Azure","Docker","GitHub"),("Git · GitHub Actions","Pull requests · Revisión de código")),
    ("Machine Learning y BI","Exploración y visualización","chart",("pandas","scikit-learn","Streamlit"),("NumPy · Plotly · D3.js · Power BI","Matplotlib · Seaborn · Jupyter · Colab")),
    ("Móvil y blockchain","Android y contratos inteligentes","phone",("Kotlin","Firebase","Solidity"),("Android Studio · Firebase Auth","Remix IDE · DApps")),
]
stack = section("TECNOLOGÍAS","Universo tecnológico","Herramientas de desarrollo, datos e infraestructura.")
for i,items in enumerate(tech):
    stack += card(43+(i%2)*466,187+(i//2)*225,448,210,*items)
svg("stack","Universo tecnológico","Stack de frontend, backend, datos, cloud, machine learning, visualización, móvil y blockchain. Lista técnica debajo del panel.",866,stack)


architecture = section("DISEÑO DE SISTEMAS","Arquitectura de sistemas","Flujo de solicitudes · Servicios · Persistencia · Infraestructura")

pipeline = [
    ("Aplicación cliente","screen"),
    ("Capa de API","api"),
    ("Servicios de backend","nodes"),
    ("Capa de datos","database"),
]
for i,(label,glyph) in enumerate(pipeline):
    y=179+i*48
    architecture += panel(374,y,252,38,11)
    architecture += icon(389,y+7,glyph,.59)
    architecture += text(423,y+25,label,19,"#fff3ff",690)
    architecture += f'<path d="M500 {y+38}v10" stroke="#d7a6ff" stroke-width="1.5" opacity=".63"/>'
    architecture += f"""<circle class="motion-decoration" cx="500" cy="{y+43}" r="3.2" fill="#f7cbff">
      <animate attributeName="opacity" values=".24;1;.24" begin="{i*.18:.2f}s" dur="2.5s" repeatCount="indefinite"/>
    </circle>"""

bus_y=388
architecture += '<path d="M500 361v27M122 388H878" fill="none" stroke="#b17ae0" stroke-opacity=".52" stroke-width="1.5"/>'
architecture += flow_line("M122 388H878","#e0adff",1.5)
architecture += """<circle class="motion-decoration" r="3.9" fill="#fff0ff">
  <animateMotion path="M122 388H878" dur="6s" repeatCount="indefinite"/>
</circle>"""

layers = [
    ("Experiencia","screen",("React","Next.js"),("Componentes UI","Android · Kotlin","Interfaces web")),
    ("Capa de API","api",("REST","Auth"),("Validación de entrada","Firebase Authentication","Integración de clientes")),
    ("Servicios","nodes",("Node.js","Python"),("Spring Boot · FastAPI","Lógica de negocio","Procesamiento de datos")),
    ("Datos","database",("SQL","NoSQL"),("PostgreSQL · Supabase","MongoDB · Firestore","Búsqueda con Pinecone")),
    ("Infraestructura","cloud",("Azure","Docker"),("GitHub Actions","Pruebas de CI","Versionado con Git")),
]
for i,(title,glyph,badges,notes) in enumerate(layers):
    x,y,w,h=30+i*189,413,184,220
    center=x+w//2
    architecture += f'<path d="M{center} {bus_y}v{y-bus_y}" stroke="#be8bf2" stroke-opacity=".57"/>'
    architecture += f'<circle cx="{center}" cy="{bus_y}" r="2.8" fill="#dcb0fa"/>'
    architecture += panel(x,y,w,h,15)
    architecture += scan_sweep(x,y,w,h,15,phase=-i*1.4,period=8.5)
    architecture += f'<path d="M{x+12} {y+2}h{w-24}" stroke="url(#accent)" stroke-width="1.7"/>'
    architecture += icon(center-20,y+18,glyph)
    architecture += text(center,y+82,title,22,"#fff4ff",735,'text-anchor="middle"')
    for j,badge in enumerate(badges):
        bx=x+13+j*81
        architecture += f'<rect x="{bx}" y="{y+99}" width="77" height="25" rx="6" fill="#633b8c" fill-opacity=".52" stroke="#bf8ce9" stroke-opacity=".48"/>'
        architecture += text(bx+38.5,y+116,badge,14,"#f7dfff",700,'text-anchor="middle"')
    for j,note in enumerate(notes):
        architecture += text(x+14,y+153+j*21,note,15,"#e8d9f6",520)
svg(
    "flujo-arquitectura",
    "Arquitectura de sistemas",
    "Flujo vertical de aplicación cliente, API, servicios de backend y capa de datos. "
    "Cinco capas conectadas de experiencia, API, servicios, datos e infraestructura. "
    "React, Next.js y Kotlin en cliente. REST y Firebase Authentication para integración. "
    "Node.js, Python, Spring Boot y FastAPI en servicios. PostgreSQL, Supabase, MongoDB, "
    "Firestore y Pinecone en datos. Azure, Docker, Git y GitHub Actions en infraestructura.",
    666,
    architecture,
)


ai_cards = [
    ("Machine Learning","Modelado y evaluación","nodes",("Python","scikit-learn"),("Regresión · K-Means · PCA","Ensambles · Validación")),
    ("IA generativa","Software y automatización","api",("Vexum","Pinecone"),("Iniciativa de software e IA","Formación en IA generativa")),
    ("Seguridad en IA","Gobernanza y privacidad","shield",("DELIA","Python"),("Enmascaramiento de datos","Pruebas y benchmarks")),
]
ai = section("INTELIGENCIA ARTIFICIAL","Ingeniería de IA","Modelado, automatización y protección de datos.")
ai += '<path d="M180 213H820M180 213v26m320-26v26m320-26v26" fill="none" stroke="#9d62c8" stroke-width="2"/>'
ai += flow_line("M180 213H820","#edb9ff",2.5)
for x in (180,500,820):
    ai += f'<circle cx="{x}" cy="213" r="5" fill="#ffceff"/>'
for i,items in enumerate(ai_cards):
    ai += card(43+i*310,242,294,211,*items)
svg("ia","Ingeniería de IA","Machine learning, Vexum e IA generativa, bases de datos vectoriales con Pinecone y contribuciones de privacidad en DELIA.",484,ai)

projects = [
    ("Spotify Tracks","Modelado de popularidad musical","Python · scikit-learn"),
    ("Ryde","Plataforma web y administración","TypeScript · Node.js · PostgreSQL"),
    ("Clínica dental y facial","Catálogo y reserva de demostración","React · Next.js"),
    ("Trazabilidad de fruta","DApp para estado y cadena de frío","Solidity · Remix IDE"),
    ("StreamView Analytics","Exploración y visualización de contenidos","Streamlit · D3.js · Power BI"),
    ("Viemms Store","Catálogo y administración en Android","Kotlin · Firebase"),
    ("Vexum","Servicios de software, automatización e IA","React · TypeScript · Tailwind CSS"),
    ("Security Auditor & Licensing","Auditoría de seguridad y licencias","Python · Backend"),
]
p = section("PORTAFOLIO","Proyectos destacados","Aplicaciones web, análisis de datos, Android y seguridad.")
for i,(title,sub,techs) in enumerate(projects):
    x,y=43+(i%2)*466,181+(i//2)*112
    p += panel(x,y,448,100,21)
    p += scan_sweep(x,y,448,100,21,phase=-(i+1)*1.1,period=11)
    p += text(x+19,y+34,title,23,"#fff4ff",710)
    p += text(x+19,y+60,sub,17.5)
    p += text(x+19,y+83,techs,16,"#e2bcff",630)
svg("proyectos","Proyectos destacados","Spotify Tracks, Ryde, Clínica dental y facial, Trazabilidad de fruta, StreamView Analytics, Viemms Store, Vexum y Security Auditor & Licensing.",640,p)

def format_metric(value, decimals=0):
    return f"{value:,.{decimals}f}".translate(str.maketrans(",.", ".,"))


def counter(x, y, value, decimals=0):
    if value == 0:
        return text(x,y+63,format_metric(value,decimals),61,"#fff4ff",790)
    frames = min(36, max(1, round(value * 10**decimals)))
    stride = 78
    number = lambda amount, baseline: text(
        0, baseline, format_metric(amount, decimals), 61, "#fff4ff", 790,
        'style="font-variant-numeric:tabular-nums"'
    )
    sequence = "".join(
        number(value * (1 - (1 - i / frames)**1.8), 63 + i * stride)
        for i in range(frames)
    ) + number(value, 63 + frames * stride)
    stops = ";".join(f"0 {-i*stride}" for i in range(frames+1))
    times = ";".join(f"{.21*i/frames:.6f}" for i in range(frames+1))
    return (
        f'<g transform="translate({x} {y})">'
        '<g class="counter-motion" clip-path="url(#counter-window)">'
        f'<g transform="translate(0 {-frames*stride})">'
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="{stops};0 {-frames*stride}" keyTimes="{times};1" '
        f'calcMode="discrete" dur="8s" repeatCount="indefinite"/>{sequence}</g>'
        '</g>'
        f'<g class="counter-static">{number(value, 63)}</g></g>'
    )


def metric_card(x, y, value, label, note, decimals=0):
    return (
        panel(x,y,294,153)
        + scan_sweep(x,y,294,153,25,phase=-(x/200+y/145),period=6.2)
        + counter(x+20,y+5,value,decimals)
        + text(x+23,y+99,label,22,"#f2d9ff",710)
        + text(x+23,y+126,note,16.5)
    )


month_names = ("ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic")


def short_date(day):
    return f"{day.day} {month_names[day.month-1]} {day.year}"


activity_start = date.fromisoformat(stats["calendar_start"])
activity_end = date.fromisoformat(stats["calendar_end"])
counts = stats["days"]
weeks = [sum(counts[i:i+7]) for i in range(0,len(counts),7)]
assert len(weeks) == 53
annual_contributions = stats["annual_contributions"]
annual_year = stats["annual_year"]
annual_as_of = date.fromisoformat(stats["annual_as_of"])
calendar_scope = "visibles" if stats["calendar_scope"] == "visible" else "públicas"

activity = section("TELEMETRÍA","Actividad en GitHub",f"Total anual al {short_date(annual_as_of)} · Actividad al {short_date(activity_end)}")
for i,(value,label,note) in enumerate([
    (annual_contributions,"Contribuciones",f"Públicas y privadas · {annual_year}"),
    (stats["public_repos"],"Repositorios públicos","Repositorios propios"),
    (stats["followers"],"Seguidores","Perfil de GitHub"),
    (stats["stars"],"Estrellas","Repositorios públicos"),
    (sum(count>0 for count in counts),"Días con actividad",f"Contribuciones {calendar_scope}"),
]):
    x = (43,353,663,198,508)[i]
    activity += metric_card(x,177+(i//3)*165,value,label,note)
activity += '<g transform="translate(0 165)">'
activity += '''<defs>
 <linearGradient id="area" x2="0" y2="1"><stop stop-color="#d291ff" stop-opacity=".48"/><stop offset="1" stop-color="#b76dff" stop-opacity=".025"/></linearGradient>
 <clipPath id="calendar-window"><rect width="863" height="123" rx="9"/></clipPath>
</defs>'''
activity += panel(43,351,914,289)
activity += text(66,388,f"Contribuciones {calendar_scope} por semana",24,"#fff0ff",730)
activity += text(932,387,"ÚLTIMAS 16 SEMANAS",13,"#dfbffe",700,'text-anchor="end" letter-spacing="1.3"')
cx, cy, cw, ch = 123, 412, 782, 170
chart_counts = weeks[-16:]
tick_step = max(5, ((max(chart_counts)+19)//20)*5)
max_tick = 4*tick_step
for tick in range(0,max_tick+1,tick_step):
    py = cy+ch-ch*tick/max_tick
    activity += f'<path d="M{cx} {py:.2f}h{cw}" stroke="#d3adf4" stroke-opacity=".25"/>'
    activity += text(106,py+5,str(tick),14.5,"#ddc6ee",500,'text-anchor="end"')
points = [(cw*i/15, ch*(1-val/max_tick)) for i,val in enumerate(chart_counts)]
path = "M" + " L".join(f"{x:.2f} {y:.2f}" for x,y in points)
activity += f'''<g transform="translate({cx} {cy})">
 <clipPath id="chart-window">
  <rect width="{cw+6}" height="{ch+9}" x="-5" y="-4">
   <animate attributeName="width" values="6;{cw+6};{cw+6}" keyTimes="0;.31;1" dur="8s" repeatCount="indefinite"/>
  </rect>
 </clipPath>
 <path d="{path}" fill="none" stroke="#ad7ae8" stroke-opacity=".28" stroke-width="2"/>
 <g class="chart-reveal" clip-path="url(#chart-window)">
  <path d="{path} V{ch} H0 Z" fill="url(#area)"/>
  <path d="{path}" fill="none" stroke="#b877ff" stroke-width="13" opacity=".17" stroke-linejoin="round"/>
  <path d="{path}" fill="none" stroke="#e7bbff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
 </g>
 <circle class="motion-decoration" r="5" fill="#fff0ff">
  <animateMotion path="{path}" dur="8s" repeatCount="indefinite"/>
 </circle>
</g>'''
activity += scan_sweep(cx,cy,cw,ch,4,phase=-1.8,period=7.9)
for i,(x,y) in enumerate(points):
    if chart_counts[i] >= 10:
        activity += f'<circle cx="{cx+x:.2f}" cy="{cy+y:.2f}" r="3.2" fill="#f0d7ff" opacity=".8"/>'
chart_start = activity_start + timedelta(weeks=len(weeks)-16)
for i in range(0,16,4):
    stamp = chart_start + timedelta(weeks=i)
    activity += text(cx+points[i][0],614,f"{stamp.day} {month_names[stamp.month-1]}",15,"#e4cdf1",670,'text-anchor="middle"')

activity += panel(43,657,914,224)
activity += text(67,696,f"Calendario de contribuciones {calendar_scope}",24,"#fff0ff",710)
for col in range(0,53,9):
    stamp = activity_start + timedelta(weeks=col)
    activity += text(76+col*16.08,724,month_names[stamp.month-1].upper(),12.5,"#e5c8f6",690)
activity += '<g transform="translate(76 733)" clip-path="url(#calendar-window)">'
levels=["#2e1e46","#603997","#9255dc","#c580ff","#f8d6ff"]
for i,n in enumerate(counts):
    col,row=divmod(i,7)
    level=sum(n>=threshold for threshold in (1,4,10,18))
    activity += f'<rect x="{col*16.08:.2f}" y="{row*15.58:.2f}" width="12.5" height="12.5" rx="3.1" fill="{levels[level]}"/>'
activity += scan_sweep(0,0,863,107,4,phase=-1.2,period=8.4)
activity += "</g></g>"
activity += text(45,1098,"Enfoque actual",37,"#fff1ff",750)
for i,(title,lines) in enumerate([
    ("IA aplicada",("ML y evaluación","Automatización · Vexum")),
    ("Ingeniería web",("React · Next.js","Node.js · APIs REST")),
    ("Datos y BI",("Python · Databricks","Streamlit · Power BI")),
    ("Seguridad",("Privacidad · DELIA","Auditoría y pruebas")),
]):
    x,y=43+(i%2)*466,1122+(i//2)*116
    activity += panel(x,y,448,100,20)+text(x+22,y+32,title,24,"#fff4ff",730)
    activity += text(x+22,y+60,lines[0],17.5)+text(x+22,y+83,lines[1],17.5)
svg("actividad","Actividad en GitHub",
    f"{format_metric(annual_contributions)} contribuciones públicas y privadas en {annual_year} al {short_date(annual_as_of)}. "
    f"{stats['public_repos']} repositorios públicos, {stats['followers']} seguidores y {stats['stars']} estrellas. "
    f"Calendario de contribuciones {calendar_scope}.",
    1361,activity)


metrics = section("EVALUACIÓN","Rendimiento y visualización","Resultados de Spotify Tracks y StreamView Analytics.")
for i,(value,label,sub,decimals) in enumerate([
    (89495,"Canciones analizadas","Conjunto de Spotify Tracks",0),
    (17913,"Canciones de reserva","Evaluación del modelo",0),
    (31991,"Títulos explorables","Catálogo de StreamView",0),
]):
    metrics += metric_card(43+310*i,184,value,label,sub,decimals)
metrics += panel(43,361,448,233,22)
metrics += scan_sweep(43,361,448,233,22,phase=-.9,period=7.8)
metrics += text(64,403,"Error de predicción",25,"#fff2ff",730)
metrics += text(64,433,"Escala de 0 a 10 puntos de popularidad",16)
for i,(label,value) in enumerate([("MAE",5.02),("RMSE",8.50)]):
    y=475+i*55
    metrics += text(65,y,label,18,"#f7e3ff",680)
    metrics += text(466,y,format_metric(value,2),20,"#fff4ff",720,'text-anchor="end"')
    metrics += f'<g transform="translate(67 {y+14})"><path d="M0 0h390" stroke="#6d4989" stroke-width="8" stroke-linecap="round"/><path d="M0 0h{value*39:.2f}" stroke="url(#accent)" stroke-width="8" stroke-linecap="round"/></g>'
metrics += panel(509,361,448,233,22)
metrics += scan_sweep(509,361,448,233,22,phase=-3.3,period=8.6)
metrics += text(531,403,"Ajuste del modelo",25,"#fff2ff",730)
metrics += text(531,446,"R² · Spotify Tracks",19,"#eed8fa",630)
metrics += text(531,508,"0,830",47,"#fff0ff",770)
metrics += text(531,546,"Evaluación en reserva",17)
metrics += """
<g transform="rotate(-90 862 484)">
  <circle cx="862" cy="484" r="65" fill="none" stroke="#563473" stroke-width="10"/>
  <circle cx="862" cy="484" r="65" fill="none" stroke="url(#accent)" stroke-width="10"
          stroke-linecap="round" pathLength="100" stroke-dasharray="100 100" stroke-dashoffset="17"/>
</g>
<g transform="translate(862 484)" aria-hidden="true">
  <g class="motion-decoration">
    <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="6.5s" repeatCount="indefinite"/>
    <path d="M-41 -61A74 74 0 0 1 0 -74" fill="none" stroke="#d7a2fa" stroke-opacity=".7" stroke-width="2"/>
    <circle cy="-74" r="3.5" fill="#fff0ff"/>
  </g>
</g>
"""
metrics += text(862,491,"R²",23,"#faeaff",740,'text-anchor="middle"')
metrics += text(43,656,"Prácticas de ingeniería",34,"#fff1ff",750)
for i,(title,sub,glyph) in enumerate([
    ("Validación","Datos fuera del entrenamiento","chart"),
    ("Pruebas","Regresiones y reproducibilidad","shield"),
    ("Automatización","Revisión y CI con GitHub Actions","cloud"),
]):
    x=43+i*310
    metrics += panel(x,679,294,104,19)+icon(x+20,699,glyph,.67)
    metrics += text(x+57,720,title,23,"#fff4ff",720)
    metrics += text(x+21,755,sub,16.5)
svg("metricas","Rendimiento y visualización",
    "Spotify Tracks: 89.495 canciones, R² de 0,830 sobre 17.913 canciones de reserva, MAE de 5,02 y RMSE de 8,50. StreamView Analytics: catálogo de 31.991 títulos.",
    812,metrics)


certificates = [
    ("IA generativa", "Usando la IA Generativa", "", "Duoc UC · 36 horas · 2026"),
    ("CEHPC", "Ethical Hacking Professional", "Certification", "CertiProf · 2026"),
    ("CSFPC", "Cyber Security Foundation", "Professional Certificate", "CertiProf · 2026"),
    ("CAPC", "Cybersecurity Awareness", "Professional Certification", "CertiProf · 2026"),
    ("AZ-900", "Microsoft Certified", "Azure Fundamentals", "Microsoft · 2026"),
    ("MongoDB", "Bases de datos NoSQL", "y modelado de documentos", "Formación complementaria"),
]
formation = section("ESTUDIOS","Formación y certificaciones","Ciencia de Datos, IA, ciberseguridad y cloud.")
formation += panel(43,185,914,133)
formation += icon(868,222,"chart",1.2)
formation += text(67,227,"Ingeniería en Informática",30,"#fff4ff",750)
formation += text(67,262,"Mención Ciencia de Datos · Duoc UC",24,"#f1d7ff",620)
formation += text(67,291,"En curso · Sexto semestre",20)
for i,(heading, first_line, second_line, provider) in enumerate(certificates):
    x,y=43+(i%2)*466,336+(i//2)*167
    formation += panel(x,y,448,152,20)
    formation += scan_sweep(x,y,448,152,phase=-(i+1)*1.4,period=11.5)
    formation += text(x+22,y+38,heading,26,"#fff3ff",740)
    formation += text(x+22,y+70,first_line,21)
    formation += text(x+22,y+96,second_line,21)
    formation += text(x+22,y+129,provider,18,"#ead2ff",620)
certificate_description = " ".join(
    f"{first_line} {second_line}. {provider}." if second_line else f"{first_line}. {provider}."
    for _,first_line,second_line,provider in certificates
)
svg("formacion","Formación y certificaciones",
    "Ingeniería en Informática, mención Ciencia de Datos en Duoc UC. En curso, sexto semestre. "
    + certificate_description,
    851,formation)

contact = icon(46,29,"screen",1.2)
contact += text(110,49,"Contacto en LinkedIn",30,"#fff4ff",730)
contact += text(110,79,"Desarrollo, datos y colaboración por proyecto",23,"#ead2ff",540)
contact += '<path d="M910 56h43m-12-12 12 12-12 12" fill="none" stroke="#f0caff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
svg("contacto","Contacto en LinkedIn","LinkedIn de Benjamín Díaz Donoso para oportunidades y colaboración.",106,contact)

details_card = text(45,60,"Detalles y enlaces del portafolio",31,"#fff4ff",710)
details_card += '<path d="M903 49h42m-12-12 12 12-12 12" stroke="#f0caff" stroke-width="3" fill="none" stroke-linejoin="round" stroke-linecap="round"/>'
svg("enlaces","Detalles y enlaces del portafolio","Abrir tecnologías, proyectos y enlaces del portafolio.",95,details_card)
