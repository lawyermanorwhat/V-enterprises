function calculateEMI() {
  const amount = document.getElementById("amount").value;
  const rate = document.getElementById("rate").value / 12 / 100;
  const months = document.getElementById("months").value;

  if (!amount || !rate || !months) return;

  const emi = (amount * rate * Math.pow(1 + rate, months)) /
              (Math.pow(1 + rate, months) - 1);

  document.getElementById("emiResult").innerText =
    `Estimated EMI: ₹${emi.toFixed(2)}`;
}

document.getElementById("leadForm").addEventListener("submit", function(e) {
  e.preventDefault();

  const name = document.getElementById("name").value;
  const phone = document.getElementById("phone").value;
  const service = document.getElementById("service").value;

  const msg = `Hi, my name is ${name}. I need ${service}. My number is ${phone}.`;

  window.open(
    `https://wa.me/919000225736?text=${encodeURIComponent(msg)}`,
    "_blank"
  );
});

