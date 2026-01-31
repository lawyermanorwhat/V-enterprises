// Live car search
document.getElementById("carSearch").addEventListener("keyup", function () {
  let filter = this.value.toLowerCase();
  let items = document.querySelectorAll("#carList li");
  items.forEach(li => {
    li.style.display = li.textContent.toLowerCase().includes(filter) ? "" : "none";
  });
});

function calculateEMI() {
  const P = amount.value;
  const R = rate.value / 12 / 100;
  const N = months.value;
  if (!P || !R || !N) return;
  const emi = (P * R * Math.pow(1 + R, N)) / (Math.pow(1 + R, N) - 1);
  emiResult.innerText = "Estimated EMI: ₹" + Math.round(emi);
}

function sendForm(e) {
  e.preventDefault();
  const msg = `Name: ${name.value}, Phone: ${phone.value}, Car: ${car.value}, Type: ${type.value}`;
  window.open("https://wa.me/919000225736?text=" + encodeURIComponent(msg));
}
