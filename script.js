// Loader
window.onload=()=>document.getElementById("loader").style.display="none";

// Counter animation
document.querySelectorAll("[data-count]").forEach(el=>{
  let target=+el.dataset.count,i=0;
  let t=setInterval(()=>{el.innerText=++i;if(i>=target)clearInterval(t)},20);
});

// Search
document.getElementById("carSearch").addEventListener("keyup",function(){
  let f=this.value.toLowerCase();
  document.querySelectorAll("#carList li").forEach(li=>{
    li.style.display=li.textContent.toLowerCase().includes(f)?"":"none";
  });
});

// EMI
function calculateEMI(){
  const P=amount.value,R=rate.value/12/100,N=months.value;
  if(!P||!R||!N){emiResult.innerText="Enter all details";return;}
  const emi=(P*R*Math.pow(1+R,N))/(Math.pow(1+R,N)-1);
  emiResult.innerText="Approx EMI: ₹"+Math.round(emi)+"/month";
}

// WhatsApp + Sheet
document.getElementById("leadForm").addEventListener("submit",function(e){
  e.preventDefault();
  const msg=`Hello Vaishnavi Enterprises 👋
Name: ${name.value}
Phone: ${phone.value}
Requirement: ${type.value}
Details: ${car.value||"Not specified"}`;
  window.open("https://wa.me/919000225736?text="+encodeURIComponent(msg));
});

// Language toggle
let alt=false;
function toggleLang(){
  alt=!alt;
  document.querySelector(".hero h1").innerHTML=alt?
  "ہم آپ کی مدد کے لیے حاضر ہیں":
  "Get What You Need<br>Without Delay";
}

// Help prompt
setTimeout(()=>document.getElementById("helpPrompt").style.display="block",5000);
