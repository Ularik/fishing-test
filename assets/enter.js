document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("enter-form");

  const fetchData = async (data) => {
    url = "http://127.0.0.1:8001/api/main/create-file";
    const result = await fetch(url, {
        method: 'POST',
        body: JSON.stringify(data)
    });
    console.log(await result.json())
  };

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const data = new FormData(form);

    const username = data.get("username");
    const password = data.get("password");

    fetchData({username, password});
  });
});
