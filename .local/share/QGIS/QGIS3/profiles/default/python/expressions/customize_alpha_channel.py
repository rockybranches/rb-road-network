from qgis.core import *
from qgis.gui import *

@qgsfunction(args='auto', group='Custom', referenced_columns=[])
def customize_alpha_channel(symbol_color, value, vmin, vmax, feature, parent, context):
    """
    For a given symbol color, Set the alpha channel based on the given value_column_name.
    <h4>Syntax</h4>
    <div>
        <b>customize_alpha_channel</b>(<i>symbol_color</i>, <i>value_column_name</i>)
    </div>
    
    <table>
    <h4>Parameters</h4>
    <tr><td>: param symbol_color:</td><td>The color of the layer style's symbol.</td></tr>
    <tr><td>: param value:</td><td>Column to be used for the alpha channel.</td></tr>
    <tr><td>: param vmin:</td><td>Minimum of column to be used for the alpha channel.</td></tr>
    <tr><td>: param vmax:</td><td>Maximum of column to be used for the alpha channel.</td></tr>
    <tr><td>: returns:</td><td>The resulting color with a new alpha value.</td></tr>
    </table>
    """
    c = symbol_color
    c.alpha = int(255 * (value - vmin) / (vmax - vmin))
    return c
