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

## 38. Prossimo passo

Rimane il modulo **Prodotti dell'azienda agricola** (verdura e prodotti ordinabili), da
aggiungere seguendo la stessa struttura.
