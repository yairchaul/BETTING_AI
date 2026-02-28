# modules/vision_reader.py

def read_ticket_image(uploaded_file):
    try:
        client = vision.ImageAnnotatorClient.from_service_account_info(dict(st.secrets["google_credentials"]))
        content = uploaded_file.getvalue()
        image = vision.Image(content=content)
        response = client.document_text_detection(image=image)
        matches = []

        if response.full_text_annotation:
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    block_text = ""
                    for para in block.paragraphs:
                        para_text = " ".join(["".join([s.text for s in w.symbols]) for w in para.words])
                        block_text += para_text + "\n"
                    
                    # Intentar buscar momios
                    odds = re.findall(r'[+-]\d{3,4}', block_text)
                    
                    # LIMPIEZA DE NOMBRES
                    clean_text = clean_ocr_noise(block_text)
                    for o in odds: clean_text = clean_text.replace(o, "")
                    lines = [l.strip() for l in clean_text.split('\n') if len(l.strip()) > 3]

                    if len(lines) >= 2:
                        # Si no hay momios, ponemos unos ficticios para que el main no explote
                        final_odds = odds[:3] if len(odds) >= 3 else ["+100", "+100", "+100"]
                        
                        matches.append({
                            "home": lines[0],
                            "away": lines[1],
                            "odds": final_odds,
                            "context": f"{lines[0]} vs {lines[1]}"
                        })
        return matches
    except Exception as e:
        st.error(f"Error: {e}")
        return []
