# EchoMark

## Grupa nr 3

- Dymicki Cezary
- Jankowski Szymon
- Okniński Ireneusz

## Opis projektu

**EchoMark** to aplikacja służąca do znakowania wodnego plików audio z wykorzystaniem techniki ukrytych ech. Jej głównym
celem jest umożliwienie niewykrywalnego dla ludzkiego ucha osadzania znaków wodnych w nagraniach oraz ich skutecznej
detekcji.
Projekt koncentruje się na metodzie **time spread echo**, która dzięki rozproszeniu ech w czasie umożliwia ukrycie
większej ilości informacji w sygnale audio przy zachowaniu jego jakości. Dodatkowo badane jest zachowanie echa przez
model **SAOS** oraz odporność znaków wodnych na szum i kompresję.

## Funkcjonalności

- Osadzanie znaku wodnego w pliku audio z wykorzystaniem ukrytego echa.
- Zachowanie niesłyszalności wprowadzonych zmian.
- Detekcja znaków wodnych w dostarczonym pliku audio.

## Szczegóły działania

### 1. Dodawanie watermarka

- Użytkownik może przesłać plik audio w popularnych formatach (`.wav`, `.mp3`).
- Dostępne są dwa tryby osadzania znaku wodnego:
    - **Proste echo**
    - **Time spread echo**
- W zależności od wybranego trybu użytkownik konfiguruje parametry watermarka:
    - **Proste echo**:
        - opóźnienie echa (`δ`),
        - siła echa (`α`),
    - **Time spread echo**:
        - opóźnienie echa (`δ`),
        - siła echa (`α`),
        - wzorzec echa (np. ciąg bitów).
- System przetwarza przesłany plik audio i generuje nową wersję z niewykrywalnym dla człowieka znakiem wodnym.
- Użytkownik ma możliwość odsłuchania i pobrania pliku z osadzonym watermarkiem.

### 2. Wykrywanie watermarka

- Użytkownik może przesłać plik audio w popularnych formatach (`.wav`, `.mp3`) oraz, w przypadku time spread echo, swój
  wzorzec.
- System analizuje sygnał audio, wykonując:
    - obliczenie **cepstrum**,
    - detekcję opartą o **z-score** dla określonego `δ` (dla prostego echa),
    - analizę korelacji ze wzorcem (dla time spread echo).
- Wyniki analizy prezentowane są w formie:
    - komunikatu: **„watermark obecny”** lub **„watermark nieobecny”**,
    - wartości liczbowej: **z-score** lub **AUROC**,
    - wizualizacji cepstrum lub funkcji korelacji.

## Harmonogram pracy

| Nr | Termin        | Zadania                                                                                                                                                                                                                              |
|----|---------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1  | 06.10 – 12.10 | Wybór tematu projektu. Analiza artykułu źródłowego i potencjalnych kierunków rozwoju badań. Przygotowanie wstępnego design proposal.                                                                                                 |
| 2  | 13.10 – 19.10 | Sformułowanie wymagań projektu. Finalizacja i wysłanie design proposal (**deadline: 15.10, 23:59**). Konfiguracja środowiska, przygotowanie szkieletu projektu. Pierwsze eksperymenty z podstawowym przetwarzaniem audio w Pythonie. |
| 3  | 20.10 – 26.10 | Przegląd literatury. Replikacja eksperymentów z artykułu. Próby tworzenia prostych znaków wodnych (echo) oraz ich detekcji. Stworzenie podstawowego frontendu aplikacji.                                                             |
| 4  | 27.10 – 02.11 | Dokończenie i prezentacja działającego prototypu (**deadline prototypu: 29.10**).                                                                                                                                                    |
| 5  | 03.11 – 09.11 | Opracowanie bibliografii. Eksperymenty z zaawansowanymi metodami ukrywania znaków wodnych (różne wartości opóźnienia `δ`, siły `α` i wzorców w time spread echo).                                                                    |
| 6  | 10.11 – 16.11 | Rozbudowa modułu wykrywania watermarków – implementacja analizy cepstrum, detekcji z-score i korelacji wzorców. Testy skuteczności i analiza false positive / false negative.                                                        |
| 7  | 17.11 – 23.11 | Nauka do kolokwium (20.11) – **przerwa w pracach projektowych.**                                                                                                                                                                     |
| 8  | 24.11 – 30.11 | Integracja systemu osadzania i wykrywania watermarków. Przygotowanie pipeline’u testowego. Początkowe testy odporności na szum i kompresję.                                                                                          |
| 9  | 01.12 – 07.12 | Optymalizacja działania systemu. Wstępne przygotowanie dokumentacji technicznej i użytkowej.                                                                                                                                         |
| 10 | 08.12 – 14.12 | Utworzenie obrazu **Docker** dla projektu oraz rezerwowy tydzień na ewentualne poprawki.                                                                                                                                             |
| 11 | 15.12 – 21.12 | Finalizacja interfejsu użytkownika oraz kodu źródłowego. Dopracowanie dokumentacji technicznej i przygotowanie instrukcji użytkownika.                                                                                               |
| 12 | 22.12 – 28.12 | **Święta – przerwa w pracach projektowych.**                                                                                                                                                                                         |
| 13 | 29.12 – 04.01 | **Nowy Rok – przerwa do 02.01.** Przygotowanie planu działań końcowych projektu.                                                                                                                                                     |
| 14 | 05.01 – 11.01 | Ostatni tydzień na wprowadzenie poprawek i dodatkowych funkcji. Przygotowanie filmu prezentacyjnego oraz finalnej prezentacji projektu.                                                                                              |
| 15 | 12.01 – 18.01 | Przygotowanie finalnego demo i dokumentacji. **Deadline oddania projektu: 19.01**.                                                                                                                                                   |
|

## Zakres planowanych eksperymentów

### 1. Analiza techniki time spread echo

- Ocena ilości informacji, którą można zakodować w znaku wodnym opartym o echo, pozostającym niesłyszalnym dla człowieka
  i zachowywanym podczas treningu modelu.
- Weryfikacja, czy każde wprowadzone echo jest przenoszone przez model w procesie generacji.

### 2. Projektowanie i detekcja zaawansowanych znaków wodnych

- Opracowanie metod kodowania różnych typów ukrytych ech, które modele potrafią zachować w generowanym audio.
- Badanie metod wykrywania znaków wodnych w wygenerowanym dźwięku – testowanie różnych technik detekcji i progów
  rozpoznania.

### 3. Zastosowania praktyczne: identyfikacja źródła audio

- Sprawdzenie, czy możliwe jest wykrycie konkretnego znaku wodnego w wygenerowanym audio, co pozwoli autorowi
  zweryfikować, czy jego utwór został wykorzystany bez zgody.
- Analiza wskaźników **false positive** i **false negative** oraz ocena wiarygodności predykcji.

### 4. Odporność na zakłócenia *(niższy priorytet)*

- Testowanie odporności znaków wodnych opartych na echu na dodany szum i kompresję.

### 5. Modele wykorzystywane w badaniach

- **DDSP** – prostszy model wykorzystywany do początkowych testów.
- **SAOS** – model trenowany z użyciem fine-tuningu.
- Możliwość wykorzystania dodatkowych modeli.

## Stack technologiczny

### Główne języki programowania

- Python

### Interfejs użytkownika

- React + FastAPI lub Streamlit

### Zarządzanie strukturą projektu

- `uv` – środowisko i zarządzanie zależnościami
- `ruff`, `isort` – lintery i formatowanie kodu
- `make` – ułatwienie uruchamiania
- `pytest` – testy jednostkowe

### Model

- PyTorch
- NumPy, SciPy – obliczenia
- matplotlib – wizualizacje
- librosa – przetwarzanie sygnałów audio

### Konteneryzacja

- Docker lub Podman

## Bibliografia

1. Christopher J. Tralie, Matt Amery, Benjamin Douglas, Ian Utz (2024). *Hidden Echoes Survive Training in Audio To
   Audio Generative Instrument Models.* arXiv:
   2412.10649. [https://doi.org/10.48550/arXiv.2412.10649](https://doi.org/10.48550/arXiv.2412.10649), [https://www.ctralie.com/echoes/](https://www.ctralie.com/echoes/)
2. Djebbar, F., Ayad, B., Meraim, K.A. et al. (2012). *Comparative study of digital audio steganography techniques.* J
   AUDIO SPEECH MUSIC PROC. 2012,
    25. [https://doi.org/10.1186/1687-4722-2012-25](https://doi.org/10.1186/1687-4722-2012-25)
3. Mohammad Shorif Uddin, Ohidujjaman, Mahmudul Hasan, Tetsuya Shimamura (2024). *Audio Watermarking: A Comprehensive
   Review.* [https://dx.doi.org/10.14569/IJACSA.2024.01505141](https://dx.doi.org/10.14569/IJACSA.2024.01505141)
