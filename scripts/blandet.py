#!/usr/bin/env python3
"""Blandet norsk og engelsk tale: språk per segment, engelsk og hull transkribert på nytt hver for seg.

Kun standardbiblioteket, så systemets python3 holder.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import wave
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Dict, List, Optional, Tuple

NORSK = {"no", "nn", "sv", "da"}
MIN_HULL_MS = 2000
MIN_LID_MS = 1500
PAD_MS = 100

SPESIALTOKEN = re.compile(r"<\|[a-zA-Z0-9_.-]+\|>|\[_[A-Z0-9_]+\]")
BEHANDLER = re.compile(r"processing '([^']+)'")
OPPDAGET = re.compile(r"auto-detected language: ([a-z]+) \(p = ([0-9.]+)\)")


@dataclass(frozen=True)
class Ord:
    start_ms: int
    end_ms: int
    text: str


@dataclass(frozen=True)
class Segment:
    start_ms: int
    end_ms: int
    text: str
    ord: Tuple[Ord, ...] = ()
    lang: Optional[str] = None


def info(melding: str) -> None:
    print(f"transkriber: {melding}", file=sys.stderr, flush=True)


def hel_utf8(tekst: str) -> str:
    return tekst.encode("utf-8", "surrogateescape").decode("utf-8", "replace")


def rens(tekst: str) -> str:
    return " ".join(SPESIALTOKEN.sub("", hel_utf8(tekst)).split())


def ord_fra_tokens(tokens: List[dict], forskyvning_ms: int) -> Tuple[Ord, ...]:
    ordliste: List[List] = []
    for t in tokens:
        if SPESIALTOKEN.fullmatch(t["text"]):
            continue
        fra, til = t["offsets"]["from"] + forskyvning_ms, t["offsets"]["to"] + forskyvning_ms
        if ordliste and not t["text"].startswith(" "):
            ordliste[-1][1] = til
            ordliste[-1][2] += t["text"]
        else:
            ordliste.append([fra, til, t["text"]])
    return tuple(Ord(fra, til, hel_utf8(tekst)) for fra, til, tekst in ordliste)


def les_json(sti: Path, forskyvning_ms: int = 0) -> List[Segment]:
    # whisper.cpp kan dele et flerbytetegn mellom to tokens, så filen er ikke alltid gyldig UTF-8.
    data = json.loads(sti.read_bytes().decode("utf-8", "surrogateescape"), strict=False)
    return [
        Segment(
            s["offsets"]["from"] + forskyvning_ms,
            s["offsets"]["to"] + forskyvning_ms,
            rens(s["text"]),
            ord_fra_tokens(s.get("tokens", []), forskyvning_ms),
        )
        for s in data.get("transcription", [])
    ]


def med_hull(segmenter: List[Segment], varighet_ms: int) -> List[Segment]:
    resultat: List[Segment] = []
    forrige_slutt = 0
    for seg in segmenter:
        if seg.start_ms - forrige_slutt >= MIN_HULL_MS:
            resultat.append(Segment(forrige_slutt, seg.start_ms, ""))
        resultat.append(seg)
        forrige_slutt = max(forrige_slutt, seg.end_ms)
    if varighet_ms - forrige_slutt >= MIN_HULL_MS:
        resultat.append(Segment(forrige_slutt, varighet_ms, ""))
    return resultat


def sprak_fra_etikett(etikett: str, p: float) -> Optional[str]:
    if etikett == "en" and p > 0.5:
        return "en"
    if etikett in NORSK:
        return "no"
    return None


def sett_sprak(segmenter: List[Segment], gjenkjent: Dict[int, Tuple[str, float]]) -> List[Segment]:
    resultat: List[Segment] = []
    forrige = "no"
    for i, seg in enumerate(segmenter):
        etikett = gjenkjent.get(i)
        lang = (sprak_fra_etikett(*etikett) if etikett else None) or forrige
        resultat.append(replace(seg, lang=lang))
        forrige = lang
    return resultat


def utsnitt_start(seg: Segment) -> int:
    return max(0, seg.start_ms - PAD_MS)


class Lyd:
    def __init__(self, sti: Path) -> None:
        with wave.open(str(sti), "rb") as w:
            self.params = w.getparams()
            self.rammer = w.readframes(w.getnframes())
        self.bredde = self.params.sampwidth * self.params.nchannels
        self.varighet_ms = self.params.nframes * 1000 // self.params.framerate

    def skriv_utsnitt(self, seg: Segment, sti: Path) -> None:
        fra = utsnitt_start(seg) * self.params.framerate // 1000
        til = min(self.varighet_ms, seg.end_ms + PAD_MS) * self.params.framerate // 1000
        with wave.open(str(sti), "wb") as w:
            w.setparams(self.params)
            w.writeframes(self.rammer[fra * self.bredde : til * self.bredde])


def kjor_whisper(args: List[str], mappe: Path) -> str:
    res = subprocess.run(args, cwd=mappe, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, errors="replace")
    if res.returncode != 0:
        sys.stderr.write(res.stderr[-2000:])
        info("whisper.cpp feilet i blandet modus")
        sys.exit(1)
    return res.stderr


def filargumenter(navn: List[str]) -> List[str]:
    return [arg for n in navn for arg in ("-f", n)]


def gjenkjenn_sprak(whisper: str, basismodell: str, mappe: Path, navn: List[str]) -> Dict[str, Tuple[str, float]]:
    if not navn:
        return {}
    logg = kjor_whisper([whisper, "-m", basismodell, "-l", "auto", "-dl", *filargumenter(navn)], mappe)
    resultat: Dict[str, Tuple[str, float]] = {}
    gjeldende = None
    for linje in logg.splitlines():
        if m := BEHANDLER.search(linje):
            gjeldende = m.group(1)
        elif (m := OPPDAGET.search(linje)) and gjeldende:
            resultat[gjeldende] = (m.group(1), float(m.group(2)))
            gjeldende = None
    return resultat


def transkriber_pa_nytt(whisper: str, modell: str, lang: str, mappe: Path, mal: Dict[str, Segment]) -> Dict[str, Segment]:
    if not mal:
        return {}
    kjor_whisper([whisper, "-m", modell, "-l", lang, "-mc", "0", "-ojf", *filargumenter(list(mal))], mappe)
    resultat = {}
    for n, seg in mal.items():
        sti = mappe / f"{n}.json"
        deler = les_json(sti, utsnitt_start(seg)) if sti.exists() else []
        tekst = " ".join(d.text for d in deler if d.text)
        resultat[n] = replace(seg, text=tekst, ord=tuple(o for d in deler for o in d.ord))
    return resultat


def undertekster(seg: Segment, maks: int) -> List[Tuple[int, int, str]]:
    if not seg.ord:
        return [(seg.start_ms, seg.end_ms, seg.text)]
    grupper: List[List[Ord]] = []
    for o in seg.ord:
        if grupper and len("".join(x.text for x in grupper[-1]).strip()) + len(o.text) <= maks:
            grupper[-1].append(o)
        else:
            grupper.append([o])
    linjer = []
    start = seg.start_ms
    for i, g in enumerate(grupper):
        slutt = seg.end_ms if i == len(grupper) - 1 else min(seg.end_ms, max(start, g[-1].end_ms))
        linjer.append((start, slutt, "".join(o.text for o in g).strip()))
        start = slutt
    return [linje for linje in linjer if linje[2]]


def tidskode(ms: int, skille: str) -> str:
    t, ms = divmod(ms, 1000)
    m, s = divmod(t, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}{skille}{ms:03d}"


def som_txt(segmenter: List[Segment]) -> str:
    linjer: List[str] = []
    for i, seg in enumerate(segmenter):
        if i and seg.lang != segmenter[i - 1].lang:
            linjer.append("")
        linjer.append(seg.text)
    return "\n".join(linjer) + "\n"


def som_vtt(segmenter: List[Segment]) -> str:
    cues = [f"{tidskode(s.start_ms, '.')} --> {tidskode(s.end_ms, '.')}\n{s.text}\n\n" for s in segmenter]
    return "WEBVTT\n\n" + "".join(cues)


def som_srt(segmenter: List[Segment], maks: int) -> str:
    linjer = [linje for s in segmenter for linje in undertekster(s, maks)]
    return "".join(
        f"{i}\n{tidskode(fra, ',')} --> {tidskode(til, ',')}\n{tekst}\n\n"
        for i, (fra, til, tekst) in enumerate(linjer, 1)
    )


def main() -> None:
    p = argparse.ArgumentParser(description="Blandet norsk og engelsk transkripsjon")
    p.add_argument("--lyd", type=Path, required=True, help="16 kHz mono WAV")
    p.add_argument("--tidslinje", type=Path, required=True, help="JSON fra NB-Whisper med -l no -ojf")
    p.add_argument("--modus", choices=["tekst", "referat", "srt"], required=True)
    p.add_argument("--maks-lengde", type=int, default=42, help="tegn per undertekstlinje")
    p.add_argument("--ut", required=True, help="utfil uten filendelse")
    p.add_argument("--whisper", required=True)
    p.add_argument("--modell", required=True, help="NB-Whisper-modellen")
    p.add_argument("--basismodell", required=True, help="Whisper base, for språkgjenkjenning")
    a = p.parse_args()

    lyd = Lyd(a.lyd)
    segmenter = med_hull(les_json(a.tidslinje), lyd.varighet_ms)

    with tempfile.TemporaryDirectory() as tmp:
        mappe = Path(tmp)
        navn = [f"s{i:05d}.wav" for i in range(len(segmenter))]
        for seg, n in zip(segmenter, navn):
            lyd.skriv_utsnitt(seg, mappe / n)

        lid = [i for i, s in enumerate(segmenter) if s.end_ms - s.start_ms >= MIN_LID_MS]
        info(f"gjenkjenner språk i {len(lid)} av {len(segmenter)} segmenter…")
        etiketter = gjenkjenn_sprak(a.whisper, a.basismodell, mappe, [navn[i] for i in lid])
        segmenter = sett_sprak(segmenter, {i: etiketter[navn[i]] for i in lid if navn[i] in etiketter})

        engelsk = {navn[i]: s for i, s in enumerate(segmenter) if s.lang == "en"}
        hull = {navn[i]: s for i, s in enumerate(segmenter) if s.lang == "no" and not s.text}
        info(f"{len(engelsk)} av {len(segmenter)} segmenter er på engelsk, {len(hull)} norske hull; transkriberer dem på nytt…")
        nytt = {
            **transkriber_pa_nytt(a.whisper, a.modell, "en", mappe, engelsk),
            **transkriber_pa_nytt(a.whisper, a.modell, "no", mappe, hull),
        }

    segmenter = [s for s in (nytt.get(n, s) for s, n in zip(segmenter, navn)) if s.text]

    if a.modus == "srt":
        Path(f"{a.ut}.srt").write_text(som_srt(segmenter, a.maks_lengde), encoding="utf-8")
    else:
        Path(f"{a.ut}.txt").write_text(som_txt(segmenter), encoding="utf-8")
        Path(f"{a.ut}.vtt").write_text(som_vtt(segmenter), encoding="utf-8")


if __name__ == "__main__":
    main()
