---
name: kahoot-creator
description: Crée un Kahoot complet à la place de l'enseignant, directement dans l'éditeur Kahoot du navigateur (Edge ou Chrome) : cadrage du thème, questions, chronos adaptés au type de question, illustrations, passage en privé, rangement et vérification. Utilise ce skill dès que l'utilisateur veut créer, préparer ou compléter un kahoot, un quiz Kahoot ou un quiz de révision pour une classe, même s'il écrit « kahoot » de travers (la dictée donne souvent « cutout », « chaos », « caoute » ou « cahoot ») et même s'il fournit seulement un module, un PDF de cours ou un thème.
---

# Créer un Kahoot

L'IA de Kahoot produit des questions médiocres. Ce skill la remplace : Claude conçoit le quiz avec l'enseignant, puis le construit lui-même dans l'éditeur. Parle en français à l'enseignant.

Avant de piloter le navigateur, charge le skill `anthropic-skills:chrome-browser`. Les outils `mcp__claude-in-chrome__*` fonctionnent aussi sur Edge. Si aucun navigateur n'est connecté, dis-le et demande à l'enseignant d'ouvrir l'extension. Il se connecte lui-même à Kahoot : ne saisis jamais son mot de passe.

Lis [references/kahoot-editor.md](references/kahoot-editor.md) juste avant de construire le quiz : il contient les gestes qui marchent dans l'éditeur et leurs pièges.

## 1. Cadrer

Lis d'abord `~/.claude/kahoot-preferences.json` s'il existe. Il contient les réglages de chaque classe : niveau, écart éventuel au barème des chronos, dossier Kahoot. Ne repose pas une question dont la réponse y figure, et annonce en une ligne les réglages repris.

Lis ensuite le support fourni. Pour un PDF sans lecture directe, extrais le texte et les images avec PyMuPDF. Si tu ne connais pas l'emplacement d'un fichier, demande le chemin au lieu de chercher dans les dossiers personnels.

Pose ensuite les questions manquantes avec AskUserQuestion, quatre au maximum par série, ta recommandation en premier :

- le thème et la partie du support à couvrir ;
- la classe et le nombre de questions ;
- les types de questions souhaités ;
- les sources d'images : banque Kahoot, images du support, schémas dessinés, Internet, ou mélange ;
- **si le quiz contient des calculs**, l'affichage des formules sur l'illustration (une seule fois pour tout le kahoot).

## 2. Rédiger et faire valider

Présente un tableau avant toute saisie : numéro, question, réponses avec la bonne en gras, type, chrono, illustration et source. Le quiz n'est construit qu'après la validation de ce tableau, car corriger dans l'éditeur coûte bien plus cher qu'à l'écrit. Pour une image d'Internet, le tableau donne l'URL exacte et la licence : la validation vaut accord pour la télécharger.

Règles de rédaction :

- **Progression** : range les questions du plus simple au plus difficile.
- **Équilibre** : répartis la bonne réponse entre les quatre cases, sans schéma prévisible.
- **Pièges réalistes** : chaque mauvaise réponse doit correspondre à une erreur plausible d'élève (conversion oubliée, mauvaise unité, confusion de grandeurs). Dis laquelle à l'enseignant.
- **Chiffres cohérents** : la valeur de l'énoncé doit correspondre à celle visible sur l'image.
- **Erreurs du support** : signale toute erreur repérée dans le document, sans la reprendre dans le quiz.
- **Indices et exposants** : écris les grandeurs et les unités comme dans un cours, dans les questions, les réponses et les images : U₁, I₂, L₃, m³/s, 10⁶. Un « U1 » à plat n'est pas accepté. Dans l'éditeur, utilise le format de Kahoot (voir la référence), car les caractères Unicode ₁ et ² s'y affichent trop petits.
- **Longueurs** : vise au plus 120 caractères pour une question et 75 pour une réponse, puis laisse l'éditeur confirmer la limite de ton abonnement.

**Calculs vérifiés** : exécute le calcul de chaque bonne réponse et de chaque piège dans un script Python avant de présenter le tableau. Un calcul de tête peut produire une fausse bonne réponse, et elle se verrait devant toute la classe.

### Chrono selon le type de question

Choisis-le toi-même et applique-le ; l'enseignant le corrige dans le tableau s'il le souhaite.

| Type de question | Chrono |
|---|---|
| Mémoire, vocabulaire, vrai ou faux | 20 s |
| Lecture d'un schéma, d'un graphique ou d'un symbole | 30 s |
| Calcul en une étape | 60 s |
| Calcul avec conversion | 90 s |
| Calcul en plusieurs étapes, problème | 120 s |
| Puzzle (remise en ordre) | 30 à 60 s selon la longueur |

Un chrono laissé à 20 s par défaut sur un calcul mesure la vitesse de frappe et non la compréhension. N'utilise que les valeurs proposées par Kahoot.

### Types de questions

Le quiz à quatre réponses reste la base. Propose le vrai ou faux pour une idée reçue, le puzzle pour une séquence, le curseur pour une valeur numérique et la réponse libre pour un mot précis. Certains types dépendent de l'abonnement : si l'éditeur en bloque un, remplace-le par un quiz et signale-le.

## 3. Préparer les illustrations

La source détermine le traitement du fond :

| Source | Fond |
|---|---|
| Schéma, symbole ou formule dessiné par Claude | **Transparent** (PNG) |
| Image d'Internet | Conservé |
| Image du support de l'enseignant | Conservé |
| Banque d'images Kahoot | Conservé |

Pour un circuit, utilise [scripts/circuit_schema.py](scripts/circuit_schema.py). Dans ses libellés et formules, ainsi que dans `formula_card.py`, `_` met en indice et `^` en exposant : `U_1`, `10^{6}`. Pour tout schéma dessiné, utilise une encre sombre et épaisse avec un contour blanc : l'image s'affiche petite en classe, et la page de détail la pose directement sur le fond violet du thème. Vérifie le rendu en ouvrant l'image, sur un fond coloré. L'illustration ne doit jamais donner la réponse, par exemple en légendant le composant demandé.

**Formules** : si l'enseignant les veut, ajoute-les à l'illustration avec [scripts/formula_card.py](scripts/formula_card.py). Montre la relation générale (`E = P · Δt`), jamais le calcul résolu.

**Internet** : privilégie les sources sous licence libre, comme Wikimedia Commons ou l'onglet Unsplash de l'éditeur. Note la source et la licence pour le rapport. Place chaque téléchargement dans un dossier neuf et vide.

## 4. Construire

Suis [references/kahoot-editor.md](references/kahoot-editor.md). L'ordre à respecter :

1. Ouvrir une toile blanche, jamais les assistants IA de Kahoot.
2. Saisir chaque question : texte, réponses, bonne réponse, chrono, image.
3. Dans les paramètres : titre clair, description vide ou sobre, **visibilité Privé**, dossier de la classe.
4. Enregistrer.

Kahoot règle les nouveaux quiz sur Public et remplit titre et description par IA : ces trois champs sont à corriger à chaque fois. Laisse le kahoot en privé sauf demande explicite de l'enseignant. Ne lance pas de partie et ne partage rien.

À partir de 15 questions, importe le texte par tableur (détails dans la référence), puis ajoute les images à la main. Pour un petit quiz, la saisie directe reste plus simple.

## 5. Vérifier

Ouvre la page de détail du kahoot, clique sur « Afficher les réponses » et compare avec le tableau validé : nombre de questions, textes, bonnes réponses, chronos, images et visibilité. Ce contrôle détecte les clics mal placés que l'enregistrement ne signale pas.

## 6. Rapport et préférences

Termine par un rapport court :

- lien vers le kahoot, dossier et visibilité ;
- questions, avec la page du support utilisée ;
- sources et licences des images ;
- écarts par rapport au tableau validé, types remplacés et points à relire ;
- ce que tu n'as pas vérifié, notamment si le quiz n'a pas été joué en démonstration.

Mets ensuite à jour `~/.claude/kahoot-preferences.json` avec les réglages de la classe (crée le fichier s'il n'existe pas), sous cette forme :

```json
{
  "classes": {
    "Nom de la classe": {
      "niveau": "année et filière",
      "dossier_kahoot": "nom du dossier Kahoot de la classe",
      "chronos": "barème standard",
      "formules_sur_illustration": "demander"
    }
  }
}
```
