def get_vision_client():
    try:
        # Hacemos una copia profunda para no alterar st.secrets original
        creds_info = {k: v for k, v in st.secrets["google_credentials"].items()}
        
        # LIMPIEZA EXTREMA DE LA LLAVE
        pk = creds_info["private_key"]
        
        # 1. Quitar comillas accidentales y espacios en los extremos
        pk = pk.strip().strip("'").strip('"')
        
        # 2. Convertir los \n literales en saltos de línea reales
        pk = pk.replace("\\n", "\n")
        
        # 3. Eliminar posibles espacios en blanco al inicio de cada línea interna
        pk = "\n".join([line.strip() for line in pk.split("\n")])
        
        creds_info["private_key"] = pk
        
        credentials = service_account.Credentials.from_service_account_info(creds_info)
        return vision.ImageAnnotatorClient(credentials=credentials)
    except Exception as e:
        st.error(f"Error de autenticación: {e}")
        return None
