# Tetris adapté de X 2019 MP/PC Version 1.0.2
# -*- coding: utf-8 -*-
import inspect,os


from Outils import *

transition(fenetre)
afficher_logo_kaiser(fenetre)
canal_musique.play(dico_son["musique"], loops = -1)
transition(fenetre)


while True:
    clock.tick(fps)
    #print("state = " + str(state))
    timer += 1
    affiche_aire_jeu()
    affiche_score(score)
    affiche_grille(jeu)
    move = detect_control()
    if move != False and state != 2 and state != 3 :
        (x_barreau, y_barreau) = reaction(jeu, x_barreau, y_barreau, taille_barreau, move)
    if state == 0: # calcul du score terminé, création d'un nouveau barreau
        taille_barreau = randint(3,5)
        if test_grille_libre(jeu, taille_barreau) == False:
            state = 2
            canal_musique.play(dico_son["son_fin"])
        else:
            (x_barreau, y_barreau ) = creer_barreau(jeu, taille_barreau)
            state = 1
    if state == 2: # game over
        fenetre.fill(white)
        affiche_game_over(score)
        detect_quitter()
    if state == 3:
        if timer % rythme == 0:
            if jeu == prec:
                state = 0
            else:
                canal_son.play(dico_son["son_point"])
                prec = [[jeu[i][j] for j in range(hauteur)] for i in range(largeur)]
                jeu, temp = efface_alignement(jeu)
                score += temp
                tassement_grille(jeu)
    if state == 1: # phase de jeu
        if timer % rythme == 0:
            if test_barreau_fige(jeu, x_barreau, y_barreau):
                state = 3
                prec = [[jeu[i][j] for j in range(hauteur)] for i in range(largeur)]
                jeu, temp = efface_alignement(jeu)
                tassement_grille(jeu)
                score += temp
                rythme = calc_rythme(score)
            else:
                (x_barreau, y_barreau) = descente(jeu, x_barreau, y_barreau, taille_barreau)
    pg.display.update()
