# Projekt IPK 2020 - HTTP resolver doménových mien
Cieľom projektu bola implementácia servera zaisťujúceho preklad doménových mien,
komunikujúceho protokolom HTTP.

## Implementácia
Pre implementáciu bol zvolený jazyk Python pre svoju jednoduchosť a využiteľnosť.
Celý projekt je implementovaný v súbore *server.py*.
Hlavná časť programu skontroluje správnosť zadaného portu (v rozsahu 2^10 až 2^16) a spustí server.
Ten následne počúva kým sa naň  nepripojí klient. Pokiaľ si klient vyberie definovanú operáciu (__GET__ alebo __POST__),
zavolá funkciu, ktorá sa ju pokúsi vykonať a výsledok mu vráti. V opačnom prípade mu vráti chybové hlásenie (*Error 405*).
Chybové hlásenie vráti aj v prípade zle zadanej požiadavky (*Error 400*) alebo nenájdenia odpovede (*Error 404*).
Neúspech odchytáva cez `try except` štruktúru kde hľadá  zachytáva `OSError`.
  * GET
Skontroluje syntax požiadavky a pokúsi sa jej vyhovieť. Využíva funkcie `gethostbyname` a `gethostbyaddr`
z knižnice `socket`. Snaží sa vyhovieť jednej žiadosti.
  * POST
Skontroluje syntax požiadavky a pokúsi sa jej vyhovieť. Snaží sa vyhovieť zoznamu žiadostí. Využíva rovnaké
funkcie ako operácia __GET__ a správa sa podobne, ale *Error 404* nevracia.
