let payload = null;
let currentIndex = 0;
let rotationTimer = null;

function setStatus(msg){document.getElementById("statusBar").textContent = msg || "";}

function renderTable(view, showGrid, fontScale){
  const table = document.getElementById("planTable"); table.innerHTML = "";
  if(!view || !view.rows || !view.rows.length){table.innerHTML = "<tr><td>Keine Daten</td></tr>"; return;}
  for(const row of view.rows){
    const tr = document.createElement("tr");
    for(const cell of row){
      const td = document.createElement("td"); td.textContent = cell || "";
      td.style.border = showGrid ? "1px solid var(--border)" : "none";
      td.style.fontSize = `calc(clamp(1rem,2.2vw,3rem) * ${fontScale})`;
      tr.appendChild(td);
    }
    table.appendChild(tr);
  }
}

function showView(idx){
  if(!payload || !payload.views || !payload.views.length){setStatus(payload?.error || "Keine aktiven Views.");return;}
  currentIndex = idx % payload.views.length;
  const view = payload.views[currentIndex];
  document.getElementById("mainTitle").textContent = payload.title || "Planungsanzeige";
  document.getElementById("viewTitle").textContent = view.title || "-";
  document.getElementById("updatedAt").textContent = payload.updated_at || "-";
  renderTable(view, payload.show_grid, payload.font_scale);
  setStatus(payload.error ? `Hinweis: ${payload.error}` : "");
  clearTimeout(rotationTimer);
  rotationTimer = setTimeout(() => showView((currentIndex+1) % payload.views.length), (view.duration_sec || 15) * 1000);
}

async function loadData(){
  try{ const res = await fetch('/api/display-data'); payload = await res.json(); showView(0); }
  catch(_){ setStatus('Fehler beim Laden der Anzeige-Daten.'); }
}

loadData();
setInterval(loadData, 30000);
