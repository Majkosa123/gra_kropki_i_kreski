import tkinter as tk
from tkinter import Canvas
import numpy as np
from wyniki import dodaj_wynik, pobierz_wyniki, inicjalizuj_wyniki
from wyniki_dane import WYNIKI
WYNIKI_PLIK = 'wyniki_dane.py'
rozmiar_ekranu = 800
liczba_kropek = 8
kolor_kropek = '#1A96F6'
gracz1_kolor = '#F79B05'
gracz2_kolor = '#50EF6B'
wypelnienie_kwadratu1 = '#f5cd8c'
wypelnienie_kwadratu2 = '#9ff5ae'
zielony_kolor = '#7BC043'
szerokosc_kropki = 0.25 * rozmiar_ekranu / liczba_kropek
szerokosc_linia = 0.1 * rozmiar_ekranu / liczba_kropek
odleglosc_miedzy_kropkami = rozmiar_ekranu / (liczba_kropek)
pomaranczowy = '#F79B05'


# Klasa reprezentująca grę Dots and Boxes
class Kropki_i_kreski():

    def __init__(self, root):
        self.root = root #glowne okno - interfejs
        self.root.title('-• Kropki i kreski •-')
        self.canvas = Canvas(self.root, width=rozmiar_ekranu, height=rozmiar_ekranu, bg='#323232')
        self.canvas.pack()
        self.root.bind('<Button-1>', self.kliknij) #kliknięcie lewym-1 przyciskiem myszy
        self.zaczyna_gracz1 = True
        self.odswiez_tablice()
        self.status_tablicy = np.zeros(shape=(liczba_kropek - 1, liczba_kropek - 1)) #tablica przechowuje informacje o aktualnym stanie pudełek między kropkami.
        self.stan_wiersza = np.zeros(shape=(liczba_kropek, liczba_kropek - 1)) #tablica przechowuje informacje o stanie każdego wiersza między kropkami.
        self.stan_kolumny = np.zeros(shape=(liczba_kropek - 1, liczba_kropek)) #to samo ale kolumny
        self.zaczyna_gracz1 = True
        self.player1_turn = not self.zaczyna_gracz1
        self.resetuj_tablice = False
        self.turntext_handle = []
        self.juz_pokolorowane_pudelko = []
        self.tura_gracza()
        inicjalizuj_wyniki()
        self.gra_wyniki = pobierz_wyniki()
        self.history_score_green = 0
        self.history_score_orange = 0
        self.game_over = False

    def zagraj_ponownie(self): #przygotowanie do kolejnej gry - czyszczenie
        # Resetowanie parametrów początkowych
        self.odswiez_tablice() #narysowanie ponownie kropek i kresek
        self.status_tablicy = np.zeros(shape=(liczba_kropek - 1, liczba_kropek - 1)) #resetowanie tablicy - od nowa - zadne pudelko nie jest ukonczone
        self.stan_wiersza = np.zeros(shape=(liczba_kropek, liczba_kropek - 1)) #zaden wiersz nie jest ukonczony
        self.stan_kolumny = np.zeros(shape=(liczba_kropek - 1, liczba_kropek)) #zadna kolumna nie jest ukonczona

        # Zmiana gracza początkowego
        self.zaczyna_gracz1 = not self.zaczyna_gracz1 #nastepna tura zacznie sie od innego gracza
        self.player1_turn = not self.zaczyna_gracz1 #połączenie z tym co sie wyswietla na dole gry
        self.resetuj_tablice = False #informuje czy plansza powinna sie zresetowac, tutaj plansza sie nie resetuje, gra rozpocznie sie od nowej tury z nowym graczem początkowym
        self.turntext_handle = [] #zerowanie listy aby móc wyswietlic informacje o aktualnym graczu

        self.juz_pokolorowane_pudelko = [] #zeruje listę która zawiera informacje o pokolorowanych pudelkach z poprzedniej tury i przygotowuje się do nastepnej tury
        self.tura_gracza() #aktualizacja interfejsu, wyswietlenie informacji i bieżacej turze i graczu

    def mainloop(self): # Rozpoczęcie głównej pętli gry
        self.root.mainloop() #czeka na interakcje z uzytkownikiem np. klikniecie myszą i potem przeprowadza daną akcje

    # logika gry:
    def czy_kratka_zajeta(self, pozycja, type): # Sprawdzenie, czy dana kratka planszy jest już zajęta i utrzymuje dzialanie aplikacji dopoki nie zamknie się głównego okna.
        r = pozycja[0]
        c = pozycja[1]
        zajeta = True #zakladamy ze kratka jest zajeta, zmieni sie na false jesli sie okaze ze nie jest zajeta

        if type == 'row' and self.stan_wiersza[c][r] == 0:
            zajeta = False #jeśli typ kratki to 'row' (czyli linia pozioma) i stan wiersza, do którego należy kratka, jest równy 0, to kratka nie jest zajęta
        if type == 'col' and self.stan_kolumny[c][r] == 0:
            zajeta = False

        return zajeta
    def konwertuj_siatke_do_pozycji(self, pozycja_siatki): # Konwertowanie pozycji kliknięcia myszą na pozycję na planszy
        pozycja_siatki = np.array(pozycja_siatki) #zamiana listy na tablice numpy
        position = (pozycja_siatki - odleglosc_miedzy_kropkami / 4) // (odleglosc_miedzy_kropkami / 2) #uzyskanie indeksów

        type = False
        pozycja = []
        if position[1] % 2 == 0 and (position[0] - 1) % 2 == 0: #czy indeksu są parzyste - jesli tak to nastąpilo kliknięcie na linie poziomą
            r = int((position[0] - 1) // 2) #obliczenie indeksu wiersza r na podstawie indeksu pionowego
            c = int(position[1] // 2) #obliczenie indeksu kolumny c na podstawie indeksu poziomego
            pozycja = [r, c] #para indeksów
            type = 'row'
        elif position[0] % 2 == 0 and (position[1] - 1) % 2 == 0: #kliknięta linia pionowa
            c = int((position[1] - 1) // 2)
            r = int(position[0] // 2)
            pozycja = [r, c]
            type = 'col'

        return pozycja, type

    def pokoloruj_pudelka(self):
        # Zaznaczenie pudełka, jeśli zostało ukończone
        boxes = np.argwhere(self.status_tablicy == -4)
        for box in boxes:
            if list(box) not in self.juz_pokolorowane_pudelko and list(box) != []:
                self.juz_pokolorowane_pudelko.append(list(box))
                color = wypelnienie_kwadratu2 if self.status_tablicy[box[0], box[1]] == -4 else wypelnienie_kwadratu1
                self.srodek_pudelka(box, color)

        boxes = np.argwhere(self.status_tablicy == 4)
        for box in boxes:
            if list(box) not in self.juz_pokolorowane_pudelko and list(box) != []:
                self.juz_pokolorowane_pudelko.append(list(box))
                color = wypelnienie_kwadratu1 if self.status_tablicy[box[0], box[1]] == 4 else wypelnienie_kwadratu2
                self.srodek_pudelka(box, color)

    def zaktualizuj_tablice(self, type, pozycja):
        # Aktualizacja planszy po ruchu gracza
        r = pozycja[0] #indeksy kratki które zostaly klikniete przez gracza
        c = pozycja[1]
        val = 1 if self.player1_turn else -1

        if c < (liczba_kropek - 1) and r < (liczba_kropek - 1):
            self.status_tablicy[c][r] += val #sledzimy ktore linie sa zajete a ktore nie

        if type == 'row': #jesli byla kliknięta pozioma to aktualizujemy status tablicy
            self.stan_wiersza[c][r] = 1
            if c >= 1:
                self.status_tablicy[c - 1][r] += val

        elif type == 'col':
            self.stan_kolumny[c][r] = 1
            if r >= 1:
                self.status_tablicy[c][r - 1] += val

    def czy_koniec_gry(self): #sprawdzenie warunkow zakonczenia gry
        if (self.stan_wiersza == 1).all() and (self.stan_kolumny == 1).all() and not np.any(self.resetuj_tablice): #macierz stan wiersza sprawdza czy wszystkie linie zapelnione. gra dobiegła konca nie bylo odswiezenia tablicy
            self.koniec_gry()
            return True
        return False

    # rysowanie na planszy:
    def make_edge(self, type, pozycja): # Rysowanie krawędzi planszy
        if type == 'row':
            start_x = odleglosc_miedzy_kropkami / 2 + pozycja[0] * odleglosc_miedzy_kropkami
            end_x = start_x + odleglosc_miedzy_kropkami
            start_y = odleglosc_miedzy_kropkami / 2 + pozycja[1] * odleglosc_miedzy_kropkami
            end_y = start_y
        elif type == 'col':
            start_y = odleglosc_miedzy_kropkami / 2 + pozycja[1] * odleglosc_miedzy_kropkami
            end_y = start_y + odleglosc_miedzy_kropkami
            start_x = odleglosc_miedzy_kropkami / 2 + pozycja[0] * odleglosc_miedzy_kropkami
            end_x = start_x

        color = gracz1_kolor if self.player1_turn else gracz2_kolor
        self.canvas.create_line(start_x, start_y, end_x, end_y, fill=color, width=szerokosc_linia) #funkcja create line z canvas ktora rysuje linie

    def koniec_gry(self): #zakonczenie gry -obsluga tego
        if not self.game_over: #sprawdza czy nie zostala predzej zakonczona zeby uniknąc powtórki
            self.game_over = True

            player1_score = len(np.argwhere(self.status_tablicy == -4))
            player2_score = len(np.argwhere(self.status_tablicy == 4)) #liczy ilosc pudelek zapelnionych przez danych graczy

            self.player1_score = player1_score
            self.player2_score = player2_score #przypisanie wyników

            if player1_score > player2_score:
                text = f'Wygrywa: zielony '
                color = '#7BC043'
                self.history_score_green += 1
            elif player2_score > player1_score:
                text = f'Wygrywa: pomarańczowy '
                color = pomaranczowy
                self.history_score_orange += 1
            else:
                text = 'Koniec gry!'
                color = 'gray'

            dodaj_wynik(player1_score, player2_score, WYNIKI) #zapis wynikow do pliku
            with open(WYNIKI_PLIK, 'w') as file:
                file.write("WYNIKI = " + repr(WYNIKI))


            self.canvas.delete("all") #czysci zawartosc plotna
            self.canvas.create_text(rozmiar_ekranu / 2, rozmiar_ekranu / 3, font="cmr 60 bold", fill=color, text=text)

            score_text = 'Wynik: \n'
            self.canvas.create_text(rozmiar_ekranu / 2, 5 * rozmiar_ekranu / 8, font="cmr 40 bold", fill=zielony_kolor,
                                    text=score_text)

            score_text = 'gracz zielony : ' + str(player1_score) + '\n'
            score_text += 'gracz pomaranczowy : ' + str(player2_score) + '\n'
            self.canvas.create_text(rozmiar_ekranu / 2, 3 * rozmiar_ekranu / 4, font="cmr 30 bold", fill=pomaranczowy,text=score_text)

            score_text = 'Zagraj jeszcze raz \n'
            play_again_button = self.canvas.create_text(rozmiar_ekranu / 2, 15 * rozmiar_ekranu / 16, font="cmr 20 bold", fill="gray", text=score_text)

            return_button = self.canvas.create_text(rozmiar_ekranu / 5, rozmiar_ekranu /15, font="cmr 20 bold", fill="gray", text="Powrót do menu")

            self.canvas.tag_bind(play_again_button, '<Button-1>', lambda event: self.zagraj_ponownie())
            self.canvas.tag_bind(return_button, '<Button-1>', lambda event: self.menu_glowne())
            self.resetuj_tablice = True

            history_text = f'Historia wyników: \n Pomarańczowy: {self.history_score_orange} \n Zielony: {self.history_score_green} '
            self.canvas.create_text(rozmiar_ekranu / 2, 3 * rozmiar_ekranu / 14, font="cmr 25 bold", fill=kolor_kropek, text=history_text, anchor=tk.CENTER, justify=tk.CENTER)

    def powrot_do_menu(self): #powrot do menu
        self.canvas.delete("all")
        self.resetuj_tablice = True
        return_button = self.canvas.create_text(rozmiar_ekranu / 2, 15 * rozmiar_ekranu / 16, font="cmr 20 bold", fill="gray", text="Powrót do menu")
        self.canvas.tag_bind(return_button, '<Button-1>', lambda event: self.menu_glowne())

    def menu_glowne(self): #przejscie do menu glownego
        self.resetuj_tablice = True
        self.canvas.delete("all")
        MainMenu(self.root).create_main_menu()

    def odswiez_tablice(self): #odswiezenie planszy
        for i in range(liczba_kropek): #iteracja po kropkach i rysowanie pomiedzy nimi linii
            x = i * odleglosc_miedzy_kropkami + odleglosc_miedzy_kropkami / 2
            self.canvas.create_line(x, odleglosc_miedzy_kropkami / 2, x,
                                    rozmiar_ekranu - odleglosc_miedzy_kropkami / 2,
                                    fill='gray', dash=(2, 2))
            self.canvas.create_line(odleglosc_miedzy_kropkami / 2, x,
                                    rozmiar_ekranu - odleglosc_miedzy_kropkami / 2, x,
                                    fill='gray', dash=(2, 2)) #dash (2,2) linia przerywana

        for i in range(liczba_kropek): #rysowanie kropek na przecięciach siatki
            for j in range(liczba_kropek):
                start_x = i * odleglosc_miedzy_kropkami + odleglosc_miedzy_kropkami / 2
                end_x = j * odleglosc_miedzy_kropkami + odleglosc_miedzy_kropkami / 2
                self.canvas.create_oval(start_x - szerokosc_kropki / 2, end_x - szerokosc_kropki / 2, start_x + szerokosc_kropki / 2, end_x + szerokosc_kropki / 2, fill=kolor_kropek, outline=kolor_kropek)
    def tura_gracza(self): # Aktualizuje informacje o bieżącym graczu
        text = 'Teraz kolej: '
        if self.player1_turn: #Sprawdzenie, czy ruch wykonuje gracz 1. Jeśli tak to do tekstu dodawane jest "Gracz 2", a kolor tekstu ustawiany jest na gracz1_kolor.
            text += f'Gracz 2'
            color = gracz1_kolor
        else:
            text += 'Gracz 1'
            color = gracz2_kolor

        self.canvas.delete(self.turntext_handle) #usunięcie poprzedniego tekstu z interfejsu
        self.turntext_handle = self.canvas.create_text(rozmiar_ekranu / 2, rozmiar_ekranu - odleglosc_miedzy_kropkami / 8, font="cmr 15 bold", text=text, fill=color) #dodanie odpowiedniego tekstu do interfejsu

    def srodek_pudelka(self, box, color): # Rysowanie pudelka a pokoloruj pudelka wypelnianie kolorem
        start_x = odleglosc_miedzy_kropkami / 2 + box[1] * odleglosc_miedzy_kropkami + szerokosc_linia / 2
        start_y = odleglosc_miedzy_kropkami / 2 + box[0] * odleglosc_miedzy_kropkami + szerokosc_linia / 2
        end_x = start_x + odleglosc_miedzy_kropkami - szerokosc_linia
        end_y = start_y + odleglosc_miedzy_kropkami - szerokosc_linia
        self.canvas.create_rectangle(start_x, start_y, end_x, end_y, fill=color, outline='')

    def kliknij(self, event): #obsługa klikniecia myszą
        if not self.resetuj_tablice and not self.game_over: #sprawdza czy gra nie jest w trakcie resetowania i czy gra nie jest zakonczona
            pozycja_siatki = [event.x, event.y] #pobiera współrzędne gdzie kliknięto
            pozycja, valid_input = self.konwertuj_siatke_do_pozycji(pozycja_siatki) #konwertuje wspolrzedne klikniecia do miejsca na planszy i sprawdza czy input jest poprawny
            if valid_input and not self.czy_kratka_zajeta(pozycja, valid_input): #Sprawdza czy pozycja jest poprawna i czy kratka na planszy nie jest już zajęta. Jeśli tak, przechodzi do aktualizacji stanu gry
                self.zaktualizuj_tablice(valid_input, pozycja) # Aktualizuje grę na podstawie ruchu gracza
                self.make_edge(valid_input, pozycja) #Rysuje krawędź planszy na podstawie ruchu gracza
                self.pokoloruj_pudelka() #Aktualizuje kolorowanie pudełek na planszy
                self.odswiez_tablice() #Aktualizuje wygląd planszy
                self.player1_turn = not self.player1_turn #Zmienia aktualnego gracza.

                if self.czy_koniec_gry(): #Sprawdza, czy gra dobiegła końca.
                    self.koniec_gry()  #Wywołuje funkcję kończącą grę jeśli warunki zakończenia zostały spełnione
                else:
                    self.tura_gracza() #W przeciwnym razie przechodzi do następnej tury gracza
        elif self.game_over: #Jeśli gra jest zakończona, usuwa zawartość planszy i przywraca możliwość ponownego zagrania.
            self.canvas.delete("all")
            self.zagraj_ponownie()
            self.game_over = False
class MainMenu: # Klasa reprezentująca menu główne gry
    def __init__(self, root): #menu glowne
        self.root = root
        self.root.title('-• Kropki i kreski •-')
        self.root.geometry('800x800')
        self.create_main_menu()
        self.root.configure(bg="light grey")

    def create_main_menu(self):  # Utworzenie widoku menu głównego
        self.clear_window()
        label = tk.Label(self.root, text="Kropki i kreski", bg='light grey', font=('Arial', 30, 'bold'), fg='#2B2D30')
        label.pack(padx=20, pady=200)

        buttonPlay = tk.Button(self.root, text="Graj", width=30, bg='lightblue', font=('Arial', 26),
                               command=self.start_game)
        buttonPlay.pack(pady=15)
        buttonHistory = tk.Button(self.root, text="Najwyższe wygrane", width=30, bg='lightblue', font=('Arial', 26),
                               command=self.pokaz_wyniki)
        buttonHistory.pack(pady=15)
        buttonExit = tk.Button(self.root, text="Wyjdź z gry", width=30, bg='lightblue', font=('Arial', 26),
                               command=self.root.destroy)
        buttonExit.pack(pady=15)

    def start_game(self): # Rozpoczęcie nowej gry
        self.clear_window()
        game_instance = Kropki_i_kreski(self.root)
        game_instance.mainloop()

    def clear_window(self): # Wyczyszczenie okna
        for widget in self.root.winfo_children():
            widget.destroy()

    def pokaz_wyniki(self): # Wyświetlenie najwyższych wyników
        self.clear_window()
        wyniki_label = tk.Label(self.root, text="Najwyższe wygrane", bg='light grey', font=('Arial', 30, 'bold'))
        wyniki_label.pack(padx=20, pady=50)

        from wyniki_dane import WYNIKI # Pobieram wyniki z pliku wyniki_dane.py
        if not WYNIKI:
            wyniki_text = "Brak dostępnych wyników."
        else:
            bubble_sort(WYNIKI) # Posortuj wyniki za pomocą bubble sort

            top_10 = WYNIKI[:10] # Wybierz tylko 10 najwyższych wyników

            wyniki_text = "Wyniki:\n\n"
            for idx, wynik in enumerate(top_10, start=1): #enumerate iteruje i zwraca indeks i wartosc
                wyniki_text += f"{idx}. Gracz 1: {wynik['Gracz1']}, Gracz 2: {wynik['Gracz2']}\n"

        wyniki_display = tk.Label(self.root, text=wyniki_text, font=('Arial', 20), bg='light grey')
        wyniki_display.pack(pady=50)

        return_button = tk.Button(self.root, text="Powrót do menu", width=30, bg='lightblue', font=('Arial', 26),
                                  command=self.create_main_menu)
        return_button.pack(pady=15)
def bubble_sort(scores): #sortowanie bubble
    n = len(scores)
    for i in range(n - 1):
        for j in range(0, n - i - 1):
            if scores[j]['Gracz1'] + scores[j]['Gracz2'] < scores[j + 1]['Gracz1'] + scores[j + 1]['Gracz2']:
                scores[j], scores[j + 1] = scores[j + 1], scores[j]

if __name__ == "__main__":
    root = tk.Tk()
    app = MainMenu(root)
    root.mainloop()
