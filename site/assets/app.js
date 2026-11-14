(function(){
  var d=document, b=d.body;
  function store(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v)}catch(e){return null}}

  // header
  var hdr=d.querySelector('.hdr');
  function onScroll(){if(hdr)hdr.classList.toggle('scrolled',window.scrollY>8)}
  window.addEventListener('scroll',onScroll,{passive:true});onScroll();
  var burger=d.querySelector('.burger');
  if(burger)burger.addEventListener('click',function(){var o=b.classList.toggle('menu-open');burger.setAttribute('aria-expanded',o)});
  d.querySelectorAll('.nav a').forEach(function(a){a.addEventListener('click',function(){b.classList.remove('menu-open')})});

  // language memory
  d.querySelectorAll('[data-lang]').forEach(function(a){a.addEventListener('click',function(){store('hf_lang',a.getAttribute('data-lang'))})});

  // reveal
  var rv=d.querySelectorAll('.rv');
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{rootMargin:'0px 0px -8% 0px'});
    rv.forEach(function(el){io.observe(el)});
  } else rv.forEach(function(el){el.classList.add('in')});

  // age gate
  var gate=d.querySelector('.gate');
  if(gate && store('hf_18')!=='1'){gate.classList.add('open');b.style.overflow='hidden';var yb=gate.querySelector('.yes');if(yb)setTimeout(function(){yb.focus()},50)}
  if(gate){
    gate.querySelector('.yes').addEventListener('click',function(){store('hf_18','1');gate.classList.remove('open');b.style.overflow=''});
  }

  // gallery filter
  var grid=d.querySelector('.masonry');
  d.querySelectorAll('.filters button').forEach(function(btn){
    btn.addEventListener('click',function(){
      d.querySelectorAll('.filters button').forEach(function(x){x.classList.remove('on')});
      btn.classList.add('on');
      var f=btn.getAttribute('data-f');
      grid.querySelectorAll('a').forEach(function(a){a.classList.toggle('hide',f!=='all'&&a.getAttribute('data-c')!==f)});
    });
  });

  // lightbox
  var lb=d.querySelector('.lb');
  if(lb){
    var img=lb.querySelector('img'),cnt=lb.querySelector('.cnt'),list=[],i=0;
    function vis(){return Array.prototype.filter.call(d.querySelectorAll('[data-lb]'),function(a){return !a.classList.contains('hide')})}
    function show(){var a=list[i];img.src=a.getAttribute('href');img.alt=(a.querySelector('img')||{}).alt||'';cnt.textContent=(i+1)+' / '+list.length}
    function open(a){list=vis();i=list.indexOf(a);show();lb.classList.add('open');b.style.overflow='hidden'}
    function close(){lb.classList.remove('open');b.style.overflow=''}
    function step(n){i=(i+n+list.length)%list.length;show()}
    d.querySelectorAll('[data-lb]').forEach(function(a){a.addEventListener('click',function(e){e.preventDefault();open(a)})});
    lb.querySelector('.x').addEventListener('click',close);
    lb.querySelector('.pv').addEventListener('click',function(e){e.stopPropagation();step(-1)});
    lb.querySelector('.nx').addEventListener('click',function(e){e.stopPropagation();step(1)});
    lb.addEventListener('click',function(e){if(e.target===lb)close()});
    d.addEventListener('keydown',function(e){if(!lb.classList.contains('open'))return;if(e.key==='Escape')close();if(e.key==='ArrowLeft')step(-1);if(e.key==='ArrowRight')step(1)});
    var sx=null;
    lb.addEventListener('touchstart',function(e){sx=e.touches[0].clientX},{passive:true});
    lb.addEventListener('touchend',function(e){if(sx===null)return;var dx=e.changedTouches[0].clientX-sx;if(Math.abs(dx)>50)step(dx<0?1:-1);sx=null});
  }

  // forms: Web3Forms if a key is set, otherwise open the e-mail app
  d.querySelectorAll('form.form').forEach(function(f){
    f.addEventListener('submit',function(e){
      e.preventDefault();
      var key=f.getAttribute('data-key')||'', to=f.getAttribute('data-to');
      var fd=new FormData(f), lines=[];
      fd.forEach(function(v,k){if(k!=='access_key'&&k!=='subject'&&k!=='botcheck'&&v)lines.push(k+': '+v)});
      if(key && key.indexOf('VLOZ')!==0){
        fd.append('access_key',key);
        var fallback=function(){location.href='mailto:'+to+'?subject='+encodeURIComponent(f.getAttribute('data-subj'))+'&body='+encodeURIComponent(lines.join('\n'))};
        fetch('https://api.web3forms.com/submit',{method:'POST',headers:{'Accept':'application/json'},body:fd}).then(function(r){return r.json()}).then(function(d){if(d&&d.success){f.classList.add('sent');f.reset()}else fallback()}).catch(fallback);
      } else {
        location.href='mailto:'+to+'?subject='+encodeURIComponent(f.getAttribute('data-subj'))+'&body='+encodeURIComponent(lines.join('\n'));
      }
    });
  });

  if(location.hash==='#casting'){var sel=d.getElementById('f-topic');if(sel&&sel.options.length>4){sel.selectedIndex=4;setTimeout(function(){var f=sel.closest('form');if(f)f.scrollIntoView({behavior:'smooth',block:'start'})},300)}}

  var y=d.querySelector('.yr'); if(y)y.textContent=new Date().getFullYear();
})();
