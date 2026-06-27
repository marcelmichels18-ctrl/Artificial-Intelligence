# Car Price Prediction API

## 1. Setup im Notebook

1. Öffne dein Notebook `California__Solution_.ipynb`.
2. Füge den Inhalt von `notebook_save_snippet.py` als neue Zelle ein,
   direkt NACH der Zelle mit `xgb.fit(X_train, y_train)`.
3. Führe sie aus. Das erzeugt 5 Dateien:
   - model.joblib
   - scaler.joblib
   - feature_columns.json
   - category_values.json
   - numeric_columns.json
4. Kopiere diese 5 Dateien in DIESEN Ordner (neben main.py).

## 2. Lokal testen (empfohlen, bevor du deployst)

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Dann im Browser: http://127.0.0.1:8000/docs
Dort kannst du den /predict-Endpunkt direkt interaktiv testen.

Beispiel-Request (z.B. mit curl):
```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "volkswagen",
    "model": "Volkswagen Golf",
    "color": "black",
    "year": 2018,
    "power_ps": 150,
    "transmission_type": "Manual",
    "fuel_type": "Petrol",
    "mileage_in_km": 70000
  }'
```

## 3. Deployment auf Render (kostenlos)

1. Erstelle ein GitHub-Repo und lade ALLE Dateien aus diesem Ordner hoch
   (main.py, requirements.txt, Procfile, die 5 .joblib/.json Dateien).
2. Gehe auf https://render.com, erstelle einen kostenlosen Account.
3. "New" -> "Web Service" -> dein GitHub-Repo verbinden.
4. Einstellungen:
   - Build Command:  pip install -r requirements.txt
   - Start Command:   uvicorn main:app --host 0.0.0.0 --port $PORT
   - Instance Type:   Free
5. Deploy klicken. Nach ein paar Minuten bekommst du eine URL wie:
   https://car-price-api-xyz.onrender.com

WICHTIG: Der kostenlose Render-Tier "schläft" nach Inaktivität ein und
braucht beim ersten Aufruf nach einer Pause ca. 30-60 Sekunden zum Hochfahren.
Für eine Sprachsteuerung mit sofortiger Antwort ist das spürbar -- falls
das stört, gibt es kostenpflichtige "Always On"-Instanzen.

## 4. In n8n einbinden

1. Node "HTTP Request" hinzufügen.
2. Method: POST
3. URL: https://DEINE-RENDER-URL.onrender.com/predict
4. Body Content-Type: JSON
5. Body (Beispiel, Werte kommen z.B. aus vorherigem Sprach-zu-Text-Node):
   {
     "brand": "{{ $json.brand }}",
     "model": "{{ $json.model }}",
     "color": "{{ $json.color }}",
     "year": {{ $json.year }},
     "power_ps": {{ $json.power_ps }},
     "transmission_type": "{{ $json.transmission_type }}",
     "fuel_type": "{{ $json.fuel_type }}",
     "mileage_in_km": {{ $json.mileage_in_km }}
   }
6. Antwort kommt als JSON zurück, z.B.:
   { "predicted_price_eur": 19450.23, "warnings": [], "input": {...} }
7. Den Wert "predicted_price_eur" kannst du dann z.B. an eine
   Text-to-Speech-Node weitergeben, um ihn vorzulesen.

## Hinweis zur Sprachsteuerung

Die Sprachsteuerung selbst (Speech-to-Text, um z.B. "BMW 3er, 2018,
150 PS, 70000 km" in die einzelnen Felder brand/model/year/etc. zu
zerlegen) übernimmt diese API NICHT. Das müsstest du vorher in n8n
lösen, z.B. mit einem LLM-Node (OpenAI/Claude), der die gesprochene
Anfrage in das benötigte JSON-Format umwandelt, bevor der HTTP-Request
an diese API geschickt wird.

## Endpunkt /valid-values

GET https://DEINE-URL.onrender.com/valid-values

Zeigt alle brand/model/color/transmission_type/fuel_type-Werte, die
im Training vorkamen. Nützlich, um z.B. den LLM-Node in n8n mit den
gültigen Werten zu "briefen", damit er aus freier Sprache die richtigen
Kategorien herausliest (z.B. "Golf" -> "Volkswagen Golf").
