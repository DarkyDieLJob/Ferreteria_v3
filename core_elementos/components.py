from reactpy import component, html

@component
def hello_world(recipient: str):
    return html.div(
        {
            "className": "card flex justify-center items-center",
            "style":{
                "background-color":"grey",
                "padding":"5px",
                }
        },
        html.div(
            {
                "className": "card-body d-flex flex-column align-items-center",
            },
            html.h1(
                {
                    "className": "text-3xl font-bold underline text-clifford",
                },
                recipient,
            ),
            html.label("Label 1"),
            html.input(
                {
                    "className":"rounded form-control",
                    "type":"number",
                    "step":"0.1",
                    "placeholder": "label 1",
                },
            ),

            html.label("Label 2"),
            html.input(
                {
                    "type":"text",
                    "placeholder": "label 2",
                },
            ),

            html.label("Label 3"),
            html.input(
                {
                    "type":"number",
                    "placeholder": "label 3",
                },
            ),

            html.label("Label 4"),
            html.input(
                {
                    "type":"file",
                },
            ),

            html.button(
                {"className": "btn btn-primary"},
                recipient,
            ),
        ),
    )
