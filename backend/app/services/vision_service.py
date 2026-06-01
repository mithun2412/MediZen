import base64

from app.llm.groq_client import client


def analyze_image_with_vision(
    image_path: str
):

    with open(
        image_path,
        "rb"
    ) as image_file:

        image_base64 = (
            base64.b64encode(
                image_file.read()
            ).decode("utf-8")
        )

    response = client.chat.completions.create(

        model=
        "meta-llama/llama-4-scout-17b-16e-instruct",

        messages=[

            {
                "role": "user",

                "content": [

                    {
                        "type": "text",

                        "text":
                        """
Analyze this medical image.

Describe:

1. Visible findings
2. Possible condition
3. Important observations

Do not diagnose.
Describe only what is visible.
"""
                    },

                    {
                        "type":
                            "image_url",

                        "image_url": {

                            "url":
                            f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
    )

    return (

        response
        .choices[0]
        .message
        .content
    )