function addItem() {

    const row =
        document.createElement(
            "div"
        );


    row.className =
        "item-row";


    row.innerHTML = `
        <input
            name="category"
            placeholder="Item category"
        >

        <input
            name="quantity"
            type="number"
            value="1"
            min="1"
        >
    `;


    document
        .getElementById("items")
        .appendChild(row);

}


function renderResult(data) {

    const element =
        document.getElementById(
            "result"
        );


    const allocations =
        (data.allocations || [])
            .map(
                allocation => `
                    <div class="allocation">

                        <span>
                            ${escapeHtml(
                                allocation.category
                            )}
                        </span>

                        <span>
                            ₹${Number(
                                allocation.amount || 0
                            ).toLocaleString(
                                "en-IN"
                            )}
                        </span>

                        <span>
                            ${Number(
                                allocation.percentage || 0
                            ).toFixed(1)}%
                        </span>

                    </div>
                `
            )
            .join("");


    const recommendations =
        (data.recommendations || [])
            .map(
                recommendation => `

                    <article class="rec-card">

                        <span class="tag">
                            ${escapeHtml(
                                recommendation.platform
                            )}
                        </span>

                        <h3>
                            ${escapeHtml(
                                recommendation.name
                            )}
                        </h3>

                        <p>
                            ${escapeHtml(
                                recommendation.reason
                            )}
                        </p>

                        <b>
                            ₹${Number(
                                recommendation.price || 0
                            ).toLocaleString(
                                "en-IN"
                            )}

                            ×

                            ${Number(
                                recommendation.quantity || 1
                            )}
                        </b>

                        <p>
                            Estimated total:
                            ₹${Number(
                                recommendation.estimated_total || 0
                            ).toLocaleString(
                                "en-IN"
                            )}
                        </p>

                        <a
                            href="${escapeHtml(
                                recommendation.url
                            )}"
                            target="_blank"
                            rel="noopener"
                        >
                            Open provider search ↗
                        </a>

                    </article>

                `
            )
            .join("");


    const notes =
        (data.ai_notes || [])
            .map(
                note => `
                    <li>
                        ${escapeHtml(note)}
                    </li>
                `
            )
            .join("");


    element.innerHTML = `

        <section class="result">

            <div class="summary">

                <h2>
                    ${escapeHtml(
                        data.summary
                    )}
                </h2>

                <p>

                    Budget:

                    <b>
                        ₹${Number(
                            data.budget
                        ).toLocaleString(
                            "en-IN"
                        )}
                    </b>

                    ·

                    Estimated:

                    <b>
                        ₹${Number(
                            data.estimated_total
                        ).toLocaleString(
                            "en-IN"
                        )}
                    </b>

                    ·

                    Remaining:

                    <b>
                        ₹${Number(
                            data.remaining_budget
                        ).toLocaleString(
                            "en-IN"
                        )}
                    </b>

                </p>

            </div>


            <h2>
                Budget allocation
            </h2>

            ${
                allocations ||
                "<p>No allocation returned.</p>"
            }


            <h2>
                Recommendations
            </h2>


            <div class="recommendation-grid">

                ${
                    recommendations ||
                    "<p>No matching recommendations.</p>"
                }

            </div>


            ${
                notes
                    ? `
                        <h2>Notes</h2>

                        <ul>
                            ${notes}
                        </ul>
                    `
                    : ""
            }


            <p>

                <small>

                    Source mode:
                    ${escapeHtml(
                        data.source_mode
                    )}

                    .

                    Provider links are
                    search links. Verify
                    live price and
                    availability before
                    purchase.

                </small>

            </p>

        </section>

    `;

}


async function submitJSON(
    endpoint,
    payload
) {

    const result =
        document.getElementById(
            "result"
        );


    result.innerHTML = `
        <div class="loading">
            Generating recommendations...
        </div>
    `;


    try {

        const response =
            await fetch(
                endpoint,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            payload
                        )
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            result.innerHTML = `
                <div class="error">
                    ${escapeHtml(
                        data.detail ||
                        "Request failed."
                    )}
                </div>
            `;

            return;

        }


        renderResult(data);

    } catch (error) {

        result.innerHTML = `
            <div class="error">
                Unable to connect to server.
                Make sure the FastAPI server
                is running.
            </div>
        `;

    }

}


function setupHome() {

    document
        .getElementById("homeForm")
        .addEventListener(
            "submit",
            function(event) {

                event.preventDefault();


                const form =
                    new FormData(
                        event.target
                    );


                const categories =
                    [
                        ...document.querySelectorAll(
                            'input[name="category"]'
                        )
                    ];


                const quantities =
                    [
                        ...document.querySelectorAll(
                            'input[name="quantity"]'
                        )
                    ];


                const items =
                    categories
                        .map(
                            (category, index) => ({

                                category:
                                    category.value,

                                quantity:
                                    Number(
                                        quantities[
                                            index
                                        ].value
                                    )

                            })
                        )
                        .filter(
                            item =>
                                item.category
                        );


                submitJSON(
                    "/api/generate-home",
                    {
                        budget:
                            Number(
                                form.get(
                                    "budget"
                                )
                            ),

                        rooms:
                            form
                                .get("rooms")
                                .split(",")
                                .map(
                                    room =>
                                        room.trim()
                                )
                                .filter(
                                    Boolean
                                ),

                        style:
                            form.get(
                                "style"
                            ),

                        city:
                            form.get(
                                "city"
                            ),

                        items
                    }
                );

            }
        );

}


function setupParty() {

    document
        .getElementById("partyForm")
        .addEventListener(
            "submit",
            function(event) {

                event.preventDefault();


                const form =
                    new FormData(
                        event.target
                    );


                submitJSON(
                    "/api/generate-party",
                    {

                        budget:
                            Number(
                                form.get(
                                    "budget"
                                )
                            ),

                        guests:
                            Number(
                                form.get(
                                    "guests"
                                )
                            ),

                        event_type:
                            form.get(
                                "event_type"
                            ),

                        venue:
                            form.get(
                                "venue"
                            ),

                        city:
                            form.get(
                                "city"
                            ),

                        preferences:
                            form.get(
                                "preferences"
                            )

                    }
                );

            }
        );

}


function setupJewelry() {

    document
        .getElementById("jewelryForm")
        .addEventListener(
            "submit",
            async function(event) {

                event.preventDefault();


                const result =
                    document.getElementById(
                        "result"
                    );


                result.innerHTML = `
                    <div class="loading">
                        Analyzing your
                        jewelry plan...
                    </div>
                `;


                try {

                    const response =
                        await fetch(
                            "/api/generate-jewelry",
                            {
                                method: "POST",

                                body:
                                    new FormData(
                                        event.target
                                    )
                            }
                        );


                    const data =
                        await response.json();


                    if (!response.ok) {

                        result.innerHTML = `
                            <div class="error">
                                ${escapeHtml(
                                    data.detail ||
                                    "Request failed."
                                )}
                            </div>
                        `;

                        return;

                    }


                    renderResult(data);

                } catch (error) {

                    result.innerHTML = `
                        <div class="error">
                            Unable to connect
                            to server.
                        </div>
                    `;

                }

            }
        );

}