# pyabitti
Python-kirjasto Abittikokeiden muokkaamiseen.

## Esimerkkejä

### Yhdistä kahden kokeen kysymykset

```python
from pyabitti import *
ex1 = Exam("transfer_koe1.zip")
ex2 = Exam("transfer_koe2.zip")
ex1.questions = ex1.questions + ex2.questions
ex1.title = "Yhdistetty koe"
ex1.save("trasnfer_koe3.zip")
```

## TODO

* Liitetiedostot eivät vielä tallennu
* Aukkomonivalinta ei ole tuettu
