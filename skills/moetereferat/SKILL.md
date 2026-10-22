---
name: moetereferat
description: Strukturer en norsk møtetranskripsjon til et referat med sammendrag, tematisk sorterte notater, beslutninger og todos. Brukes når en rå transkripsjon skal bli et lesbart dokument.
---

# Møtereferat

Du får en rå transkripsjon fra NB-Whisper. Den er kronologisk, uten tegnsetting
mange steder, uten avsnitt, og uten markering av hvem som snakker. Jobben din er
å gjøre den om til et dokument noen faktisk kan lese og handle på.

Den viktigste operasjonen er **omorganisering**. Et møte hopper fram og tilbake
mellom temaer; et referat gjør det ikke. Samle alt som hører til samme sak på
ett sted, uansett hvor spredt det ligger i transkripsjonen.

## Format

````markdown
# Referat — {kort, beskrivende tittel utledet fra innholdet}

**Kilde:** {lydfilnavn}
**Dato:** {fra innholdet hvis det nevnes, ellers filens dato}
**Varighet:** {hvis kjent}

## Sammendrag

{3–5 setninger. Hva handlet møtet om, og hva kom ut av det. Skal kunne leses
alene av noen som ikke var til stede.}

## Tema

### {Tema 1}
{Hva ble sagt, samlet og sammenhengende. Prosa eller punktliste — det som
passer innholdet. Ikke gjenfortell ordrett; komprimer til det som betyr noe.}

### {Tema 2}
…

## Beslutninger

- {Hva som ble bestemt, ikke hva som ble diskutert. Én linje per beslutning.}

## Todos

| Oppgave | Ansvarlig | Frist |
|---|---|---|
| {konkret handling} | {navn, eller tomt} | {dato, eller tomt} |

## Åpne spørsmål

- {Ting som ble tatt opp uten å bli avklart, og som noen må følge opp.}
````

Utelat en seksjon helt hvis den er tom. Et referat uten beslutninger skal ikke
ha en tom «Beslutninger»-overskrift.

## Regler

**Skriv på norsk, i samme målform som transkripsjonen.** NB-Whisper skriver
normalisert bokmål eller nynorsk. Følg det den bruker.

**Transkripsjonen kan blande norsk og engelsk.** Skriv referatet på norsk
likevel.

**Ikke dikt opp.** Dette er hovedregelen, og den overstyrer ønsket om et pent
dokument. Konkret:

- Står det ingen ansvarlig, la feltet stå tomt. Ikke gjett ut fra hvem som
  antagelig snakket.
- Står det ingen frist, la feltet stå tomt. «Så snart som mulig» er ikke en
  frist — skriv det i oppgaveteksten i stedet.
- En diskusjon som ikke endte i noe er ikke en beslutning. Den hører hjemme
  under «Åpne spørsmål».
- Ikke legg til handlinger som virker fornuftige, men som ingen faktisk sa.

Et tomt felt er nyttig. Et feil felt sender noen i feil retning, og leseren har
ingen måte å oppdage det på uten å høre gjennom opptaket.

**Håndter talegjenkjenningsfeil åpent.** Transkripsjonen inneholder ekte feil,
særlig ved dialekt, kryssnakking, dårlig mikrofon og fagterminologi. Når noe
åpenbart er mistolket:

- Ser du hva som var ment, skriv det korrekt.
- Er du usikker, behold det som står og merk med `[uklart]`.
- Er en hel passasje uforståelig, si det i stedet for å improvisere:
  `[uklart parti — ca. 12:30–14:00]`.

**Ingen taleridentifikasjon.** Pipelinen kjører uten diarisering, så
transkripsjonen sier ikke hvem som snakker. Tilskriv bare navn når noen sies
eksplisitt i teksten («Jeg tar den, sa Kari» / «Kari, kan du…»). Ellers skriv
upersonlig.

**Vær kortfattet.** Referatet skal være vesentlig kortere enn transkripsjonen.
Fjern småprat, gjentakelser og tenkepauser. Beholder du alt, har du bare
formatert en transkripsjon.
