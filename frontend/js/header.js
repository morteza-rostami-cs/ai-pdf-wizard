// loading header
export async function loadHeader() {
  const res = await fetch("./partials/header.html");

  // insert into doc
  document.getElementById("header").innerHTML = await res.text();
}
