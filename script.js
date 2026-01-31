// Search filter
document.getElementById("carSearch").addEventListener("keyup", function(){
  let f=this.value.toLowerCase();
  document.querySelectorAll("#carList li").forEach(li=>{
    li.style.display=li.textContent.toLowerCase().includes(f)?"":"none";
  });
});

// EMI
function calculateEMI(){
  const P=amount.value;
  const R=rate.value/12/100;
  const N=months.value;
  if(!P||!R||!N){emiResult.innerText="Enter all details";return;}
  const emi=(P*R*Math.pow(1+R,N))/(Math.pow(1+R,N)-1);
  emiResult.innerText="Approx EMI: ₹"+Math.round(emi)+"/month";
}

// Loan form + analytics
function sendForm(e){
  e.preventDefault();
  if(window.gtag){gtag('event','loan_form_submit');}
  const msg=`Name:${name.value}, Phone:${phone.value}, Car:${car.value}, Type:${type.value}`;
  window.open("https://wa.me/919000225736?text="+encodeURIComponent(msg));
}

// Language toggle
let isAlt=false;
function toggleLang(){
  isAlt=!isAlt;
  document.querySelector(".hero h1").innerHTML=isAlt?
    "اپنی گاڑی جلدی حاصل کریں":
    "Get Your Car<br>Faster Than You Think";
}

// Help prompt
setTimeout(()=>{
  document.getElementById("helpPrompt").style.display="block";
},5000);
