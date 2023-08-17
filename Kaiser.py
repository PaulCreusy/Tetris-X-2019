# Moteur Kaiser Version 1.1.0
# -*- coding: utf-8 -*-
import pygame as pg
import inspect,os
from pygame.locals import *

pg.init()

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

# Les couleurs basiques
black = 0,0,0
white = 255,255,255
red = 255,0,0
blue = 0,0,255
green = 0,255,0
gray = 100,100,100

# Les tailles de police standards
SMALL = 12
MEDIUM = 16
LARGE = 34
TITLE = 50

# Réglage du nombre de fps
clock = pg.time.Clock()
fps = 60

# Taille de la fenêtre
width = 1280
height = 720

# Création de la fenêtre
fenetre = pg.display.set_mode((width,height)) # Ajouter un ,FULLSCREEN pour mettre la fenêtre en plein écran.
fenetre.fill(white)
rectFenetre = fenetre.get_rect()

# Importation du logo du moteur
logo_kaiser = pg.image.load("Ressources Kaiser/logo_kaiser.png")
police_logo = pg.font.Font("Ressources Kaiser/Ancient.ttf",120)
nom_moteur = police_logo.render("Kaiser Engine",True,black)
musique_logo = pg.mixer.Sound("Ressources Kaiser/bist_a_kaiser.wav")

# Réglage de la fenetre
pg.display.set_caption("Kaiser")
pg.display.set_icon(logo_kaiser) # on met le logo comme icone de la fenêtre

# Réglage du volume
volume_musique = 0.2
volume_bruitage = 0.5

# Création des objets liés au son
canal_musique = pg.mixer.Channel(0)
canal_musique.set_volume(volume_musique)
canal_son = pg.mixer.Channel(1)
canal_son.set_volume(volume_bruitage)

def ajuster_texte(chaine, length):
    """Fonction qui ajoute des \n là où il faut pour avoir une largeur de 'length' caractère.
    Renvoie une simple chaine avec les \n aux bons endroits.
    """
    mots = chaine.split(" ")
    chaine = ""
    somme = 0
    for mot in mots:
        if somme + len(mot) >= length:
            chaine = chaine + "\n" + mot
            somme = 0
        else:
            chaine = chaine + " " + mot
            somme += len(mot)
    return chaine

def gen_texte(x, y, chaine, size=SMALL, couleur=black, bold=False):
    """Fonction qui génère la surface et le rectangle du texte.
    Renvoie un tuple avec la surface de texte et le rect correspondant.
    Le texte est centré sur la position (x, y).
    """
    #chaine = chaine.encode('iso-8859-1') # Conversion de la ligne en unicode
    font = pg.font.Font("Ressources Kaiser/standard.ttf", size)
    if bold: font.set_bold(True)
    texte = font.render(chaine, True, couleur)
    if bold: font.set_bold(False)
    rect = texte.get_rect()
    rect.center = (x,y)
    return texte, rect

def dec_texte(x, y, chaine, size=SMALL, couleur=black, bold=False):
    """Fonction qui découpe le texte au niveau des '\n'.
    Renvoie un tableau contenant les lignes de texte générées par gtexte.
    Justifie en centrant le texte.
    La première ligne est centrée sur la position (x, y).
    """
    liste = chaine.split("\n")
    lignes = []
    for i in range(len(liste)):
        ligne = gtexte(x, y + (size+5)*i, liste[i], size, couleur, bold)
        lignes.append(ligne)
    return lignes

def transition(fenetre, couleur = white):
    """Fonction pour faire une transition d'un état à un autre avec une pause d'une demi-seconde.
    Affiche un écran de la couleur choisie pour les transitions.
    """
    time_left = fps//2
    while clock.tick(fps) and time_left > 0:
        time_left -= 1
        fenetre.fill(couleur)
        pg.display.update()
    #print("transition")

def quitter():
    """Fonction qui ferme pygame et python."""
    pg.quit()
    quit()

def chargement_image(dico):
    """Fonction pour charger toutes les images d'un coup.
    Prend en entrée un dictionnaire avec le nom de chaque image et sa position.
    Renvoie un dictionnaire avec le nom de chaque image et l'image elle même.
    """
    for nom_image in dico:
        dico[nom_image] = pg.image.load(dico[nom_image])
    return dico

def chargement_musique(dico):
    """Fonction pour charger toutes les musiques d'un coup.
    Prend en entrée un dictionnaire avec le nom de chaque musique et sa position.
    Renvoie un dictionnaire avec le nom de chaque musique et la musique elle même.
    """
    for nom_musique in dico:
        dico[nom_musique] = pg.mixer.Sound(dico[nom_musique])
    return dico

def chargement_donnees(path):
    """Fonction pour charger des fichiers en .json.
    Prend en entrée le chemin du fichier.
    Renvoie le dictionnaire data.
    """
    with open(path, 'r') as file:
        data_raw = file.read().replace('\n', '')
    data = json.loads(data_raw)
    return data

def detect_quitter():
    """Fonction qui détecte l'ordre de fermeture de la fenêtre et quitte.
    """
    for event in pg.event.get():
        if event.type == QUIT:
            quitter()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                quitter()

def afficher_image(image, long, larg, x, y):
    """Fonction qui modifie la taille et affiche une image.
    Prend en entrée une image, la dimension à lui donner et la position à laquelle l'afficher.
    """
    img = pg.transform.scale(image, (long, larg))
    rectPos = img.get_rect()
    rectPos.topleft = (x,y)
    fenetre.blit(img,rectPos)

def transparent(img,valeur = 150):
    """Fonction qui convertit une image en image transparente.
    Prend en entrée une image et valeur entre 0 et 255 (0  = transparent).
    Renvoie une nouvelle image transparente sans modifier l'originale.
    """
    res = img.copy()
    res = pg.Surface.convert_alpha(res)
    res.fill((255,255,255,valeur), special_flags = BLEND_RGBA_MULT)
    return res

def afficher_logo_kaiser(fenetre):
    """Fonction qui afficher le logo kaiser pendant quelques secondes puis se ferme.
    """
    canal_musique.play(musique_logo)
    l = min(width,height)
    img_logo = pg.transform.scale(logo_kaiser, (l//2,l//2))
    rectPos = img_logo.get_rect()
    rectPos.center = rectFenetre.center
    rectNom = nom_moteur.get_rect()
    rectNom.centerx = rectFenetre.centerx
    rectNom.top = rectPos.bottom
    duree_fondu = 75
    duree_maintenir = 180
    for i in range(duree_fondu):
        clock.tick(fps)
        fenetre.fill(white)
        fenetre.blit(transparent(img_logo,(255*i)//duree_fondu), rectPos)
        fenetre.blit(transparent(nom_moteur,(255*i)//duree_fondu), rectNom)
        detect_quitter()
        pg.display.update()

    for i in range(duree_maintenir):
        clock.tick(fps)
        fenetre.blit(img_logo,rectPos)
        fenetre.blit(nom_moteur,rectNom)
        detect_quitter()
        pg.display.update()

# Tester et compléter les fonctions d'affichage de texte
# Ajouter une classe de bouton cliquable