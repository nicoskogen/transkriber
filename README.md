# Transkriber

Norsk tale til tekst for Claude Code. Du gir den et lyd- eller videoopptak og
velger hva du vil ha ut:

| Du får | Fil | Passer til |
|---|---|---|
| Møtereferat | `<navn>-referat.md` | Beslutninger, todos og tematisk sorterte notater |
| Ren transkripsjon | `<navn>.txt` og `.vtt` | Alt som ble sagt, uten tolkning |
| Undertekster | `<navn>.srt` | Import rett i redigeringsprogrammet |

Transkriberingen kjører på din egen maskin, så lyden lastes aldri opp noe sted.
Referatet skrives av Claude Code i økten din, på Pro- eller Max-abonnementet du
allerede har. Da er det ingen API-nøkkel å holde styr på, og ingen kostnad per
opptak.

Video går rett inn. Du trenger ikke eksportere lyd fra `.mp4` eller `.mov`
først.

## Hvorfor NB-Whisper

Generisk Whisper er 2–3 ganger dårligere på norsk. Ordfeilrate:

| Modell | NST bokmål | Common Voice nynorsk |
|---|---|---|
| NB-Whisper Large | 2,2 % | 12,6 % |
| Whisper large-v3 | 6,8 % | 30,0 % |

Forskjellen er størst på dialekt, og det er nettopp der generiske modeller
svikter. NB-Whisper er trent av Nasjonalbiblioteket på 66 000 timer norsk tale
med ekte dialekter og begge målformer.

## Krav

- Mac med Apple Silicon
- [Homebrew](https://brew.sh)
- Claude Code, innlogget med Pro- eller Max-abonnement
- Rundt 1,5 GB ledig plass

## Installasjon

### Har du aldri brukt Claude Code?

Du trenger ikke installere noe nytt, og du trenger ikke terminalen. Claude Code
ligger inne i Claude-appen du allerede har.

1. Åpne Claude-appen.
2. Velg **Code** i sidemenyen. Det er en egen del av appen, ved siden av chat
   og Cowork.
3. Lim inn denne setningen:

   > Installer transkriber-pluginen fra github.com/nicoskogen/transkriber, og
   > kjør oppsettet etterpå.

4. Claude gjør resten og sier fra når du må starte appen på nytt.

Det må skje under **Code**. Vanlig chat har ingen tilgang til maskinen din, og
Cowork har et eget pluginsystem som dette ikke ligger i. Begge deler vil bare
svare at de ikke får det til.

### Kommandoene, hvis du foretrekker det

```
/plugin marketplace add nicoskogen/transkriber
/plugin marketplace add floka-as/floka-marketplace
/plugin install transkriber
/transkriber-setup
```

Start Claude Code på nytt etterpå, slik at pluginen lastes.

`/transkriber-setup` installerer `whisper-cpp` og `ffmpeg` via Homebrew, laster
ned modellen på 1 GB til `~/.cache/nb-whisper/`, sjekker kontrollsummen og
tester til slutt at alt virker. Det tar noen minutter, og du gjør det bare én
gang.

Den andre katalogen er der for
[`humanizer`](https://github.com/Floka-as/floka-marketplace/tree/main/humanizer),
som vasker språket i referatet. Den installeres automatisk som avhengighet, men
Claude Code henter ikke plugins fra en katalog du ikke har lagt til selv.

Du trenger ikke klone noe, og ingen HuggingFace-token er involvert. Blandet
norsk og engelsk bruker `python3` som allerede ligger på maskinen sammen med
utviklerverktøyene Homebrew krever, uten ekstra pakker.

## Bruk

Du trenger ikke opprette noe prosjekt eller noen mappe. Pluginen bryr seg ikke
om hvor Claude Code er åpnet, og legger resultatet ved siden av opptaket
uansett.

```
/transkriber ~/Downloads/mote.m4a
```

Claude spør hva du vil ha ut, og om opptaket er bare norsk eller norsk og
engelsk. Sier du det med én gang, slipper du spørsmålene:

> lag undertekster av intervjuet som ligger på skrivebordet

Alle formater ffmpeg kan lese fungerer, både lyd og video: `m4a`, `mp3`, `wav`,
`aiff`, `mp4`, `mov`, `mkv`. Opptak fra Teams, Zoom, Meet eller en telefon som
lå på bordet går like fint.

En time med opptak tar omtrent 10–20 minutter på en M1 Pro. Resultatet
mellomlagres, så ber du om det samme igjen, kommer svaret med én gang.

### Undertekster

Linjene deles på omtrent 42 tegn og brytes på hele ord, som er vanlig
kringkastingsstandard. Filen er alminnelig SRT og kan importeres rett i
Premiere, Resolve, Final Cut og alt annet som leser undertekster.

Underteksten språkvaskes ikke. Den skal gjengi det som faktisk ble sagt, ellers
stemmer den ikke med lyden.

### Norsk og engelsk om hverandre

Svarer du «norsk og engelsk» på språkspørsmålet, blir hver del skrevet på sitt
eget språk. Med «bare norsk» blir engelsk tale oversatt til norsk, eller den
forsvinner.

Det krever en ekstra modell på 190 MB. Første gang du velger norsk og engelsk,
spør Claude om den skal lastes ned. Du kan også hente den på forhånd med
`/transkriber-setup --blandet`.

Språket avgjøres per bit av talen, ikke per ord. Et engelsk ord midt i en norsk
setning blir derfor gjengitt som før. Det koster også et ekstra pass over de
engelske delene. Er det meste av møtet på engelsk, tar det omtrent tre ganger
så lang tid som vanlig.

## Slik virker det

```
lyd/video ──► ffmpeg ──► whisper.cpp + NB-Whisper ──► .txt / .vtt / .srt
              16k mono     lokalt, Metal-akselerert          │
                                                              ▼
                                      Claude Code leser den i økten (kun referat)
                                                              ▼
                                                        referat.md
```

Transkriberingen er et lokalt bash-steg. Ren transkripsjon og undertekster
stopper der. Bare referatet går videre til Claude Code, som allerede er
autentisert med abonnementet ditt, og det er derfor ingen API-nøkkel dukker opp
noe sted i kjeden.

## Begrensninger

Referatet skiller ikke mellom talere. Det forteller hva som ble sagt, ikke hvem
som sa det, med mindre navn nevnes i samtalen. Å legge det til ville dratt inn
Python, PyTorch og en tilgangsstyrt modell fra HuggingFace, og det er ikke verdt
det for noe bare enkelte har bruk for.

Engelske produktnavn blir dårlig gjengitt. Modellen er trent på norsk, så vanlig
norsk er til å stole på, mens engelske låneord og merkenavn som regel må rettes
for hånd. Det merkes særlig på undertekster.

Les gjennom resultatet før du bruker det. Talegjenkjenning svikter fremdeles ved
kryssprat og dårlige mikrofoner. I referatet er passasjer modellen var usikker
på merket `[uklart]`, men det fanger ikke alt.

Du må kjøre det selv. Ingenting plukker opp møter automatisk, siden uovervåket
kjøring ville krevd API-tilgang og dermed en egen API-nøkkel utenfor
abonnementet.

Foreløpig virker det bare på macOS med Apple Silicon.

Hvor mikrofonen står betyr mer for resultatet enn hvilken modell du velger. Et
opptak fra en mikrofon på bordet blir merkbart bedre enn en laptop i andre enden
av rommet.

## Kreditering

- [NB-Whisper](https://huggingface.co/NbAiLab/nb-whisper-large),
  Nasjonalbiblioteket, Apache 2.0
- [whisper.cpp](https://github.com/ggerganov/whisper.cpp), MIT
- [humanizer](https://github.com/Floka-as/floka-marketplace/tree/main/humanizer),
  Floka AS, MIT

## Lisens

MIT
