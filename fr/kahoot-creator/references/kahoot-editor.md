# Piloter l'éditeur Kahoot

Notes tirées d'une création réelle dans Edge, à 1528 × 746. L'interface peut changer : prends une capture d'écran au début, et de nouveau dès qu'un geste ne donne pas le résultat attendu. Les coordonnées de cette page ne sont que des repères. Regroupe les gestes avec `browser_batch` pour gagner du temps.

## Méthode rapide

Une fois l'éditeur chargé, colle [scripts/editor_helpers.js](../scripts/editor_helpers.js) avec `javascript_tool`. Une question Quiz se construit alors ainsi, dans un seul `browser_batch` :

1. `window.__open()`, puis un vrai clic sur le type dans le menu (Quiz vers (302, 200), Vrai ou faux vers (462, 195)). Un clic par script sur le type ne marche pas.
2. `window.__top()`, un vrai clic sur le menu du chrono vers (1272, 303), puis `window.__time('1 minute')`.
3. `await window.__title('… U_1 …')`, puis, seulement si la réponse est `ok`, `await window.__fill([a, b, c, d], n)`.
4. Capture d'écran pour contrôler texte, coche et chrono.
5. `await window.__imp()`, `find` « input type=file », `file_upload`.

`__title` et `__fill` refusent les champs déjà remplis : c'est le signe que l'ajout de question a échoué. Pour corriger un champ, passe par le clavier (`ctrl+a`, `Delete`, saisie), car `execCommand('delete')` n'efface rien. Sur un kahoot neuf, la diapo 1 est déjà un Quiz : ne l'ajoute pas. Ces aides ne remplacent pas la saisie pour les puzzles, dont les champs n'ont pas encore été testés avec elles.

Les sections suivantes décrivent les gestes un par un, utiles quand une aide ne fonctionne plus.

## Ouvrir

1. Va sur `https://create.kahoot.it/creator`. Si une page de connexion s'affiche, attends que l'enseignant se connecte.
2. Dans « Crée un nouveau kahoot », choisis **Toile blanche**.
3. Ferme le panneau Kahoot! Assistant, à droite.

## Saisir une question

Clique sur le champ, tape, passe au suivant. Le texte tapé s'affiche bien avec les accents et les signes −, · et Δ.

- Titre : zone blanche du haut.
- Réponses : les quatre cases colorées. Clique au milieu de la case, pas sur l'icône d'image à droite.
- Bonne réponse : après la saisie, clique hors des champs, dans le fond violet à gauche de l'image, puis sur le cercle à droite de la bonne case. Une coche verte confirme. Évite la bande du haut : la barre de mise en forme du titre s'y affiche.

Le premier champ d'une nouvelle question met parfois une seconde à répondre : attends 1 à 2 secondes après l'ajout.

Une question qui passe sur deux lignes (environ 70 caractères et plus) décale les cases et l'image de 30 pixels vers le bas. Le cercle de bonne réponse n'est alors plus à sa place : contrôle la coche sur la vignette après chaque question longue.

La toile blanche commence par une diapo Quiz vide. Si la première question est d'un autre type, supprime cette diapo avec la corbeille à gauche, puis confirme.

Pour ajouter une question, clique sur **+ Ajouter** puis choisis le type dans le menu. Ce bouton descend à chaque question, jusqu'à ce que la colonne défile : relis sa position avant de cliquer, car un clic à l'ancienne position ne fait rien.

## Indices et exposants

Le titre et les réponses ont une barre de mise en forme avec **Format indice** et **Format exposant**. Sa position change selon le champ : active-la par son nom, sans clic de position. Après chargement de l'éditeur, définis une fois cette aide avec `javascript_tool` :

```js
window.__fmt = (label) => {
  const b = [...document.querySelectorAll('[aria-label]')]
    .find(x => x.getAttribute('aria-label') === label && x.getBoundingClientRect().width > 0);
  if (!b) return 'absent';
  ['mousedown', 'mouseup', 'click'].forEach(t =>
    b.dispatchEvent(new MouseEvent(t, { bubbles: true, cancelable: true, view: window })));
  return 'ok';
};
```

Puis enchaîne dans `browser_batch` : `type "U"`, `window.__fmt('Format indice')`, `type "1"`, `window.__fmt('Format indice')`, `type " + U"`, et ainsi de suite. Le deuxième appel désactive le format. Comme l'interception d'import, cette aide disparaît au rechargement de la page.

## Chrono

Ouvre le panneau **Propriétés**, à droite, et garde-le ouvert pour tout le kahoot : il reste affiché d'une question à l'autre. Le menu **Temps imparti** propose 5, 10, 15, 20, 30, 45, 60, 90, 120, 180 et 240 secondes.

La taille de la fenêtre change parfois en cours de construction (1512 × 786 ou 1528 × 746), ce qui décale le menu et fait choisir la mauvaise durée. Après avoir ouvert le menu, choisis la durée par son texte :

```js
window.__time = (label) => {
  const c = [...document.querySelectorAll('li,[role=option],button,div,span')].filter(x =>
    x.innerText && x.innerText.trim() === label && x.children.length <= 2 &&
    x.getBoundingClientRect().width > 0);
  const inMenu = c.filter(x => x.getBoundingClientRect().top > 150);
  const t = inMenu[inMenu.length - 1];
  if (!t) return 'absent';
  ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'].forEach(e =>
    t.dispatchEvent(new MouseEvent(e, { bubbles: true, cancelable: true, view: window })));
  return 'ok';
};
```

Les libellés sont `20 secondes`, `30 secondes`, `45 secondes`, `1 minute`, `1 minute 30 secondes` et `2 minutes`. Vérifie le champ après chaque réglage. Le panneau rétrécit la zone de question, donc relis les coordonnées des cases une fois ouvert. La vignette de gauche affiche le chrono de chaque question.

## Importer une image locale

Un clic sur « Importer un fichier » ouvre la fenêtre Windows, que les outils du navigateur ne peuvent pas piloter. Avant ce clic, intercepte l'ouverture avec `javascript_tool` :

```js
window.__fc = window.__fc || HTMLInputElement.prototype.click;
HTMLInputElement.prototype.click = function () {
  if (this.type === 'file') {
    this.style.display = 'block';
    if (!this.isConnected) document.body.appendChild(this);
    return;
  }
  return window.__fc.call(this);
};
```

Ensuite :

1. Clique sur « Importer un fichier ».
2. Trouve le champ avec `find` (requête « input type=file »). Sa référence change à chaque fois.
3. Envoie l'image avec `file_upload`.
4. Attends 3 secondes puis contrôle la vignette.

Si `find` ne trouve aucun champ, la fenêtre « Importer une image » est ouverte sans champ prêt : clique sur son bouton **Importer un fichier multimédia**, puis relance `find`.

L'interception reste active jusqu'au prochain rechargement de la page. Après un rechargement, réexécute-la. Le lien « Importer un fichier » se décale légèrement selon que la question a déjà du texte ou non.

### Corriger un kahoot existant

Ouvre `https://create.kahoot.it/creator/<id>`, redéfinis les aides, puis ferme le panneau Kahoot! Assistant. Pour remplacer une image, clique sur `window.__fmt('Supprimer le média')`, puis sur le bouton « Importer un fichier » (`.click()` suffit), trouve le champ et envoie l'image. Pour un titre : clic, `ctrl+a`, `Delete`, nouvelle saisie. Les réponses, les coches et les chronos ne bougent pas. Termine par **Enregistrer** : la visibilité et le dossier sont conservés. L'image de couverture ne suit pas les diapos.

### Puzzle

Dans le menu d'ajout, **Puzzle** se trouve sous **Vrai ou faux**. Sa diapo a une autre disposition : image à gauche, quatre réponses empilées à droite. Saisis les réponses dans le bon ordre, Kahoot les mélange pendant le jeu. Son chrono par défaut est de 60 s, et son menu commence à 20 s. Pour quitter un champ, clique dans le panneau de droite. La page de détail marque toutes les réponses comme bonnes, c'est normal.

## Banque d'images

Si une recherche ne donne rien d'exact, décris l'objet précisément : « carbon film resistor color bands » a trouvé de vrais résistors là où « résistance électronique » renvoyait des circuits imprimés.

Le « + » au centre ouvre la médiathèque, avec Getty Images et Unsplash. Le menu de gauche change de source. Clique dans la recherche, tape des mots-clés, valide, attends 2 à 3 secondes, regarde le résultat, puis clique sur l'image. Essaie le français pour les objets du quotidien : « multiprise » donne de bons résultats alors que « power strip » renvoie surtout du sport. Quand le résultat n'est pas pertinent, reformule plutôt que de prendre une image approximative.

## Tableur pour les gros kahoots

Dans le menu de **+ Ajouter**, l'onglet **Importer** donne accès à l'import par tableur.

1. Télécharge le modèle proposé par Kahoot : ses colonnes et ses chronos font référence.
2. Remplis-le avec le skill `anthropic-skills:xlsx`.
3. Importe-le par la même méthode que les images.
4. Contrôle que le nombre de questions correspond, puis ajoute les images.

Ce parcours n'a pas encore été testé : pour le premier usage, vérifie chaque étape par capture d'écran.

## Paramètres

Clique sur le nom du kahoot, en haut à gauche.

- **Titre** : clique, `ctrl+a`, tape. Kahoot a pu proposer un titre par IA.
- **Description** : clique, `ctrl+a`, `Delete`, sauf si une description sobre est utile.
- **Visibilité** : clique sur **Privé**, Public étant coché par défaut.
- **Enregistrer sous** : **Modifier**, clique sur le dossier de la classe pour y entrer, puis **Déplacer**.
- **Terminer** valide. L'image de couverture reprend souvent celle de la première question.

Clique ensuite sur **Enregistrer**, puis sur **Terminer** dans « Ton kahoot est prêt ». Ne lance pas la démonstration ou la présentation sauf demande de l'enseignant.

## Vérifier

L'identifiant du kahoot est dans l'URL de l'éditeur (`/creator/<id>`). La page de détail est `https://create.kahoot.it/details/<id>`.

Sa page affiche la visibilité. Le bouton **Afficher les réponses** dévoile les réponses, avec « bonne réponse » accolé à la correcte : lis-les avec `get_page_text`. L'API `/rest/kahoots/<id>` a répondu 403 depuis la page, inutile d'y revenir.
