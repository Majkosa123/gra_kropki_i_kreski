WYNIKI_PLIK = 'wyniki_dane.py'

def inicjalizuj_wyniki():
    global WYNIKI
    WYNIKI = []

def pobierz_wyniki():
    return WYNIKI

def dodaj_wynik(player1_score, player2_score, lista_wynikow):
    wynik = {'Gracz1': player1_score, 'Gracz2': player2_score}
    lista_wynikow.append(wynik)
    with open(WYNIKI_PLIK, 'w') as file:
        file.write("WYNIKI = " + repr(lista_wynikow))
