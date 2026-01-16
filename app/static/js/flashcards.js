const FLASHCARD_ENDPOINT = "/api/flashcards";
const FLASHCARD_SET_ENDPOINT = "/api/flashcards/sets";
const FLASHCARD_PROGRESS_ENDPOINT = "/api/flashcards/progress";

const state = {
  store: null,
  activeSet: null,
  index: 0,
  flipped: false,
  streak: 0,
  points: 0,
  sessionPoints: 0,
};

const elements = {
  library: document.getElementById("flashcards-library"),
  grid: document.getElementById("flashcards-grid"),
  stats: document.getElementById("flashcards-stats"),
  study: document.getElementById("flashcards-study"),
  create: document.getElementById("flashcards-create"),
  front: document.getElementById("flashcards-front"),
  back: document.getElementById("flashcards-back"),
  card: document.getElementById("flashcards-card"),
  progress: document.getElementById("flashcards-progress"),
  createButton: document.getElementById("create-deck-btn"),
  backButton: document.getElementById("back-to-library"),
  cancelCreate: document.getElementById("cancel-create"),
  flipButton: document.getElementById("flip-card"),
  knownButton: document.getElementById("mark-known"),
  reviewButton: document.getElementById("mark-review"),
  nextButton: document.getElementById("next-card"),
  prevButton: document.getElementById("prev-card"),
  form: document.getElementById("flashcards-form"),
  deckTitle: document.getElementById("deck-title"),
  deckDescription: document.getElementById("deck-description"),
  deckTags: document.getElementById("deck-tags"),
  deckCards: document.getElementById("deck-cards"),
};

const parseCards = (raw) => {
  return raw
    .split("\n")
    .map((line) => line.split("|").map((part) => part.trim()))
    .filter((parts) => parts.length === 2 && parts[0] && parts[1])
    .map(([front, back]) => ({ front, back }));
};

const setView = (view) => {
  elements.library.classList.toggle("d-none", view !== "library");
  elements.study.classList.toggle("d-none", view !== "study");
  elements.create.classList.toggle("d-none", view !== "create");
};

const badgeForPoints = (points) => {
  if (points >= 80) return "Legend";
  if (points >= 40) return "Ace";
  if (points >= 20) return "Spark";
  return "Rookie";
};

const renderStats = () => {
  if (!state.store) return;
  const stats = state.store.stats || {};
  const badge = badgeForPoints(stats.total_points || 0);
  elements.stats.innerHTML = `
    <div class="flashcards-stat">
      <span>🏅 ${badge}</span>
      <small>Total points: ${stats.total_points || 0}</small>
    </div>
    <div class="flashcards-stat">
      <span>🔥 Best streak</span>
      <small>${stats.best_streak || 0}</small>
    </div>
    <div class="flashcards-stat">
      <span>🎯 Sessions</span>
      <small>${stats.sessions || 0}</small>
    </div>
  `;
};

const renderLibrary = () => {
  elements.grid.innerHTML = "";
  if (!state.store.sets.length) {
    elements.grid.innerHTML = "<p class=\"text-white\">No decks yet. Create one to get started.</p>";
    return;
  }
  state.store.sets.forEach((deck) => {
    const card = document.createElement("button");
    card.className = "flashcards-deck";
    card.type = "button";
    card.innerHTML = `
      <h3>${deck.title}</h3>
      <p>${deck.description || "No description yet."}</p>
      <div class="flashcards-deck-meta">
        <span>${deck.cards.length} cards</span>
        <span>${deck.difficulty}</span>
      </div>
      <div class="flashcards-deck-tags">${(deck.tags || [])
        .map((tag) => `<span>#${tag}</span>`)
        .join("")}</div>
    `;
    card.addEventListener("click", () => startStudy(deck.id));
    elements.grid.appendChild(card);
  });
};

const renderCard = () => {
  if (!state.activeSet) return;
  const card = state.activeSet.cards[state.index];
  elements.front.textContent = card.front;
  elements.back.textContent = card.back;
  elements.card.classList.toggle("flipped", state.flipped);
  elements.progress.textContent = `${state.index + 1} / ${state.activeSet.cards.length} · Points ${state.sessionPoints} · Streak ${state.streak}`;
};

const updateProgress = async () => {
  if (state.sessionPoints <= 0) return;
  await fetch(FLASHCARD_PROGRESS_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ points: state.sessionPoints, streak: state.streak }),
  });
};

const startStudy = (id) => {
  state.activeSet = state.store.sets.find((deck) => deck.id === id);
  state.index = 0;
  state.flipped = false;
  state.streak = 0;
  state.sessionPoints = 0;
  setView("study");
  renderCard();
};

const nextCard = () => {
  if (!state.activeSet) return;
  state.index = (state.index + 1) % state.activeSet.cards.length;
  state.flipped = false;
  renderCard();
};

const prevCard = () => {
  if (!state.activeSet) return;
  state.index = (state.index - 1 + state.activeSet.cards.length) % state.activeSet.cards.length;
  state.flipped = false;
  renderCard();
};

const flipCard = () => {
  state.flipped = !state.flipped;
  renderCard();
};

const markKnown = () => {
  state.streak += 1;
  state.sessionPoints += 5;
  nextCard();
};

const markReview = () => {
  state.streak = 0;
  state.sessionPoints = Math.max(0, state.sessionPoints - 1);
  nextCard();
};

const setupEvents = () => {
  elements.createButton.addEventListener("click", () => setView("create"));
  elements.backButton.addEventListener("click", async () => {
    await updateProgress();
    setView("library");
    fetchStore();
  });
  elements.cancelCreate.addEventListener("click", () => setView("library"));
  elements.flipButton.addEventListener("click", flipCard);
  elements.knownButton.addEventListener("click", markKnown);
  elements.reviewButton.addEventListener("click", markReview);
  elements.nextButton.addEventListener("click", nextCard);
  elements.prevButton.addEventListener("click", prevCard);

  elements.form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const cards = parseCards(elements.deckCards.value);
    const payload = {
      title: elements.deckTitle.value.trim(),
      description: elements.deckDescription.value.trim(),
      tags: elements.deckTags.value
        .split(",")
        .map((tag) => tag.trim())
        .filter(Boolean),
      cards,
    };
    const response = await fetch(FLASHCARD_SET_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (response.ok) {
      elements.form.reset();
      await fetchStore();
      setView("library");
    } else {
      alert("Deck creation failed. Please check your entries.");
    }
  });

  document.addEventListener("keydown", (event) => {
    if (elements.study.classList.contains("d-none")) return;
    if (event.key === "ArrowLeft") prevCard();
    if (event.key === "ArrowRight") nextCard();
    if (event.key === "ArrowUp" || event.key === "ArrowDown" || event.key === " ") {
      event.preventDefault();
      flipCard();
    }
  });
};

const fetchStore = async () => {
  const response = await fetch(FLASHCARD_ENDPOINT);
  state.store = await response.json();
  state.store.sets = state.store.sets || [];
  renderStats();
  renderLibrary();
};

document.addEventListener("DOMContentLoaded", () => {
  setupEvents();
  fetchStore();
});
