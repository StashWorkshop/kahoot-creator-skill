// Aides pour l'éditeur Kahoot, à coller avec javascript_tool une fois l'éditeur
// chargé. Elles disparaissent au rechargement de la page.

// Empêche la fenêtre de fichiers Windows : le champ reste accessible à file_upload.
window.__fc = window.__fc || HTMLInputElement.prototype.click;
HTMLInputElement.prototype.click = function () {
  if (this.type === 'file') {
    this.style.display = 'block';
    if (!this.isConnected) document.body.appendChild(this);
    return;
  }
  return window.__fc.call(this);
};

const wait = (ms) => new Promise((r) => setTimeout(r, ms));
const visible = (x) => x.getBoundingClientRect().width > 0;
const mouse = (el, events) => events.forEach((t) =>
  el.dispatchEvent(new MouseEvent(t, { bubbles: true, cancelable: true, view: window })));
const fieldText = (el) => (el.innerText || '').replace(/​|\n/g, '').trim();

window.__fmt = (label) => {
  const b = [...document.querySelectorAll('[aria-label]')]
    .find((x) => x.getAttribute('aria-label') === label && visible(x));
  if (!b) return 'absent';
  mouse(b, ['mousedown', 'mouseup', 'click']);
  return 'ok';
};

// Écrit dans le champ actif. U_1 met le 1 en indice.
window.__w = async (s) => {
  for (const p of s.split(/(_[^ ,.?:]+)/).filter(Boolean)) {
    if (p[0] === '_') {
      window.__fmt('Format indice');
      await wait(60);
      document.execCommand('insertText', false, p.slice(1));
      await wait(60);
      window.__fmt('Format indice');
      await wait(60);
    } else {
      document.execCommand('insertText', false, p);
      await wait(60);
    }
  }
  return 'ok';
};

// Refuse d'écrire dans un champ rempli : un ajout de question raté aurait
// sinon collé le texte à la suite de la question précédente.
window.__title = async (s) => {
  const el = document.querySelector('[aria-label^="Titre de la question"]');
  if (!el) return 'pas de titre';
  if (fieldText(el)) return 'REFUS titre rempli';
  el.focus();
  mouse(el, ['mousedown', 'mouseup', 'click']);
  await wait(250);
  await window.__w(s);
  await wait(200);
  el.blur();
  await wait(300);
  return 'ok';
};

window.__fill = async (answers, good) => {
  const fields = [...document.querySelectorAll('[role=textbox],[contenteditable=true]')]
    .filter((x) => (x.getAttribute('aria-label') || '').includes('réponse '));
  if (fields.some(fieldText)) return 'REFUS réponses remplies';
  for (let i = 0; i < answers.length; i++) {
    const el = fields.find((x) => x.getAttribute('aria-label').includes('réponse ' + (i + 1)));
    el.focus();
    mouse(el, ['mousedown', 'mouseup', 'click']);
    await wait(250);
    await window.__w(answers[i]);
    await wait(200);
  }
  document.activeElement && document.activeElement.blur();
  await wait(500);
  return window.__fmt('Marquer la réponse ' + good + ' comme correcte.');
};

// Le menu du chrono doit être ouvert par un vrai clic avant cet appel.
window.__time = (label) => {
  const c = [...document.querySelectorAll('li,[role=option],button,div,span')]
    .filter((x) => x.innerText && x.innerText.trim() === label && x.children.length <= 2 && visible(x));
  const inMenu = c.filter((x) => x.getBoundingClientRect().top > 150);
  const t = inMenu[inMenu.length - 1];
  if (!t) return 'absent';
  mouse(t, ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click']);
  return 'ok';
};

// Remet le panneau Propriétés en haut, sinon le clic du chrono tombe sur un autre réglage.
window.__top = () => {
  [...document.querySelectorAll('*')]
    .filter((x) => x.getBoundingClientRect().left > 1100 && x.scrollTop > 0)
    .forEach((x) => { x.scrollTop = 0; });
  return 'ok';
};

window.__open = () => {
  const a = [...document.querySelectorAll('button')]
    .find((x) => x.innerText.trim() === 'Ajouter' && visible(x));
  if (!a) return 'absent';
  a.click();
  return 'ok';
};

// Ouvre l'import d'image ; il reste à trouver le champ et à appeler file_upload.
window.__imp = async () => {
  const i = [...document.querySelectorAll('button')]
    .find((x) => /^Importer un fichier$/.test(x.innerText.trim()) && visible(x));
  if (i) i.click();
  await wait(900);
  if (!document.querySelectorAll('input[type=file]').length) {
    const m = [...document.querySelectorAll('button')]
      .find((x) => /Importer un fichier multimédia/.test(x.innerText) && visible(x));
    if (m) m.click();
    await wait(600);
  }
  return { imp: !!i, inputs: document.querySelectorAll('input[type=file]').length };
};

// Remplace l'image de la diapo affichée.
window.__swap = async () => {
  window.__fmt('Supprimer le média');
  await wait(800);
  return window.__imp();
};

'ok';
