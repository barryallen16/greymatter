// Job-form autofill bookmarklet — pure JS, no page, no server.
// Use: paste the whole file into devtools console, or save it as a bookmark URL
// prefixed with  javascript:  then click it on any application tab.
// First run per site prompts for your details once (cached in that site's
// localStorage). Only empty fields are filled; review before submitting.
function jdAutofill(){
  var K='jd-autofill-v1',P=null;
  try{P=JSON.parse(localStorage.getItem(K)||'null')}catch(e){P=null}
  if(P&&!confirm('Autofill with saved details?\nOK = fill, Cancel = re-enter them.'))P=null;
  function ask(m){var r=prompt(m,'');return r===null?'':r.trim()}
  if(!P){
    P={first:ask('First name:'),last:ask('Last name:'),email:ask('Email:'),phone:ask('Phone:'),loc:ask('Current location (City, State):'),li:ask('LinkedIn URL:'),gh:ask('GitHub URL:'),web:ask('Portfolio / website URL:')};
    try{localStorage.setItem(K,JSON.stringify(P))}catch(e){}
  }
  P.full=(P.first+' '+P.last).trim();
  var F=[
    [/first\s?name/i,'first'],[/last\s?name|sur\s?name|family\s?name/i,'last'],
    [/full\s?name/i,'full'],[/e-?mail/i,'email'],[/phone|mobile/i,'phone'],
    [/linkedin/i,'li'],[/github/i,'gh'],[/portfolio|website|personal\s*site/i,'web'],
    [/locat|city|address|based|country/i,'loc']
  ];
  function set(el,v){
    if(!v||el.value||el.disabled||el.readOnly)return 0;
    try{
      var d=Object.getOwnPropertyDescriptor(Object.getPrototypeOf(el),'value'),
          s=(d&&d.set)||Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;
      s.call(el,v);
    }catch(e){el.value=v}
    el.dispatchEvent(new Event('input',{bubbles:true}));
    el.dispatchEvent(new Event('change',{bubbles:true}));
    return 1;
  }
  var n=0;
  Array.prototype.forEach.call(document.querySelectorAll('input,textarea'),function(el){
    if(el.tagName==='INPUT'&&!/^(text|email|tel|url|search|number)$/i.test(el.type||''))return;
    if(el.type==='email'&&P.email){n+=set(el,P.email);return}
    if(el.type==='tel'&&P.phone){n+=set(el,P.phone);return}
    if(/^name$/i.test(el.name||'')||/^name$/i.test(el.id||'')){n+=set(el,P.full);return}
    var hay=[el.name,el.id,el.placeholder,el.getAttribute('aria-label')];
    try{if(el.labels&&el.labels.length)hay.push(el.labels[0].innerText)}catch(e){}
    var lab=el.closest?el.closest('label'):null;
    if(lab)hay.push(lab.innerText);
    hay=hay.join(' ');
    for(var i=0;i<F.length;i++){if(F[i][0].test(hay)){n+=set(el,P[F[i][1]]);return}}
  });
  alert(n+' field(s) filled. Review before submitting.');
}
jdAutofill();
