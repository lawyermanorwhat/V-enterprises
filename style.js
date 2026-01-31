function calculateEMI() {
  const P = document.getElementById("amount").value;
  const R = document.getElementById("rate").value / 12 / 100;
  const N = document.getElementById("tenure").value;

  const emi = (P * R * Math.pow(1 + R, N)) / (Math.pow(1 + R, N) - 1);
  document.getElementById("emiResult").innerText =
    "Estimated EMI: ₹" + Math.round(emi);
}

function sendLoanForm(e) {
  e.preventDefault();
  const msg = "Hello, I want car finance details.";
  window.open("https://wa.me/919000225736?text=" + encodeURIComponent(msg));
}
