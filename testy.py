import pytest
from tkinter import Tk
from main import Kropki_i_kreski

@pytest.fixture #stworzenie nowej gry, dostarczanie danych wejsciowych do testow
def new_game():
    root = Tk()
    game = Kropki_i_kreski(root)
    return game

def test_inicjalizacja_gry():
    try:
        root = Tk()
        game = Kropki_i_kreski(root)
    except Exception as e: # gdy w trakcie inicjalizacji gry wystąpi błąd ten fragment kodu przechwytuje ten błąd
        pytest.fail(f"Inicjalizacja gry zakończona błędem: {e}") #tutaj będą informacje o bledzie

def test_zaktualizuj_tablice(new_game): #czy aktualizacja jest okej
    new_game.odswiez_tablice()
    new_game.zaktualizuj_tablice('row', [0, 0])
    assert new_game.status_tablicy[0][0] == -1.0

def test_czy_kratka_zajeta(new_game): #czy zajeta czy nie
    new_game.odswiez_tablice()
    assert not new_game.czy_kratka_zajeta([0, 0], 'row')

def test_koniec_gry(new_game): #sprawdza czy koniec gry na podstawie aktualnej gry
    new_game.odswiez_tablice()
    assert not new_game.czy_koniec_gry()

#def test_pokoloruj_pudelka(new_game):
  #  new_game.odswiez_tablice()
   # new_game.zaktualizuj_tablice('row', [0, 0])
   # new_game.pokoloruj_pudelka()