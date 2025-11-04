# 🍎 UH Kalkulator - Kalkulator Ugljenih Hidrata

Android aplikacija za računanje ugljenih hidrata u hrani i obrocima.

---

## 📋 Šta aplikacija radi?

✅ **Pretraga namirnica** iz lokalne baze  
✅ **Automatsko računanje UH** - sabira sve stavke  
✅ **Dodavanje custom stavki** - ručno unesi bilo šta  
✅ **Čuvanje novih obroka** - kombinuj namirnice i sačuvaj kao novi obrok  
✅ **Offline rad** - sve je lokalno, bez interneta

---

## 🚀 Kako pokrenuti projekat?

### Korak 1: Pripremi svoj CSV

Ako već imaš svoj `items.csv`, stavi ga u `data/items.csv`.

Format CSV fajla:
```csv
name,gram,unit,carbs_g,protein_g,fat_g
Šargarepa,100,gram,5.0,0.9,0.2
Kroasan,50,komad,25.0,5.0,12.0
```

### Korak 2: Kreiraj SQLite bazu

```bash
cd uh_kalkulator
python3 utils/db_init.py
```

✅ Ovo kreira `data/items.db` iz tvog CSV-a

---

## 🔧 Testiranje na računaru (pre Android build-a)

Instaliraj Kivy:

```bash
pip install kivy
```

Pokreni aplikaciju:

```bash
python3 main.py
```

Ovo će ti otvoriti prozor na računaru gde možeš testirati aplikaciju!

---

## 📱 Android Build (sa Docker-om)

### Opcija A: Build sa Dockerom (preporučeno)

```bash
docker run -it --rm \
  -v "$PWD":/home/user/hostcwd \
  kivy/buildozer \
  bash -c "cd hostcwd && buildozer android debug"
```

⏳ **Pažnja:** Prvi build traje 20-40 minuta (skida SDK, NDK, Python...)

### Opcija B: Build bez Dockera (Linux/Mac)

Instaliraj buildozer:

```bash
pip install buildozer
```

Pokreni build:

```bash
buildozer android debug
```

---

## 📦 Gde je APK fajl?

Nakon uspešnog build-a, APK se nalazi ovde:

```
uh_kalkulator/bin/uhkalkulator-0.1-debug.apk
```

**Prebaci ga na telefon i instaliraj!**

---

## 🎨 Kako funkcioniše aplikacija?

### Glavni ekran:

```
┌─────────────────────────────┐
│  🔍 Search bar              │  ← Pretraži hranu
├─────────────────────────────┤
│  📋 Rezultati pretrage      │  ← Klikni da dodaš
├─────────────────────────────┤
│  📋 Trenutna kalkulacija:   │
│  • Šargarepa – 5 UH      ✕  │
│  • Kroasan – 25 UH       ✕  │  ← Obriši stavku
│  • Jogurt – 15 UH        ✕  │
├─────────────────────────────┤
│  Ukupno: 45.0 UH            │  ← Automatski zbir
├─────────────────────────────┤
│ [➕ Dodaj] [🗑 Očisti] [💾]  │  ← Akcije
└─────────────────────────────┘
```

### Funkcionalnosti:

1. **Pretraga** - Kucaj u search bar, prikazuju se rezultati
2. **Dodavanje** - Klikni na rezultat, dodaje se u kalkulaciju
3. **Brisanje** - Klikni ✕ pored stavke
4. **Ručno dodavanje** - "Dodaj novi" za custom unos
5. **Čuvanje obroka** - "Sačuvaj obrok" kombinuje sve i računa UH po porciji

---

## 🧮 Logika računanja obroka

Kada sačuvaš obrok:

```
Primer:
- Ukupno UH svih sastojaka: 60 UH
- Ukupna masa: 1000g
- Jedna porcija: 200g

Računanje:
uh_po_porciji = 60 × (200 / 1000) = 12 UH
```

Novi obrok se čuva u bazi i možeš ga koristiti kao bilo koju drugu namirnicu!

---

## 📁 Struktura projekta

```
uh_kalkulator/
├── main.py              # Glavna logika (Kivy app)
├── buildozer.spec       # Android build config
├── Dockerfile           # Docker build
├── data/
│   ├── items.csv        # Tvoj CSV (input)
│   └── items.db         # SQLite baza (generisana)
└── utils/
    └── db_init.py       # CSV → SQLite konverter
```

---

## ⚙️ Prilagođavanja

### Promeni naziv aplikacije:

U `buildozer.spec`:
```ini
title = Moja UH Aplikacija
package.name = mojaubapp
```

### Dodaj ikonu:

Stavi PNG fajl u `data/icon.png` i u `buildozer.spec` odkomentiraj:
```ini
icon.filename = %(source.dir)s/data/icon.png
```

### Promeni boje:

U `main.py`, potraži `background_color` i menjaj RGB vrednosti.

---

## 🐛 Česti problemi

### "Buildozer command not found"
Rešenje: Koristi Docker metod ili instaliraj buildozer

### "Permission denied"
Rešenje: Dodaj `sudo` ispred docker komande

### Aplikacija se ruši na telefonu
Rešenje: Proveri da li postoji `data/items.db` u APK-u

---

## 📞 Pomoć

Ako imaš pitanja:
1. Proveri da li je `items.db` kreiran (`ls data/`)
2. Testiraj prvo na računaru (`python3 main.py`)
3. Pogledaj buildozer log (`~/.buildozer/logs/`)

---

## 📄 Licenca

Slobodno koristi i menjaj!
