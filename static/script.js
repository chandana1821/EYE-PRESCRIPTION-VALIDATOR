const form = document.querySelector('#prescription-form');
const result = document.querySelector('#result');
const labels = {od_sph:'Right Eye SPH',od_cyl:'Right Eye CYL',od_axis:'Right Eye Axis',os_sph:'Left Eye SPH',os_cyl:'Left Eye CYL',os_axis:'Left Eye Axis'};

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  result.hidden = true;
  document.querySelectorAll('.fields input').forEach((input) => input.removeAttribute('aria-invalid'));
  const data = Object.fromEntries(new FormData(form).entries());
  try {
    const response = await fetch('/validate', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
    const payload = await response.json();
    result.hidden = false;
    if (!response.ok) {
      result.className = 'result error';
      result.replaceChildren();
      const title = document.createElement('strong'); title.textContent = 'Please check the highlighted values'; result.append(title);
      const list = document.createElement('ul');
      Object.entries(payload.errors || {}).forEach(([key,message]) => {
        const item = document.createElement('li'); item.textContent = `${labels[key] || 'Request'}: ${message}`; list.append(item);
        if (labels[key]) document.getElementById(key).setAttribute('aria-invalid','true');
      });
      result.append(list); return;
    }
    result.className = 'result success';
    result.replaceChildren();
    const title = document.createElement('strong'); title.textContent = 'Prescription looks good'; result.append(title);
    const summary = document.createElement('span'); summary.textContent = 'All six values are within the permitted ranges.'; result.append(summary);
    const output = document.createElement('div'); output.className = 'prescription-output';
    Object.entries(payload.prescription).forEach(([key,value]) => {
      const cell = document.createElement('div'); const label = document.createElement('b');
      label.textContent = key.replace('_',' ').toUpperCase(); cell.append(label, document.createTextNode(String(value))); output.append(cell);
    });
    result.append(output);
  } catch {
    result.hidden = false; result.className = 'result error'; result.textContent = 'Unable to reach the validator. Please try again.';
  }
});

form.addEventListener('reset', () => {
  result.hidden = true; result.replaceChildren();
  document.querySelectorAll('.fields input').forEach((input) => input.removeAttribute('aria-invalid'));
});
