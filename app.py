# app.py
import gradio as gr
import math

def evaluate_expression(expr):
    """
    Convert calculator-style expression to a python expression using math,
    balance parentheses and evaluate. Returns value or "Error: ..." string.
    """
    try:
        if expr is None:
            return ""
        expr = str(expr).strip()
        if expr == "":
            return ""

        # basic replacements
        expr = expr.replace("×", "*")     # in case you have this symbol
        # keep '*' and '/' and '+' '-' as-is
        expr = expr.replace("^", "")   # power operator

        # function replacements (these add extra '(' so we will balance later)
        expr = expr.replace("sin(", "math.sin(math.radians(")
        expr = expr.replace("cos(", "math.cos(math.radians(")
        expr = expr.replace("tan(", "math.tan(math.radians(")
        expr = expr.replace("log10(", "math.log10(")
        expr = expr.replace("ln(", "math.log(")
        expr = expr.replace("sqrt(", "math.sqrt(")
        expr = expr.replace("fact(", "math.factorial(")
        expr = expr.replace("antilog10(", "(10**")
        expr = expr.replace("e^(", "math.exp(")   # e^(x) -> math.exp(x)

        # balance parentheses by appending missing ')' at the end
        opens = expr.count("(")
        closes = expr.count(")")
        if opens > closes:
            expr = expr + (")" * (opens - closes))

        # Evaluate with only math allowed in global namespace
        result = eval(expr, {"math": math})
        # show ints without ".0"
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return result
    except Exception as e:
        return f"Error: {e}"

# pressed button handler: receives the button label (string) and current state
def press_button(btn_label, state):
    expr = state or ""
    if btn_label == "C":
        new = ""
    elif btn_label == "⌫":
        new = expr[:-1]
    elif btn_label == "=":
        res = evaluate_expression(expr)
        new = str(res)
    else:
        # Append the literal button text to expression (buttons include '(' where needed)
        new = expr + btn_label
    # return values for both display and state (so both update)
    return new, new

# --- Gradio UI ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("<h2 style='text-align:center; color:#2E86C1;'>🧮 Scientific Calculator</h2>")
    display = gr.Textbox(label="Display", value="", interactive=False)
    state = gr.State("")  # store the current expression

    # buttons layout (functions use "(" so user can type argument then ')' or rely on auto-balance)
    buttons = [
        ["7","8","9","/","sin("],
        ["4","5","6","*","cos("],
        ["1","2","3","-","tan("],
        ["0",".","=","+","log10("],
        ["(",")","C","ln(","e^("],
        ["sqrt(","^","fact(","antilog10("],
        ["⌫"]  # backspace
    ]

    for row in buttons:
        with gr.Row():
            for b in row:
                btn = gr.Button(b, size="lg")
                # create a hidden textbox with the button label so gradio passes the label string
                hidden = gr.Textbox(value=b, visible=False)
                btn.click(press_button, inputs=[hidden, state], outputs=[display, state])

# Important for Hugging Face Spaces
if _name_ == "_main_":
    demo.launch(server_name="0.0.0.0", server_port=7860)
