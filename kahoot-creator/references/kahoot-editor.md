# Driving the Kahoot editor

Notes taken from a real creation in Edge, at 1528 × 746. The interface can change: take a screenshot at the start, and again as soon as an action does not give the expected result. The coordinates on this page are only landmarks. Group the actions with `browser_batch` to save time.

## Fast method

Once the editor is loaded, paste [scripts/editor_helpers.js](../scripts/editor_helpers.js) with `javascript_tool`. A Quiz question is then built like this, in a single `browser_batch`:

1. `window.__open()`, then a real click on the type in the menu (Quiz near (302, 200), "Vrai ou faux" (True or false) near (462, 195)). A scripted click on the type does not work.
2. `window.__top()`, a real click on the timer menu near (1272, 303), then `window.__time('1 minute')`.
3. `await window.__title('… U_1 …')`, then, only if the answer is `ok`, `await window.__fill([a, b, c, d], n)`.
4. Screenshot to check the text, the check mark and the timer.
5. `await window.__imp()`, `find` "input type=file", `file_upload`.

`__title` and `__fill` refuse fields that are already filled: this is the sign that adding the question failed. To correct a field, use the keyboard (`ctrl+a`, `Delete`, typing), because `execCommand('delete')` erases nothing. On a new kahoot, slide 1 is already a Quiz: do not add it. These helpers do not replace manual entry for puzzles, whose fields have not yet been tested with them.

The following sections describe the actions one by one, useful when a helper no longer works.

## Open

1. Go to `https://create.kahoot.it/creator`. If a login page appears, wait for the teacher to log in.
2. In "Crée un nouveau kahoot" (Create a new kahoot), choose **Toile blanche** (Blank canvas).
3. Close the Kahoot! Assistant panel, on the right.

## Enter a question

Click the field, type, move to the next one. The typed text displays correctly with accents and the signs −, · and Δ.

- Title: white area at the top.
- Answers: the four colored boxes. Click in the middle of the box, not on the image icon on the right.
- Correct answer: after typing, click outside the fields, in the purple background to the left of the image, then on the circle to the right of the correct box. A green check mark confirms. Avoid the top strip: the formatting bar of the title appears there.

The first field of a new question sometimes takes a second to respond: wait 1 to 2 seconds after adding it.

A question that runs over two lines (about 70 characters and more) shifts the boxes and the image 30 pixels down. The correct-answer circle is then no longer in its place: check the check mark on the thumbnail after each long question.

The blank canvas starts with an empty Quiz slide. If the first question is of another type, delete this slide with the trash icon on the left, then confirm.

To add a question, click **+ Ajouter** (Add) then choose the type in the menu. This button moves down with each question, until the column scrolls: read its position again before clicking, because a click at the old position does nothing.

## Subscripts and superscripts

The title and the answers have a formatting bar with **Format indice** (subscript format) and **Format exposant** (superscript format). Its position changes depending on the field: activate it by its name, without a position click. After the editor loads, define this helper once with `javascript_tool`:

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

Then chain in `browser_batch`: `type "U"`, `window.__fmt('Format indice')`, `type "1"`, `window.__fmt('Format indice')`, `type " + U"`, and so on. The second call turns the format off. Like the import interception, this helper disappears when the page reloads.

## Timer

Open the **Propriétés** (Properties) panel, on the right, and keep it open for the whole kahoot: it stays displayed from one question to the next. The **Temps imparti** (Time limit) menu offers 5, 10, 15, 20, 30, 45, 60, 90, 120, 180 and 240 seconds.

The window size sometimes changes during the build (1512 × 786 or 1528 × 746), which shifts the menu and makes you pick the wrong duration. After opening the menu, choose the duration by its text:

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

The labels are `20 secondes`, `30 secondes`, `45 secondes`, `1 minute`, `1 minute 30 secondes` and `2 minutes`. Check the field after each setting. The panel shrinks the question area, so read the coordinates of the boxes again once it is open. The thumbnail on the left shows the timer of each question.

## Import a local image

A click on "Importer un fichier" (Import a file) opens the Windows dialog, which the browser tools cannot drive. Before this click, intercept the opening with `javascript_tool`:

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

Then:

1. Click "Importer un fichier".
2. Find the field with `find` (query "input type=file"). Its reference changes every time.
3. Send the image with `file_upload`.
4. Wait 3 seconds then check the thumbnail.

If `find` finds no field, the "Importer une image" (Import an image) window is open without a ready field: click its **Importer un fichier multimédia** (Import a media file) button, then run `find` again.

The interception stays active until the next page reload. After a reload, run it again. The "Importer un fichier" link shifts slightly depending on whether the question already has text or not.

### Correct an existing kahoot

Open `https://create.kahoot.it/creator/<id>`, define the helpers again, then close the Kahoot! Assistant panel. To replace an image, click with `window.__fmt('Supprimer le média')`, then on the "Importer un fichier" button (`.click()` is enough), find the field and send the image. For a title: click, `ctrl+a`, `Delete`, type again. The answers, the check marks and the timers do not move. Finish with **Enregistrer** (Save): the visibility and the folder are kept. The cover image does not follow the slides.

### Puzzle

In the add menu, **Puzzle** is under **Vrai ou faux** (True or false). Its slide has a different layout: image on the left, four answers stacked on the right. Enter the answers in the right order, Kahoot shuffles them during the game. Its default timer is 60 s, and its menu starts at 20 s. To leave a field, click in the right panel. The details page marks all the answers as correct, this is normal.

## Image library

If a search gives nothing exact, describe the object precisely: "carbon film resistor color bands" found real resistors where "résistance électronique" returned printed circuit boards.

The "+" in the center opens the media library, with Getty Images and Unsplash. The left menu changes the source. Click in the search, type keywords, confirm, wait 2 to 3 seconds, look at the result, then click the image. Try French for everyday objects: "multiprise" gives good results while "power strip" returns mostly sports. When the result is not relevant, rephrase rather than take an approximate image.

## Spreadsheet for large kahoots

In the **+ Ajouter** (Add) menu, the **Importer** (Import) tab gives access to the spreadsheet import.

1. Download the template offered by Kahoot: its columns and its timers are the reference.
2. Fill it in with the `anthropic-skills:xlsx` skill.
3. Import it with the same method as the images.
4. Check that the number of questions matches, then add the images.

This path has not been tested yet: for the first use, check each step with a screenshot.

## Settings

Click the name of the kahoot, at the top left.

- **Titre** (Title): click, `ctrl+a`, type. Kahoot may have suggested an AI title.
- **Description**: click, `ctrl+a`, `Delete`, unless a plain description is useful.
- **Visibilité** (Visibility): click **Privé** (Private), since Public is checked by default.
- **Enregistrer sous** (Save to): **Modifier** (Edit), click the class folder to enter it, then **Déplacer** (Move).
- **Terminer** (Done) confirms. The cover image often reuses the one from the first question.

Then click **Enregistrer** (Save), then **Terminer** (Done) in "Ton kahoot est prêt" (Your kahoot is ready). Do not start the demo or the presentation unless the teacher asks.

## Check

The kahoot identifier is in the editor URL (`/creator/<id>`). The details page is `https://create.kahoot.it/details/<id>`.

Its page shows the visibility. The **Afficher les réponses** (Show answers) button reveals the answers, with "bonne réponse" (correct answer) next to the correct one: read them with `get_page_text`. The `/rest/kahoots/<id>` API returned 403 from the page, no point going back to it.
