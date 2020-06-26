# Implementácia HTTP resolveru doménových mien
##### Autor: Maroš Geffert (xgeffe00)
##### Dátum: 6.3.2020
---
## 1. Zadanie
Našou úlohou bola implementácia serveru, ktorý komunikuje s HTTP protokolom a zisťuje preklad doménových men. Pre preklad mien, server používa lokálny resolver stanice.

## 2. Popis riešenia
Pred začatím komunikácie spustíme server. Komunikáciu začína strana klienta, ktorého si reprezentujeme príkazom "curl".

Príklad simulacie klienta:
``` bash
    $ curl localhost:5353/resolve?
```

Náš "klient" predáva 2 vstupné parametre vo formáte DOTAZ:TYP, ktoré sú potrebné pre preklad domény. 
>name -> doménové meno alebo IP adresa
>type -> typ odpovede

Príklad vstupu:
``` bash
    $ curl localhost:5353/resolve?name=www.fit.vutbr.cz\&type=A
```
Po odoslaní vstupných parametrov server inicializuje HTTP hlavičku a následne spracováva či sa jedná o operáciu GET (spracováva 1 dotaz), alebo o operáciu POST (spracováva viacero dotazov). Na základe výberu operátora sa zavolá funkcia pre GET "get_function", alebo pre POST "post_function". 

### 2.2 GET
Pri spracovaní operácie GET pomocou vstupného parametru "type" zistím o aku operáciu sa ma jednať (či prekladám doménu na adresu alebo naopak) a parameter "name" obsahuje samotnú doménu/ip_adresu ktorú prekladám.

Na preklad domény/ip_adresy používam funkciu:

```javascript
gethostbyname()
gethostbyaddr()
```

Po spracovaní je požiadavka zaslaná naspäť "klientovi". V prípade že dôjde na serverovej strane k chybe (to je napríklad chybny vstup, alebo nenájdená doména) sa klientovi vypíše prislušná chybová odpoveď. Po prijatí odpovedi server stále beži a klient môže posielať dalšie dotazy.

### 3.3 POST
Operácie POST spracuváva viacero dotazov naraz, ktoré su uložene subore "queries.txt". V prípade chybného alebo nenájdeneho dotazu sa daný dotaz vynecháva. Po spracovaní všetkých dotazov a vygenerovaní hlavičky s návratovou hodnotou sa následne odpoveď aj s hlavičkou zasiela klientovi. 

### Zdroje
https://wiki.python.org/moin/TcpCommunication
Prednáška 2 z IPK
Fórum IPK

