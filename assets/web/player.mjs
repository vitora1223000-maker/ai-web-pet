/* Independently implemented minimal frame player; no inherited pet pipeline. */
export class Timeline {
  constructor(manifest, draw, emit = () => {}) {
    this.m = manifest; this.draw = draw; this.emit = emit;
    this.reduced = false; this.destroyed = false; this.serial = 0;
  }
  play(action, {once = false} = {}, now = performance.now()) {
    if (this.destroyed) throw new Error('Player destroyed');
    const family = this.m.actions[action];
    if (!family) throw new Error(`Unknown action: ${action}`);
    this.serial++; this.action = action; this.family = family; this.once = once;
    this.stopping = false;
    this.setPhase(family.single ? 'single' : 'enter', now);
  }
  setPhase(phase, now) {
    this.phase = phase; this.clip = this.m.clips[this.family[phase]]; this.started = now;
    this.drawFrame(this.reduced ? this.clip.reduced_motion_frame : this.clip.sequence[0]);
    this.emit('state', {action: this.action, phase});
  }
  drawFrame(id) { this.draw(this.clip, id); }
  requestStop(now = performance.now()) {
    if (this.destroyed) return;
    if (this.reduced) this.finish(now);
    else this.stopping = true;
  }
  setReduced(value, now = performance.now()) {
    this.reduced = value;
    if (this.clip) {
      this.started = now;
      this.drawFrame(value ? this.clip.reduced_motion_frame : this.clip.sequence[0]);
      // A once preview must not hang when animation is disabled.
      if (value && (this.once || (this.phase === 'single' && this.action !== this.m.default_action))) this.finish(now);
    }
  }
  finish(now) {
    const action = this.action, serial = this.serial;
    this.emit('complete', {action});
    if (!this.destroyed && this.serial === serial) this.play(this.m.default_action, {}, now);
  }
  tick(now) {
    if (this.destroyed || !this.clip) return;
    if (this.reduced) {
      if (this.once || (this.phase === 'single' && this.action !== this.m.default_action)) this.finish(now);
      return;
    }
    const total = this.clip.durationsMs.reduce((a,b) => a+b, 0);
    let elapsed = Math.max(0, now - this.started);
    if (elapsed >= total) {
      if (this.phase === 'enter') this.setPhase(this.stopping ? 'exit' : 'loop', now);
      else if (this.phase === 'loop') {
        if (this.once || this.stopping) this.setPhase('exit', now);
        else { this.started = now; this.drawFrame(this.clip.sequence[0]); }
      } else if (this.phase === 'exit' || this.once || this.stopping || this.action !== this.m.default_action) this.finish(now);
      else { this.started = now; this.drawFrame(this.clip.sequence[0]); }
      // Background-tab gaps advance at most one phase; no callback burst.
      return;
    }
    let index = 0;
    while (index < this.clip.sequence.length-1 && elapsed >= this.clip.durationsMs[index]) {
      elapsed -= this.clip.durationsMs[index++];
    }
    this.drawFrame(this.clip.sequence[index]);
  }
  destroy() { this.destroyed = true; this.serial++; }
}

function assert(ok, text) { if (!ok) throw new Error(text); }
export function checkManifest(m) {
  const positive = n => Number.isSafeInteger(n) && n > 0;
  const anchor = (a,w,h) => a && Number.isFinite(a.x) && Number.isFinite(a.y) && a.x>=0 && a.y>=0 && a.x<=w && a.y<=h;
  assert(m?.schema_version === '0.1', 'Unsupported manifest');
  assert(positive(m.host?.width) && positive(m.host?.height) && anchor(m.host.anchor,m.host.width,m.host.height), 'Invalid host');
  assert(typeof m.ariaLabel === 'string' && m.ariaLabel.length, 'Missing ariaLabel');
  assert(m.clips && m.actions && m.actions[m.default_action]?.single, 'Missing default action');
  for (const c of Object.values(m.clips)) {
    assert(positive(c.width) && positive(c.height) && anchor(c.anchor,c.width,c.height), 'Invalid clip geometry');
    assert(Array.isArray(c.sequence) && c.sequence.length && c.sequence.length===c.durationsMs?.length && c.durationsMs.every(positive), 'Invalid timing');
    assert(c.frames && c.sequence.every(id=>Object.hasOwn(c.frames,id)) && Object.hasOwn(c.frames,c.reduced_motion_frame), 'Missing frame');
    for (const p of Object.values(c.frames)) assert(typeof p==='string' && /^[a-zA-Z0-9_./-]+$/.test(p) && !p.startsWith('/') && !p.split('/').includes('..'), 'Unsafe resource path');
  }
  for (const f of Object.values(m.actions)) {
    const keys = Object.keys(f).sort().join(',');
    assert(keys==='single' || keys==='enter,exit,loop', 'Invalid action family');
    assert(Object.values(f).every(id=>Object.hasOwn(m.clips,id)), 'Unknown clip');
  }
}

export async function loadPet({element, manifest}) {
  if (!element) throw new Error('element required');
  const url = new URL(manifest, document.baseURI);
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Manifest HTTP ${response.status}`);
  const m = await response.json(); checkManifest(m);
  const loaded = new Map();
  await Promise.all(Object.values(m.clips).flatMap(c => Object.values(c.frames).map(async path => {
    const resource = new URL(path,url);
    assert(resource.origin===url.origin, 'Cross-origin asset not allowed');
    const image = new Image(); image.src = resource.href;
    await image.decode();
    assert(image.naturalWidth===c.width && image.naturalHeight===c.height, 'Asset dimensions differ');
    loaded.set(path,resource.href);
  })));
  const host = document.createElement('div');
  host.setAttribute('role','img'); host.setAttribute('aria-label',m.ariaLabel);
  Object.assign(host.style,{width:`${m.host.width}px`,height:`${m.host.height}px`,position:'relative'});
  const image = document.createElement('img'); image.alt=''; image.draggable=false;
  Object.assign(image.style,{position:'absolute',pointerEvents:'none',maxWidth:'none'});
  host.append(image); element.append(host);
  const events = new EventTarget();
  const timeline = new Timeline(m,(c,id)=>{
    const src=loaded.get(c.frames[id]);
    if(image.src!==src) image.src=src;
    Object.assign(image.style,{width:`${c.width}px`,height:`${c.height}px`,left:`${m.host.anchor.x-c.anchor.x}px`,top:`${m.host.anchor.y-c.anchor.y}px`});
  },(name,detail)=>events.dispatchEvent(new CustomEvent(name,{detail})));
  const preference=matchMedia('(prefers-reduced-motion: reduce)');
  timeline.reduced=preference.matches;
  const change=()=>timeline.setReduced(preference.matches);
  preference.addEventListener('change',change);
  timeline.play(m.default_action);
  let raf;
  const tick=now=>{timeline.tick(now);if(!timeline.destroyed)raf=requestAnimationFrame(tick);};
  raf=requestAnimationFrame(tick);
  return {manifest:m,host,events,play:(...args)=>timeline.play(...args),requestStop:()=>timeline.requestStop(),
    destroy(){timeline.destroy();cancelAnimationFrame(raf);preference.removeEventListener('change',change);host.remove();}};
}
