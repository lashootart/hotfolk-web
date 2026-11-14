(function(){
  var root=document.getElementById('vote'); if(!root) return;
  var C=JSON.parse(root.getAttribute('data-cfg'));
  var api=C.api, live=api && api.indexOf('http')===0;
  var cards=root.querySelectorAll('.vcard'), form=root.querySelector('.vform'), msg=root.querySelector('.vmsg');
  var totalEl=root.querySelector('.vtotal b'), cdEl=root.querySelector('.vcd');
  var chosen=null, ended=Date.now()>new Date(C.end).getTime();
  function store(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v)}catch(e){return null}}

  function show(counts){
    if(!counts) return;
    var t=0; C.models.forEach(function(m){t+=counts[m]||0});
    cards.forEach(function(c){
      var id=c.getAttribute('data-id'), n=counts[id]||0, p=t?Math.round(n*100/t):0;
      c.querySelector('.vbar i').style.width=p+'%';
      c.querySelector('.vpct').textContent=p+' %';
      var f=C.t.votes;c.querySelector('.vn').textContent=n+' '+(n===1?f[0]:(n>=2&&n<=4?f[1]:f[2]));
    });
    if(totalEl) totalEl.textContent=t;
    root.classList.add('has-res');
  }
  function load(){ if(!live) return; fetch(api+'?round='+encodeURIComponent(C.round)).then(function(r){return r.json()}).then(function(d){if(d&&d.ok)show(d.counts)}).catch(function(){}); }

  function tick(){
    var ms=new Date(C.end).getTime()-Date.now();
    if(ms<=0){ cdEl.textContent=C.t.closed; ended=true; root.classList.add('ended'); return; }
    var d=Math.floor(ms/864e5), h=Math.floor(ms%864e5/36e5), m=Math.floor(ms%36e5/6e4);
    cdEl.textContent=d+' '+C.t.left[0]+'  '+h+' '+C.t.left[1]+'  '+m+' '+C.t.left[2];
  }
  if(cdEl){ tick(); setInterval(tick,30000); }

  var voted=store('hf_vote_'+C.round);
  if(voted){ root.classList.add('voted'); var vc=root.querySelector('.vcard[data-id="'+voted+'"]'); if(vc) vc.classList.add('mine'); }
  if(!live){ root.classList.add('soon'); }

  cards.forEach(function(c){
    c.querySelector('.vbtn').addEventListener('click',function(){
      if(ended||!live||root.classList.contains('voted')) return;
      chosen=c.getAttribute('data-id');
      cards.forEach(function(x){x.classList.toggle('sel',x===c)});
      form.querySelector('.vchosen').textContent=c.querySelector('h3').textContent;
      form.hidden=false; msg.hidden=true;
      form.scrollIntoView({behavior:'smooth',block:'center'});
      setTimeout(function(){form.querySelector('input[name=name]').focus({preventScroll:true})},400);
    });
  });

  form.addEventListener('submit',function(e){
    e.preventDefault(); if(!chosen) return;
    var b=form.querySelector('button[type=submit]'), lbl=b.textContent;
    var data={round:C.round,model:chosen,name:form.name.value,email:form.email.value,lang:C.lang,consent:form.consent.checked,website:form.website.value};
    b.disabled=true; b.textContent=C.t.sending;
    fetch(api,{method:'POST',headers:{'Content-Type':'text/plain;charset=utf-8'},body:JSON.stringify(data)})
      .then(function(r){return r.json()})
      .then(function(d){
        msg.hidden=false;
        if(d.ok){ msg.className='vmsg ok'; msg.textContent=C.t.ok; form.hidden=true; store('hf_vote_'+C.round,chosen); root.classList.add('voted');
          cards.forEach(function(x){x.classList.toggle('mine',x.getAttribute('data-id')===chosen);x.classList.remove('sel')}); }
        else if(d.error==='duplicate'){ msg.className='vmsg warn'; msg.textContent=C.t.dup; }
        else { msg.className='vmsg err'; msg.textContent=C.t.err; }
        if(d.counts) show(d.counts);
      })
      .catch(function(){ msg.hidden=false; msg.className='vmsg err'; msg.textContent=C.t.err; })
      .then(function(){ b.disabled=false; b.textContent=lbl; });
  });

  if(ended) root.classList.add('ended');
  load(); if(live) setInterval(load,60000);
})();
