def get_email_body(table_str: str, subject: str) -> str:
    """Monta o corpo do email

    Args:
        subject (str): _description_
        body (str): _description_

    Returns:
        bool: _description_
    """
    return f"""
    <html>
        <head>
            <style>
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-family: Arial, sans-serif;
                }}
                th, td {{
                    border: 1px solid #dddddd;
                    text-align: left;
                    padding: 8px;
                }}
                th {{
                    background-color: #f2f2f2;
                    color: #333333;
                    font-weight: bold;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                tr:hover {{
                    background-color: #f1f1f1;
                }}
            </style>
        </head>
        <body>
            <h2 style="font-family: Arial, sans-serif; color: #333333;">Relatório de {subject}</h2>
            {table_str}
        </body>
    </html>
    """
