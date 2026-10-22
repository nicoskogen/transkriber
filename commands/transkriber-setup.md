---
description: Engangsoppsett — installer whisper.cpp og last ned NB-Whisper-modellen
argument-hint: "[--full] [--blandet]"
allowed-tools: Bash
---

Kjør engangsoppsettet for transkriber-pluginen.

```
${CLAUDE_PLUGIN_ROOT}/scripts/setup.sh $ARGUMENTS
```

**Bruk `run_in_background: true`** — nedlastingen er på 1 GB (eller 2,9 GB med
`--full`) og går ofte over Bash-verktøyets timeout.

`--blandet` laster i tillegg ned Whisper small (omtrent 190 MB), som trengs for
opptak der folk snakker norsk og engelsk om hverandre. Valgene kan kombineres
og stå i hvilken som helst rekkefølge.

Skriptet installerer `whisper-cpp` og `ffmpeg` via Homebrew, laster ned
NB-Whisper til `~/.cache/nb-whisper/`, verifiserer kontrollsummen og kjører til
slutt en røyktest med den norske systemstemmen. Med `--blandet` kjører det også
en røyktest med norsk og engelsk tale om hverandre.

Vis utdataene til brukeren når jobben er ferdig. Skriptet er trygt å kjøre på
nytt: det hopper over det som allerede er på plass og gjenopptar en avbrutt
nedlasting. Hvis det feiler, vis feilmeldingen som den er — ikke prøv å
installere avhengighetene manuelt.
