const viewsContainer = document.getElementById('viewsContainer');
const addViewBtn = document.getElementById('addViewBtn');
const setupForm = document.getElementById('setupForm');
const viewsInput = document.getElementById('views_json');
const reloadFilesBtn = document.getElementById('reloadFilesBtn');
const shareLinkInput = document.getElementById('share_link');
const selectedFile = document.getElementById('selected_file');

let views = Array.isArray(window.INIT_VIEWS) ? window.INIT_VIEWS : [];

function mkInput(label, value, onChange, type='text'){
  const wrap = document.createElement('label'); wrap.textContent = label;
  const input = document.createElement('input'); input.type = type; input.value = value ?? '';
  input.addEventListener('input', ()=>onChange(input.value)); wrap.appendChild(input); return wrap;
}

function mkCheckbox(label, checked, onChange){
  const wrap = document.createElement('label'); wrap.className = 'toggle';
  const cb = document.createElement('input'); cb.type = 'checkbox'; cb.checked = !!checked;
  cb.addEventListener('change', ()=>onChange(cb.checked)); wrap.appendChild(cb); wrap.appendChild(document.createTextNode(label)); return wrap;
}

function renderViews(){
  viewsContainer.innerHTML = '';
  views.forEach((v, idx)=>{
    const card = document.createElement('div'); card.className='view-card';
    const head = document.createElement('div'); head.className='view-head';
    const title = document.createElement('strong'); title.textContent = `View ${idx+1}`;
    const del = document.createElement('button'); del.type='button'; del.className='delete-btn'; del.textContent='Löschen';
    del.onclick=()=>{views.splice(idx,1); renderViews();};
    head.appendChild(title); head.appendChild(del); card.appendChild(head);
    card.appendChild(mkInput('Titel', v.title, val=>v.title=val));
    card.appendChild(mkInput('Sheet', v.sheet, val=>v.sheet=val));
    card.appendChild(mkInput('Zellbereich (A1:G12)', v.range, val=>v.range=val));
    card.appendChild(mkInput('Dauer (Sekunden)', v.duration_sec ?? 15, val=>v.duration_sec=Number(val||15), 'number'));
    card.appendChild(mkCheckbox('Aktiv', v.active !== false, val=>v.active=val));
    viewsContainer.appendChild(card);
  });
}

addViewBtn.addEventListener('click', ()=>{ views.push({title:'Neue View',sheet:'Sheet1',range:'A1:G12',duration_sec:15,active:true}); renderViews(); });
setupForm.addEventListener('submit', ()=>{ viewsInput.value = JSON.stringify(views); });

reloadFilesBtn.addEventListener('click', async ()=>{
  const share = (shareLinkInput.value || '').trim(); if(!share) return;
  reloadFilesBtn.disabled = true;
  try{
    const res = await fetch(`/api/files?share_link=${encodeURIComponent(share)}`);
    const data = await res.json();
    const current = selectedFile.value;
    selectedFile.innerHTML = '<option value="">-- bitte wählen --</option>';
    (data.files || []).forEach(f=>{
      const opt = document.createElement('option'); opt.value=f; opt.textContent=f; if(f===current) opt.selected=true; selectedFile.appendChild(opt);
    });
  } finally { reloadFilesBtn.disabled = false; }
});

renderViews();
