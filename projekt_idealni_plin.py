import pygame
import numpy as np
import sys
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

# Početne varijable i konstante
WIDTH, HEIGHT = 800, 600
MASA = 10**-20 #kg
RADIJUS_ČESTICA = 5 #pikseli
BROJ_ČESTICA = 100
KONSTANTA = 1.38*(10**-23)  #J/K 
VOLUMEN = 49.3 #L
TLAK = 1 #atm
TEMPERATURA = 300 #K

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulacija idealnog plina")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
# Postavljanje početnih brzina čestica pomoću srednje kinetičke energije
k = (BROJ_ČESTICA/100)*1.21*(10**24)
UEN = (3/2)*TLAK*101325*(VOLUMEN/1000)
EK = UEN/(k)
v_čestica = math.sqrt((2*EK)/MASA)

# Kreiranje čestica
čestice = [{'x': np.random.randint(RADIJUS_ČESTICA, WIDTH - RADIJUS_ČESTICA),
              'y': np.random.randint(RADIJUS_ČESTICA, HEIGHT - RADIJUS_ČESTICA),
              'vx': np.random.uniform(-v_čestica, v_čestica),
              'vy': np.random.uniform(-v_čestica, v_čestica),} for _ in range(BROJ_ČESTICA)]

TLAK_list = []
VOLUMEN_list = []
TEMPERATURA_list = []

class Button:
    def __init__(self, text_input, text_size, text_color, rectangle_width_and_height, rectangle_color, rectangle_hovering_color, position):
        self.text_input = text_input
        #rectangle ispod teksta
        self.rectangle = pygame.Rect((position[0]-(rectangle_width_and_height[0]/2), position[1]-(rectangle_width_and_height[1]/2)), rectangle_width_and_height)
        self.rectangle_color, self.rectangle_hovering_color = rectangle_color, rectangle_hovering_color
        #tekst u gumbu
        self.font = pygame.font.Font(None, text_size)
        self.text_surface = self.font.render(text_input, False, text_color)
        self.text_rectangle = self.text_surface.get_rect(center = self.rectangle.center)
    def update(self, screen):
        pygame.draw.rect(screen, self.rectangle_color, self.rectangle)
        screen.blit(self.text_surface, self.text_rectangle)
    def checkForCollision(self, mouse_position):
        if mouse_position[0] in range(self.rectangle.left, self.rectangle.right) and mouse_position[1] in range(self.rectangle.top, self.rectangle.bottom):
            return True
        return False
    def changeButtonColor(self):
        self.rectangle_color = self.rectangle_hovering_color
    def changeTextInput(self, new_text):
        self.text_input = new_text
        self.text_surface = self.font.render(self.text_input, False, (255, 255, 255))
        self.text_rectangle = self.text_surface.get_rect(center=self.rectangle.center)
# Stvaranje gumba
btn1 = Button("ZAGRIJAVANJE",20,"black",(100,50),"red","grey",(WIDTH-700,HEIGHT-60))
btn2 = Button("HLAĐENJE",20,"black",(100,50),"blue","grey",(WIDTH-600,HEIGHT-60))
btn3 = Button("POVEĆAJ",20,"black",(100,50),"green","grey",(WIDTH-450,HEIGHT-60))
btn4 = Button("SMANJI",20,"black",(100,50),"yellow","grey",(WIDTH-350,HEIGHT-60))
btn5 = Button("DODAJ ČESTICE",20,"black",(120,50),"orange","grey",(WIDTH-200,HEIGHT-60))
btn6 = Button("MAKNI ČESTICE",20,"black",(120,50),"pink","grey",(WIDTH-80,HEIGHT-60))
btn7 = Button("R",20,"black",(50,50),"purple","grey",(WIDTH-750,HEIGHT//2))

mouse_pos = pygame.mouse.get_pos()
for gumb in [btn1,btn2,btn3,btn4,btn5,btn6,btn7]:
            if gumb.checkForCollision(mouse_pos):
                gumb.changeButtonColor()
            gumb.update(screen)

# Funkcija za crtanje čestica na ekranu
def draw_čestice(screen):
    screen.fill(BLACK)
    for čestica in čestice:
        pygame.draw.circle(screen, WHITE, (int(čestica['x']), int(čestica['y'])), RADIJUS_ČESTICA)

# Funkcija za ažuriranje pozicija čestica
def update_čestice(kvadrat_širina, kvadrat_visina):
    for čestica in čestice:
        čestica['x'] += čestica['vx']
        čestica['y'] += čestica['vy']
        # Odbijanje od stijenka spremnika
        if čestica['x'] - RADIJUS_ČESTICA <= 100:
            čestica['x'] = 100 + RADIJUS_ČESTICA
            čestica['vx'] *= -1
        elif čestica['x'] + RADIJUS_ČESTICA >= 100 + kvadrat_širina:
            čestica['x'] = 100 + kvadrat_širina - RADIJUS_ČESTICA
            čestica['vx'] *= -1
        if čestica['y'] - RADIJUS_ČESTICA <= 100:
            čestica['y'] = 100 + RADIJUS_ČESTICA
            čestica['vy'] *= -1
        elif čestica['y'] + RADIJUS_ČESTICA >= 100 + kvadrat_visina:
            čestica['y'] = 100 + kvadrat_visina - RADIJUS_ČESTICA
            čestica['vy'] *= -1
    
    #Provjera sudara čestica
    for i in range(len(čestice)):
        for j in range(i + 1, len(čestice)):
            dx = čestice[j]['x'] - čestice[i]['x']
            dy = čestice[j]['y'] - čestice[i]['y']
            udaljenost = (dx ** 2 + dy ** 2) ** 0.5

            if udaljenost < 2 * RADIJUS_ČESTICA and udaljenost > 0:  #provjerava jesu li se čestice sudarile 
                #računa relativne brzine
                dvx = čestice[j]['vx'] - čestice[i]['vx']
                dvy = čestice[j]['vy'] - čestice[i]['vy']
                dot_product = dx * dvx + dy * dvy

                if dot_product < 0:  #provjerava gibaju li se čestice jedna prema drugoj
                    #računa nove brzine nakon sudara
                    nx = dx / udaljenost
                    ny = dy / udaljenost
                    dp = čestice[j]['vx'] * nx + čestice[j]['vy'] * ny - čestice[i]['vx'] * nx - čestice[i]['vy'] * ny
                    čestice[i]['vx'] += dp * nx
                    čestice[i]['vy'] += dp * ny
                    čestice[j]['vx'] -= dp * nx
                    čestice[j]['vy'] -= dp * ny

# Funkcija koja stvara prozor za prikaz grafova
def grafovi_menu():
    prikaz = True
    while prikaz:
        screen.fill((255,255,255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    VOLUMEN_list.clear()
                    TLAK_list.clear()
                    TEMPERATURA_list.clear()
                    display_menu()
        grafovi()
        pygame.display.flip()

#Funkcija koja crta grafove
def grafovi():
    plt.figure(figsize=(8, 6))  
    VOLUMEN_TLAK = list(zip(VOLUMEN_list, TLAK_list))
    TLAK_TEMPERATURA = list(zip(TEMPERATURA_list,TLAK_list))
    VOLUMEN_TEMPERATURA = list(zip(TEMPERATURA_list,VOLUMEN_list))
    # Volumen vs Tlak
    plt.subplot(3, 1, 1)
    plt.plot(*zip(*VOLUMEN_TLAK), color='red')
    plt.title('Tlak vs Volumen')
    plt.xlabel('Volumen/L')
    plt.ylabel('Tlak/atm')
    # Tlak vs Temperatura
    plt.subplot(3, 1, 2)
    plt.plot(*zip(*TLAK_TEMPERATURA), color='green')
    plt.title('Tlak vs Temperatura')
    plt.xlabel('Temperatura/K')
    plt.ylabel('Tlak/atm')
    # Volumen vs Temperatura
    plt.subplot(3, 1, 3)
    plt.plot(*zip(*VOLUMEN_TEMPERATURA), color='blue')
    plt.title('Volumen vs Temperatura')
    plt.xlabel('Temperatura/K')
    plt.ylabel('Volumen/L')

    plt.tight_layout()  
    plt.savefig('all_plots.png')  
    plt.close()  

    all_plots = pygame.image.load('all_plots.png')
    screen.blit(all_plots, (0, 0))
    os.remove('all_plots.png')
   
# Funkcija za prikazivanje glavnog menua
def display_menu():
    global WIDTH, HEIGHT
    font = pygame.font.Font(None, 36)
    menu = True
    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    grafovi_menu()
                    WIDTH, HEIGHT = screen.get_size()
                    return
                elif event.key == pygame.K_2:
                    simulacija()
                    WIDTH, HEIGHT = screen.get_size()
                    return
        screen.fill(BLACK)
        text = font.render("1 - Grafovi", True, WHITE)
        screen.blit(text, (50, 50))
        text = font.render("2 - Simulacija gibanja idealnog plina", True, WHITE)
        screen.blit(text, (50, 100))
        pygame.display.flip()

# Funkcija za simulaciju gibanja čestica
def simulacija():
    global TLAK_list, VOLUMEN_list, BROJ_ČESTICA, TEMPERATURA, VOLUMEN, TLAK   
    running = True
    clock = pygame.time.Clock()
    kvadrat_širina = WIDTH-400
    kvadrat_visina = HEIGHT-200
    while running:
        k = (BROJ_ČESTICA/100)*1.21*(10**24) # računa stvaran broj čestica jer 100 čestica prikazuje 1.21*(10**24) čestica
        VOLUMEN1= ((k*1.38*(10**-23)*300)/(101325))*1000
        VOLUMEN2 = ((k*1.38*(10**-23)*301)/(101325))*1000
        dV = VOLUMEN2-VOLUMEN1 # računa promjenu volumena kada se temperatura smanji ili poveća za 1K
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    kvadrat_širina = WIDTH-400
                    kvadrat_visina = HEIGHT-200
                    TLAK = 1
                    TEMPERATURA = 300
                    BROJ_ČESTICA = 100
                    k = (BROJ_ČESTICA/100)*1.21*(10**24)
                    VOLUMEN = ((k*KONSTANTA*TEMPERATURA)/(TLAK*101325))*1000
                    UEN = (3/2)*TLAK*101325*(VOLUMEN/1000)
                    EK = UEN/(k)
                    v_čestica = math.sqrt((2*EK)/MASA)
                    čestice.clear()
                    čestice.extend([{'x': np.random.randint(RADIJUS_ČESTICA, WIDTH - RADIJUS_ČESTICA),
                                    'y': np.random.randint(RADIJUS_ČESTICA, HEIGHT - RADIJUS_ČESTICA),
                                    'vx': np.random.uniform(-v_čestica, v_čestica),
                                    'vy': np.random.uniform(-v_čestica, v_čestica)} for _ in range(BROJ_ČESTICA)])
                    display_menu()
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if btn1.checkForCollision(mouse_pos): # određuje što se dešava kada se povećava T
                    if TEMPERATURA < 600:
                        TEMPERATURA += 1
                        if VOLUMEN<(66):
                            if BROJ_ČESTICA == 100:
                                VOLUMEN = ((k*KONSTANTA*TEMPERATURA)/(TLAK*101325))*1000
                                kvadrat_širina +=2
                            else:
                                VOLUMEN = ((k*KONSTANTA*TEMPERATURA)/(TLAK*101325))*1000
                                kvadrat_širina +=2
                        if VOLUMEN >= (66):
                            TLAK = ((k*KONSTANTA*TEMPERATURA)/(VOLUMEN/1000))/101325
                        k = (BROJ_ČESTICA/100)*1.21*(10**24)
                        UEN = (3/2)*TLAK*101325*(VOLUMEN/1000)
                        EK = UEN/(k)
                        v_čestica = math.sqrt((2*EK)/MASA)
                        for čestica in čestice:
                            čestica['vx'] = np.random.uniform(-v_čestica, v_čestica)
                            čestica['vy'] = np.random.uniform(-v_čestica, v_čestica)
                if btn2.checkForCollision(mouse_pos): # određuje što se dešava kada se smanjuje T
                    if TEMPERATURA <= 600 and TEMPERATURA >180:
                        TEMPERATURA -= 1
                        if VOLUMEN >(45):
                            if BROJ_ČESTICA == 100:
                                VOLUMEN = ((k*KONSTANTA*TEMPERATURA)/(TLAK*101325))*1000
                                kvadrat_širina -= 2
                            else:
                                VOLUMEN = ((k*KONSTANTA*TEMPERATURA)/(TLAK*101325))*1000
                                kvadrat_širina -= 2
                        if VOLUMEN <= (45):
                            TLAK = ((k*KONSTANTA*TEMPERATURA)/(VOLUMEN/1000))/101325
                        k = (BROJ_ČESTICA/100)*1.21*(10**24)
                        UEN = (3/2)*TLAK*101325*(VOLUMEN/1000)
                        EK = UEN/(k)
                        v_čestica = math.sqrt((2*EK)/MASA)
                        for čestica in čestice:
                            čestica['vx'] = np.random.uniform(-v_čestica, v_čestica)
                            čestica['vy'] = np.random.uniform(-v_čestica, v_čestica)
                if btn3.checkForCollision(mouse_pos): # određuje što se dešava kada se direktno povećava volumen spremnika
                    if VOLUMEN < (66):
                        if BROJ_ČESTICA == 100:
                            kvadrat_širina+=2
                        else:
                            kvadrat_širina += 1
                        VOLUMEN +=dV
                        TLAK = ((k*KONSTANTA*TEMPERATURA)/(VOLUMEN/1000))/101325
                if btn4.checkForCollision(mouse_pos): # određuje što se dešava kada se direktno smanjuje volumen spremnika
                    if VOLUMEN >(45):
                        if BROJ_ČESTICA == 100:
                            kvadrat_širina -= 2
                        else:
                            kvadrat_širina -= 1
                        VOLUMEN -= dV
                        TLAK = ((k*KONSTANTA*TEMPERATURA)/(VOLUMEN/1000))/101325
                if btn5.checkForCollision(mouse_pos): # određuje što se dešava kada se povećava broj čestica plina
                    if BROJ_ČESTICA<100:
                        BROJ_ČESTICA += 50
                        k = (BROJ_ČESTICA/100)*1.21*(10**24)
                        VOLUMEN = ((k*KONSTANTA*TEMPERATURA)/(TLAK*101325))*1000
                        if VOLUMEN > 66:
                            VOLUMEN = 66
                            TLAK = ((k*KONSTANTA*TEMPERATURA)/(VOLUMEN/1000))/101325
                            kvadrat_širina = 600
                        UEN = (3/2)*TLAK*101325*(VOLUMEN/1000)
                        EK = UEN/(k)
                        v_čestica = math.sqrt((2*EK)/MASA)
                        čestice.clear()
                        čestice.extend([{'x': np.random.randint(RADIJUS_ČESTICA, WIDTH - RADIJUS_ČESTICA),
                                        'y': np.random.randint(RADIJUS_ČESTICA, HEIGHT - RADIJUS_ČESTICA),
                                        'vx': np.random.uniform(-v_čestica, v_čestica),
                                        'vy': np.random.uniform(-v_čestica, v_čestica)} for _ in range(BROJ_ČESTICA)])
                if btn6.checkForCollision(mouse_pos): # određuje što se dešava kada se smanjuje broj čestica plina
                    if BROJ_ČESTICA >50:
                        BROJ_ČESTICA -= 50
                        k = (BROJ_ČESTICA/100)*1.21*(10**24)
                        VOLUMEN = ((k*KONSTANTA*TEMPERATURA)/(TLAK*101325))*1000
                        if VOLUMEN < 45:
                            VOLUMEN = 45
                            TLAK = ((k*KONSTANTA*TEMPERATURA)/(VOLUMEN/1000))/101325
                            kvadrat_širina = 350
                        UEN = (3/2)*TLAK*101325*(VOLUMEN/1000)
                        EK = UEN/(k)
                        v_čestica = math.sqrt((2*EK)/MASA)
                        čestice.clear()
                        čestice.extend([{'x': np.random.randint(RADIJUS_ČESTICA, WIDTH - RADIJUS_ČESTICA),
                                        'y': np.random.randint(RADIJUS_ČESTICA, HEIGHT - RADIJUS_ČESTICA),
                                        'vx': np.random.uniform(-v_čestica, v_čestica),
                                        'vy': np.random.uniform(-v_čestica, v_čestica)} for _ in range(BROJ_ČESTICA)])
                if btn7.checkForCollision(mouse_pos): # opcija za reset simulacije
                    TLAK_list.clear()
                    TEMPERATURA_list.clear()
                    VOLUMEN_list.clear()
                    kvadrat_širina = WIDTH-400
                    kvadrat_visina = HEIGHT-200
                    TLAK = 1
                    TEMPERATURA = 300
                    BROJ_ČESTICA = 100
                    k = (BROJ_ČESTICA/100)*1.21*(10**24)
                    VOLUMEN = ((k*KONSTANTA*TEMPERATURA)/(TLAK*101325))*1000
                    UEN = (3/2)*TLAK*101325*(VOLUMEN/1000)
                    EK = UEN/(k)
                    v_čestica = math.sqrt((2*EK)/MASA)
                    čestice.clear()
                    čestice.extend([{'x': np.random.randint(RADIJUS_ČESTICA, WIDTH - RADIJUS_ČESTICA),
                                    'y': np.random.randint(RADIJUS_ČESTICA, HEIGHT - RADIJUS_ČESTICA),
                                    'vx': np.random.uniform(-v_čestica, v_čestica),
                                    'vy': np.random.uniform(-v_čestica, v_čestica)} for _ in range(BROJ_ČESTICA)])

                    
    
        update_čestice(kvadrat_širina, kvadrat_visina)  # Ažuriranje pozicija čestica
        
        # Ažuriranje tlaka i volumena
        TLAK_list.append(float(TLAK))
        VOLUMEN_list.append(VOLUMEN)
        TEMPERATURA_list.append(TEMPERATURA)

        # Crta čestice unutar spremnika
        draw_čestice(screen)

        # Crta spremnik
        pygame.draw.rect(screen, WHITE, (100, 100, kvadrat_širina, kvadrat_visina), 1)

        btn1.update(screen)
        btn2.update(screen)
        btn3.update(screen)
        btn4.update(screen)
        btn5.update(screen)
        btn6.update(screen)
        btn7.update(screen)

        # tipke za promjenu broja čestica
        pygame.draw.rect(screen, WHITE, (WIDTH - 200, 50, 150, 30), 2)
        font = pygame.font.Font(None, 24)
        text = font.render(f"Broj čestica: {BROJ_ČESTICA}", True, WHITE)
        screen.blit(text, (WIDTH - 195, 55))
        # tipke za promjenu temperature čestica
        pygame.draw.rect(screen, WHITE, (WIDTH - 400, 50, 150, 30), 2)
        font = pygame.font.Font(None, 24)
        text = font.render(f"T čestica: {TEMPERATURA}K", True, WHITE)
        screen.blit(text, (WIDTH - 380, 55))
        #prikaz tlaka
        pygame.draw.rect(screen, WHITE, (WIDTH - 605, 50, 175, 30), 2)
        font = pygame.font.Font(None, 24)
        text = font.render(f"p čestica: {round(TLAK,2)}atm", True, WHITE)
        screen.blit(text, (WIDTH - 600, 55))
        #prikaz volumena
        pygame.draw.rect(screen, WHITE, (WIDTH - 800, 50, 175, 30), 2)
        font = pygame.font.Font(None, 24)
        text = font.render(f"V čestica:{round(VOLUMEN,2)}L", True, WHITE)
        screen.blit(text, (WIDTH - 790, 55))

        pygame.display.flip()
        clock.tick(60)

running = True
while running:
    display_menu()

pygame.quit()