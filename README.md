# App Agriturismo — Prenotazioni + Menu (Passo 1)

Questa è la prima parte dell'app: **prenotazioni tavoli** (senza registrazione per i clienti)
e **menu digitale**. Il pannello di gestione per lo staff permette di modificare in ogni
momento: tavoli, menu, prenotazioni.

## Cosa contiene il progetto

- Pagina pubblica con menu del ristorante
- Form pubblico di prenotazione tavolo (nessun login richiesto dal cliente)
- Pannello di gestione per lo staff (login richiesto) per: tavoli, piatti/categorie, prenotazioni
- Piccola dashboard "Prenotazioni di oggi" per un colpo d'occhio veloce

---

## 1. Come provarla sul tuo computer (facoltativo, per vederla prima di pubblicarla)

Serve **Python 3.11 o superiore** installato sul computer.

Apri il Terminale (Mac) o Prompt dei comandi/PowerShell (Windows), spostati nella cartella
del progetto (quella che contiene questo file `README.md`) ed esegui questi comandi, uno alla volta:

```
python3 -m venv venv
source venv/bin/activate        # su Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

Con `createsuperuser` ti verrà chiesto di scegliere un nome utente e una password:
sarà l'account con cui lo staff accede al pannello di gestione. Rispondi alle domande.

Poi avvia il server locale:

```
python manage.py runserver
```

Apri il browser su **http://127.0.0.1:8000/** → vedrai il sito pubblico.
Per entrare nel pannello di gestione vai su **http://127.0.0.1:8000/admin/** e accedi
con l'utente creato prima.

La prima cosa da fare nel pannello admin: crea qualche **Tavolo** (menu "Tavoli") e qualche
**Categoria** + **Piatto** (menu "Categorie" e "Piatti") così il sito pubblico avrà contenuti.

---

## 1bis. Configurare l'invio delle email (conferma cliente + avviso interno)

Finché non configuri questa parte, l'app funziona lo stesso: le email "vengono scritte"
solo nella finestra nera del terminale invece che inviate davvero (così non si rompe nulla).

Per attivare l'invio vero con Gmail:

1. **Crea una "Password per le app" di Google** (non usare mai la tua password normale):
   - Vai su https://myaccount.google.com/apppasswords (devi avere la verifica in due
     passaggi attiva sul tuo account Google — se non ce l'hai, il sito ti guiderà ad attivarla)
   - Scegli un nome a piacere (es. "Agriturismo App") e clicca crea
   - Google ti mostra una password di 16 lettere: copiala, ti servirà subito dopo
     (non potrai più rivederla in seguito, ma potrai sempre crearne un'altra se la perdi)

2. **Crea il file `.env`** nella cartella del progetto (quella con `manage.py`):
   - Copia il file `.env.example` che trovi già nel progetto
   - Rinomina la copia in `.env` (attenzione: deve iniziare con il punto, niente altro dopo)
   - Aprilo con il Blocco Note e compila:
     - `EMAIL_HOST_USER` → la tua email Gmail
     - `EMAIL_HOST_PASSWORD` → la password di 16 lettere generata al passo 1 (senza spazi)
     - `EMAIL_STAFF_NOTIFICHE` → l'email dove volete ricevere l'avviso di nuova prenotazione
       (per ora può essere la stessa Gmail)
   - Salva e chiudi

3. **Riavvia il server** (`Ctrl+C` per fermarlo, poi di nuovo `python manage.py runserver`)
   e prova a fare una prenotazione dal sito pubblico inserendo la tua email: dovresti
   ricevere sia la mail di conferma che quella di avviso interno.

Quando in futuro avrete un'email dedicata al locale, basterà aggiornare questi valori
nel file `.env` (o le stesse variabili su Render, quando pubblicheremo online) — non
serve toccare il codice.

## 2. Come metterla online gratis/economico con Render

Questi passaggi ricalcano quelli già usati per l'altro progetto (ticketing Terberg).

### A. Carica il codice su GitHub

1. Vai su [github.com](https://github.com) e crea un nuovo repository (es. `agriturismo-app`)
2. Carica dentro tutti i file di questa cartella (puoi trascinarli dall'interfaccia web di
   GitHub, oppure usare Git da terminale se preferisci)

### B. Crea il servizio su Render

1. Vai su [render.com](https://render.com) e accedi (o registrati)
2. **New +** → **PostgreSQL** → crea un database gratuito, dagli un nome (es. `agriturismo-db`)
   → dopo la creazione copia la stringa **Internal Database URL**
3. **New +** → **Web Service** → collega il repository GitHub appena creato
4. Configura così:
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command**: `gunicorn ristorante_project.wsgi`
5. Nella sezione **Environment** aggiungi queste variabili:
   - `DATABASE_URL` → incolla la Internal Database URL copiata prima
   - `SECRET_KEY` → una stringa lunga e casuale a tua scelta (es. genera una password lunga)
   - `DEBUG` → `False`
   - `ALLOWED_HOSTS` → l'indirizzo che Render ti assegnerà (es. `agriturismo-app.onrender.com`)
   - `CSRF_TRUSTED_ORIGINS` → `https://agriturismo-app.onrender.com` (con https davanti)
   - `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_STAFF_NOTIFICHE` → stessi valori del
     tuo file `.env` locale (o quelli definitivi, quando li avrete)
6. Fai il deploy. Al termine, apri una **Shell** dal pannello Render del servizio ed esegui:
   ```
   python manage.py migrate
   python manage.py createsuperuser
   ```
   per creare il database e l'utente staff, esattamente come in locale.

Il sito sarà online sull'indirizzo che Render ti mostra (tipo `https://agriturismo-app.onrender.com`).

---

## 3. Uso quotidiano per lo staff

- **Pannello di gestione completo**: `/admin/` — qui si gestiscono tavoli, menu, e si possono
  modificare/confermare le prenotazioni (colonna "tavolo" e "stato" sono modificabili
  direttamente dalla lista, senza aprire ogni singola prenotazione)
- **Vista rapida del giorno**: `/staff/dashboard/` — comodo per un colpo d'occhio veloce
  sulle prenotazioni di oggi, accessibile anche dal menu in alto una volta effettuato l'accesso

## 4. Novità: Ordini al tavolo (cliente da QR + cameriere da tablet/telefono)

Aggiornati i file, per attivare anche questa parte serve rilanciare le migrazioni:

```
python manage.py migrate
```

**Come funziona:**

- **Sala** (`/ordini/staff/sala/`, link in alto una volta fatto l'accesso staff) — colpo d'occhio
  su tutti i tavoli: verde = conto aperto con il totale, grigio = libero
- Cliccando su un tavolo si entra nella sua gestione: il cameriere può **aggiungere piatti/bevande,
  rimuovere righe, e vedere anche quello che il cliente ha eventualmente già ordinato da solo**
  (colonna "Da": Cliente/Staff)
- **"Chiudi conto"** — mostra il totale finale e libera il tavolo per il prossimo servizio
- **Pagina cliente da QR** — ogni tavolo ha un indirizzo dedicato:
  `http://ilnostrosito.it/ordini/tavolo/NUMEROTAVOLO/` (es. `/ordini/tavolo/3/` per il tavolo
  numero 3). Il cliente la apre scansionando il QR e può aggiungere piatti da solo, che finiscono
  nello stesso conto gestito dal cameriere
- **Vini e bevande**: non serve nessuna modifica al codice — create semplicemente nuove
  Categorie (es. "Vini", "Bevande") dal pannello `/admin/` e aggiungete i relativi prodotti come
  Piatti, con il loro prezzo. Compariranno automaticamente ovunque nel menu e negli ordini

**Per generare i QR code fisici da stampare e mettere sui tavoli**: non serve integrare
nulla nel codice, basta un generatore gratuito online (es. https://www.qr-code-generator.com/)
a cui incollate l'indirizzo del tavolo (es. `https://ilnostrosito.it/ordini/tavolo/3/`) — genera
un'immagine scaricabile e stampabile.

## 5. Novità: vista Cucina (chi ha ordinato, cosa preparare, in che ordine)

Aggiornati i file, per attivare anche questa parte serve di nuovo:

```
python manage.py migrate
```

**Come funziona:**

- **Cucina** (`/ordini/staff/cucina/`, link in alto una volta fatto l'accesso staff) — mostra
  tutti i piatti ancora da preparare, **raggruppati per categoria** (quindi nell'ordine giusto:
  prima gli Antipasti, poi i Primi, ecc. — segue l'ordine impostato nelle Categorie del menu)
- Ogni piatto mostra: **tavolo**, **quantità**, eventuali **note** (es. "senza cipolla"),
  e **quale cameriere l'ha inviato** (oppure "Cliente (QR)" se ordinato direttamente dal tavolo)
- Un pulsante fa avanzare lo stato del piatto: **In attesa → In preparazione → Pronto → Servito**
  (una volta "Servito" sparisce dalla vista cucina, così resta sempre pulita)
- Lo stesso stato è visibile anche al cameriere nella pagina del tavolo, così sa cosa è pronto
  da portare

## 6. Correzione: Cucina raggruppata per tavolo (non più solo per portata)

I piatti dello stesso tavolo ora restano visivamente uniti nella vista Cucina, anche se sono
di portate diverse — così è chiaro cosa deve uscire insieme.

## 7. Novità: Menù fisso oppure Carta (alternativi, sceglie lo staff)

Aggiornati i file, serve di nuovo:

```
python manage.py migrate
```

**Come funziona:**

- Ogni **Categoria** del menu (da `/admin/`) ha ora un campo "Tipo di menù": **Menù fisso**
  oppure **Carta**. Impostatelo per ogni categoria che create (es. "Antipasti fissi" → Menù
  fisso, "Antipasti alla carta" → Carta — potete anche avere categorie diverse per ciascuna)
- Pagina **"Menù"** in alto (una volta fatto l'accesso staff) → scegliete con un clic cosa
  vedono i clienti in questo momento: *Solo menù fisso* / *Solo carta* / *Entrambi visibili*
- Il cambiamento è immediato su tutto: sito pubblico, ordini da QR, ordini da tablet dei
  camerieri — mostrano sempre solo le categorie del tipo attivo (o tutte, se scegliete "Entrambi")

## 9. Correzione: prezzo unico per il menù fisso (non più per singolo piatto)

Aggiornati i file, serve di nuovo:

```
python manage.py migrate
```

**Come funziona ora:**

- Dalla pagina **"Menù"** (staff) trovi un nuovo campo: **"Prezzo menù fisso, a persona"** —
  impostalo una volta (es. 25.00), resta valido finché non lo cambi
- Nella pagina del tavolo (Sala → apri un tavolo), in alto trovi **"Numero coperti"**: il
  cameriere lo imposta con quante persone sono al tavolo
- Il **totale** del conto ora si calcola così: se il tavolo ha ordinato dal menù fisso,
  quella parte del conto è *numero coperti × prezzo a persona* (i singoli piatti fissi non
  hanno un prezzo proprio, compare scritto "incluso nel menù"); vini/bevande/carta invece
  restano sommati singolarmente come sempre — le due parti si sommano nel totale finale
- Stessa cosa sul menu pubblico: se è attivo il menù fisso, in alto compare il prezzo unico
  a persona, e i piatti non mostrano più un prezzo individuale (la carta invece continua a
  mostrare il prezzo per piatto)

## 11. Correzione: vini/bevande sempre visibili, anche col menù fisso attivo

Aggiornati i file, serve di nuovo:

```
python manage.py migrate
```

**Cosa cambia:**

- Ogni Categoria ora ha **3 opzioni** possibili per "Tipo di menù" (da `/admin/`):
  - **Menù fisso** — visibile solo quando è attiva quella modalità
  - **Carta (à la carte)** — visibile solo quando è attiva quella modalità
  - **Sempre visibile** — pensata per Vini/Bevande: **compare sempre**, indipendentemente
    da quale delle due modalità sopra è attiva
- Quindi: mettete le vostre categorie di piatti veri e propri come "Menù fisso" o "Carta"
  (si escludono a vicenda), e la categoria "Vini"/"Bevande" come **"Sempre visibile"** — così
  non sparisce mai e non dovete più usare "Entrambi visibili" solo per farla comparire
  (cosa che mescolava anche tutti i piatti alla carta insieme al menù fisso)
- Nel conto: tutto ciò che è "Sempre visibile" (vini/bevande) si somma sempre a prezzo
  singolo, esattamente come la carta — solo il "Menù fisso" entra nel calcolo a persona

## 13. Novità: pagina QR code + primo restyling grafico

Nessuna nuova migrazione richiesta stavolta, solo file di template/viste aggiornati.

**QR code**: pagina **"QR Code"** in alto (staff) — mostra il QR di ogni tavolo attivo pronto
da stampare, con un pulsante "Stampa" che apre la stampa del browser mostrando solo i QR
(nasconde menu/pulsanti). Basta ritagliare e posizionare ogni QR sul tavolo giusto.

**Restyling**: prima passata di miglioramento estetico — palette (verde oliva + rosso ruggine
caldo su sfondo color grano), font più curati (Fraunces per i titoli, Work Sans per il testo).
Il logo e le foto vere del locale arriveranno in un prossimo aggiornamento.

## 15. Novità: loghi veri, contatti reali, e chi sei loggato

Nessuna nuova migrazione richiesta.

- Inseriti i due loghi: **La Marsena** (navbar, home, footer) e **MD Ranch** (accanto alla
  domanda sulla lezione a cavallo nel form di prenotazione). Sono ritagliati dalle foto/
  screenshot che hai mandato — non sono file vettoriali puliti, quindi se in futuro ti
  procuri i loghi originali in alta qualità (es. file .png/.svg dal grafico che ve li ha
  fatti), basta sostituire i due file dentro `static/branding/` con quelli nuovi (stessi
  nomi: `logo_marsena.png` e `logo_mdranch.png`) e ricompaiono automaticamente ovunque
- Aggiunti indirizzo e telefono reali nel footer di ogni pagina
- **Corretto**: ora la barra in alto mostra "Ciao, [nome utente]" quando sei loggato — così
  sai sempre con quale account (tuo o di un cameriere) sei entrato. Se vuoi controllare
  come cameriere, prima fai "Esci" col tuo account, poi accedi con quello del cameriere

## 17. Restyling completo: navbar pulita + look più curato

Nessuna nuova migrazione richiesta, solo template aggiornati.

- **Navbar pulita**: ora mostra solo "Menu" e "Prenota" in chiaro (quello che serve al
  cliente); i link di lavoro (Area staff, Sala, Cucina, QR Code, Impostazioni menù, Esci)
  sono raccolti in un menu a tendina **"Staff: [nome utente]"**, visibile solo a chi ha
  fatto l'accesso
- **Home page**: logo grande, tre card di presentazione (Prodotti dell'azienda, Cucina
  genuina, MD Ranch)
- **Menu pubblico**: intestazione più curata, prezzi in evidenza col colore del brand
- **Form di prenotazione**: racchiuso in un riquadro con ombra leggera, più ordinato

## 19. Novità: conferma/annulla prenotazioni dalla dashboard, loghi definitivi

Nessuna nuova migrazione richiesta.

- Nella dashboard staff (**Area staff**), ogni prenotazione "In attesa" ha ora due pulsanti:
  **Conferma** (la segna come confermata, sparisce il pulsante e resta il badge verde) e
  **Annulla** (per una disdetta: la prenotazione sparisce dalla dashboard, ma resta comunque
  nello storico su `/admin/` se un giorno vi serve consultarla)
- Aggiornato il logo **MD Ranch** con la versione pulita e vettoriale che avete recuperato —
  molto meglio della foto ritagliata di prima
- Corretto anche il logo circolare nel footer (prima era tagliato a metà)

## 21. Correzione importante: menù fisso/carta ora è per singolo piatto

**Prima**: la scelta "menù fisso / carta / sempre visibile" era sulla Categoria intera —
se "Primi" era segnata come fisso, uscivano automaticamente TUTTI i primi.

**Ora**: la scelta è sul **singolo Piatto**. La stessa categoria "Primi" può avere alcuni
piatti nel menù fisso e altri disponibili solo alla carta.

⚠️ Questa volta serve rifare le migrazioni **e ricontrollare i vostri piatti**, perché il
campo si è spostato:

```
python manage.py migrate
```

Poi vai su `/admin/menu_digitale/piatto/` (o "Piatti" dal menu laterale): ora la colonna
**"Tipo di menù"** è lì, editabile riga per riga direttamente dalla lista — imposta ogni
piatto singolarmente (fisso / carta / sempre visibile). Le vecchie impostazioni sulle
categorie sono state rimosse, quindi tutti i piatti sono ripartiti da "Carta" di default:
ricontrollali tutti prima di procedere con altri test.

## 23. Correzione: "Entrambi visibili" ora è a tutti gli effetti "tutto alla carta"

Nessuna nuova migrazione richiesta.

Prima, in modalità "Entrambi visibili", i piatti etichettati "Menù fisso" restavano senza
prezzo singolo ("incluso nel menù"), il che non aveva senso: in quella modalità non c'è
nessun conteggio "a persona" in corso.

**Ora**: il calcolo speciale a persona (coperti × prezzo) si applica **solo** quando la
modalità attiva è davvero "Solo menù fisso". In "Carta" e in "Entrambi visibili", ogni
piatto — compresi quelli etichettati "fisso" — mostra ed è fatturato al suo prezzo singolo,
esattamente come fosse tutto alla carta. Utile per quelle occasioni (una volta l'anno o più)
in cui decidete di offrire tutto il menù à la carte.

Vale ovunque: menu pubblico, pagina cliente da QR, pagina cameriere, e nel calcolo del conto.

## 25. Novità: "Giro d'uscita" — sincronizzare le portate in cucina

Serve una nuova migrazione:

```
python manage.py migrate
```

**Il problema che risolve**: un tavolo da 4 ordina 3 antipasti e un secondo (chi salta
l'antipasto). Quel secondo deve uscire insieme agli antipasti, non dopo.

**Come funziona:**

- Ogni piatto ordinato ha ora un **numero di "Giro"**, calcolato automaticamente
  dall'ordine delle categorie (Antipasti → giro 1, Primi → giro 2, ecc. — segue l'ordine
  che avete impostato in `/admin/menu_digitale/categoria/`)
- Nella pagina del tavolo (Sala → apri un tavolo), ogni riga ha ora una colonna **"Giro"**
  con un numero modificabile: basta cambiare il numero e premere ↻ per spostare quel piatto
  su un altro giro
- In **Cucina**, dentro la card di ogni tavolo, i piatti sono ora raggruppati per **Giro**
  (con l'etichetta "Giro 1", "Giro 2"...) invece che mescolati — è immediato vedere cosa
  deve uscire insieme

**Nota**: la richiesta di "avvisare il cameriere quando un piatto è pronto" non è stata
implementata — la gestite direttamente voi via comunicazione diretta in cucina/sala, come
discusso.

## 27. Novità importante: le portate del menù fisso si generano da sole

Nessuna nuova migrazione richiesta (usa il campo "portata" già aggiunto prima).

**Il problema che risolve**: con il menù fisso, il cameriere non deve più cercare e
aggiungere a mano "4 antipasti, 4 primi, 4 secondi, 4 dolci" — è già deciso cosa mangia
tutto il tavolo.

**Come funziona ora, in modalità "Solo menù fisso":**

- Il cameriere apre il tavolo e imposta solo il **numero di coperti** → il sistema crea da
  solo le righe delle portate standard (una per ogni categoria con un solo piatto fisso),
  con quantità = numero di coperti
- Se aumentano i coperti (arriva un altro commensale), aggiornando il numero le quantità
  salgono di conseguenza — **non scendono mai da sole**, quindi non si rischia di cancellare
  eccezioni già segnate
- Per le **eccezioni** (qualcuno non vuole più una portata): il cameriere abbassa il numero
  nella colonna **"Qtà"** della riga interessata, con la freccina ↻ per confermare
- Per gli **extra** (acqua, vino, caffè, o qualsiasi cosa "sempre visibile"): si aggiungono
  a mano come sempre, dal modulo in alto
- Se in una categoria ci sono **più piatti fissi a scelta** (es. 2 primi diversi inclusi nel
  menù), quella categoria NON si genera in automatico: il cameriere la gestisce a mano dal
  modulo in alto, inserendo quante persone hanno scelto ciascuna opzione

**Anche il cliente da QR cambia**, in modalità menù fisso: non vede più tutto il menù da
scegliere, ma solo un modulo per ordinare gli **extra** (bevande ecc.) — le portate sono già
previste per il tavolo.

**In modalità "Solo carta" o "Entrambi visibili"** tutto resta come prima: sia il cliente da
QR sia il cameriere scelgono e aggiungono ogni piatto a mano, uno per uno.

## 29. Riprogettazione: cucina e servizio separati, per giro intero

Serve una nuova migrazione:

```
python manage.py migrate
```

**Cosa cambia, ragionando come cuoco e cameriere:**

- Tolto lo stato "In preparazione" — inutile cliccarlo, il cuoco sa già cosa sta cucinando.
  Restano solo 3 stati: **In cucina → Pronto → Servito**
- **Cucina**: un solo pulsante **"Pronto — tutto il giro"** per l'intero gruppo di piatti
  di quel giro, non più un pulsante per ogni singolo piatto. Appena lo premi, quel giro
  sparisce dalla vista Cucina — il cuoco non deve più pensarci
- **Cameriere** (pagina del tavolo): ora è raggruppata per giro, con lo stato ben visibile.
  Quando un giro diventa "Pronto", compare il pulsante **"✅ Pronto — Segna servito"**: lo
  preme il cameriere quando lo consegna davvero al tavolo — è lui, non la cucina, a saperlo
  con certezza
- La colonna "Giro" per spostare un piatto (es. un secondo che deve uscire con gli
  antipasti) resta, ora si chiama "Sposta a giro" per chiarezza

## 31. Novità: aggiornamento automatico "intelligente" + badge tavoli pronti

Nessuna nuova migrazione richiesta.

**Auto-refresh**: le pagine **Sala**, **Cucina**, **pagina del tavolo** e **Area staff
(prenotazioni)** ora si ricaricano da sole ogni 15 secondi — non serve più premere F5.
Se in quel momento stai scrivendo in un campo (es. una nota), l'aggiornamento si mette in
pausa automaticamente e riprova ogni secondo finché non lasci il campo: **non si perde mai
nulla di quello che stai scrivendo**.

**Badge "pronto da ritirare" in Sala**: ogni tavolo con almeno un giro pronto mostra ora un
avviso arancione con il numero di giri in attesa di essere ritirati — prima bisognava
entrare in ogni tavolo (o andare in Cucina) per saperlo.

**Lasciato fuori per ora, come deciso insieme**: i prodotti dell'azienda agricola (verdura
ecc.) — li gestirete a voce o con un cartello, non serve metterli online.

## 33. Implementati anche i due punti minori dell'analisi precedente

Nessuna nuova migrazione richiesta.

- **Tempo di attesa in Cucina**: ogni piatto mostra ora da quanti minuti è in coda
  (es. "8 min"). Se supera i 15 minuti, la card diventa rossa — colpo d'occhio per capire
  cosa sta rallentando
- **Conferma visiva su ogni azione dello staff** (pagina tavolo): aggiungere un piatto,
  rimuoverlo, cambiare quantità/giro/nota, aggiornare i coperti, chiudere il conto — ognuna
  di queste azioni ora mostra un messaggio di conferma in alto (es. "Quantità aggiornata.",
  "Spostato al giro 1.") invece di ricaricare la pagina in silenzio

## 35. Novità: collegamento Prenotazioni ↔ Tavoli

Serve una nuova migrazione:

```
python manage.py migrate
```

**Come funziona:**

- Nella dashboard prenotazioni (Area staff), ogni prenotazione di oggi non ancora arrivata
  ha ora un piccolo selettore **"Tavolo..."** + pulsante **"Assegna"**
- Scegliendo un tavolo e premendo Assegna: si apre (o si aggancia a quello già aperto) il
  conto di quel tavolo, i **coperti si compilano da soli** con il numero di persone della
  prenotazione, la prenotazione passa allo stato **"Arrivata"** (resta visibile nello
  storico, non sparisce), e si viene portati direttamente alla pagina del tavolo
- Sulla pagina del tavolo, se è collegato a una prenotazione, compare un avviso con nome e
  contatti di chi ha prenotato
- Una prenotazione "Arrivata" mostra un pulsante **"Vai al tavolo"** per tornarci comodamente

Corretto anche un piccolo bug tecnico trovato per strada: in tre pagine (Cucina, pagina
tavolo, Dashboard prenotazioni) il blocco dell'auto-refresh era duplicato per errore — ora
sistemato.

## 37. Blocco novità: QR solo consultazione, Mappa tavoli, conferma onesta, suono avviso

Serve una nuova migrazione (due app coinvolte):

```
python manage.py migrate
```

### QR solo consultazione
Nuovo interruttore in **Menù → Impostazioni**: "Permetti ordini dal QR", **spento di default**.
Da spento, chi scansiona il QR del tavolo vede solo il menù/la carta, senza nessuna
possibilità di ordinare — solo consultazione. Il cameriere continua a gestire tutto
normalmente dalla pagina del tavolo. Riaccendibile in qualsiasi momento, stesso indirizzo QR.

### Mappa tavoli
Nuova voce **"Mappa tavoli"** nel menu Staff. Funziona così:
- **Vista normale**: i tavoli colorati (grigio=libero, verde=aperto, rosso con numero=pronti
  da ritirare) — clic su un tavolo apre la sua gestione, come dalla Sala
- **"Modifica disposizione"**: entra in modalità modifica — trascina i tavoli per
  posizionarli, clicca su un punto vuoto per aggiungere un angolo del perimetro della sala
  (funziona per qualsiasi forma, non solo rettangoli — utile per la futura sala con più
  pareti/zone), trascina i punti rossi per aggiustarli, "Salva disposizione" per confermare
- L'aggiornamento automatico si mette in pausa mentre sei in modalità modifica, così non
  perdi il lavoro fatto prima di salvare

### Messaggio di conferma onesto
La pagina dopo l'invio e l'email al cliente ora dicono chiaramente che la prenotazione
**non è ancora confermata** — la conferma arriva con una telefonata dello staff.

### Telefono obbligatorio
Nel form di prenotazione il telefono è ora sempre richiesto; l'email resta facoltativa.

### Suono di avviso
Su Cucina, Sala e pagina del tavolo, un "ding" avvisa quando c'è una novità rilevante
(nuovo piatto da preparare, un giro diventato pronto) — utile per accorgersene anche senza
guardare lo schermo. Nota: alcuni browser richiedono un primo tocco/clic sulla pagina prima
di poter riprodurre suoni — è una restrizione di sicurezza dei browser, non un difetto.

## 39. Blocco novità: conferma apertura, invia in cucina, extra separati, mappa migliorata

Serve una nuova migrazione (due app coinvolte):

```
python manage.py migrate
```

### Conferma prima di aprire un tavolo
Cliccando un tavolo **libero** (da Sala o Mappa), ora compare una pagina "Tavolo X è
libero. Vuoi aprirlo?" con un pulsante — sfogliare la mappa non occupa più tavoli per
sbaglio. Un tavolo già aperto continua ad aprirsi direttamente come prima.

### Blocco assegnazione a tavolo occupato
Dalla dashboard prenotazioni, se provi ad assegnare una prenotazione a un tavolo che ha
già un conto aperto, ora te lo impedisce con un avviso invece di mescolare i due gruppi.

### "Invia in cucina" — l'ordine non parte più da solo
Ogni piatto aggiunto (sia dall'automatismo del menù fisso sia a mano) resta ora in una
sezione **"📝 Da inviare"** sulla pagina del tavolo — modificabile con calma (note,
quantità, giro). Solo quando premi il pulsante **"📤 Invia in cucina"** tutto parte
davvero: i piatti delle categorie "cucina" vanno in Cucina, gli extra (vini/bibite/caffè)
saltano direttamente in una sezione **"🔔 Da consegnare"**.

### Categorie "Richiede cucina"
Da `/admin/menu_digitale/categoria/` ogni categoria ha ora un interruttore **"Richiede
cucina"** (acceso di default). Spegnetelo per Vini/Bibite/Caffè — i piatti dentro non
passeranno mai dalla vista Cucina, restando comunque nel conto e visibili nella sezione
"Da consegnare" del tavolo, con un pulsante "✅ Consegnato" per segnarli.

### Nuovo stato "Servizio completo"
Su Sala e Mappa, un tavolo con tutto già servito (ma conto non ancora chiuso) mostra ora
un badge scuro **"✅ Servizio completo"**, distinto dal verde "Aperto" di un tavolo ancora
in corso.

### Pulsante Cucina ridisegnato
"Pronto — tocca per segnare servito" ora ha uno stile diverso (arancione/rosso, non più
verde con spunta), per essere chiaramente un pulsante da premere e non un'etichetta di
qualcosa già fatto.

### Mappa: dimensione tavoli e "muri magnetici"
- I tavoli sulla mappa sono ora **dimensionati in base alla capienza** — un tavolo da 6
  è visibilmente più grande di uno da 2
- Disegnando il perimetro, trascinando un punto **si "aggancia" automaticamente** se ti
  avvicini ad essere allineato in orizzontale/verticale col punto vicino — molto più
  facile fare muri dritti

### Messaggi di errore colorati
Corretto un dettaglio: i messaggi di errore (es. "tavolo già occupato") ora appaiono in
rosso, non più con lo stesso azzurro di un messaggio normale.

### Testo home
Tolto "Lezioni a cavallo e" dalla card MD Ranch — resta solo "Battesimo della sella per
grandi e piccini" (le lezioni vere sono fuori dall'orario del servizio ristorante).

## 41. Video di presentazione e card cliccabili in home

Nessuna migrazione richiesta, ma questo zip è più pesante del solito (~15 MB in più) perché
contiene i due video.

- Le tre card della home (**Prodotti dell'azienda**, **Cucina genuina**, **MD Ranch**) sono
  ora cliccabili, con un piccolo effetto di sollevamento al passaggio del mouse
- **Prodotti dell'azienda** → apre una pagina dedicata con il video di presentazione
  dell'azienda agricola e i pulsanti Instagram/Facebook
- **MD Ranch** → stessa cosa, con il video del maneggio e i suoi social
- **Cucina genuina** → per ora porta al menù pubblico (non c'è ancora un video dedicato
  alla cucina — se un giorno lo girate, lo aggiungiamo con la stessa struttura)
- I video sono in `static/video/` — per sostituirli con video veri in futuro, basta
  rimpiazzare i due file mantenendo lo stesso nome (`azienda_agricola.mp4`,
  `md_ranch.mp4`) e ricaricare

## 43. Correzioni "anti-errore" e rifiniture

Nessuna migrazione richiesta.

### ⭐ Le note si salvano da sole (la più importante)
Prima, se il cameriere scriveva una nota e dimenticava di premere ↻, la nota si perdeva
inviando la comanda. **Ora**: quantità, giro e note si salvano **da sole** appena esci dal
campo — nessun pulsante da premere. In più, per doppia sicurezza, il pulsante "Invia in
cucina" raccoglie comunque tutte le note scritte in quel momento, anche se non fossero
ancora state salvate. Impossibile perdere una nota.

### Note molto più visibili in Cucina
Le note ora appaiono in un riquadro giallo con bordo e icona ⚠️, non più come una riga di
testo qualsiasi — impossibile non vederle durante il servizio.

### Mappa: tavoli con dimensioni davvero diverse
Nuova scala a scaglioni, come tavoli affiancati: 2-3 posti = un tavolo, 4-5 = largo il
doppio, 6-7 = il triplo, 8+ = il quadruplo. La differenza ora è evidente a colpo d'occhio.

### Mappa: punti del perimetro più facili da spostare
I punti rossi sono ora molto più grandi (30px invece di 16px) e — soprattutto — corretto un
difetto per cui a volte "si bloccavano" durante il trascinamento: il ridisegno continuo
interrompeva il movimento. Ora si spostano sempre fluidamente.

### Dashboard prenotazioni più leggibile
Resta una tabella (come richiesto) ma molto più curata: righe più spaziose, orario in
evidenza, contatti e note raccolti sotto il nome del cliente, badge "Lezione a cavallo",
azioni allineate a destra, il tutto dentro una card con bordo e ombra.

## 45. Audit finale — correzioni critiche e nuove funzionalità

Due nuove migrazioni:

```
python manage.py migrate
```

### Correzioni critiche (audit)
- **Prezzo menù fisso congelato** all'apertura del tavolo: cambiarlo a metà servizio non
  altera più i conti già aperti (prima li ricalcolava retroattivamente!)
- **Storno righe già inviate**: pulsante "Storna" su ogni piatto già mandato in cucina —
  prima un errore restava sul conto per sempre. Se il piatto è già in preparazione, avvisa
  di dirlo anche alla cucina di persona
- **Tempo di attesa cucina corretto**: parte dall'invio, non da quando il cameriere ha
  iniziato a comporre la comanda
- **Avviso alla chiusura conto** se ci sono voci non ancora servite
- Corretti: pulsante "Rimuovi" fragile, QR rotti con numeri tavolo contenenti spazi,
  errori 500 sul salvataggio mappa, lentezza con molti tavoli aperti

### 🧾 Preconto stampabile (nuovo)
Pulsante **"Preconto"** sulla pagina del tavolo: apre un foglio pronto da stampare con
logo, contatti, elenco consumazioni e totale. Include un campo **"Dividi il conto tra N"**
per la divisione alla romana, con l'importo a testa calcolato.

⚠️ **Importante**: è un documento di cortesia, **non uno scontrino fiscale** — quello va
sempre emesso a parte con il registratore di cassa, come richiesto dalla legge.

### 🔄 Conti chiusi e riapertura (nuovo)
Nuova voce **"Conti chiusi"** nel menu Staff: elenco dei conti chiusi oggi, con il totale
incassato in giornata a colpo d'occhio. Ogni conto ha:
- **"Vedi conto"** — ristampa il preconto
- **"Riapri"** — rimette il tavolo in servizio esattamente com'era (utile se chiuso per
  errore). Bloccato se quel tavolo ha già un altro conto aperto. Le riaperture restano
  tracciate ("riaperto 1×") per non perdere lo storico

### ⏱️ Soglia ritardo cucina configurabile (nuovo)
Da **Menù → Impostazioni**: quanti minuti prima che un piatto venga evidenziato in rosso
in Cucina (prima era fisso a 15). Alzatelo se durante il servizio l'allarme scatta troppo
spesso — un allarme che suona sempre viene ignorato.

## 47. Via libera cucina, colori sala, prenotazioni completate

Due nuove migrazioni:

```
python manage.py migrate
```

### 🟢 Via libera manuale per ogni giro (anche il primo)
"Invia in cucina" non fa più partire nulla da solo: ogni giro, **compreso il primo**,
resta nello stato **"Previsto"** finché il cameriere non preme il pulsante dedicato
**"🟢 Via libera cucina"** sulla pagina del tavolo. La cucina vede comunque tutto
l'ordine fin da subito (per organizzarsi), ma i giri "Previsti" sono mostrati attenuati,
senza cronometro e senza pulsante — il cuoco sa a colpo d'occhio cosa può già iniziare e
cosa no.

### 🏠 Pulsante "Torna alla Sala"
Ben visibile in cima alla pagina del tavolo, accanto al numero — non serve più scorrere
fino in fondo.

### 🎨 Sala e Mappa: 5 colori invece di 3
Nuovi stati distinti: **libero** (grigio), **aperto senza ordini** (blu), **in cucina**
(ambra), **pronto da ritirare** (rosso, invariato), **servizio completo** (antracite,
invariato). Sala e Mappa mostrano anche il **numero del giro** in corso accanto al colore.

### 👨‍🍳 Riepilogo sala nella schermata Cucina
In cima alla pagina Cucina, una striscia compatta con lo stato colorato di tutti i
tavoli (stessa legenda di Sala/Mappa) — il cuoco vede il colpo d'occhio della sala senza
cambiare pagina.

### 📋 Prenotazioni: nuovo stato "Completata"
Quando il conto collegato a una prenotazione viene chiuso, la prenotazione passa da sola
a **"Completata"** — resta visibile nell'elenco di oggi (utile per il riepilogo di fine
serata) ma chiaramente distinta, senza più pulsanti d'azione. Se il conto viene riaperto
per errore, torna "Arrivata" in automatico.

## 49. Struttura a due livelli: Giro + Step (menù degustazione)

Nuova migrazione:

```
python manage.py migrate
```

Per i menù degustazione, dove lo stesso giro può avere più portate in sequenza per la
stessa persona (es. due secondi diversi), ogni piatto ha ora — oltre al **Giro** — anche
uno **Step** (sotto-passo), modificabile nella sezione "Da inviare" della pagina tavolo
esattamente come il giro.

**Come funziona in pratica:**
- Lasciando Step = 1 su tutto (il caso normale, quasi sempre), **non cambia nulla**: si
  vede "Giro 2" come sempre
- Se invece due piatti dello stesso Giro hanno Step diversi (es. Step 1 e Step 2), il
  sistema li tratta come **due sotto-passi indipendenti**, ciascuno con il proprio via
  libera e il proprio "Pronto" — e li mostra ovunque come **"Giro 2.1"**, **"Giro 2.2"**
  (in Sala, Mappa, Cucina, pagina tavolo) invece del semplice "Giro 2"

**Cucina**: ogni sotto-passo ancora "Previsto" (non chiamato) è mostrato con **opacità
ridotta al 50% e sfondo desaturato**, senza pulsante — visivamente "congelato". Appena il
cameriere dà il via libera, il sotto-passo si accende con un **bordo verde acceso** e
compare il pulsante "Pronto".

**Suono corretto**: prima scattava solo quando arrivava un ordine nuovo — ora scatta
anche (anzi, soprattutto) quando il cameriere dà il via libera a un giro, il momento in
cui la cucina deve davvero accorgersene.

## 51. Correzione: controllo per singolo piatto, non più per giro/step

Nuova migrazione (rimuove il campo "step" appena introdotto, non serve più):

```
python manage.py migrate
```

Dopo un confronto con l'uso reale (esempio concreto: due secondi diversi nello stesso
giro, dove uno resta pronto sotto le lampade ad aspettare l'altro), la struttura
Giro+Step del punto precedente è stata **sostituita** con qualcosa di più semplice e più
corretto per come funziona davvero un servizio:

- **Il "Giro"** (Antipasti, Primi, Secondi...) resta solo un'**etichetta di
  orientamento** — non controlla più nulla
- **Il via libera e il "Pronto" sono sempre per singolo piatto**, non per l'intero giro:
  se nello stesso giro ci sono due piatti diversi (es. Spigola e Filetto), ciascuno ha il
  suo pulsante indipendente. Un piatto ripetuto per più persone (es. "6x Tagliere")
  resta comunque un'unica riga con un unico pulsante — è davvero una sola preparazione
- **Zero configurazione in più** rispetto a prima: non c'è nessun numero da impostare da
  nessuna parte, il sistema è già granulare per natura (una riga = un piatto)

**In Cucina**: ogni piatto ancora "Previsto" (non attivato) è mostrato attenuato al 50%,
senza pulsante. Appena il cameriere dà il via libera (dalla pagina del tavolo, pulsante
"🟢 Via libera" su quel piatto), la card si accende con **bordo verde acceso**, parte il
cronometro, e compare il pulsante "✅ Pronto" — sempre riferito solo a quel piatto.

**Sulla pagina del tavolo**: ogni riga della tabella ha ora la sua colonna "Stato" con
il pulsante giusto (Via libera / In cucina / Pronto — consegna / Servito).

## 53. Rifiniture dopo il primo test con più tavoli

Nuova migrazione:

```
python manage.py migrate
```

### 🔥 Cucina riorganizzata in due zone — il cambio più importante
Prima, ogni piatto (anche quelli ancora "in attesa del via libera") occupava una card
grande quanto quelli davvero da cucinare — con tanti tavoli diventava un muro di scroll
infinito. Ora:
- **"🔥 Da cucinare ora"**: solo i piatti attivi (via libera già dato), grandi, ordinati dal
  più vecchio al più recente — la vera coda di lavoro, di solito poche card anche a sala
  piena
- **"⏳ In arrivo"**: i piatti ancora "Previsti", raccolti in un elenco compatto **per
  tavolo**, richiudibile (clicca sul nome del tavolo per aprire/chiudere) — restano
  visibili per organizzarsi in anticipo, ma senza occupare lo schermo come prima

### 🔊 Suono più forte e riconoscibile
Volume al massimo, tono più "squillante" (onda quadra invece che morbida), ripetuto tre
volte — pensato per un ambiente rumoroso.

### 🎨 Nuovo colore "Appena servito"
Quando un piatto viene consegnato, il tavolo mostra per **4 minuti** un colore dedicato
(verde-acqua) in Sala, Mappa e nella striscia di Cucina — poi torna da solo allo stato
normale. Conferma visiva che la consegna è andata a buon fine, senza dover scrivere nulla
(lo spazio nei quadratini è troppo piccolo per il nome del piatto, e la lista ordini è già
lì accanto per chi vuole il dettaglio).

### 🔘 Pulsanti che sembrano davvero pulsanti
I pulsanti d'azione (Via libera, Pronto, Consegnato, Invia in cucina) ora hanno un aspetto
"in rilievo" (bordo/ombra, si "premono" visivamente al tocco) — chiaramente diversi dai
badge informativi (Servito, In cucina), che restano piatti e senza ombra. A colpo d'occhio
si distingue cosa richiede un tocco da cosa è solo da leggere.

## 55. Blocco grande: Menù multipli, Coperto, Conto alla romana

⚠️ **Tre nuove migrazioni**, e questa volta è un cambiamento importante nella struttura:

```
python manage.py migrate
```

La prima volta, la migrazione crea automaticamente un **"Menù Principale"** con dentro
tutto quello che avevate già configurato (categorie, piatti, modalità, prezzo del fisso)
— non perdete nulla, non dovete ricreare niente a mano.

### 📅 Menù multipli (il cambiamento più grande)
Ora potete avere **più edizioni di menù** nello stesso sistema (es. "Menù di Agosto",
"Cena a tema Halloween"), tutte gestite da **/admin/ → Menù**:
- Ogni Menù ha nome, descrizione, date **informative** (non attivano nulla da sole),
  modalità (fisso/carta/entrambi) e prezzo del fisso — **tutti campi propri di ogni
  edizione**, non più globali
- Solo **un Menù alla volta è "Attivo"** — quello usato davvero per cucina/QR/ordini.
  Attivandone uno, quello prima si spegne da solo (mai due attivi insieme)
- I Menù **non scadono mai da soli** e non si cancellano: restano pronti per essere
  riattivati quando tornano di stagione
- Nuova pagina pubblica **"Tutti i menù"** (link in home e nel menù di navigazione):
  i clienti vedono anche le edizioni non ancora attive, con le loro date previste — utile
  per farli prenotare apposta per un menù che gli piace di più
- Il QR al tavolo resta come sempre scoped al solo menù di stasera, con un link in più
  verso questa pagina

**Protezione anti-errore** (stesso principio già usato per il prezzo): modalità e
edizione di menù vengono **congelate all'apertura di ogni tavolo**. Se cambiate menù
attivo a metà servizio, i tavoli già aperti continuano regolarmente con quello che
avevano all'inizio — nessun conto cambia sotto gli occhi del cliente.

**Impostazioni generali** (`/menu/impostazioni/`) ora contiene solo QR, soglia ritardo
cucina e coperto — tutto il resto si gestisce da /admin/ → Menù.

### 🍞 Coperto
Nuovo interruttore + importo nelle Impostazioni generali (unico per tutti i menù):
- **Menù fisso**: mai una voce a parte — sotto il prezzo compare "Coperto incluso"
- **Carta / Entrambi visibili**: si aggiunge come voce separata nel conto e sul preconto
  ("Coperto ×N: €X")

### 🍽️ Conto alla romana
Solo quando la modalità è **"Solo carta"**, sul preconto compare il pulsante **"Dividi
alla romana"**: apri il calcolatore, aggiungi le persone, assegni quante unità di ogni
piatto tocca a ciascuno — il subtotale (coperto compreso) si calcola da solo in tempo
reale. Nessuna modifica al database: è solo uno strumento al momento del conto, il modo
di ordinare resta identico a sempre.

## 57. Correzione: Categorie condivise, Piatti in più menù, e bug del coperto

⚠️ **Tre nuove migrazioni**, un'altra ristrutturazione dei dati:

```
python manage.py migrate
```

La migrazione dati unisce automaticamente eventuali categorie doppie con lo stesso nome
create per menù diversi (es. due "Antipasti" separate), spostando tutti i piatti sulla
categoria superstite — non serve alcun intervento manuale.

### 🗂️ Categorie di nuovo condivise
Le categorie (Antipasti, Primi, Secondi, Dolci...) sono di nuovo **globali**, create una
volta sola — coerente con come funziona davvero un menù: la struttura resta la stessa,
cambiano solo i piatti.

### 🍽️ Un piatto può stare in più menù, con tipo diverso in ciascuno
Ogni Piatto (nome, prezzo, descrizione — **sempre gli stessi ovunque**) può ora essere
collegato a **più edizioni di Menù contemporaneamente**, e in **ognuna può avere un tipo
diverso** (fisso in un'edizione, alla carta in un'altra) — utile per non dover ricreare lo
stesso piatto più volte. Nella scheda del Piatto su /admin/, in basso trovi la sezione "In
quali menù compare, e con che tipo in ciascuno" per gestirlo.

**Protezione anti-errore** (stesso principio di prezzo/modalità): il tipo di un piatto
viene **congelato quando finisce nel conto**, non ricalcolato dal vivo — se cambiate il
tipo di un piatto dopo, i conti già aperti non cambiano.

### 🍞 Corretti due problemi sul coperto
- Il coperto ora compare correttamente anche nel menù **alla carta/entrambi visibili**
  (prima si vedeva solo nel fisso — bug confermato e sistemato)
- Nelle Impostazioni generali, il campo del prezzo del coperto **compare solo quando
  spunti "Applica il coperto"**, per non fare confusione

## 59. Semplificazione: niente più "tipo" da scegliere piatto per piatto

⚠️ **Cinque nuove migrazioni** (tre su menu_digitale, due su ordini) — questa volta il
cambiamento va nella direzione di **togliere** complessità, non aggiungerla:

```
python manage.py migrate
```

Il flusso per creare un nuovo menù ora è quello più semplice che ci si aspetterebbe:

1. **Categorie** (Antipasti, Primi, Secondi, Vini...) — condivise, create una volta sola,
   invariato
2. **Piatti** — assegni la categoria, invariato. **Niente più "tipo" da scegliere**: quello
   è sparito del tutto
3. **Crei un Menù** — scegli il nome, se è **fisso o alla carta**, e poi (da
   `/admin/menu_digitale/menu/`) trovi un **elenco a doppia colonna con checkbox**: a
   sinistra tutti i piatti disponibili, a destra quelli scelti per questo menù — sposti con
   un clic o cerchi per nome

Il tipo di ogni piatto **lo eredita in automatico dal Menù in cui lo metti**: se il menù è
fisso, quel piatto lì dentro è fisso; se è alla carta, è alla carta. Lo stesso piatto può
stare in più menù contemporaneamente, anche con comportamento diverso in ciascuno, senza
nessuna selezione in più.

**L'unica eccezione**: Vini/Bibite/Caffè, che devono restare sempre a prezzo singolo anche
in un menù fisso. Ora è un interruttore sulla **Categoria** (non più sul piatto):
`/admin/menu_digitale/categoria/` → spunta **"Sempre a prezzo singolo"** per quella
categoria, una volta sola, vale per tutti i menù.

## 61. Bevande automatiche, extra a pagamento, Sala a bottoni

⚠️ Due nuove migrazioni (una per menù_digitale, non serve stavolta perché il cambiamento
è solo nella logica; una per ordini):

```
python manage.py migrate
```

### 🥤 Vini/Bibite compaiono da soli in ogni menù
Le categorie marcate **"Sempre a prezzo singolo"** (da `/admin/menu_digitale/categoria/`)
ora compaiono **automaticamente in ogni edizione di menù**, senza bisogno di spuntarle una
per una. L'unico modo di escludere un piatto è segnarlo **"Non disponibile"** sulla sua
scheda (es. la Coca Cola finita) — sparisce ovunque, subito.

### ➕ Extra a pagamento nel menù fisso
Corretto un bug reale: se durante una cena a menù fisso il cliente chiedeva un secondo
piatto in più (es. un'altra Panna Cotta), il sistema lo inseriva ma **non lo contava nel
conto** (il totale del fisso è una cifra fissa a persona, indifferente alle quantità).

Ora sulla pagina del tavolo c'è un pulsante dedicato **"➕ Extra (a pagamento)"**: qualsiasi
cosa aggiunta da lì **si paga sempre a parte**, anche con il menù fisso, e compare sul
preconto come voce separata con l'etichetta "(a pagamento)".

### 🍽️🥤 Sala: pulsanti grandi al posto del menù a tendina
Il vecchio modulo con la tendina unica (cibo e bevande mischiati) è sparito. Al suo posto,
tre pulsanti grandi che aprono una finestra a schermo intero:
- **🍽️ Aggiungi cibo** — solo le portate
- **🥤 Aggiungi bevanda** — solo vini/bibite/caffè
- **➕ Extra (a pagamento)** — solo cibo, sempre fatturato a parte

Ogni piatto è un bottone grande, raggruppato per categoria — **nessuna barra di ricerca**,
si vede tutto a colpo d'occhio. Toccando un piatto si aggiunge subito (i tocchi ripetuti
sullo stesso piatto si sommano, non creano righe doppie) e la finestra **si riapre da
sola**, pronta per il piatto successivo, senza doverla riaprire ogni volta a mano.

## 63. Blocco grande: Vini/Dolci/Bevande, Menù bambini, restyling menù pubblico

⚠️ **7 nuove migrazioni** (4 menu_digitale, 2 ordini, 1 prenotazioni) — il blocco più ricco
di funzionalità nuove finora:

```
python manage.py migrate
```

### 🗑️ Rimossa "Entrambi visibili"
Non serviva più (si comportava identica a "Solo carta" dopo le ultime semplificazioni) e
generava confusione. Restano solo "Solo menù fisso" e "Solo carta". Eventuali menù già
impostati su "Entrambi" vengono convertiti automaticamente a "Carta" dalla migrazione.

### 🍷🍰☕ Vini, Dolci, Bevande — pagine dedicate
Ogni Categoria ha ora un **"Ruolo nel menù"**: Portata (resta nella pagina principale),
Vini, Dolci, o Bevande (comprende caffè e digestivi). Potete continuare a dividere i vini
in più categorie (Rossi, Bianchi, Bollicine...): basta segnarle tutte con ruolo "Vini",
compariranno raggruppate nella stessa pagina.

La pagina principale del menù ora mostra **solo le Portate**, con tre pulsanti in fondo
che portano a pagine dedicate — **"Carta dei Vini"**, **"I Nostri Dolci"**,
**"Bevande & Caffetteria"** — curate con lo stesso stile del resto del sito. Anche il
link "guarda i menù futuri" è diventato un vero pulsante invece di un semplice link.

### 🎨 Restyling del menù principale
Colonna più stretta e centrata, ogni piatto con testo centrato (non più nome-a-sinistra
prezzo-a-destra), una **cornice sottile a doppio bordo** con piccoli ornamenti a foglia
negli angoli — la sensazione di una vera carta del menù stampata con cura. Applicato sia
alla pagina pubblica sia a quella mostrata dal QR al tavolo.

### 👶 Menù bambini
Per le edizioni a menù fisso: un percorso **completamente dedicato**, con piatti propri
e prezzo proprio.
- Si gestisce da `/admin/menu_digitale/menu/` (scheda del Menù): interruttore
  **"Menù bambini attivo"** (acceso di default appena il menù è fisso, disattivabile per
  singola edizione), prezzo a persona, e l'elenco a doppia colonna con checkbox per
  scegliere quali piatti ne fanno parte
- Riepilogo/gestione rapida anche da **Impostazioni** (staff), senza dover sempre passare
  da /admin/
- **In prenotazione**: nuovo campo "Di cui bambini" (sempre visibile) e "Seggioloni
  richiesti" (compare solo se ci sono bambini) — utile alla sala per organizzarsi, a
  prescindere da quale menù sarà attivo quel giorno
- **Alla pagina del tavolo**: nuovo campo "di cui bambini" (visibile solo se il menù
  bambini è attivo per quell'edizione) — genera in automatico le portate bambini,
  esattamente come già succede per gli adulti col fisso
- **Prezzo congelato** all'apertura del tavolo, stessa protezione anti-errore già usata
  per il resto (cambiare il prezzo a metà servizio non altera i conti aperti)
- **Preconto**: adulti e bambini mostrati come righe separate, ciascuno al proprio prezzo

## 65. Tre correzioni dopo i test dal vivo

Nessuna nuova migrazione — solo logica e visualizzazione.

### ✓ Casellina "Servito Gx" persistente
Quando un giro viene consegnato mentre un altro è ancora in cucina, il colore/testo del
tavolo passava subito al giro attivo, facendo sparire l'informazione "il Giro 1 è stato
consegnato". Ora una nuova casellina indipendente (sotto il riquadro principale, sia in
Sala che nella striscia Cucina) mostra **"✓ Servito G1"** — e a differenza del colore
"Appena servito" delle bevande, **non scade a tempo**: resta finché non viene consegnato
anche il giro successivo (tra una portata e l'altra può passare più di qualche minuto,
l'informazione resterebbe comunque vera).

### 👶 Menù bambini finalmente visibile
Bug corretto: avevamo costruito tutta la parte gestionale ma dimenticato di mostrarlo ai
clienti. Ora, quando è attivo, compare **direttamente nella pagina principale del menù**
(non dietro un pulsante come Vini/Dolci/Bevande — è un'informazione che chi prenota o è
già al tavolo vuole vedere subito): un riquadro dedicato "👶 Menù Bambini" con il prezzo e
l'elenco dei piatti, sia nel menù pubblico sia in quello mostrato dal QR.

### 🎨 Prezzi senza badge rosso
I prezzi accanto a ogni piatto (menù portate, Vini, Dolci, Bevande) non hanno più lo
sfondo colorato acceso — solo testo semplice ed elegante, coerente con lo stile "carta
scritta a mano" della cornice sottile. Il banner del prezzo del menù fisso in alto resta
invece con il suo risalto: è un annuncio unico, non un'etichetta ripetuta su ogni riga.

## 67. Stato "Previsto" separato, Posti rimasti, capienza in Sala, tavoli ruotabili

⚠️ **1 nuova migrazione** (solo `prenotazioni`, il campo `ruotato` sul Tavolo):

```
python manage.py migrate
```

### 🟡 "Previsto" e "In preparazione" finalmente distinti ovunque
Il colore arancione "In cucina" veniva usato sia per i giri ancora in attesa del via
libera sia per quelli davvero partiti — fuorviante, l'hai segnalato giusto guardando la
Sala. Ora sono due stati distinti, con colore diverso, coerenti in **Sala, Mappa e
striscia Cucina**:
- **Giallo/oro "Previsto"**: "⏳ In attesa del via libera · Giro X" — il cameriere non ha
  ancora dato il via, la cucina non deve muoversi
- **Arancione "In preparazione"** (rinominato da "In cucina"): via libera già dato, il
  cuoco ci sta davvero lavorando

`Ordine.stato_sala` ora riusa la stessa logica già usata per il testo del giro
(`giro_in_evidenza`), invece di ricalcolarla separatamente — colore e testo non potranno
più disallinearsi in futuro.

### 📊 Posti rimasti per data
Nuova pagina staff (menu Staff → **"Posti rimasti"**): scegli una data, vedi posti totali,
già prenotati, e liberi stimati. È una stima semplice (capienza totale meno coperti
prenotati quel giorno) — non tiene conto di eventuali doppi turni sullo stesso tavolo
nella stessa sera, per un servizio a turno unico va benissimo.

### 🪑 Capienza visibile in Sala
Sotto il numero di ogni tavolo, ora si legge quanti posti ha ("4 posti").

### ⟲ Tavoli ruotabili sulla Mappa
In modalità "Modifica disposizione", ogni tavolo ha ora un piccolo pulsante **"⟲"** che lo
ruota (scambia larghezza/altezza) — utile per un tavolo grande da posizionare di traverso
rispetto agli altri. La rotazione si salva insieme alla posizione.

## 68. Prossimo passo

Rimane il modulo **Prodotti dell'azienda agricola** (verdura e prodotti ordinabili), da
aggiungere seguendo la stessa struttura.
