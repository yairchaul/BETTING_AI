import streamlit as st
import os
import sys
import json  # <-- Importante añadir esto arriba

# ... (tus rutas y configuración inicial se mantienen igual) ...

if archivo:
    st.image(archivo, caption="Captura lista para procesar", use_column_width=True)
    
    if st.button("🔥 Analizar con IA"):
        with st.spinner("🤖 IA analizando mercados y calculando ventaja..."):
            # 1. Obtener la respuesta (es un texto con formato JSON)
            resultado_raw = analyze_betting_image(archivo)
            
            try:
                # 2. Convertir el texto de la IA en una lista de Python
                # Limpiamos posibles etiquetas que a veces pone la IA
                json_limpio = resultado_raw.replace('```json', '').replace('```', '').strip()
                juegos = json.loads(json_limpio)
                
                if juegos and len(juegos) > 0:
                    st.success(f"✅ Se detectaron {len(juegos)} juegos con éxito.")
                    
                    for j in juegos:
                        # Usamos los nombres de llaves que definimos en el prompt de vision_reader
                        home = j.get('home', 'N/A')
                        away = j.get('away', 'N/A')
                        linea = j.get('handicap', j.get('total', 'N/A'))
                        momio = j.get('moneyline', 'N/A')
                        
                        ev_detectado = 0.052  # Simulación
                        stake_sugerido = bankroll * 0.05
                        
                        with st.expander(f"📌 {away} vs {home}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Línea/Total:** {linea}")
                                st.write(f"**Momio:** {momio}")
                            with col2:
                                st.metric("Expected Value", f"{ev_detectado*100:.1f}%")
                                st.write(f"**Stake:** ${stake_sugerido:,.2f}")
                            
                            guardar_pick_automatico(j, ev_detectado, stake_sugerido)
                            st.caption("📂 Datos guardados en data/picks.csv")
                else:
                    st.warning("⚠️ La IA no encontró datos claros en la imagen.")

            except Exception as e:
                st.error(f"❌ Error al procesar la respuesta de la IA: {e}")
                st.info("Respuesta cruda recibida:")
                st.code(resultado_raw) # Esto nos ayuda a ver qué respondió la IA si falla

