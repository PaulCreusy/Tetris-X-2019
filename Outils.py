import inspect,os
from random import sample, randint

chemin =""
chemin = inspect.getsourcefile(lambda:0)
chemin = chemin.replace("\\","/")
imax = 0
for i in range(len(chemin)):
    car = chemin[i]
    if car == "/":
        imax = i
chemin = chemin[:imax+1]
os.chdir(chemin)

from Kaiser import *

# Réglages de jeu
hauteur = 20
largeur = 8
score = 0
x_score = 200
y_score = 100
state = 0
timer = 0
rythme_start = 25
rythme = rythme_start
nombre_couleurs = 5

# Dico pour l'importation des images
dico_image = chargement_image({"R":"ressources/graphismes/Rouge.png", "V":"ressources/graphismes/Vert.png", "J":"ressources/graphismes/Jaune.png", "B":"ressources/graphismes/Bleu.png", "O":"ressources/graphismes/Orange.png", "r":"ressources/graphismes/Rose.png", "v":"ressources/graphismes/Violet.png"})

# Dico pour l'importation des sons
dico_son = chargement_musique({"musique":"ressources/son/musique_tetris.wav", "son_point":"ressources/son/son_point.wav", "son_fin":"ressources/son/son_fin.wav"})

def creer_grille():
    return [[0 for j in range(hauteur)] for i in range(largeur)]

# Création des ressources du jeu
jeu = creer_grille()
liste_couleurs = ["R","V","B","J","O","r","v"]
taille_case = 600//hauteur
taille_aire_jeu = (largeur * taille_case, hauteur*taille_case)
aire_jeu = pg.Rect(0, 0, taille_aire_jeu[0], taille_aire_jeu[1])
aire_jeu.center = (width//2, height//2)
move = False

def affiche_grille(grille):
    for i in range(largeur):
        for j in range(hauteur):
            if grille[i][j] != 0:
                couleur = grille[i][j]
                x = aire_jeu.left + i * taille_case
                y = aire_jeu.top + (hauteur-1-j) * taille_case
                afficher_image(dico_image[couleur], taille_case, taille_case, x , y)

def test_grille_libre(grille, k):
    res = []
    for i in range(largeur):
        cond = True
        for j in range(hauteur - k, hauteur):
            if grille[i][j] != 0:
                cond = False
                break
        if cond:
            res.append(i)
    if len(res) == 0:
        return False
    return res

def descente(grille, x, y, k):
    if grille[x][y-1] == 0:
        for i in range(k):
            grille[x][y-1+i] = grille[x][y+i]
        grille[x][y+k-1] = 0
    return (x, y-1)

def check_coord(x_t = 0, y_t = 0):
    return not(x_t > largeur - 1 or x_t < 0 or y_t > hauteur - 1 or y_t < 0)

def deplacer_barreau(grille, x, y, k, direction):
    cond = check_coord(x_t = x + direction, y_t = y+k-1)
    if cond:
        for i in range(k):
            if grille[x+direction][y+i] != 0:
                cond = False
    if cond:
        for i in range(k):
            grille[x+direction][y+i] = grille[x][y+i]
            grille[x][y+i] = 0
        return (x + direction, y)
    else:
        return (x,y)

def permuter_barreau(grille, x, y, k):
    mem = grille[x][y+k-1]
    for i in range(k-1,0,-1):
        grille[x][y+i] = grille[x][y-1+i]
    grille[x][y] = mem

def descente_rapide(grille, x , y, k):
    i = y
    while grille[x][i-1] == 0 and i > 0:
        i = i-1
    l = [0]*k
    for j in range(k):
        l[j] = grille[x][y+j]
        grille[x][y+j] = 0
    for j in range(k):
        grille[x][i+j] = l[j]
    return (x, i)

def detecte_alignement(rangee):
    compt = 1
    marking = [False]*len(rangee)
    res = 0
    for i in range(1,len(rangee)):
        if rangee[i-1] == rangee[i]:
            compt += 1
        else:
            if compt >= 3:
                if rangee[i-1] != 0:
                    res += compt - 2
                    for j in range(i-compt, i):
                        marking[j] = True
            compt = 1
    i = len(rangee)
    if compt >= 3:
        if rangee[i-1] != 0:
            res += compt - 2
            for j in range(i-compt, i):
                marking[j] = True
    return (marking, res)

def tassement_grille(grille):
    for i in range(largeur):
        for j in range(hauteur):
            if grille[i][j] != 0:
                descente_rapide(grille, i, j, 1)

def score_rangee(grille, g, i, j, dx, dy):
    if dx == 0 and dy == 0:
        return 0
    if check_coord(x_t = i, y_t = j) == False:
        return 0
    rangee = [grille[i][j]]
    a = i
    b = j
    while check_coord(x_t = a + dx, y_t = b + dy):
        a += dx
        b += dy
        rangee.append(grille[a][b])
    scan, res = detecte_alignement(rangee)
    for k in range(len(rangee)):
        if scan[k] == True:
            g[i + k*dx][j + k*dy] = 0
    return res

def efface_alignement(grille):
    res = 0
    g = [[grille[i][j] for j in range(hauteur)] for i in range(largeur)]
    for j in range(hauteur):
        res += score_rangee(grille, g, 0, j, 1, -1) # diagonale \
        res += score_rangee(grille, g, 0, j, 1, 0) # horizontale
        res += score_rangee(grille, g, 0, j, 1, 1) # diagonale /
    for i in range(largeur):
        res += score_rangee(grille, g, i, 0, 0, 1)
        if i > 0:
            res += score_rangee(grille, g, i, hauteur-1, 1, -1)
            res += score_rangee(grille, g, i, 0, 1, 1)
    return (g, res)

def calcul_score(grille):
    prec = [[grille[i][j] for j in range(hauteur)] for i in range(largeur)]
    grille, res = efface_alignement(grille)
    tassement_grille(grille)
    while grille != prec:
        prec = [[grille[i][j] for j in range(hauteur)] for i in range(largeur)]
        grille, temp = efface_alignement(grille)
        res += temp
        tassement_grille(grille)
    return res

def creer_barreau(grille, taille_barreau):
    barreau = [liste_couleurs[randint(0,nombre_couleurs-1)] for i in range(taille_barreau)]
    l_pos = test_grille_libre(grille, taille_barreau)
    pos = l_pos[randint(0,len(l_pos)-1)]
    #print(l_pos)
    for j in range(taille_barreau):
        #print(pos,hauteur -1-j,j)
        grille[pos][hauteur - 1 - j] = barreau[j]
    return (pos, hauteur - taille_barreau)

def affiche_aire_jeu():
    fenetre.fill(white)
    pg.draw.rect(fenetre, black, aire_jeu, width=10)

def affiche_score(score):
    chaine = "Score: " + str(score)
    texte, texte_rect = gen_texte(x_score, y_score, chaine, size = TITLE)
    fenetre.blit(texte, texte_rect)

def detect_control():
    for event in pg.event.get():
        if event.type == QUIT:
            quitter()
        elif event.type == KEYDOWN:
            if event.key == K_UP:
                #print("say up")
                return "up"
            if event.key == K_DOWN:
                return "down"
            if event.key == K_RIGHT:
                return "right"
            if event.key == K_LEFT:
                return "left"
            if event.key == K_ESCAPE:
                quitter()
    return False

def reaction(grille, x, y, k, move):
    if move == "up":
        permuter_barreau(grille, x, y, k)
    if move == "down":
        (x, y) = descente_rapide(grille, x, y, k)
    if move == "left":
        (x, y) = deplacer_barreau(grille, x, y, k, -1)
    if move == "right":
        (x, y) = deplacer_barreau(grille, x, y, k, 1)
    return (x, y)

def affiche_game_over(score):
    chaine = "Score: " + str(score)
    texte, texte_rect = gen_texte(width // 2, height // 2 - 100, chaine, size = TITLE)
    fenetre.blit(texte, texte_rect)
    chaine = "Game Over"
    texte, texte_rect = gen_texte(width // 2, height // 2 + 100, chaine, size = TITLE)
    fenetre.blit(texte, texte_rect)

def test_barreau_fige(grille, x, y):
    if grille[x][y-1] != 0 or y == 0:
        return True
    return False

def affiche_grille_simple(grille):
    for j in range(hauteur):
        for i in range(largeur):
            print(str(grille[i][hauteur-1 - j]), end = " ")
        print()

def calc_rythme(score):
    return max([rythme_start - (score // 10)*1,15])

# a modifier:
# calcul du score et effacement, tassement