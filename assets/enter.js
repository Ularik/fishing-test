document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("enter-form");

  const fetchData = async (data) => {
    const url = "/api/main/create-file"; // относительный путь

    const result = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
        body: JSON.stringify(data),
        credentials: "same-origin"
      });

      console.log(await result.json());
  };

  const viewErrorMess = () => {
    const message = document.querySelector('.error-mess');
    message.style.display = 'block';
    const inputFields = document.querySelectorAll('.field input');
    inputFields.forEach(input => {
        input.style.borderBottom = '1px solid rgb(215, 73, 66)';
    });
  };

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    viewErrorMess();
    const data = new FormData(form);

    const username = data.get("username");
    const password = data.get("password");

    fetchData({username, password});
  });
});
