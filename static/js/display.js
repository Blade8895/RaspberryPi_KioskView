let payload = null;
let currentIndex = 0;
let rotationTimer = null;

function setStatus(msg){document.getElementById("statusBar").textContent = msg || "";}

function mapBorderStyle(style){
  const map = {
    thin: '1px solid',
    medium: '2px solid',
    thick: '3px solid',
    dashed: '1px dashed',
    dotted: '1px dotted',
    double: '3px double'
  };
  return map[style] || null;
}

function applyCellStyle(td, cellStyle, showGrid, fontScale){
  td.style.fontSize = `calc(clamp(1rem,2.2vw,3rem) * ${fontScale})`;
  td.style.border = showGrid ? "1px solid var(--grid-border)" : "none";

  if(!cellStyle) return;

  const font = cellStyle.font || {};
  if(font.bold) td.style.fontWeight = '700';
  if(font.italic) td.style.fontStyle = 'italic';
  if(font.name) td.style.fontFamily = font.name;
  if(font.size) td.style.fontSize = `${font.size}pt`;
  if(font.color) td.style.color = font.color;

  const fill = cellStyle.fill || {};
  if(fill.background) td.style.backgroundColor = fill.background;

  const alignment = cellStyle.alignment || {};
  if(alignment.horizontal) td.style.textAlign = alignment.horizontal;
  if(alignment.vertical) {
    const verticalMap = {center: 'middle', distributed: 'middle', justify: 'top'};
    td.style.verticalAlign = verticalMap[alignment.vertical] || alignment.vertical;
  }
  if(alignment.wrap_text) td.style.whiteSpace = 'pre-wrap';

  const border = cellStyle.border || {};
  for (const side of ['left','right','top','bottom']) {
    const sideCfg = border[side] || {};
    const cssBorder = mapBorderStyle(sideCfg.style);
    if(cssBorder){
      td.style[`border${side.charAt(0).toUpperCase() + side.slice(1)}`] = `${cssBorder} ${sideCfg.color || 'currentColor'}`;
    }
  }
}

function applyLayout(table, layout){
  if(!layout) return;

  const existingColgroup = table.querySelector('colgroup');
  if(existingColgroup) existingColgroup.remove();

  if(Array.isArray(layout.column_widths) && layout.column_widths.length){
    const colgroup = document.createElement('colgroup');
    for(const width of layout.column_widths){
      const col = document.createElement('col');
      if(width){
        const px = Math.max(20, (Number(width) * 7) + 5);
        col.style.width = `${px}px`;
      }
      colgroup.appendChild(col);
    }
    table.appendChild(colgroup);
  }
}

function renderTable(view, showGrid, fontScale){
  const table = document.getElementById("planTable");
  table.innerHTML = "";

  document.body.classList.toggle('theme-override', !!view?.theme_override);

  const cells = Array.isArray(view?.cells) ? view.cells : null;
  if(!cells || !cells.length){
    const rows = view?.rows || [];
    if(!rows.length){table.innerHTML = "<tr><td>Keine Daten</td></tr>"; return;}
    for(const row of rows){
      const tr = document.createElement("tr");
      for(const cellValue of row){
        const td = document.createElement("td");
        td.textContent = cellValue || "";
        applyCellStyle(td, null, showGrid, fontScale);
        tr.appendChild(td);
      }
      table.appendChild(tr);
    }
    return;
  }

  applyLayout(table, view.layout);

  cells.forEach((row, rowIdx)=>{
    const tr = document.createElement('tr');

    const rowHeights = view.layout?.row_heights || [];
    const rowHeight = rowHeights[rowIdx];
    if(rowHeight){
      tr.style.height = `${Math.max(16, Number(rowHeight) * 1.333)}px`;
    }

    row.forEach(cell=>{
      if(cell?.merge?.hidden) return;
      const td = document.createElement('td');
      td.textContent = cell?.value || '';

      if(cell?.merge?.row_span > 1) td.rowSpan = cell.merge.row_span;
      if(cell?.merge?.col_span > 1) td.colSpan = cell.merge.col_span;

      applyCellStyle(td, cell?.style, showGrid, fontScale);
      tr.appendChild(td);
    });

    table.appendChild(tr);
  });
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
