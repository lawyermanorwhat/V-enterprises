document.getElementById("leadForm").addEventListener("submit", function(e){
  e.preventDefault();

  const name = document.getElementById("name").value;
  const phone = document.getElementById("phone").value;
  const service = document.getElementById("service").value;

  const msg = `Hi, I am ${name}. I need ${service}. Phone: ${phone}`;

  window.open(
    `https://wa.me/919000225736?text=${encodeURIComponent(msg)}`,
    "_blank"
  );
});
