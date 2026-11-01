# Niveaus: welk internationaal systeem gebruiken we?

Doel: één benaming die op de Engelstalige site voor leerlingen overal ter wereld te begrijpen is. De NL-site noemt leerjaar 3, 4 en 5 per niveau (vmbo-tl/kader, havo, vwo). Op de EN-site staan **geen** niveau- of methodenamen in de leerlingtekst; alleen in de navigatie staat een leeftijdsbenaming met het UK-jaar en de US Grade tussen haakjes.

## Vergelijking per leerjaar (Nederlands leerjaar 1 begint rond 12 jaar)

| Nederland (leerjaar) | Leeftijd | UK (England) | US | IB | Cambridge |
|---|---|---|---|---|---|
| Leerjaar 3 (vmbo-tl/kader, havo, vwo) | 14–15 | Year 10 | Grade 9 | MYP 4 | IGCSE, 1e jaar |
| Leerjaar 4 (vmbo-tl/kader: eindexamen; havo, vwo) | 15–16 | Year 11 | Grade 10 | MYP 5 | IGCSE, 2e jaar (examen) |
| Leerjaar 5 (havo: eindexamen; vwo) | 16–17 | Year 12 | Grade 11 | DP 1 | AS / A Level, 1e jaar |
| Leerjaar 6 (alleen vwo: eindexamen) | 17–18 | Year 13 | Grade 12 | DP 2 | A Level, 2e jaar |

De leeftijd per jaar is overal ongeveer gelijk (met een jaar speling per land of staat). Verschillen zitten in de **inhoud en diepte**, niet in de jaarnaam.

### Diploma-niveau (Nuffic, Nederlandse waardering van buitenlandse diploma's)

| Nederlands diploma | Vergelijkbaar met |
|---|---|
| vmbo-tl (4 jaar, ca. 12–16) | GCSE in 6 vakken met D–G (3–1) = vmbo-t; GCSE in 6 vakken met A*–C (9–4) = "minstens vmbo-t" |
| havo (5 jaar, ca. 12–17) | GCSE A*–C in 4 vakken + 2 relevante AS-levels met A*–C (of A-levels met D/E), samen 6 vakken |
| vwo (6 jaar, ca. 12–18) | GCSE A*–C in 3 vakken + 3 relevante A-levels met A*–C, samen 6 vakken; IB Diploma = vwo-diploma |

Bron: Nuffic (tabellen "level of diplomas"). Let op: dit zijn vergelijkingen van **diploma's** door Nuffic, geen officiële vakinhoudelijke gelijkwaardigheid per leerjaar. Voor de leerlingteksten gebruiken we daarom de leeftijd/het jaar, niet het niveau.

## Aanbeveling (besloten door Peter, 1 november 2026)

**Gebruik op de EN-site de leeftijd als hoofdlabel, met het UK-jaar en de US Grade in kleinere letters tussen haakjes erachter.** Een leeftijd snapt iedereen wereldwijd meteen. De niveaus (vmbo/havo/vwo) blijven op de NL-site en worden op de EN-site niet genoemd.

Exacte labels in het menu van de EN-beginpagina (`lang/en/ui.json`, sleutels `index.groep_*`):

| Leerjaar | Hoofdlabel (kop) | Klein, tussen haakjes |
|---|---|---|
| Leerjaar 3 | Age 14–15 | (Year 10 / Grade 9) |
| Leerjaar 3 en 4 samen (groep "Basics") | Basics · Age 14–16 | (Year 10–11 / Grade 9–10) |
| Leerjaar 4 (nog niet apart in de pilot) | Age 15–16 | (Year 11 / Grade 10) |
| Leerjaar 5 (nog niet in de pilot) | Age 16–17 | (Year 12 / Grade 11) |
| Leerjaar 6 (nog niet in de pilot) | Age 17–18 | (Year 13 / Grade 12) |

Opmaak van het kleine stuk: CSS-klasse `.jaar-klein` (14 px, dus ruim boven 10 pt; kleur #111111; niet grijs). De NL-site van de pilot is ongewijzigd.

Eerder voorstel (vervangen): "Year 10 · age 14–15 · US Grade 9". Terugzetten kan met de git-tag `voor-leeftijdslabels`.

Dit is mijn voorstel, geen officiële gelijkwaardigheid.

| | Voordelen | Nadelen |
|---|---|---|
| **Age + Year (UK/IGCSE)** (aanbevolen) | Veel gebruikt op internationale scholen (IGCSE wordt door schoolgidsen aangeduid als de meest afgelegde internationale kwalificatie voor 14–16-jarigen); Year 10/11 = IGCSE-jaren, dus direct herkenbaar; leeftijd werkt ook voor leerlingen met US- of IB-benaming; sluit aan op A Levels en IB DP (Year 12–13) | Zegt niets over niveau: een vmbo-tl-leerling en een vwo-leerling zitten allebei in Year 10; Amerikaanse leerlingen kennen "Year" minder (daarom Grade erbij) |
| US Grades | Eenvoudig, bekend in VS/Canada/veel internationale scholen | Minder gebruikt buiten VS; leeftijd per Grade verschilt per staat een jaar |
| IB (MYP/DP) | Duidelijke programma's (MYP 4–5, DP 1–2), Nuffic: IB Diploma = vwo-diploma | Alleen IB-scholen; MYP 1–5 niet overal gebruikt voor natuurwetenschappen; niet afdekkend voor de rest |
| Cambridge (IGCSE/AS/A) | Sterke vakinhoud-anker, veel scholen | Alleen leerlingen in dat systeem; Core/Extended-tiers kennen veel leerlingen niet |
| Eigen niveaulabel (Basic/Standard/Advanced) | Zegt wel iets over diepte | Niet standaard; nodigt uit tot "welk niveau ben ik?" en dwingt tot een eigen definitie |

Optioneel voor later: een **Core/Extended**-aanduiding (IGCSE-tiers) per onderwerp, alleen als Peter per pagina wil aangeven dat het onderwerp bij de kern of de uitbreiding hoort. In de pilot is dat niet gedaan.

## Bronnen

- Nuffic, UK/England: niveau van diploma's: https://www.nuffic.nl/en/education-systems/united-kingdom-england-wales-and-northern-ireland/level-of-diplomas
- Nuffic, UK/England: primair en secundair onderwijs: https://www.nuffic.nl/en/education-systems/united-kingdom-england-wales-and-northern-ireland/primary-and-secondary-education
- Nuffic, IB-diploma's: https://www.nuffic.nl/en/education-systems/international-baccalaureate/level-of-the-ib-diplomas
- Nuffic, niveau van Nederlandse diploma's: https://www.nuffic.nl/en/education-systems/the-netherlands/level-of-dutch-diplomas
- Nuffic, onderwijs in Nederland (duur vmbo/havo/vwo): https://www.nuffic.nl/en/study-and-work-in-the-netherlands/education-in-the-netherlands
- Cambridge International, IGCSE (leeftijd 14–16): https://help.cambridgeinternational.org/hc/en-gb/articles/203476042-Who-can-take-Cambridge-IGCSE
- Cambridge International, Upper Secondary / AS & A Level (16–19): https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-upper-secondary/
- Jaar/Grade/IB/leeftijd-tabellen: TISB https://www.tisb.org/assets/doc/Naming-of-Grade-Levels.pdf, ASL https://resources.finalsite.net/images/v1528727305/asl/dd3su1wo0dm7cndmoivj/UK_US_IB_Systems.pdf, Tendoria https://tendoria.com/wp-content/uploads/2024/02/Curriculum-and-Grade-Equivalences.pdf
- IGCSE als "meest afgelegde internationale kwalificatie voor 14–16": Nord Anglia, https://www.nordangliaeducation.com/bisb-boston/-/media/bisb-boston/academic-excellence/curriculum-guide-2025---2026/igcse-guide-2025-26.pdf (schoolgids, geen onafhankelijke bron)
