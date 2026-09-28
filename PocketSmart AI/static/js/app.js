async function updateAuthLink() {

    const link =
        document.getElementById(
            "authLink"
        );


    if (!link) {
        return;
    }


    try {

        const response =
            await fetch(
                "/api/session-info"
            );


        const session =
            await response.json();


        if (session.logged_in) {

            link.textContent =
                "Logout";

            link.href = "#";


            link.onclick =
                async function(event) {

                    event.preventDefault();


                    await fetch(
                        "/api/logout",
                        {
                            method: "POST"
                        }
                    );


                    location.href = "/";

                };

        }

    } catch (error) {

        console.error(
            "Session check failed:",
            error
        );

    }

}


function escapeHtml(value) {

    return String(
        value ?? ""
    ).replace(
        /[&<>"']/g,
        function(character) {

            return {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;"
            }[character];

        }
    );

}


updateAuthLink();