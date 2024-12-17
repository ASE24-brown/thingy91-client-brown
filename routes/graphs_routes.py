from decorators import login_required
from flask import render_template

@login_required
def graphs():
    """
    Renders the device coupling page.

    Returns:
        str: The rendered HTML for the coupling page.
    """
    return render_template('graphs.html')