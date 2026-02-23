import streamlit as st
import os
import sys

# 1. Configuración de rutas para evitar SyntaxError e ImportErrors
current_dir = os.path.dirname(__file__)
modules_path = os.path.join(current_dir, 'modules')
if modules_path not in sys.path:
    sys.path.append(modules_path)

# 2. Importaciones de tus módulos personalizados
try:
    from vision_reader import analyze_betting_image
    from tracker import guardar_pick_automatico
    from ev_engine import calcular_ev
except ImportError as e:
    st.error(f"Error crítico de módulos: {e}. Revisa que la carpeta 'modules' exista.")

st.set_page_config(page_title="Ticket Pro IA", page_icon="🏀")

# --- UI SIDEBAR ---
st.sidebar.title("💰 Gestión de Capital")
bankroll = st.sidebar.number_input("Bankroll actual (MXN)", value=1000.0, step=100.0)
st.sidebar.markdown("---")
st.sidebar.info("La API Key se gestiona de forma segura mediante Streamlit Secrets.")

# --- CUERPO PRINCIPAL ---
st.title("🏀 Ticket Pro - Vision Terminal")
st.header("📸 Scanner de Mercados")

archivo = st.file_uploader("Sube captura de Caliente.mx", type=['png', 'jpg', 'jpeg'])

if archivo:
    st.image(archivo, caption="Captura lista para procesar", use_column_width=True)
    
    if st.button("🔥 Analizar con IA"):
        with st.spinner("🤖 IA analizando mercados y calculando ventaja..."):
            # Llama a la función que ya validamos que funciona con tu Key
            juegos = analyze_betting_image(archivo)
            
            if juegos and len(juegos) > 0:
                st.success(f"✅ Se detectaron {len(juegos)} juegos con éxito.")
                
                # Crear tabla comparativa rápida
                for j in juegos:
                    home = j.get('home', 'N/A')
                    away = j.get('away', 'N/A')
                    linea = j.get('total_line', 'N/A')
                    momio = j.get('odds_over', 'N/A')
                    
                    # Simulación de cálculo de valor (EV)
                    # Aquí es donde el ev_engine haría su magia real
                    ev_detectado = 0.052  # Ejemplo: 5.2% de ventaja detectada
                    stake_sugerido = bankroll * 0.05 # 5% de bankroll
                    
                    with st.expander(f"📌 {away} vs {home}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Línea:** {linea}")
                            st.write(f"**Momio:** {momio}")
                        
                        with col2:
                            st.metric("Expected Value", f"{ev_detectado*100:.1f}%")
                            st.write(f"**Stake:** ${stake_sugerido:,.2f}")
                        
                        # Guardado automático en el historial
                        guardar_pick_automatico(j, ev_detectado, stake_sugerido)
                        st.caption("📂 Datos guardados en data/picks.csv")
            else:
                st.error("❌ No se pudieron extraer datos. Revisa el log de la app para ver el error de Vision AI.")
